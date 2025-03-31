import asyncio
from fastapi import Depends
# from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, TIMESTAMP, Boolean, Integer, Identity, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase
from src.database import engine, get_async_session
from random import randint

class Base(DeclarativeBase):
    pass

class Links_Table(Base):
    __tablename__ = "links_table"

    id = Column(Integer, Identity(start=1, increment=1), primary_key=True, index=True)
    full_link = Column(String, nullable=False,primary_key=True)
    short_link = Column(String, nullable=False)
    clicks = Column(Integer, default=randint(0,100))
    expires_at = Column(DateTime, default= None)

########################
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase

class User(SQLAlchemyBaseUserTableUUID, Base):
    pass


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

########################
# async def create_db_and_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


async def create_db_and_tables():
    retries = 5
    while retries > 0:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            break
        except ConnectionRefusedError:
            retries -= 1
            await asyncio.sleep(5)
    else:
        raise Exception("Could not connect to database after multiple attempts")



# async def get_user_db(session: AsyncSession = Depends(get_async_session)):
#     yield SQLAlchemyUserDatabase(session, User)