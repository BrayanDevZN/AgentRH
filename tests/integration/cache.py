"""
testes de cache
"""


async def test_cache() -> None:
    from src.cache.manage import cache_control
    from src.config.settings import enviroiments

    instance = cache_control(port=enviroiments["redis_port"], host=enviroiments["redis_host"], 
                             password=enviroiments["redis_password"])

    name_hash = "teste"

    await instance.hset(name=name_hash, data={"test": "ok"})
    data = await instance.get(name=name_hash, hash=True)
    print(data)

    name_incr = "testev2"

    await instance.increment(name=name_incr)
    data = await instance.get(name=name_incr)
    print(data)

    await instance.delete(name=name_hash), await instance.delete(name=name_incr)

    print("Cache ok!!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_cache())



