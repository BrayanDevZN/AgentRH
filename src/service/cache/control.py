"""
junta client com task
"""

from src.service.cache.task import increment,hset, delete, client, set
class  ControlCacheBackground:

    async def increment(self, name:str) -> None:

        increment.delay(name=name)

    async def hset(self, name:str, data:dict) -> None:

        hset.delay(name=name, data=data)


    async def get(self, name:str, hash:bool=False) -> dict|int|None:

        return await client.get(hash=hash, name=name)

    async def delete(self, name:str) -> None:

        delete.delay(name=name)

    async def set(self, name:str, data:str, ttl:int=None) -> None:

        set.delay(name=name, data=data, ttl=ttl)





client_background = ControlCacheBackground()

    




