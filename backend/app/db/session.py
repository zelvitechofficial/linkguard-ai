from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
import re

# Fix up the database URL for async pg since most providers give a synchronous URL
db_url = settings.DATABASE_URL
if db_url:
    # 1. Standardize prefix to postgresql+asyncpg://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # 2. NUCLEAR OPTION: Strip ALL query parameters from the URL entirely.
    # This prevents any 'sslmode', 'channel_binding' or other trash from leaking in.
    db_url = db_url.split('?')[0]

# CRITICAL: asyncpg is extremely sensitive to 'sslmode' and other standard PG env vars.
# We purge them from the environment entirely to ensure no overrides happen.
import os
for env_key in ["sslmode", "PGSSLMODE", "channel_binding", "target_session_attrs"]:
    if env_key in os.environ:
        print(f"Purging incompatible env var: {env_key}")
        del os.environ[env_key]

# For debugging purposes on Render - will be visible in logs
if db_url and "asyncpg" in db_url:
    # Mask password for safety
    safe_url = re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", db_url)
    print(f"DEBUG FINAL DSN (Nuclear): {safe_url}")

if not db_url:
    db_url = "sqlite+aiosqlite:///./test.db"

# Create async engine for PostgreSQL
# We use connect_args to explicitly set SSL to 'require' which is supported by asyncpg 0.29.0+
# This bypasses the need for it to be in the URL string itself.
engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    connect_args={"ssl": "require"}
)

# Create session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
