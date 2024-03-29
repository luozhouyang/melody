from typing import Annotated, TypeAlias

from databases import Database
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import database_settings

engine = create_async_engine(database_settings.database_uri)


async def database_session():
    async with AsyncSession(engine) as session:
        yield session


DatabaseSession: TypeAlias = Annotated[AsyncSession, Depends(database_session)]


database = Database(
    database_settings.database_uri,
    min_size=database_settings.conn_pool_min_size,
    max_size=database_settings.conn_pool_max_size,
)
