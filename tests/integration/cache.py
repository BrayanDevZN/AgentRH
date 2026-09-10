"""
testes de cache
"""


async def test_cache() -> None:
    from src.service.cache.control import client_background

    name_hash = "teste"

    await client_background.hset(name=name_hash, data={"test": "ok"})
    data = await client_background.get(name=name_hash, hash=True)
    print(data)

    name_incr = "testev2"

    await client_background.increment(name=name_incr)
    data = await client_background.get(name=name_incr)
    print(data)

    await client_background.delete(name=name_hash), await client_background.delete(name=name_incr)

    print("Cache ok!!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_cache())

