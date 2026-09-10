"""
Junta o modulo de banco de dados com sua variavel de ambiente e com cache
"""

from typing import Literal

from src.database.manage import ControlDb
from src.service.cache.control import client_background
from src.service.db.change_types import ChangeTypes
from src.service.db.connetion import engine_session


class ControlResumes:

    def __init__(self) -> None:

        self.resumes = ControlDb(engine=engine_session).resumes

    #Insere e salva cache
    async def insert(self, user_id:int, vancancie_id:int, pdf:bytes,
                     status:Literal["aproved", "recuse", "pending"] = "pending", reason:str = "null") -> dict:

        data = locals().copy()
        data.pop("self")

        resume = await self.resumes.insert(**data)
        cache_data = ChangeTypes.to_cache(resume)

        await client_background.hset(name=f"resume:id:{resume['id']}", data=cache_data)
        await client_background.hset(name=f"resume:user_id:{resume['user_id']}", data=cache_data)
        await client_background.hset(name=f"resume:vancancie_id:{resume['vancancie_id']}", data=cache_data)

        return resume

    #Busca cache, se for nulo, pega do banco
    async def select(self, search:Literal["id", "user_id", "vancancie_id"], value:int) -> None|dict:

        match search:

            case "id":
                name = f"resume:id:{value}"

            case "user_id":
                name = f"resume:user_id:{value}"

            case "vancancie_id":
                name = f"resume:vancancie_id:{value}"

        cache = await client_background.get(name=name, hash=True)

        if cache:
            return ChangeTypes.from_cache(cache)

        resume = await self.resumes.select(search=search, value=value)
        if resume is None:
            return None

        cache_data = ChangeTypes.to_cache(resume)

        await client_background.hset(name=f"resume:id:{resume['id']}", data=cache_data)
        await client_background.hset(name=f"resume:user_id:{resume['user_id']}", data=cache_data)
        await client_background.hset(name=f"resume:vancancie_id:{resume['vancancie_id']}", data=cache_data)

        return resume

    #Atualiza e deleta cache
    async def update(self, search:Literal["id", "user_id", "vancancie_id"], field:int,
                     set:Literal["pdf", "status", "reason"], value:bytes|str) -> None|dict:

        data = locals().copy()
        data.pop("self")

        resume = await self.resumes.update(**data)
        if not resume:
            return None

        await client_background.delete(name=f"resume:id:{resume['id']}")
        await client_background.delete(name=f"resume:user_id:{resume['user_id']}")
        await client_background.delete(name=f"resume:vancancie_id:{resume['vancancie_id']}")

        return resume

    #Deleta curriculo e cache
    async def delete(self, id:int) -> None:

        resume = await self.select(search="id", value=id)
        if resume is None:
            return

        await self.resumes.delete(id=id)

        await client_background.delete(name=f"resume:id:{resume['id']}")
        await client_background.delete(name=f"resume:user_id:{resume['user_id']}")
        await client_background.delete(name=f"resume:vancancie_id:{resume['vancancie_id']}")
