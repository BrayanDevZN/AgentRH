"""Teste funcional das rotas de autenticação."""

import requests


def test_auth() -> None:
    url = "http://0.0.0.0:650"
    email = "flowr3898@gmail.com"
    old_password = "13Marco1978"
    new_password = "Brayan12345"

    session = requests.Session()

    # Cria o usuário.
    response = session.post(
        f"{url}/sender/",
        json={"email": email, "name": "Brayan"}
    )
    print(response.text)
    code = response.json()["code"]

    response = session.post(
        f"{url}/users/",
        json={
            "email": email,
            "name": "Brayan",
            "password": old_password,
            "cpf": "12345678910",
            "age": 18,
            "permission": True,
            "code": str(code),
            "gender": "male"
        }
    )
    print(response.text)

    # Login.
    response = session.get(
        f"{url}/auth/",
        json={"email": email, "password": old_password}
    )
    print(response.text)

    # Código do 2FA.
    response = session.post(f"{url}/sender/2fa")
    print(response.text)
    code = response.json()["code"]

    # Confirma o login e recebe os tokens.
    response = session.get(
        f"{url}/auth/",
        json={
            "email": email,
            "password": old_password,
            "code": str(code)
        }
    )
    print(response.text)

    # Atualiza os tokens.
    response = session.put(f"{url}/auth/")
    print(response.text)

    # Atualiza a senha.
    response = session.patch(
        f"{url}/auth/",
        json={
            "password": old_password,
            "new_password": new_password
        }
    )
    print(response.text)

    # Faz login novamente com a senha nova.
    response = session.get(
        f"{url}/auth/",
        json={"email": email, "password": new_password}
    )
    print(response.text)

    response = session.post(f"{url}/sender/2fa")
    print(response.text)
    code = response.json()["code"]

    response = session.get(
        f"{url}/auth/",
        json={
            "email": email,
            "password": new_password,
            "code": str(code)
        }
    )
    print(response.text)

    # Logout.
    response = session.delete(f"{url}/auth/")
    print(response.text)

    # Faz login novamente para excluir o usuário.
    session.cookies.clear()

    response = session.get(
        f"{url}/auth/",
        json={"email": email, "password": new_password}
    )
    print(response.text)

    response = session.post(f"{url}/sender/2fa")
    print(response.text)
    code = response.json()["code"]

    response = session.get(
        f"{url}/auth/",
        json={
            "email": email,
            "password": new_password,
            "code": str(code)
        }
    )
    print(response.text)

    # Exclui o usuário criado pelo teste.
    response = session.delete(
        f"{url}/users/",
        json={"password": new_password}
    )
    print(response.text)


if __name__ == "__main__":
    test_auth()
