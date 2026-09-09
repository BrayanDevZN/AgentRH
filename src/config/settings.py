from src.logs.log import LayerLogger
logger = LayerLogger("config").build()


"""
Cria a configuração das variaveis de ambiente
"""


class NotFoundEnviroment(Exception):
    pass

import os
from pathlib import Path
class Environment:

    def __init__(self)-> None:

        self.envs = ["redis_port", "redis_host", "url", "sing", "origin", "rate_limit", "global_rate_limit"]



    #carrega as variaveis de ambiente se o .env existir
    @staticmethod
    def _load() -> None:

        try:

            BASE_DIR = Path(__file__).resolve().parent / ".env"
            from dotenv import load_dotenv

            load_dotenv (BASE_DIR) if os.path.exists(BASE_DIR) else load_dotenv()

               
        except Exception as e:

            logger.error(e)
            raise Exception(e)


    #Cria um dicionario que carrega as variaveis de ambiente
    def _envs(self) -> None:

        self.envroins = {}
        for name in self.envs:

            env = os.getenv(name)

            if env is None:
                msg = f"Expeted enviroin {name}"
                logger.error(msg)

                raise NotFoundEnviroment(msg)

            self.envroins[name] = env

    #Chama os metodos em retorna o dicionario com as variaveis
    def get(self) -> dict:

        self._load()
        self._envs()
        return self.envroins



"""
Cria o objeto pra pegar as variaveis
"""
instance = Environment()
enviroiments = instance.get()




        