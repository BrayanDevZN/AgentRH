"""
Cria a conexão do banco de dados juntando a variavel de ambiente url com o modulo de conexão
"""

from src.config.settings import enviroiments
from src.database.manage import ConenctionDb
import asyncio
instance = ConenctionDb(url=enviroiments["url"])
instance.run()
engine_session = instance.make_session
engine = instance.engine


if __name__ == "__main__":
    import asyncio
    asyncio.run(instance.test())
