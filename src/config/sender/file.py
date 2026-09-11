from src.logs.log import LayerLogger
logger = LayerLogger("config").build()


"""
Le os arquivos html
"""

import os
from pathlib import Path
class NotFoundFileSenderError(Exception):
    pass

class FileSender:
    def __init__(self)-> None:

        self.BASE_DIR = Path(__file__).resolve().parent
        self.files = ["create_account.html", "update_password.html"]


    #Confere se os arquivos existem
    def _exists(self) -> None:

        for file in self.files:

            path = self.BASE_DIR / file
            

            if not os.path.exists(path):

                raise NotFoundFileSenderError(f"Expeted {file} in path {path}")


    #Cria um dict com o conteudo dos arquivos
    def _read(self) -> None:

        self.file_sender = {}

        for file in self.files:

            name = file.replace(".html", "")


            with open(self.BASE_DIR / file, "r", encoding="utf-8") as f:

                file = f.read()

            self.file_sender[name] = file


    #Chama os metodos e retorna os hmtls
    def get(self) -> dict:

        self._exists()
        self._read()
        return self.file_sender



"""
instancia a classe
"""

instance = FileSender()
senders = instance.get()

    
        