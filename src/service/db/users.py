"""
Junta o modulo de banco de dados com sua variavel de ambiente e com cache
"""

from typing import Literal

from src.database.manage import ControlDb
from src.service.cache import client
from src.service.db.change_types import ChangeTypes
from src.service.db.connetion import engine_session


class ControlUsers:

    def __init__(self) -> None:

        self.users = ControlDb(engine=engine_session).users

    #Cria o usuario e salva o cache
    async def insert(self, name:str, age:int, email:str, password:str, cpf:str, gender:Literal["male", "female", "other"],
                     permission:bool = False, role:Literal["user", "admin"] = "user") -> dict:

        data = locals().copy()
        data.pop("self")

        user = await self.users.insert(**data)
        cache_data = ChangeTypes.to_cache(user)

        await client.hset(name=f"user:public_id:{user['public_id']}", data=cache_data)
        await client.hset(name=f"user:email:{user['email']}", data=cache_data)
        await client.hset(name=f"user:cpf:{user['cpf']}", data=cache_data)
        await client.hset(name=f"user:id:{user['id']}", data=cache_data)

        return user

    #Le no cache, se existir, retorna, se nao, busca no banco, e depois salva cache
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

        if cache:
            return ChangeTypes.from_cache(cache)

        user = await self.users.select(search=search, value=value)
        if user is None:
            return None

        cache_data = ChangeTypes.to_cache(user)

        await client.hset(name=f"user:public_id:{user['public_id']}", data=cache_data)
        await client.hset(name=f"user:email:{user['email']}", data=cache_data)
        await client.hset(name=f"user:cpf:{user['cpf']}", data=cache_data)
        await client.hset(name=f"user:id:{user['id']}", data=cache_data)

        return user

    #Atualiza o usuario e deleta cache
    async def update(self, search:Literal["public_id", "email", "cpf", "id"], field:str|int,
                     set:Literal["password", "permission", "role"], value:str|bool) -> dict|None:

        data = locals().copy()
        data.pop("self")

        user = await self.users.update(**data)
        if not user:
            return None

        await client.delete(name=f"user:public_id:{user['public_id']}")
        await client.delete(name=f"user:email:{user['email']}")
        await client.delete(name=f"user:cpf:{user['cpf']}")
        await client.delete(name=f"user:id:{user['id']}")

        return user

    #Deleta usuario e cache
    async def delete(self, public_id:str) -> None:

        user = await self.select(search="public_id", value=public_id)
        if user is None:
            return

        await self.users.delete(public_id=public_id)

        await client.delete(name=f"user:public_id:{user['public_id']}")
        await client.delete(name=f"user:email:{user['email']}")
        await client.delete(name=f"user:cpf:{user['cpf']}")
        await client.delete(name=f"user:id:{user['id']}")
