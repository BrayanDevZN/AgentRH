"""
Junta os modulos
"""

from src.cache.connection import RedisConnection
from src.cache.control import RedisCache



def cache_control(port:int|str, host:str, password:str=None)-> RedisCache:

        client = RedisConnection(port=port, host=host, password=password)

        return RedisCache(client=client)




        