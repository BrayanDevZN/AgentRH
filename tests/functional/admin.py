def test_admin() -> None:

    import requests
    from src.config.module import enviroiments

    url = "http://0.0.0.0:650/"
    email = "flowr3898@gmail.com"
    password = "13Marco1978"
    admin_email = enviroiments["email_user"]

    session = requests.Session()

    # Cria o usuário que será administrado.
    body = {
        "email": email,
        "name": "Brayan"
    }

    response = session.post(url=url + "sender/", json=body)
    print(response.text if response.status_code > 400 else response.json())
    code = response.json()["code"]

    body["password"] = password
    body["cpf"] = "12345678910"
    body["age"] = 18
    body["permission"] = False
    body["code"] = str(code)
    body["gender"] = "male"

    response = session.post(url=url + "users/", json=body)
    print(response.text if response.status_code > 400 else response.json())

    # Faz login com o admin criado na inicialização da aplicação.
    session = requests.Session()
    body = {
        "email": admin_email
    }

    response = session.get(url=url + "auth/", json=body)
    print(response.text if response.status_code > 400 else response.json())

    response = session.post(url=url + "sender/2fa")
    print(response.text if response.status_code > 400 else response.json())
    code = response.json()["code"]

    body["code"] = str(code)
    response = session.get(url=url + "auth/", json=body)
    print(response.text if response.status_code > 400 else response.json())

    # Lista todos os usuários.
    response = session.get(
        url=url + "admin/",
        json={"is_all": True}
    )
    print(response.text if response.status_code > 400 else response.json())

    # Busca o usuário pelo e-mail.
    response = session.get(
        url=url + "admin/",
        json={
            "search": "email",
            "value": email
        }
    )
    print(response.text if response.status_code > 400 else response.json())

    # Transforma o usuário em admin.
    response = session.patch(
        url=url + "admin/",
        json={
            "search": "email",
            "field": email,
            "value": "admin"
        }
    )
    print(response.text if response.status_code > 400 else response.json())

    # Deleta o usuário.
    response = session.delete(
        url=url + "admin/",
        json={
            "search": "email",
            "value": email
        }
    )
    print(response.text if response.status_code > 400 else response.json())


if __name__ == "__main__":
    test_admin()
