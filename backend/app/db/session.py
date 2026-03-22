from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# Fix up the database URL for async pg since most providers give a synchronous URL
db_url = settings.DATABASE_URL
if db_url:
    # 1. Standardize prefix
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # 2. asyncpg does not support 'sslmode'. It uses 'ssl'.
    # Most cloud providers (Neon/Supabase) include ?sslmode=require
    if "sslmode=" in db_url:
        import urllib.parse as urlparse
        url_parts = list(urlparse.urlparse(db_url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        if "sslmode" in query:
            # Map sslmode=require to ssl=true for asyncpg
            if query["sslmode"] in ["require", "verify-ca", "verify-full"]:
                query["ssl"] = "true"
            del query["sslmode"]
        url_parts[4] = urlparse.urlencode(query)
        db_url = urlparse.urlunparse(url_parts)
    
if not db_url:
    db_url = "sqlite+aiosqlite:///./test.db"

# Create async engine for PostgreSQL
# The URL should be in the format: postgresql+asyncpg://user:password@host:port/dbname
engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True
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
