"""
Testa os logs
"""

def test_logs() -> None:

    try:

        from src.logs.log import LayerLogger

        instance = LayerLogger(layer_name="test")
        logger = instance.build()

        logger.info("sucess")
        logger.warning("sucess")
        logger.error("sucess")

    except Exception as e:

        raise Exception(e)

    
if __name__ == "__main__":

    test_logs()