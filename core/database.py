import logging

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from core import configs

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{configs.POSTGRES_USER}:"
    f"{configs.POSTGRES_PASSWORD}@"
    f"{configs.POSTGRES_HOSTNAME}:"
    f"{configs.DATABASE_PORT}/"
    f"{configs.POSTGRES_DB}"
)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    echo=configs.SQLALCHEMY_ECHO,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            logging.debug(e)
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            logging.debug("Async DB session closed.")
