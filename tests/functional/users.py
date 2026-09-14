def test_account() -> None:

    import time
    import requests

    url = " http://0.0.0.0:650/"
    
    session = requests.Session()

    body = {
        "email": "flowr3898@gmail.com", "name": "Brayan"
    }

    response = session.post(url=url + "sender/", json=body)

    if response.status_code > 400:
        print(response.text)
        return
    response = response.json()
    print(response)
    code = response["code"]
    body["password"] = "13Marco1978"
    body["cpf"] = "12345678910"
    body["age"] = 18
    body["permission"] = True
    body["code"] = str(code)
    body["gender"] = "male"
    print(body)
    response = session.post(url=url + "users/", json=body)
    if response.status_code > 400:
        print(response.text)
        return

    response = response.json()
    
    print(response)

    user = session.get(url= url + "users/")
    print(user.text if user.status_code>400 else user.json())

    response = session.patch(url=url +"users/", json={"set": "age", "value":20})
    print(response.text if response.status_code>400 else response.json())

    response = session.delete(url + "users/", json={"password": "13Marco1978"})
    print(response.text if response.status_code>400 else response.json())


if __name__ == "__main__":
    test_account()
