def test_resumes() -> None:

    import requests
    from src.config.module import enviroiments

    url = "http://0.0.0.0:650/"
    email = "flowr3898@gmail.com"
    password = "13Marco1978"
    vancancie_name = "Desenvolvedor Backend Resume"
    vancancie_description = "Desenvolvimento de APIs com Python"

    # Faz login com o admin.
    admin_session = requests.Session()
    body = {
        "email": enviroiments["email_user"]
    }

    response = admin_session.get(url=url + "auth/", json=body)
    print(response.text if response.status_code > 400 else response.json())

    if response.status_code > 400:
        return

    response = admin_session.post(url=url + "sender/2fa")
    print(response.text if response.status_code > 400 else response.json())

    if response.status_code > 400:
        return

    body["code"] = str(response.json()["code"])

    response = admin_session.get(url=url + "auth/", json=body)
    print(response.text if response.status_code > 400 else response.json())

    if response.status_code > 400:
        return

    # Cria a vaga.
    response = admin_session.post(
        url=url + "vancancies/",
        json={
            "name": vancancie_name,
            "description": vancancie_description
        }
    )
    print(response.text if response.status_code > 400 else response.json())

    if response.status_code > 400:
        return

    vancancie_id = response.json()["id"]

    # Cria o usuário que enviará o currículo.
    user_session = requests.Session()
    body = {
        "email": email,
        "name": "Brayan"
    }

    response = user_session.post(url=url + "sender/", json=body)
    print(response.text if response.status_code > 400 else response.json())

    if response.status_code > 400:
        return

    body["password"] = password
    body["cpf"] = "12345678910"
    body["age"] = 18
    body["permission"] = False
    body["code"] = str(response.json()["code"])
    body["gender"] = "male"

    response = user_session.post(url=url + "users/", json=body)
    print(response.text if response.status_code > 400 else response.json())

    if response.status_code > 400:
        return

    # Envia o currículo para a vaga.
    pdf = b"%PDF-1.4\nResume functional test\n%%EOF"
    response = user_session.post(
        url=url + "resumes/",
        data={
            "vancancie_id": str(vancancie_id),
            "status": "pending",
            "reason": "null"
        },
        files={
            "pdf": ("curriculo.pdf", pdf, "application/pdf")
        }
    )
    print(response.text if response.status_code > 400 else response.json())

    if response.status_code > 400:
        return

    # Busca o currículo enviado.
    response = user_session.get(
        url=url + "resumes/",
        json={
            "vancancie_id": vancancie_id
        }
    )
    print(response.text if response.status_code > 400 else response.json())

    if response.status_code > 400:
        return

    resume_id = response.json()["id"]

    # Admin busca todos os currículos.
    response = admin_session.get(
        url=url + "resumes/",
        json={"get_all": True}
    )
    print(response.text if response.status_code > 400 else response.json())

    # Busca a vaga com o currículo relacionado.
    response = user_session.get(
        url=url + "vancancies/",
        json={
            "search": "id",
            "value": vancancie_id
        }
    )
    print(response.text if response.status_code > 400 else response.json())

    # Deleta o currículo.
    response = user_session.delete(
        url=url + "resumes/",
        params={
            "id": resume_id,
            "vancancie_id": vancancie_id
        }
    )
    print(response.text if response.status_code > 400 else response.json())

    # Deleta o usuário.
    response = user_session.delete(
        url=url + "users/",
        json={"password": password}
    )
    print(response.text if response.status_code > 400 else response.json())

    # Deleta a vaga.
    response = admin_session.delete(
        url=url + "vancancies/",
        json={
            "search": "id",
            "field": vancancie_id,
            "set": "description",
            "value": vancancie_description
        }
    )
    print(response.text if response.status_code > 400 else response.json())


if __name__ == "__main__":
    test_resumes()
