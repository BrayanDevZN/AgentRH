"""Testes de auth"""


async def test_auth() -> None:

    payload = {
        "email": "teste", "password":"123"
    }

    from src.service.auth import auth_hash, auth_jwt

    payload["password"] = await auth_hash.encode(password=payload["password"])

    token = await auth_jwt.encode(payload=payload)

    print(f"Token gerado: {token}")


    payload = await auth_jwt.decode(token=token)

    password = "123"

    print("valid password" if await auth_hash.check(password=password, hashed_passowrd=payload["password"]) 
          else "invalid password")

    print("Auth Ok!!")



if __name__ == "__main__":
    import asyncio
    asyncio.run(test_auth())


    