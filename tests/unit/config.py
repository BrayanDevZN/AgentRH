"""
testes de config
"""


def test_config() -> None:

    from src.config.settings import enviroiments

    for name in enviroiments:

        print(f"Found enviroiment {name}")


if __name__ == "__main__":
    test_config()