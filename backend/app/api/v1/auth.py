from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings
from app.core.logger import setup_logger
from app.services.clerk_service import ClerkService

logger = setup_logger(__name__)
security = HTTPBearer()

import httpx

# Cache for JWKS to avoid redundant network calls
_jwks_cache = None

async def get_jwks(force_refresh=False):
    global _jwks_cache
    if _jwks_cache is None or force_refresh:
        if not settings.CLERK_JWKS_URL:
            return None
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(settings.CLERK_JWKS_URL)
                response.raise_for_status()
                _jwks_cache = response.json()
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            return None
    return _jwks_cache

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to verify the Clerk JWT token.
    Tries JWKS first with robust key rotation handling, then falls back to CLERK_JWT_PUBLIC_KEY.
    """
    jwks = await get_jwks()
    
    decode_options = {
        "verify_signature": True,
        "verify_aud": False,
        "verify_iss": False,
        "verify_exp": True,
        "verify_nbf": False,
        "verify_at_hash": False
    }
    
    if jwks:
        try:
            # Extract header to find the kid (Key ID)
            unverified_header = jwt.get_unverified_header(token.credentials)
            kid = unverified_header.get("kid")
            
            # Find the matching key in JWKS
            rsa_key = next((key for key in jwks.get("keys", []) if key.get("kid") == kid), None)
            
            # If the kid is not found in cache, JWKS might have rotated.
            if not rsa_key:
                logger.info("JWKS key 'kid' not found in cache, forcing refresh.")
                jwks = await get_jwks(force_refresh=True)
                if jwks:
                    rsa_key = next((key for key in jwks.get("keys", []) if key.get("kid") == kid), None)
            
            if rsa_key:
                try:
                    payload = jwt.decode(
                        token.credentials,
                        rsa_key,
                        algorithms=["RS256"],
                        options=decode_options
                    )
                    return payload
                except jwt.ExpiredSignatureError:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication token has expired. Please log in again."
                    )
                except jwt.JWTError as e:
                    logger.warning(f"JWKS validation error: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Token validation failed (JWKS): {str(e)}"
                    )
        except Exception as e:
            logger.warning(f"JWKS verification setup failed, trying static key: {e}")

    # Fallback to static public key if configured
    if settings.CLERK_JWT_PUBLIC_KEY:
        try:
            public_key = settings.CLERK_JWT_PUBLIC_KEY.replace('\\n', '\n')
            payload = jwt.decode(
                token.credentials, 
                public_key, 
                algorithms=["RS256"],
                options=decode_options
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired. Please log in again."
            )
        except jwt.JWTError as e:
            logger.error(f"Static JWT Verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed (Static): {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected Static JWT Verification failed: {str(e)}")

    # Debug Mock Mode
    if settings.DEBUG:
        try:
            # Try to get unverified claims for better multi-account testing in DEBUG mode
            unverified_claims = jwt.get_unverified_claims(token.credentials)
            sub = unverified_claims.get("sub", "mock_user_id")
            email = unverified_claims.get("email", settings.ADMIN_EMAIL)
            
            logger.warning(f"Authentication verification failed/not configured. Using UNVERIFIED token data for mock user: {email}")
            return {"sub": sub, "email": email}
        except Exception:
            logger.warning("Authentication failed. Using MOCK user in DEBUG mode.")
            return {"sub": "mock_user_id", "email": settings.ADMIN_EMAIL}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or completely invalid authentication credentials. JWKS or Static keys could not verify it.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_user_with_email(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Ensures that the user object has an 'email' field.
    Fetches it from Clerk API if it's missing from the JWT.
    """
    if not current_user.get("email"):
        sub = current_user.get("sub")
        if sub:
            email = await ClerkService.fetch_user_email(sub)
            if email:
                current_user["email"] = email
            else:
                current_user["email"] = "unset@example.com"
        else:
            current_user["email"] = "unset@example.com"
    return current_user

async def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to verify if the current user is an admin.
    Checks the 'email' claim against settings.ADMIN_EMAIL.
    """
    user_email = current_user.get("email")
    sub = current_user.get("sub")
    
    # Clerk session tokens often lack the 'email' claim by default.
    if not user_email and sub:
        user_email = await ClerkService.fetch_user_email(sub)
        if user_email:
            current_user["email"] = user_email  # Cache it for the rest of the request
    
    if not user_email or user_email.lower() != settings.ADMIN_EMAIL.lower():
        logger.warning(f"Unauthorized admin access attempt by: {user_email} (sub: {sub})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have administrative privileges."
        )
        
    return current_user
