from src.logs.log import LayerLogger
logger = LayerLogger("service").build()

"""
Cria o usuario admin
"""

async def create_admin() -> None:
    try:

        logger.info("Criando admin...")

        from src.service.module import enviroiments, control_db, auth_hash, auth_jwt

        email= enviroiments["email_user"]
        

        user = await control_db.users.select(search="email", value=email)
        if user is None:

            await control_db.users.insert(email=email,  role="admin", permission=True)



    except Exception as e:
        logger.error(e)
        raise Exception(e)


if __name__ == "__main__":
    import sys
    if sys.argv[1] == "create_admin":
        import asyncio
        asyncio.run(create_admin())

    else:
        raise ValueError(f"Not expeted argument {sys.argv[1]}")
        

        
