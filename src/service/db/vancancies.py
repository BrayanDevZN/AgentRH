"""
Junta o modulo de banco de dados com sua variavel de ambiente e com cache
"""

from typing import Literal

from src.database.manage import ControlDb
from src.service.cache import client
from src.service.db.change_types import ChangeTypes
from src.service.db.connetion import engine_session


class ControlVancancies:

    def __init__(self) -> None:

        self.vancancies = ControlDb(engine=engine_session).vancancies

    #Insere e salva cache
    async def insert(self, created_by:int, name:str, description:str) -> dict:

        vancancie = await self.vancancies.insert(created_by=created_by, name=name, description=description)
        cache_data = ChangeTypes.to_cache(vancancie)

        await client.hset(name=f"vancancie:id:{vancancie['id']}", data=cache_data)
        await client.hset(name=f"vancancie:name:{vancancie['name']}", data=cache_data)
        await client.hset(name=f"vancancie:created_by:{vancancie['created_by']}", data=cache_data)

        return vancancie

    #Busca cache, se for nulo, pega do banco
    async def select(self, search:Literal["name", "id", "created_by"], value:str|int) -> None|dict:

        match search:

            case "name":
                name = f"vancancie:name:{value}"

            case "id":
                name = f"vancancie:id:{value}"

            case "created_by":
                name = f"vancancie:created_by:{value}"

        cache = await client.get(name=name, hash=True)

        if cache:
            return ChangeTypes.from_cache(cache)

        vancancie = await self.vancancies.select(search=search, value=value)
        if vancancie is None:
            return None

        cache_data = ChangeTypes.to_cache(vancancie)

        await client.hset(name=f"vancancie:id:{vancancie['id']}", data=cache_data)
        await client.hset(name=f"vancancie:name:{vancancie['name']}", data=cache_data)
        await client.hset(name=f"vancancie:created_by:{vancancie['created_by']}", data=cache_data)

        return vancancie

    #Atualiza e deleta cache
    async def update(self, search:Literal["name", "id", "created_by"], field:str|int,
                     set:Literal["name", "description"], value:str) -> None|dict:

        data = locals().copy()
        data.pop("self")

        vancancie = await self.vancancies.update(**data)
        if not vancancie:
            return None

        await client.delete(name=f"vancancie:id:{vancancie['id']}")
        await client.delete(name=f"vancancie:created_by:{vancancie['created_by']}")
        await client.delete(name=f"vancancie:name:{vancancie['name']}")

        return vancancie

    #Deleta vaga e cache
    async def delete(self, id:int) -> None:

        vancancie = await self.select(search="id", value=id)
        if vancancie is None:
            return

        await self.vancancies.delete(id=id)

        await client.delete(name=f"vancancie:id:{vancancie['id']}")
        await client.delete(name=f"vancancie:created_by:{vancancie['created_by']}")
        await client.delete(name=f"vancancie:name:{vancancie['name']}")
