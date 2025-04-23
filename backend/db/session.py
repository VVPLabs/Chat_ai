from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from config import settings

DATABASE_URL = settings.DATABASE_URL

# SQLAlchemy async engine
engine = create_async_engine(DATABASE_URL, echo=True)


# session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
