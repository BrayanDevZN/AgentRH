"""
Executa os testes de repository
"""


async def test_repository() -> None:

    from src.database.manage import ControlDb, migration_db, Users, Vancancies, Resumes, ConenctionDb
    from src.config.module import enviroiments
    import uuid
    

    instance_connection = ConenctionDb(url=enviroiments["url"])
    instance_connection._engine()
    instance_connection._session()
    await instance_connection.test()

    await migration_db(engine=instance_connection.engine)

    instance_db = ControlDb(engine=instance_connection.make_session)

    identify = uuid.uuid4().hex

    user_insert = await instance_db.users.insert(
        name="Usuario teste",
        email=f"{identify[:20]}@teste.com",
        password="12345678",
        cpf=str(uuid.uuid4().int)[:12],
        gender="other",
        age=18
    )
    print(user_insert)

    user_select = await instance_db.users.select(search="id", value=user_insert["id"])
    print(user_select)

    user_update = await instance_db.users.update(
        search="id",
        field=user_insert["id"],
        set="permission",
        value=True
    )
    print(user_update)

    vancancie_insert = await instance_db.vancancies.insert(
        created_by=user_insert["id"],
        name=f"Vaga teste {identify[:20]}",
        description="Descrição da vaga de teste"
    )
    print(vancancie_insert)

    vancancie_select = await instance_db.vancancies.select(search="id", value=vancancie_insert["id"])
    print(vancancie_select)

    vancancie_update = await instance_db.vancancies.update(
        search="id",
        field=vancancie_insert["id"],
        set="description",
        value="Descrição atualizada"
    )
    print(vancancie_update)

    resume_insert = await instance_db.resumes.insert(
        user_id=user_insert["id"],
        vancancie_id=vancancie_insert["id"],
        pdf=b"curriculo teste"
    )
    print(resume_insert)

    resume_select = await instance_db.resumes.select(search="id", value=resume_insert["id"])
    print(resume_select)

    resume_update = await instance_db.resumes.update(
        search="id",
        field=resume_insert["id"],
        set="status",
        value="aproved"
    )
    print(resume_update)

    resume_delete = await instance_db.resumes.delete(id=resume_insert["id"])
    print(resume_delete)

    vancancie_delete = await instance_db.vancancies.delete(id=vancancie_insert["id"])
    print(vancancie_delete)

    user_delete = await instance_db.users.delete(public_id=str(user_insert["public_id"]))
    print(user_delete)


if __name__ == "__main__":

    import asyncio
    asyncio.run(test_repository())
