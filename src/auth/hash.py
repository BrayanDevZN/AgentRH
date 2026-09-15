from src.logs.log import LayerLogger
logger = LayerLogger("auth").build()



"""
Cria e compara ahsh de senha
"""

import bcrypt

class AuthHash:

    #Cria o hash de senha
    @staticmethod
    async def encode(password:str) -> str:

        try:

            logger.info("Criptografando senha...")
            
            password = bcrypt.hashpw(
                salt=bcrypt.gensalt(),
                password=password.encode("utf-8")
            )

            return password.decode("utf-8")

        except Exception as e:

            logger.error(e)
            raise Exception(e)


    #Compara senha
    @staticmethod
    async def check(password:str, hashed_passowrd:str) -> bool:

        try:

            logger.info("Comparando senhas...")

            return bcrypt.checkpw(
                password=password.encode(),
                hashed_password=hashed_passowrd.encode()
            )


        except Exception as e:
            logger.error(e)

            raise Exception(e)