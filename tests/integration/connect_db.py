"""
Executa os teste da conexão do bancos de dados
"""

def test_connection_db() -> None:


    from src.database.manage import ConenctionDb
    from src.config.module import enviroiments
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine
    import asyncio

    instace = ConenctionDb(url=enviroiments["url"])
    instace.run()


    if not isinstance(instace.make_session, async_sessionmaker):

        raise TypeError(f"expeted {async_sessionmaker}")


    if not isinstance(instace.engine, AsyncEngine):

        raise TypeError(f"expeted {AsyncEngine}")


    print("Valid connection database!!!")


if __name__ == "__main__":
    test_connection_db()


