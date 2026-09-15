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

        control = ControlDb(engine=engine_session)
        self.resumes = control.resumes
        self.vancancies = control.vancancies

    async def _delete_vancancie_cache(self, vancancie_id:int) -> None:

        vancancie = await self.vancancies.select(search="id", value=vancancie_id)
        if vancancie is None:
            return

        await client_background.delete(name=f"vancancie:id:{vancancie['id']}")
        await client_background.delete(name=f"vancancie:name:{vancancie['name']}")
        await client_background.delete(name=f"vancancie:created_by:{vancancie['created_by']}")
        await client_background.delete(name="vancancies")

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
        await client_background.hset(
            name=f"resume:user_id+vancancie_id:{resume['user_id']}:{resume['vancancie_id']}",
            data=cache_data
        )
        await client_background.delete(name="resumes")
        await self._delete_vancancie_cache(vancancie_id=resume["vancancie_id"])

        return resume

    #Busca cache, se for nulo, pega do banco
    async def select(self, user_id:int|None=None, vancancie_id:int|None=None, id:int|None=None,
                     get_all:bool=False) -> None|dict|list[dict]:

        if get_all:
            name = "resumes"
        elif id is not None and user_id is not None and vancancie_id is not None:
            name = f"resume:id:{id}:user_id:{user_id}:vancancie_id:{vancancie_id}"
        elif id is not None:
            name = f"resume:id:{id}"
        else:
            name = f"resume:user_id+vancancie_id:{user_id}:{vancancie_id}"
        cache = await client_background.get(name=name, hash=True)

        if cache:
            cache_data = ChangeTypes.from_cache(cache)

            if get_all and "items" in cache_data:
                return [ChangeTypes.from_cache(item) for item in cache_data["items"]]

            if not get_all:
                return cache_data

        resume = await self.resumes.select(
            id=id,
            user_id=user_id,
            vancancie_id=vancancie_id,
            get_all=get_all
        )
        if resume is None:
            return None

        if get_all:
            items = [ChangeTypes.to_cache(item) for item in resume]
            cache_data = ChangeTypes.to_cache({"items": items})
            await client_background.hset(name="resumes", data=cache_data)
            return resume

        cache_data = ChangeTypes.to_cache(resume)

        await client_background.hset(name=name, data=cache_data)
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
        await client_background.delete(
            name=f"resume:user_id+vancancie_id:{resume['user_id']}:{resume['vancancie_id']}"
        )
        await client_background.delete(
            name=f"resume:id:{resume['id']}:user_id:{resume['user_id']}:vancancie_id:{resume['vancancie_id']}"
        )
        await client_background.delete(name="resumes")
        await self._delete_vancancie_cache(vancancie_id=resume["vancancie_id"])

        return resume

    #Deleta curriculo e cache
    async def delete(self, id:int) -> None:

        resume = await self.select(id=id)
        if resume is None:
            return

        await self.resumes.delete(id=id)

        await client_background.delete(name=f"resume:id:{resume['id']}")
        await client_background.delete(name=f"resume:user_id:{resume['user_id']}")
        await client_background.delete(name=f"resume:vancancie_id:{resume['vancancie_id']}")
        await client_background.delete(
            name=f"resume:user_id+vancancie_id:{resume['user_id']}:{resume['vancancie_id']}"
        )
        await client_background.delete(
            name=f"resume:id:{resume['id']}:user_id:{resume['user_id']}:vancancie_id:{resume['vancancie_id']}"
        )
        await client_background.delete(name="resumes")
        await self._delete_vancancie_cache(vancancie_id=resume["vancancie_id"])
