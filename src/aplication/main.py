"""
Inicializa a aplicação
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.aplication.handles.users import router_users
from src.aplication.handles.sender import router_sender
from src.aplication.handles.auth import router_auth
from src.aplication.handles.admin import router_admin
from src.aplication.handles.vancancies import router_vancancies
from src.aplication.handles.resumes import router_resumes
from src.aplication.midlleware import Midlleware
from src.service.module import enviroiments


class Aplication:

    def __init__(self)-> None:

        self.routes = [router_sender, router_users, router_auth, router_admin, router_vancancies, router_resumes]
        self.origin = enviroiments["origin"]
        self.app = FastAPI()


    #Adiciona as configurações de cors
    def _cors(self) -> None:

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[self.origin],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
            
        )

    #Adiciona as rotas
    def _routes(self) -> None:

        for router in self.routes:

            self.app.include_router(router)

    #Adiciona o midlleware
    def _mid(self) -> None:

        self.app.add_middleware(Midlleware)


    #Executa os metodos e retorna a instancia do fast api
    def run(self) -> FastAPI:

        self._cors()
        self._mid()
        self._routes()
        return self.app




"""Instancia Aplication"""
instance = Aplication()
app = instance.run()



        