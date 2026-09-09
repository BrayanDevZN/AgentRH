from src.logs.log import LayerLogger
logger = LayerLogger("database").build()


"""
Cria a engine e sessão do banco de dados
"""

class ConenctionDbError(Exception):
    pass

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

class ConenctionDb:

    def __init__(self, url:str)-> None:

        self.url = url


    #Cria a engine do banco de dados
    def _engine(self) -> None:

        try:

            logger.info("Criando engine do banco de dados...")

            self.engine = create_async_engine(self.url)

        except Exception as e:

            logger.error(e)
            raise Exception(e)

    #Cria o orquestrador de sessoes do banco
    def _session(self) -> None:

        try:

            logger.info("Criando orquestrador de sessoes...")

            self.make_session = async_sessionmaker(bind=self.egnine, expire_on_commit=False)

        except Exception as e:
            logger.error(e)
            raise Exception(e)

    #testa a conexão
    async def _test(self) -> None:

        try:

            logger.info("Testando conexão do banco de dados...")

            async with self.make_session.begin() as session:

                session.execute("SELECT 1;")

            logger.info("Teste concluido!!!")

        except Exception as e:

            logger.error(e)
            raise Exception(e)


    #Executa os metodos
    def run(self) -> ConenctionDb:

        self._engine()
        self._session()

        import asyncio
        asyncio.run(self._test())






    


        