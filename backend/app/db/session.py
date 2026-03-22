from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# Fix up the database URL for async pg since most providers give a synchronous URL
db_url = settings.DATABASE_URL
if db_url:
    # 1. Standardize prefix to postgresql+asyncpg://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # 2. Aggressively strip incompatible parameters which crash asyncpg (sslmode, channel_binding)
    import re
    # Remove ?sslmode=... or &sslmode=... and ?channel_binding=... or &channel_binding=...
    db_url = re.sub(r"(\?|&)(sslmode|channel_binding)=[^&]+", "", db_url)
    
    # 3. Ensure we have at least one query param for SSL if it's a cloud DB
    # Most cloud DBs require SSL. We'll add ssl=true if not present.
    if "postgresql+asyncpg" in db_url and "ssl=" not in db_url:
        separator = "&" if "?" in db_url else "?"
        db_url += f"{separator}ssl=true"
    
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
