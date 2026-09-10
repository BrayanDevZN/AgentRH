"""
testa a task do agente
"""


async def test_agent() -> None:

    from src.service.db.module import control_db
    from src.service.db.connetion import instance
    from src.service.utils.agent import run_agent
    import asyncio
    import uuid

    await instance.test()

    identify = uuid.uuid4().hex

    user_insert = await control_db.users.insert(
        name="Joao da Silva",
        email=f"{identify[:20]}@teste.com",
        password="12345678",
        cpf=str(uuid.uuid4().int)[:12],
        gender="male",
        age=28
    )
    print(user_insert)

    description = """
Vaga: Desenvolvedor Python Junior

Buscamos uma pessoa desenvolvedora para atuar na criacao e manutencao de APIs,
integracoes com bancos de dados e testes automatizados. E necessario possuir
conhecimento em Python, Git, APIs REST e SQL. Experiencia com FastAPI, Docker,
Redis e Celery sera considerada um diferencial.
"""

    vancancie_insert = await control_db.vancancies.insert(
        created_by=user_insert["id"],
        name=f"Desenvolvedor Python Junior {identify[:10]}",
        description=description
    )
    print(vancancie_insert)

    resume = """
Joao da Silva
Desenvolvedor Python Junior

Resumo profissional:
Desenvolvedor com experiencia na construcao de APIs REST utilizando Python e
FastAPI. Possui conhecimento em bancos de dados relacionais, Git e testes
automatizados.

Experiencia profissional:
Desenvolvedor Python Junior - Tech Solutions - 2024 ate o momento
- Desenvolvimento e manutencao de endpoints REST com Python e FastAPI.
- Integracao de aplicacoes com PostgreSQL utilizando SQLAlchemy.
- Criacao de testes automatizados com Pytest.
- Versionamento de codigo com Git e GitHub.

Projetos:
- API de gerenciamento de candidaturas com FastAPI, PostgreSQL e Redis.
- Processamento de tarefas em segundo plano utilizando Celery.

Formacao:
Tecnologia em Analise e Desenvolvimento de Sistemas - cursando.

Habilidades:
Python, FastAPI, SQL, PostgreSQL, SQLAlchemy, Git, GitHub, Redis, Celery,
Docker e Pytest.
"""

    resume_insert = await control_db.resumes.insert(
        user_id=user_insert["id"],
        vancancie_id=vancancie_insert["id"],
        pdf=resume.encode("utf-8")
    )
    print(resume_insert)

    run_agent.delay(
        email="flowr3898@gmail.com",
        resume=resume_insert["pdf"],
        description=vancancie_insert["description"],
        name_vancancie=vancancie_insert["name"],
        name_user=user_insert["name"],
        id=resume_insert["id"]
    )

    await asyncio.sleep(60)

    resume_select = await control_db.resumes.select(search="id", value=resume_insert["id"])
    print(resume_select)

    resume_delete = await control_db.resumes.delete(id=resume_insert["id"])
    print(resume_delete)

    vancancie_delete = await control_db.vancancies.delete(id=vancancie_insert["id"])
    print(vancancie_delete)

    user_delete = await control_db.users.delete(public_id=str(user_insert["public_id"]))
    print(user_delete)


if __name__ == "__main__":

    import asyncio
    asyncio.run(test_agent())
