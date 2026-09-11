"""
testes de config
"""


def test_config() -> None:

    from src.config.module import enviroiments, prompt

    for name in enviroiments:

        print(f"Found enviroiment {name}")


    print(f"\nFound prompt: {prompt}")


if __name__ == "__main__":
    test_config()
