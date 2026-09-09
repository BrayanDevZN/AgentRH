from src.logs.log import LayerLogger
logger = LayerLogger("database").build()


"""
Controla a tabela resumes
"""
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload
from src.database.models.resumes import Resumes
from typing import Literal
class ResumesDbError(Exception):
    pass
class ResumesDb:

    def __init__(self, session_engine:async_sessionmaker)-> None:

        self.eng = session_engine


    #Insere na tabela
    async def insert(self, user_id:int, vancancie_id:int, pdf:bytes,
                     status:Literal["aproved", "recuse", "pending"] = "pending",
                     reason:str = "null") -> Resumes:

        try:

            logger.info(f"Criando curriculo do usuario {user_id}...")

            async with self.eng.begin() as session:

                #Objeto de resumes preenchido
                instance = Resumes(user_id=user_id, vancancie_id=vancancie_id, pdf=pdf,
                                   status=status, reason=reason)

                session.add(instance)

            return instance


        except Exception as e:

            logger.error(e)
            raise ResumesDbError(e)

    async def select(self, search:Literal["id", "user_id", "vancancie_id", "status"],
                     value:str|int) -> Resumes|None:


        try:

            logger.info(f"Buscando curriculo pelo {search}...")

            items = {
                "id": Resumes.id,
                "user_id": Resumes.user_id,
                "vancancie_id": Resumes.vancancie_id,
                "status": Resumes.status
            }

            async with self.eng.begin() as session:

                query = select(Resumes).options(selectinload(Resumes.vancancie)).where(items[search] == value)

                result = await session.execute(query)

                result = result.scalars().first()

            return result

        except Exception as e:

            logger.error(e)
            raise ResumesDbError(e)

    async def update(self, search:Literal["id", "user_id", "vancancie_id"], field:int,
                     set:Literal["pdf", "status", "reason"], value:bytes|str) -> Resumes|None:


        try:

            logger.info(f"Atualizando {set} do curriculo...")

            items = {
                "id": Resumes.id,
                "user_id": Resumes.user_id,
                "vancancie_id": Resumes.vancancie_id
            }

            async with self.eng.begin() as session:

                #pega o curriculo e usa lock
                query = select(Resumes).options(selectinload(Resumes.vancancie)).where(items[search] == field).with_for_update()
                resume = await session.scalar(query)

                if resume is None:

                    return None


                match set:

                    case "pdf":
                        resume.pdf = value
                    case "status":
                        resume.status = value
                    case "reason":
                        resume.reason = value

            return resume

        except Exception as e:

            logger.error(e)
            raise ResumesDbError(e)


    async def delete(self, id:int) -> None:

        try:

            logger.info("Deletando curriculo...")

            async with self.eng.begin() as session:

                query = delete(Resumes).where(Resumes.id == id)

                await session.execute(query)


        except Exception as e:

            logger.error(e)
            raise ResumesDbError(e)
