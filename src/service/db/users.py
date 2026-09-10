"""
Junta o modulo de bancho de dados com sua varivael de ambiente e com cache
"""

from src.service.db.connetion import engine_session
from src.database.manage import ConenctionDb, ControlDb
from src.service.cache import client
from typing import Literal
import json
class ControlUsers:

    def __init__(self)-> None:

        
        self.users = ControlDb(engine=engine_session).users


    #Cria o usaurio e salva o cache
    async def insert(self, name:str,age:int, email:str, password:str, cpf:str, gender:Literal["male", "female", "other"],
                     permission:bool = False, role:Literal["user", "admin"] = "user") -> dict:

        data = locals().copy()
        data.pop("self")

        user = await self.users.insert(**data)

        user["public_id"] = str(user["public_id"])
        user["created_at"] = str(user["created_at"])

        await client.hset(name=f"user:public_id:{user["public_id"]}")
        await client.hset(name=f"user:email:{user["email"]}")
        await client.hset(name=f"user:cpf:{user["cpf"]}")
        await client.hset(name=f"user:id:{user["id"]}")

        return user

    #Le no cache, se existir, retorna, se não, busca no banco, e depois salva cache
    async def select(self, search:Literal["public_id", "email", "id", "cpf"], value:str|int) -> None|dict:

        match search:
            case "public_id":
                name = f"user:public_id:{value}"

            case "email":
                name = f"user:email:{value}"
            case "id":
                name = f"user:id:{value}"
            case "cpf":
                name = f"user:cpf:{value}"


        cache = await client.get(hash=True, name=name)

        if cache is not None:

            return cache

        user = await self.users.select(search=search, value=value)
        if user is None:

            return None


        await client.hset(name=f"user:public_id:{user["public_id"]}")
        await client.hset(name=f"user:email:{user["email"]}")
        await client.hset(name=f"user:cpf:{user["cpf"]}")
        await client.hset(name=f"user:id:{user["id"]}")

        return user

    #atualiza o usuario e deleta cache
    async def update(self, search:Literal["public_id", "email", "cpf", "id"] , field:str|int,
                     set:Literal["password", "permission", "role"], value:str|bool) -> dict|None:

        data = locals().copy()
        data.pop("self")
        user = await self.users.update(**data)
        if user is None:
            return None

        match search:
            case "public_id":
                name = f"user:public_id:{field}"

            case "email":
                name = f"user:email:{field}"
            case "id":
                name = f"user:id:{field}"
            case "cpf":
                name = f"user:cpf:{field}"

        await client.delete(name)

        return user

    #Deleta usaurio e cache
    async def delete(self, public_id:str) -> None:

        user = await self.select(search="public_id", value=public_id)
        if user is None:
            return

        await self.delete(public_id=public_id)


        await client.delete(name=f"user:public_id:{user["public_id"]}")
        await client.delete(name=f"user:email:{user["email"]}")
        await client.delete(name=f"user:cpf:{user["cpf"]}")
        await client.delete(name=f"user:id:{user["id"]}")

        



        


        



        

        
        



        

        

    