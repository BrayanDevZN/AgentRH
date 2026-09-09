from src.logs.log import LayerLogger
logger = LayerLogger("database").build()


"""
Controla a tabela vancancies
"""
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload
from src.database.models.vancancies import Vancancies
from src.database.models.resumes import Resumes
from typing import Literal
class VancanciesDbError(Exception):
    pass
class VancanciesDb:

    def __init__(self, session_engine:async_sessionmaker)-> None:

        self.eng = session_engine


    #Insere na tabela
    async def insert(self, created_by:int, name:str, description:str) -> Vancancies:

        try:

            logger.info(f"Criando vaga {name}...")

            async with self.eng.begin() as session:

                #Objeto de vancancies preenchido
                instance = Vancancies(created_by=created_by, name=name, description=description)

                session.add(instance)

            return instance


        except Exception as e:

            logger.error(e)
            raise VancanciesDbError(e)

    async def select(self, search:Literal["public_id", "name", "id", "created_by"], value:str|int) -> Vancancies|None:


        try:

            logger.info(f"Buscando vaga pelo {search}...")

            items = {
                "public_id": Vancancies.public_id,
                "name": Vancancies.name,
                "id": Vancancies.id,
                "created_by": Vancancies.created_by
            }

            async with self.eng.begin() as session:

                query = select(Vancancies).options(selectinload(Vancancies.resumes)).where(items[search] == value)

                result = await session.execute(query)

                result = result.scalars().first()

            return result

        except Exception as e:

            logger.error(e)
            raise VancanciesDbError(e)

    async def update(self, search:Literal["public_id", "name", "id", "created_by"], field:str|int,
                     set:Literal["name", "description"], value:str) -> Vancancies|None:


        try:

            logger.info(f"Atualizando {set} da vaga...")

            items = {
                "public_id": Vancancies.public_id,
                "name": Vancancies.name,
                "id": Vancancies.id,
                "created_by": Vancancies.created_by
            }

            async with self.eng.begin() as session:

                #pega a vaga e usa lock
                query = select(Vancancies).options(selectinload(Vancancies.resumes)).where(items[search] == field).with_for_update()
                vancancie = await session.scalar(query)

                if vancancie is None:

                    return None


                match set:

                    case "name":
                        vancancie.name = value
                    case "description":
                        vancancie.description = value

            return vancancie

        except Exception as e:

            logger.error(e)
            raise VancanciesDbError(e)


    async def delete(self, public_id:str) -> None:

        try:

            logger.info("Deletando vaga...")

            async with self.eng.begin() as session:

                query = delete(Vancancies).where(Vancancies.public_id == public_id)

                await session.execute(query)


        except Exception as e:

            logger.error(e)
            raise VancanciesDbError(e)
