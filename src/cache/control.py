from src.logs.log import LayerLogger
logger = LayerLogger("cache").build()


"""
Controla redis
"""
import json
from redis import Redis, WatchError

class RedisCache:

    def __init__(self, client: Redis)-> None:

        self.client = client


    #Salva um hash
    async def hset(self, name:str, data:dict) -> None:

        while True:

            try:

                logger.info(f"Tentando salvar {name}...")

                with self.client.pipeline(transaction=True) as session:

                    session.watch(name)
                    session.multi()
                    

                    session.hset(name=name, mapping=data)

                    session.expire(name=name, time=70)

                    session.execute()

                    logger.info(f"{name} salvo!!!")
                    break

            except WatchError:
                logger.warning(f"Alguem ja estava tentando alterar {name}!!")
                continue

    #Le um hash ou um dado normal
    async def get(self, name:str, hash:bool=False) -> dict|None:

        while True:

            try:

                logger.info(f"Tentando ler {name}...")

                with self.client.pipeline(transaction=True) as session:

                    session.watch(name)
                    session.multi()

                    

                    session.hgetall(name=name) if hash else session.get(name=name)

                    result = session.execute()

                    logger.info(name + "" + "encontrado" if result is not None else "não encontrado")
                    return result[0]

            except WatchError:
                logger.warning(f"Alguem ja estava tentando alterar {name}!!")
                continue

    #Deleta um cache
    async def delete(self, name:str) -> None:

        try:

            logger.info(f"Deletando {name}...")

            self.client.delete(name)

        except Exception as e:

            logger.error(e)
            raise Exception(e)


    #Cria uma operação atomica
    async def increment(self, name:str) -> None:

        

            try:

                logger.info(f"Tentando incrementar {name}...")

                with self.client.pipeline(transaction=True) as session:
                    session.multi()

                    session.incr(name=name)
                    session.expire(name=name, time=70)

                    session.execute()

                    logger.info(f"{name} incrementado!!")
                    
            except Exception as e:

                logger.error(e)
                raise Exception(e)

   

            

                







        