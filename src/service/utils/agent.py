"""
Cria o agente, juntando ele com a sua key, prompt e enviando o email e transforma tudo em task
"""

from src.service.utils.sender import sender
from src.utils.agent import analyze_agent
from src.config.module import enviroiments, prompt
from src.service.db.module import control_db
from src.service.task import task_app
import asyncio
class AgentRH:

    def __init__(self, email:str, resume:bytes, description:str, name_vancancie:str, name_user:str, id:int)-> None:

        self.email = email
        self.resume = resume.decode("utf-8")
        self.resumes = control_db.resumes
        self.desc = description
        self.name = name_user
        self.name_vancancie = name_vancancie
        self.id = id
        

    #gera a resposta da ia
    async def _response(self) -> None:

        input = f"vancancie name: {self.name_vancancie}, description: {self.desc},name user:{self.name}, resume: {self.resume}"
        self.res = await analyze_agent(key=enviroiments["open_ai_key"], prompt=prompt, input=input)

    #Separa a resposta
    async def _get_responses(self) -> None:

        response = self.res.split("|", 2)

        self.result = response[0].strip()
        self.sub = response[1].strip()
        self.body = response[2].strip()


    #Envia a resposta pro usuario
    async def _sender(self) -> None:

        sender.delay(email=self.email, subject=self.sub, body=self.body)

    #Atualiza status do da candidatura
    async def _update(self) -> None:

        await self.resumes.update(search="id", field=self.id, set="reason", value=self.sub + self.body)
        await self.resumes.update(search="id", field=self.id, set="status", value=self.result)

    #Executa todos os metodos
    async def run(self) -> None:

        await self._response()
        await self._get_responses()
        await self._sender()
        await self._update()




@task_app.task()
def run_agent(email:str, resume:bytes, description:str, name_vancancie:str, name_user:str, id:int) -> None:

    data = locals().copy()
    

    instance = AgentRH(**data)

    asyncio.run(instance.run())







        


    
        
