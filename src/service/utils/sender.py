"""
junta sender com as variaveis de ambiente e task
"""


from src.utils.sender import SenderEmail
from src.config.module import enviroiments
from src.service.task import task_app
import asyncio
@task_app.task()
def sender(email:str, subject:str, body:str) -> None:

    instance = SenderEmail(user=enviroiments["email_user"], password=enviroiments["password_user"])

    asyncio.run(instance.send(subject=subject, body=body, email=email))

