"""
Teste de sender
"""


async def test_sender() -> None:

    from src.utils.sender import SenderEmail
    from src.config.settings import enviroiments

    instance = SenderEmail(user=enviroiments["email_user"], password=enviroiments["password_user"])

    await instance.send(email="flowr3898@gmail.com", subject="Teste", body="Teste")


if __name__ == "__main__":

    import asyncio
    asyncio.run(test_sender())