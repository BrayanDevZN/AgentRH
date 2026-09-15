from src.logs.log import LayerLogger
logger = LayerLogger("auth").build()



"""
Gera e le jwt
"""

import jwt


class AuthJwt:

    def __init__(self, sing:str)->None:

        self.sing = sing
        self.alg = "HS256"


    #Cria o token
    async def encode(self, payload:str) -> str:

        try:

            logger.info("Criando token...")


            return jwt.encode(
                algorithm=self.alg,
                payload=payload,
                key=self.sing
            )

        except Exception as e:

            logger.error(e)
            raise Exception(e)


    #le o token
    async def decode(self, token:str) -> dict:

        try:

            logger.info("Lendo token...")

            return jwt.decode(
                algorithms=[self.alg],
                jwt=token,
                key=self.sing
            )

        except Exception as e:
            logger.error(e)
            raise Exception(e)
        