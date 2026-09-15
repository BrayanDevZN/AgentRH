from src.logs.log import LayerLogger
logger = LayerLogger("database").build()


"""
Controla a tabela resumes
"""
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload
from src.database.models.resumes import Resumes
from src.database.repository.serializer import model_to_dict
from typing import Literal
class ResumesDbError(Exception):
    pass
class ResumesDb:

    def __init__(self, session_engine:async_sessionmaker)-> None:

        self.eng = session_engine


    #Insere na tabela
    async def insert(self, user_id:int, vancancie_id:int, pdf:bytes,
                     status:Literal["aproved", "recuse", "pending"] = "pending",
                     reason:str = "null") -> dict:

        try:

            logger.info(f"Criando curriculo do usuario {user_id}...")

            async with self.eng.begin() as session:

                #Objeto de resumes preenchido
                instance = Resumes(user_id=user_id, vancancie_id=vancancie_id, pdf=pdf,
                                   status=status, reason=reason)

                session.add(instance)
                await session.flush()
                await session.refresh(instance)

                return model_to_dict(instance)


        except Exception as e:

            logger.error(e)
            raise ResumesDbError(e)

    async def select(self, user_id:int|None=None, vancancie_id:int|None=None, id:int|None=None,
                     get_all:bool=False) -> dict|list[dict]|None:


        try:

            logger.info(f"Buscando curriculo...")

            async with self.eng.begin() as session:

                query = select(Resumes).options(selectinload(Resumes.vancancie))

                if not get_all:
                    filters = []

                    if id is not None:
                        filters.append(Resumes.id == id)

                    if user_id is not None:
                        filters.append(Resumes.user_id == user_id)

                    if vancancie_id is not None:
                        filters.append(Resumes.vancancie_id == vancancie_id)

                    query = query.where(*filters)

                result = await session.execute(query)

                if get_all:
                    resumes = result.scalars().all()
                    return [model_to_dict(resume) for resume in resumes]

                resume = result.scalars().first()
                return model_to_dict(resume) if resume is not None else None

        except Exception as e:

            logger.error(e)
            raise ResumesDbError(e)

    async def update(self, search:Literal["id", "user_id", "vancancie_id"], field:int,
                     set:Literal["pdf", "status", "reason"], value:bytes|str) -> dict:


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

                    return {}


                match set:

                    case "pdf":
                        resume.pdf = value
                    case "status":
                        resume.status = value
                    case "reason":
                        resume.reason = value

                await session.flush()
                await session.refresh(resume)
                return model_to_dict(resume)

        except Exception as e:

            logger.error(e)
            raise ResumesDbError(e)


    async def delete(self, id:int) -> dict:

        try:

            logger.info("Deletando curriculo...")

            async with self.eng.begin() as session:

                query = delete(Resumes).where(Resumes.id == id)

                result = await session.execute(query)
                return {"deleted": result.rowcount > 0}


        except Exception as e:

            logger.error(e)
            raise ResumesDbError(e)
