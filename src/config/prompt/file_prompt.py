from src.logs.log import LayerLogger
logger = LayerLogger("config").build()



"""
Le o prompt
"""
from pathlib import Path
import os
class NotFoundFilePromptError(Exception):
    pass
class FilePrompt:

    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent / "prompt.md"


    #Levanta erro se não existit
    def _exists(self) -> None:

        if not os.path.exists(self.BASE_DIR):

            msg = f"Exepted file prompt in path {self.BASE_DIR}"

            logger.error(msg)
            raise NotFoundFilePromptError(msg)


    #Le o arquivo
    def _read(self) -> None:

        try:

            with open(self.BASE_DIR, "r", encoding="utf-8") as f:

                self.prompt = f.read()

        except Exception as e:

            logger.error(e)
            raise Exception(e)

    #Executa os metodos e retorna o prompt
    def get(self) -> str:

        self._exists()
        self._read()
        return self.prompt



"""
Cria o objeto da classe
"""
prompt = FilePrompt().get()


