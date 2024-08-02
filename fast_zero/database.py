from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session

from fast_zero.settings import Settings

engine = create_engine(Settings().DATABASE_URL)

async_engine = create_async_engine(Settings().DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


async def get_async_session():
    session = AsyncSession(async_engine, expire_on_commit=False)
    yield session
    await session.close()
