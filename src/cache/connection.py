from src.logs.log import LayerLogger
logger = LayerLogger("cache").build()


"""
Cria conexão comr edis e testa
"""

class RedisConnectionError(Exception):
    pass


from redis import Redis

class RedisConnection:
    def __init__(self, port:int|str, host:str, password:str=None)-> None:
        self.port = port
        self.host = host
        self.password = password


    #Cria conexão 
    def _con(self) -> None:

        try:

            logger.info("Criando conexão com redis...")

            self.con = Redis(host=self.host, port=self.port, password=self.password, decode_responses=True)

        except Exception as e:
            logger.error(e)
            raise RedisConnectionError(e)


    #testa conexão
    def _test(self) -> None:

        try:

            logger.info("testando conexão com redis...")

            self.con.ping()

        except Exception as e:
            logger.error(e)
            raise RedisConnectionError(e)


    #Executa os metodos e retorna conexão
    def run(self) -> Redis:
        self._con()
        self._test()
        return self.con

    


        
