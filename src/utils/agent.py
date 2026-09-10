from src.logs.log import LayerLogger
logger = LayerLogger("utils").build()


"""
Envia requisição pra open ai
"""

from openai import AsyncOpenAI

async def analyze_agent(key:str, prompt:str, input:str) -> str:

    try:

        logger.info("Enviando requisição para open ai...")

        client = AsyncOpenAI(api_key=key)

        response = await client.responses.create(
            instructions=prompt,
            input=input,
            model="gpt-5.6-luna"
        )


        return response.output_text

    except Exception as e:
        logger.error(e)

        raise Exception(e)
    
