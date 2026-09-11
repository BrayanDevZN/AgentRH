"""
teste da open ai
"""

async def test_agent() -> None:

    from src.config.module import enviroiments, prompt
    from src.utils.agent import analyze_agent

    resume  = """
                João da Silva
                Desenvolvedor Backend Python
                São Paulo, Brasil
                E-mail: joao.silva@example.com

                RESUMO PROFISSIONAL

                Desenvolvedor Backend com três anos de experiência na criação e manutenção
                de APIs REST utilizando Python e FastAPI. Experiência com bancos de dados
                PostgreSQL, cache com Redis, aplicações assíncronas, Docker, testes
                automatizados e integração com serviços externos.

                EXPERIÊNCIA PROFISSIONAL

                Desenvolvedor Backend Python
                Tech Solutions Ltda.
                Janeiro de 2023 até o momento

                - Desenvolvimento de APIs REST utilizando Python e FastAPI.
                - Criação de operações assíncronas para acesso ao banco de dados.
                - Modelagem e manutenção de bancos PostgreSQL com SQLAlchemy.
                - Implementação de cache utilizando Redis.
                - Criação de testes unitários e de integração com Pytest.
                - Integração com APIs externas e serviços de envio de e-mail.
                - Containerização de aplicações utilizando Docker.
                - Participação em revisões de código e decisões técnicas.
                - Redução do tempo médio de resposta de uma API em aproximadamente 30%.

                Desenvolvedor Python Júnior
                Sistemas Digitais Brasil
                Fevereiro de 2021 a dezembro de 2022

                - Manutenção de aplicações desenvolvidas em Python.
                - Desenvolvimento de endpoints para sistemas internos.
                - Criação e otimização de consultas SQL.
                - Correção de falhas e implementação de novas funcionalidades.
                - Utilização de Git e GitHub para controle de versão.
                - Colaboração com equipes de desenvolvimento e produto.

                FORMAÇÃO ACADÊMICA

                Tecnologia em Análise e Desenvolvimento de Sistemas
                Faculdade de Tecnologia Exemplo
                Conclusão: dezembro de 2022

                COMPETÊNCIAS TÉCNICAS

                - Python
                - FastAPI
                - SQLAlchemy
                - PostgreSQL
                - Redis
                - Docker
                - Git e GitHub
                - Pytest
                - APIs REST
                - Programação assíncrona
                - Linux
                - HTML e CSS básicos

                PROJETOS

                Sistema de Recrutamento

                Desenvolvimento de uma API para cadastro de usuários, publicação de vagas,
                envio de currículos em PDF e gerenciamento de candidaturas. O sistema
                utiliza FastAPI, PostgreSQL, SQLAlchemy, Redis e Docker.

                API de Gerenciamento de Tarefas

                Criação de uma API REST com autenticação, controle de permissões,
                documentação automática e testes de integração.

                IDIOMAS

                - Português: nativo
                - Inglês: intermediário

                INFORMAÇÕES ADICIONAIS

                - Conhecimento de metodologias ágeis.
                - Facilidade para trabalhar em equipe.
                - Interesse contínuo em arquitetura de software e desenvolvimento backend.
                """

    vancancie =  """
        Desenvolvedor Backend Python Pleno

        Estamos buscando uma pessoa Desenvolvedora Backend Python para integrar
        nossa equipe de tecnologia. A pessoa será responsável pelo desenvolvimento,
        manutenção e evolução de APIs e serviços utilizados pelos sistemas da
        empresa.

        RESPONSABILIDADES

        - Desenvolver e manter APIs REST utilizando Python e FastAPI.
        - Criar soluções assíncronas, eficientes e escaláveis.
        - Integrar aplicações com bancos de dados PostgreSQL.
        - Implementar estratégias de cache utilizando Redis.
        - Criar testes unitários e de integração.
        - Investigar e corrigir falhas nas aplicações.
        - Integrar o sistema com APIs e serviços externos.
        - Participar de revisões de código e decisões técnicas.
        - Documentar endpoints e funcionalidades desenvolvidas.
        - Utilizar Docker para executar e distribuir aplicações.
        - Trabalhar em colaboração com as equipes de produto e desenvolvimento.

        REQUISITOS OBRIGATÓRIOS

        - Pelo menos dois anos de experiência profissional com Python.
        - Experiência com desenvolvimento de APIs REST.
        - Conhecimento prático de FastAPI.
        - Experiência com SQLAlchemy.
        - Conhecimento de PostgreSQL e criação de consultas SQL.
        - Experiência com Redis ou outra solução de cache.
        - Conhecimento de programação assíncrona.
        - Experiência com Git e GitHub.
        - Conhecimento de Docker.
        - Experiência na criação de testes automatizados.
        - Capacidade de trabalhar em equipe e comunicar decisões técnicas.

        REQUISITOS DESEJÁVEIS

        - Experiência com arquitetura de microsserviços.
        - Conhecimento de integração contínua e entrega contínua.
        - Experiência com serviços de nuvem.
        - Conhecimento de segurança em APIs.
        - Familiaridade com sistemas de filas e processamento em segundo plano.
        - Inglês em nível intermediário ou superior.

        FORMAÇÃO

        Ensino superior completo ou em andamento em Análise e Desenvolvimento de
        Sistemas, Ciência da Computação, Engenharia de Software ou áreas
        relacionadas.

        MODELO DE TRABALHO

        - Contratação em período integral.
        - Trabalho remoto.
        - Horário comercial com flexibilidade.
        - Participação em reuniões periódicas com a equipe.

        PERFIL PROFISSIONAL ESPERADO

        Buscamos uma pessoa organizada, responsável e colaborativa, que tenha
        atenção à qualidade do código, interesse em aprender continuamente e
        capacidade para desenvolver soluções backend confiáveis e bem estruturadas.
        """

    input = f"Descrição da vaga: {vancancie}, curriculo: {resume}"



    response = await analyze_agent(key=enviroiments["open_ai_key"], prompt=prompt, input=input)
    print(response)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agent())
