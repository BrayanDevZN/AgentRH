from src.logs.log import LayerLogger
logger = LayerLogger("database").build()


"""
cria as tabelas
"""

from sqlalchemy.ext.asyncio import AsyncEngine
from src.database.base import Base

class MigrationDbError(Exception):
    pass


async def migration_db(engine:AsyncEngine) -> None:

    try:
        logger.info("criando tabelas do banco de dados...")

        async with engine.begin() as session:

            await session.run_sync(Base.metadata.create_all)


        logger.info("Criadas com sucesso!!!")