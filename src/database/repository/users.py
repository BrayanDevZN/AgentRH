from src.logs.log import LayerLogger
logger = LayerLogger("database").build()


"""
Controla a tabela users
"""
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.database.models.users import Users
from src.database.repository.serializer import model_to_dict
from typing import Literal
class UsersDbError(Exception):
    pass
class UsersDb:

    def __init__(self, session_engine:async_sessionmaker)-> None:

        self.eng = session_engine


    #Insere na tabela
    async def insert(self, name:str,age:int, email:str, password:str, cpf:str, gender:Literal["male", "female", "other"],
                     permission:bool = False, role:Literal["user", "admin"] = "user"
                     )-> dict:

        try:

            logger.info(f"Criando usuario {name} {role} com a permissão {"Concedida" if permission else "Negada"}...")

            async with self.eng.begin() as session:

                #Objeto de users preenchido
                instance = Users(name=name, email=email,password=password, cpf=cpf,
                                 gender=gender, permission=permission, role=role,
                                 age=age
                                 )

                session.add(instance)
                await session.flush()
                await session.refresh(instance)

                return model_to_dict(instance)


        except Exception as e:

            logger.error(e)
            raise UsersDbError(e)

    async def select(self, search:Literal["public_id", "email", "id", "cpf"], value:str|int) -> dict|None:


        try:

            logger.info(f"Buscando usuario pelo {search}...")

            items = {
                "public_id": Users.public_id,
                "email": Users.email,
                "id": Users.id,
                "cpf": Users.cpf
            }

            async with self.eng.begin() as session:

                query = select(Users).where(items[search] == value)

                result = await session.execute(query)

                result = result.scalars().first()

                return model_to_dict(result) if result is not None else None

        except Exception as e:

            logger.error(e)
            raise UsersDbError(e)

    async def update(self,search:Literal["public_id", "email", "cpf", "id"] , field:str|int,
                     set:Literal["password", "permission", "role"], value:str|bool) -> dict:


        try:

            logger.info(f"Atualziando {set} do usuario...")

            async with self.eng.begin() as session:

                #pega o usuario e usa lock
                items = {
                    "public_id": Users.public_id,
                    "email": Users.email,
                    "id": Users.id,
                    "cpf": Users.cpf
                }
                query = select(Users).where(items[search] == field).with_for_update()
                user = await session.scalar(query)

                if user is None:

                    return {}


                match set:

                    case "password":
                        user.password = value
                    case "permission":
                        user.permission = value
                    case "role":
                        user.role = value

                await session.flush()
                await session.refresh(user)
                return model_to_dict(user)

        except Exception as e:

            logger.error(e)
            raise UsersDbError(e)


    async def delete(self, public_id:str) -> dict:

        try:

            logger.info("Deletando usuario...")

            async with self.eng.begin() as session:

                query = delete(Users).where(Users.public_id == public_id)

                result = await session.execute(query)
                return {"deleted": result.rowcount > 0}


        except Exception as e:

            logger.error(e)
            raise UsersDbError(e)


