def test_vancancies() -> None:

    import requests
    from src.config.module import enviroiments

    url = "http://0.0.0.0:650/"
    name = "Desenvolvedor Backend"
    description = "Desenvolvimento de APIs com Python"

    session = requests.Session()

    # Faz login com o admin.
    body = {
        "email": enviroiments["email_user"]
    }

    response = session.get(url=url + "auth/", json=body)
    print(response.text if response.status_code > 400 else response.json())

    if response.status_code > 400:
        return

    response = session.post(url=url + "sender/2fa")
    print(response.text if response.status_code > 400 else response.json())

    if response.status_code > 400:
        return

    body["code"] = str(response.json()["code"])

    response = session.get(url=url + "auth/", json=body)
    print(response.text if response.status_code > 400 else response.json())

    if response.status_code > 400:
        return

    # Cria a vaga.
    response = session.post(
        url=url + "vancancies/",
        json={
            "name": name,
            "description": description
        }
    )
    print(response.text if response.status_code > 400 else response.json())

    # Busca a vaga pelo nome.
    response = session.get(
        url=url + "vancancies/",
        json={
            "search": "name",
            "value": name
        }
    )
    print(response.text if response.status_code > 400 else response.json())

    # Busca todas as vagas.
    response = session.get(
        url=url + "vancancies/",
        json={"search": "all"}
    )
    print(response.text if response.status_code > 400 else response.json())

    # Atualiza a descrição da vaga.
    description = "Desenvolvimento de APIs assíncronas com Python"
    response = session.patch(
        url=url + "vancancies/",
        json={
            "search": "name",
            "field": name,
            "set": "description",
            "value": description
        }
    )
    print(response.text if response.status_code > 400 else response.json())

    # Busca a vaga atualizada.
    response = session.get(
        url=url + "vancancies/",
        json={
            "search": "name",
            "value": name
        }
    )
    print(response.text if response.status_code > 400 else response.json())

    # Deleta a vaga.
    response = session.delete(
        url=url + "vancancies/",
        json={
            "search": "name",
            "field": name,
            "set": "description",
            "value": description
        }
    )
    print(response.text if response.status_code > 400 else response.json())


if __name__ == "__main__":
    test_vancancies()
