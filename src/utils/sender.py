from src.logs.log import LayerLogger
logger = LayerLogger("utils").build()


"""
Envia emails para o usuario
"""
import yagmail
class SenderEmailError(Exception):
    pass


class SenderEmail:

    def __init__(self, user: str, password:str)-> None:

        self.instance = yagmail.SMTP(
            user=user,
            password=password
        )


    #Envia o email
    async def send(self, email:str, subject:str, body:str) -> None:

        try:

            logger.info(f"Enviando email para {email}...")

            self.instance.send(
                to=email, subject=subject, contents=body
            )

            logger.info("Enviado com sucesso!!!")

        except Exception as e:

            logger.error(e)
            raise SenderEmailError(e)
        