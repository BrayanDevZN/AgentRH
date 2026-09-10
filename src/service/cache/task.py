"""
Faz os metodos delete, increment e hset se tornarem tasks
"""

from src.service.cache.connection import client
from src.service.task import task_app
import asyncio

@task_app.task()
def increment(name:str) -> None:

    asyncio.run(client.increment(name=name))



@task_app.task()
def hset(name:str, data:dict) -> None:

    asyncio.run(client.hset(name=name, data=data))



@task_app.task()
def delete(name:str) -> None:

    asyncio.run(client.delete(name=name))