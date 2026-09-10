from src.logs.log import LayerLogger
logger = LayerLogger("tasks").build()



"""
Cria o controlador de tasks
"""
from celery import Celery
class TaskControl:

    def __init__(self, port:str|int, host:str, password:str|int=None)-> None:

        self.port = port
        self.host = host
        self.password = password


    #Forma a url
    def _formated(self) -> None:

        logger.info("Formantando url do redis...")

        if self.password is None:

            self.broker = f"redis://{self.host}:{self.port}/1"
            self.back = f"redis://{self.host}:{self.port}/2"

        else:
            self.broker = f"redis://{self.password}@{self.host}:{self.port}/1"
            self.back = f"redis://{self.password}@{self.host}:{self.port}/2"


    #Cria conexão com celery
    def _connect(self) -> None:

        try:

            logger.info("Criando conexão com celery...")

            self.con = Celery(
                broker=self.broker, backend=self.back
                
            )

            logger.info("Conexão criada com sucesso!!!")

        except Exception as e:

            logger.error(e)
            raise Exception(e)

    #chama os metodos e retorna a conexão
    def run(self) -> Celery:
        self._formated()
        self._connect()
        return self.con





        