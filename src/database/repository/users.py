from src.logs.log import LayerLogger
logger = LayerLogger("database").build()


"""
Controla a tabela users
"""
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.database.models.users import Users
from typing import Literal
class UsersDbError(Exception):
    pass
class UsersDb:

    def __init__(self, session_engine:async_sessionmaker)-> None:

        self.eng = session_engine


    #Insere na tabela
    async def insert(self, name:str, email:str, password:str, cpf:str, gender:Literal["male", "female", "other"],
                     permission:bool = False, role:Literal["user", "admin"] = "user"
                     )-> Users:

        try:

            logger.info(f"Criando usaurio {name} {role} com a permissão {"Concedida" if permission else "Negada"}...")

            async with self.eng.begin() as session:

                #Objeto de users preenchido
                instance = Users(name=name, email=email,password=password, cpf=cpf,
                                 gender=gender, permission=permission, role=role
                                 )

                session.add(instance)

            return instance


        except Exception as e:

            logger.error(e)
            raise UsersDbError(e)

    async def select(self, search:Literal["public_id", "email", "id", "cpf"], value:str|int) -> Users|None:


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

            return result

        except Exception as e:

            logger.error(e)
            raise UsersDbError(e)

    async def update(self,search:Literal["public_id", "email", "cpf", "id"] , field:str|int,
                     set:Literal["password", "permission", "role"], value:str|bool) -> Users|None:


        try:

            logger.info(f"Atualziando {set} do usuario...")

            async with self.eng.begin() as session:

                #pega o usuario e usa lock
                query = select(Users).where(search == field).with_for_update()
                user = await session.scalar(query)

                if user is None:

                    return None


                match set:

                    case "password":
                        user.password = value
                    case "permission":
                        user.permission = value
                    case "role":
                        user.role = value

            return user

        except Exception as e:

            logger.error(e)
            raise UsersDbError(e)


    async def delete(self, public_id:str) -> None:

        try:

            logger.info("Deletando usuario...")

            async with self.eng.begin() as session:

                query = delete(Users).where(Users.public_id == public_id)

                await session.execute(query)


        except Exception as e:

            logger.error(e)
            raise UsersDbError(e)





    







        




                


    




                
        