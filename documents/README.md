<h1 align="center">AgentRH</h1>

<p align="center">
  <img src="assets/agentrh-flow.gif" alt="Fluxo animado do AgentRH" width="100%">
</p>

<p align="center">
  <strong>API assíncrona para recrutamento, gestão de vagas e análise automatizada de currículos.</strong>
</p>

<p align="center">
  <a href="https://github.com/BrayanDevZN/AgentRH/actions/workflows/unit.yml"><img alt="Testes unitários" src="https://img.shields.io/github/actions/workflow/status/BrayanDevZN/AgentRH/unit.yml?branch=develop&style=for-the-badge&label=UNIT%C3%81RIOS&logo=githubactions&logoColor=white"></a>
  <a href="https://github.com/BrayanDevZN/AgentRH/actions/workflows/integration.yml"><img alt="Testes de integração" src="https://img.shields.io/github/actions/workflow/status/BrayanDevZN/AgentRH/integration.yml?branch=develop&style=for-the-badge&label=INTEGRA%C3%87%C3%83O&logo=githubactions&logoColor=white"></a>
  <a href="https://github.com/BrayanDevZN/AgentRH/actions/workflows/functional.yml"><img alt="Testes funcionais" src="https://img.shields.io/github/actions/workflow/status/BrayanDevZN/AgentRH/functional.yml?branch=develop&style=for-the-badge&label=FUNCIONAIS&logo=githubactions&logoColor=white"></a>
  <img alt="CD com Docker Compose" src="https://img.shields.io/badge/CD-DOCKER_COMPOSE-2496ED?style=for-the-badge&logo=docker&logoColor=white">
</p>

<p align="center">
  <img alt="Python 3.14" src="https://img.shields.io/badge/PYTHON-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="FastAPI 0.141" src="https://img.shields.io/badge/FASTAPI-0.141-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img alt="PostgreSQL assíncrono" src="https://img.shields.io/badge/POSTGRESQL-ASYNC-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">
  <img alt="Redis" src="https://img.shields.io/badge/REDIS-CACHE_%2B_BROKER-DC382D?style=for-the-badge&logo=redis&logoColor=white">
  <img alt="Celery 5.6" src="https://img.shields.io/badge/CELERY-5.6-37814A?style=for-the-badge&logo=celery&logoColor=white">
  <img alt="OpenAI" src="https://img.shields.io/badge/OPENAI-AN%C3%81LISE_COM_IA-412991?style=for-the-badge&logo=openai&logoColor=white">
</p>

O AgentRH organiza o ciclo de uma candidatura em uma API FastAPI: cadastro e autenticação, administração de usuários, publicação de vagas, upload de currículos, processamento em segundo plano, análise com IA, envio de e-mail e atualização do resultado. PostgreSQL mantém os dados, Redis sustenta cache e filas, e Celery executa o trabalho assíncrono.

> O código utiliza atualmente as grafias `aplication`, `vancancies`, `vancancie_id`, `enviroiments`, `sing` e `ConenctionDb`. Este README preserva esses nomes nos comandos e exemplos para que possam ser copiados sem quebrar imports ou contratos existentes.

## Sumário

- [Principais recursos](#principais-recursos)
- [Como funciona](#como-funciona)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Pré-requisitos](#pré-requisitos)
- [Início rápido com Docker](#início-rápido-com-docker)
- [Configuração do ambiente](#configuração-do-ambiente)
- [Como usar a API](#como-usar-a-api)
- [Execução local sem Docker](#execução-local-sem-docker)
- [Containers e publicação](#containers-e-publicação)
- [Testes](#testes)
- [CI/CD](#cicd)
- [Documentação das camadas](#documentação-das-camadas)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Segurança e limitações atuais](#segurança-e-limitações-atuais)
- [Solução de problemas](#solução-de-problemas)

## Principais recursos

- Cadastro com código temporário enviado por e-mail.
- Login com cookies HTTP-only e autenticação em duas etapas opcional.
- Admin inicial criado automaticamente no bootstrap.
- Controle de acesso por papel `user`/`admin`.
- Gestão de usuários e promoção/rebaixamento administrativo.
- CRUD de vagas com consulta individual ou listagem completa.
- Upload de currículo em `multipart/form-data`.
- Persistência do arquivo como bytes e retorno JSON em Base64.
- Relação entre vagas e candidaturas carregada pelo SQLAlchemy.
- Análise assíncrona de currículo usando OpenAI Responses API.
- Resposta estruturada da IA em decisão, assunto e HTML.
- E-mail de resultado enviado por worker Celery.
- Cache-aside e rate limiting apoiados por Redis.
- Testes unitários, de integração e funcionais no GitHub Actions.
- Três imagens Docker separadas para API, worker e bootstrap.

## Como funciona

Uma candidatura percorre este fluxo:

```mermaid
sequenceDiagram
    autonumber
    actor Candidate as Candidato
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Redis as Redis
    participant Worker as Celery Worker
    participant AI as OpenAI
    participant Mail as SMTP

    Candidate->>API: POST /resumes/ (multipart + PDF)
    API->>DB: Cria candidatura pending
    API->>Redis: Enfileira run_agent
    API-->>Candidate: 201 {status: true}
    Redis->>Worker: Entrega tarefa
    Worker->>AI: Vaga + candidato + currículo
    AI-->>Worker: decisão + assunto + HTML
    Worker->>Redis: Enfileira e-mail
    Worker->>DB: Atualiza reason e status
    Redis->>Mail: Entrega tarefa de envio
    Mail-->>Candidate: Resultado por e-mail
```

Com `environment=test`, a etapa OpenAI é substituída por uma resposta HTML determinística no mesmo formato. Os códigos de cadastro e 2FA também aparecem no JSON para permitir automação.

## Arquitetura

```mermaid
flowchart LR
    Client[Cliente HTTP] --> MW[Middleware<br/>CORS + rate limit]
    MW --> Routes[FastAPI routers<br/>schemas + dependências]
    Routes --> Services[Camada service]

    Services --> Auth[bcrypt + JWT]
    Services --> Repositories[Repositórios SQLAlchemy]
    Repositories --> Postgres[(PostgreSQL)]

    Services --> Cache[(Redis /0<br/>cache e códigos)]
    Services --> Broker[(Redis /1<br/>broker Celery)]
    Broker --> Worker[Worker Celery]
    Worker --> OpenAI[OpenAI Responses API]
    Worker --> SMTP[SMTP / yagmail]
    Worker --> Repositories
    Worker --> Cache

    Broker -. resultados .-> Backend[(Redis /2)]
```

### Separação por camadas

| Camada | Caminho | Responsabilidade |
| --- | --- | --- |
| Aplicação | `src/aplication` | FastAPI, rotas, schemas, cookies, dependências e middleware |
| Autenticação | `src/auth` | Hash bcrypt e tokens JWT |
| Cache | `src/cache` | Cliente Redis e primitivas de cache |
| Configuração | `src/config` | Ambiente, prompt e templates HTML |
| Containers | `src/controller` | Compose, Dockerfiles e dependências |
| Banco | `src/database` | Engine, sessões, models, tabelas e repositórios |
| Logs | `src/logs` | Formatação e handlers de log |
| Serviços | `src/service` | Orquestração, cache-aside, Celery, admin e agente |
| Tarefas | `src/task` | Construção da aplicação Celery |
| Integrações | `src/utils` | OpenAI e SMTP |

## Tecnologias

| Categoria | Tecnologia |
| --- | --- |
| Linguagem | Python 3.14 |
| API e validação | FastAPI, Starlette, Pydantic |
| Servidor ASGI | Uvicorn |
| Persistência | PostgreSQL, SQLAlchemy assíncrono, asyncpg |
| Cache e mensageria | Redis |
| Processamento assíncrono | Celery |
| Segurança | bcrypt, PyJWT |
| IA | OpenAI Python SDK e Responses API |
| E-mail | yagmail/SMTP e templates HTML |
| Containers | Docker e Docker Compose |
| Testes HTTP | requests |

## Pré-requisitos

Para o caminho recomendado com containers:

- Docker Engine ou Docker Desktop;
- plugin Docker Compose;
- uma instância PostgreSQL acessível pelos containers;
- conta SMTP compatível com yagmail;
- chave OpenAI para ambientes diferentes de `test`.

O Compose inclui Redis, mas **não inclui PostgreSQL**. A URL do banco deve apontar para um serviço externo ou para um PostgreSQL executado separadamente.

## Início rápido com Docker

### 1. Clone o projeto

```bash
git clone https://github.com/BrayanDevZN/AgentRH.git
cd AgentRH
```

### 2. Crie o arquivo de ambiente

```bash
cp src/config/core/.env.example src/config/core/.env
```

Se `.env.example` ainda não estiver disponível na sua revisão, crie manualmente `src/config/core/.env` usando a tabela da próxima seção.

### 3. Ajuste o DSN do PostgreSQL

Exemplo:

```dotenv
url=postgresql+asyncpg://agentrh:senha@host-do-postgres:5432/agentrh
```

Se o banco estiver no host e o Docker rodar no Linux, use um hostname alcançável pelos containers. `localhost` dentro do container aponta para o próprio container.

### 4. Construa e inicie

```bash
docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml \
  up -d --build
```

O bootstrap executa, em ordem:

1. Redis;
2. criação das tabelas;
3. criação do admin inicial;
4. API;
5. worker Celery.

### 5. Confira os serviços

```bash
docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml \
  ps
```

```bash
docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml \
  logs -f api-agent agent migration
```

### 6. Abra a API

- Swagger UI: `http://localhost:650/docs`
- OpenAPI JSON: `http://localhost:650/openapi.json`
- Redis no host: `localhost:6350`

### 7. Encerre o ambiente

```bash
docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml \
  down
```

## Configuração do ambiente

Crie `src/config/core/.env`:

```dotenv
# Redis usado dentro do Compose
redis_port=6379
redis_host=redis
redis_password=

# PostgreSQL assíncrono
url=postgresql+asyncpg://USER:PASSWORD@HOST:5432/DATABASE

# Autenticação e CORS
sing=UMA_CHAVE_LONGA_E_ALEATORIA
origin=http://localhost:3000

# Janela de aproximadamente 60 segundos
rate_limit=100
global_rate_limit=1000

# SMTP e admin inicial
email_user=conta@gmail.com
password_user=SENHA_DE_APLICATIVO

# IA e comportamento do ambiente
open_ai_key=SUA_CHAVE_OPENAI
environment=test
test_email=
```

| Variável | Obrigatória | Descrição |
| --- | --- | --- |
| `redis_port` | Sim | Porta interna do Redis |
| `redis_host` | Sim | Host Redis visto pela aplicação |
| `redis_password` | Não | Senha Redis, quando utilizada |
| `url` | Sim | URL SQLAlchemy com driver assíncrono |
| `sing` | Sim | Chave HS256 dos JWTs |
| `origin` | Sim | Origem permitida pelo CORS |
| `rate_limit` | Sim | Máximo aproximado por cliente/token |
| `global_rate_limit` | Sim | Máximo aproximado global |
| `email_user` | Sim | Remetente SMTP e e-mail do admin inicial |
| `password_user` | Sim | Credencial ou senha de aplicativo SMTP |
| `open_ai_key` | Sim | Chave usada pela análise em produção |
| `environment` | Sim | Use `test` para respostas determinísticas |
| `test_email` | Não | Campo auxiliar opcional de teste |

Nunca envie esse arquivo para o Git. O caminho já está ignorado em `src/.gitignore`.

## Como usar a API

Os exemplos abaixo usam `curl` e um arquivo `cookies.txt` para preservar os cookies. O código atual recebe JSON também em algumas operações `GET`, por isso os exemplos usam `-X GET -d`.

### 1. Solicitar código de cadastro

```bash
curl -X POST http://localhost:650/sender/ \
  -H 'Content-Type: application/json' \
  -d '{"name":"Ada Lovelace","email":"ada.lovelace@gmail.com"}'
```

Em `environment=test`:

```json
{"status":true,"code":"12345"}
```

Nos demais ambientes, o código é enviado por e-mail e não aparece na resposta.

### 2. Criar usuário

```bash
curl -X POST http://localhost:650/users/ \
  -c cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{
    "name":"Ada Lovelace",
    "email":"ada.lovelace@gmail.com",
    "password":"Senha123",
    "cpf":"12345678910",
    "age":28,
    "gender":"other",
    "permission":false,
    "code":"12345"
  }'
```

A criação bem-sucedida grava os cookies de acesso e renovação.

### 3. Consultar a própria conta

```bash
curl -X GET http://localhost:650/users/ -b cookies.txt
```

### 4. Entrar como admin

O admin inicial usa `email_user`, não possui senha e entra por código:

```bash
curl -X GET http://localhost:650/auth/ \
  -c admin-cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"email":"conta@gmail.com"}'
```

```bash
curl -X POST http://localhost:650/sender/2fa \
  -b admin-cookies.txt -c admin-cookies.txt
```

Use o código retornado em teste ou recebido por e-mail:

```bash
curl -X GET http://localhost:650/auth/ \
  -b admin-cookies.txt -c admin-cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"email":"conta@gmail.com","code":"12345"}'
```

### 5. Criar uma vaga

```bash
curl -X POST http://localhost:650/vancancies/ \
  -b admin-cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{
    "name":"Desenvolvedor Backend",
    "description":"Python, FastAPI, PostgreSQL, Redis e Docker"
  }'
```

Exemplo de resposta:

```json
{
  "id": 1,
  "name": "Desenvolvedor Backend",
  "description": "Python, FastAPI, PostgreSQL, Redis e Docker",
  "created_at": "2026-09-15 00:00:00"
}
```

### 6. Listar vagas

```bash
curl -X GET http://localhost:650/vancancies/ \
  -b cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"search":"all"}'
```

`search="all"` retorna uma lista. Para admin, as vagas podem conter `created_by` e `resumes`; usuários comuns recebem esses campos removidos.

### 7. Enviar currículo

```bash
curl -X POST http://localhost:650/resumes/ \
  -b cookies.txt \
  -F 'vancancie_id=1' \
  -F 'status=pending' \
  -F 'reason=null' \
  -F 'pdf=@curriculo.pdf;type=application/pdf'
```

A resposta confirma a criação. A análise continua no worker:

```json
{"status":true}
```

### 8. Consultar candidatura

```bash
curl -X GET http://localhost:650/resumes/ \
  -b cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"vancancie_id":1}'
```

O campo `pdf` volta em Base64 porque JSON não suporta bytes diretamente:

```json
{
  "id": 10,
  "user_id": 4,
  "vancancie_id": 1,
  "pdf": "JVBERi0xLjQ...",
  "status": "pending",
  "reason": "null",
  "created_at": "2026-09-15 00:00:00"
}
```

O admin pode listar todas as candidaturas com:

```bash
curl -X GET http://localhost:650/resumes/ \
  -b admin-cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"get_all":true}'
```

## Referência rápida das rotas

| Método | Rota | Autorização | Finalidade |
| --- | --- | --- | --- |
| `POST` | `/sender/` | Pública | Código de cadastro |
| `PATCH` | `/sender/` | Pública | Código de recuperação |
| `POST` | `/sender/2fa` | Cookie temporário | Código de 2FA |
| `POST` | `/users/` | Pública | Criar usuário |
| `GET/PATCH/DELETE` | `/users/` | Usuário | Ler, atualizar ou excluir a própria conta |
| `GET` | `/auth/` | Pública/2FA | Login em uma ou duas etapas |
| `PATCH/PUT/DELETE` | `/auth/` | Conforme operação | Senha, refresh e logout |
| `GET/PATCH/DELETE` | `/admin/` | Admin | Administração de usuários |
| `POST/GET/PATCH/DELETE` | `/vancancies/` | GET: usuário; mutações: admin | Vagas |
| `POST/GET/DELETE` | `/resumes/` | Usuário; `get_all`: admin | Candidaturas |

Consulte contratos completos em [documentação da aplicação](https://github.com/BrayanDevZN/AgentRH/blob/develop/documents/application.md) ou no Swagger.

## Execução local sem Docker

Você precisa ter PostgreSQL e Redis ativos e configurar `redis_host=localhost` e a porta local correta.

### 1. Ambiente Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r src/controller/dependences/requirements.txt
```

### 2. Criar tabelas e admin

```bash
python -m src.service.db.migration make_migration_tables
python -m src.service.admin create_admin
```

### 3. Iniciar API

```bash
python -m uvicorn \
  src.aplication.main:app \
  --host 0.0.0.0 \
  --port 650 \
  --reload
```

### 4. Iniciar worker em outro terminal

```bash
python -m celery \
  -A src.service.task:task_app \
  worker --loglevel=INFO
```

## Containers e publicação

O Compose cria imagens com o formato `namespace/repository:tag`:

| Serviço | Imagem |
| --- | --- |
| API | `brayandevzn/agent_rh:api` |
| Worker | `brayandevzn/agent_rh:agent` |
| Bootstrap | `brayandevzn/agent_rh:migration` |

Construir:

```bash
docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml build
```

Autenticar e publicar:

```bash
docker login
docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml push
```

O projeto possui CI automatizada, mas a publicação/deploy das imagens é manual no estado atual.

## Testes

### Unitários

```bash
python -m tests.unit.logs
python -m tests.unit.config
python -m tests.unit.sender
python -m tests.unit.tasks
python -m tests.unit.auth
python -m tests.unit.agent
```

### Integração

```bash
python -m tests.integration.connect_db
python -m tests.integration.repository
python -m tests.integration.cache
python -m tests.integration.control_db
python -m tests.integration.agent
```

### Funcionais

Com a API ativa em `http://localhost:650`:

```bash
python -m tests.functional.users
python -m tests.functional.auth
python -m tests.functional.admin
python -m tests.functional.vancancies
python -m tests.functional.resumes
```

Os testes funcionais são lineares e reutilizam cookies com `requests.Session()`. Se uma execução parar antes da limpeza, dados fixos podem permanecer no banco e causar `409` no próximo ciclo.

## CI/CD

Três workflows validam o projeto em push e pull request:

| Pipeline | Arquivo | Escopo |
| --- | --- | --- |
| Unit | `.github/workflows/unit.yml` | Logs, configuração, e-mail, tarefas e autenticação |
| Integration | `.github/workflows/integration.yml` | PostgreSQL, repositórios, Redis e serviços |
| Functional | `.github/workflows/functional.yml` | Build do Compose e fluxos HTTP completos |

Os badges no topo mostram o estado da branch `develop`. Os jobs usam Python 3.14 e secrets do environment `develop`.

### Secrets esperados no GitHub

```text
REDIS_PORT
REDIS_HOST
URL
SING
ORIGIN
RATE_LIMIT
GLOBAL_RATE_LIMIT
EMAIL_USER
PASSWORD_USER
OPEN_AI_KEY
ENVIRONMENT
```

Não existe workflow automático de CD. O badge `CD · Docker Compose manual` documenta essa condição sem indicar um deploy inexistente.

## Documentação das camadas

| Documento | Conteúdo |
| --- | --- |
| [Aplicação](https://github.com/BrayanDevZN/AgentRH/blob/develop/documents/application.md) | FastAPI, middleware, dependências, rotas e upload |
| [Autenticação](https://github.com/BrayanDevZN/AgentRH/blob/develop/documents/auth.md) | bcrypt, JWT, cookies e login |
| [Cache](https://github.com/BrayanDevZN/AgentRH/blob/develop/documents/cache.md) | Redis, chaves, TTL e serialização |
| [Configuração](https://github.com/BrayanDevZN/AgentRH/blob/develop/documents/config.md) | Ambiente, prompt e templates |
| [Containers](https://github.com/BrayanDevZN/AgentRH/blob/develop/documents/controller.md) | Dockerfiles, Compose e publicação |
| [Banco de dados](https://github.com/BrayanDevZN/AgentRH/blob/develop/documents/database.md) | SQLAlchemy, models, relações e repositórios |
| [Logs](https://github.com/BrayanDevZN/AgentRH/blob/develop/documents/logs.md) | Formato, arquivos e operação |
| [Serviços](https://github.com/BrayanDevZN/AgentRH/blob/develop/documents/service.md) | Fachadas, cache-aside, admin e agente |
| [Tarefas](https://github.com/BrayanDevZN/AgentRH/blob/develop/documents/task.md) | Celery, broker e worker |
| [Integrações](https://github.com/BrayanDevZN/AgentRH/blob/develop/documents/utils.md) | OpenAI e SMTP |
| [Testes](https://github.com/BrayanDevZN/AgentRH/blob/develop/documents/testing.md) | Suítes locais e GitHub Actions |

## Estrutura do repositório

```text
AgentRH/
├── .github/workflows/       # CI unitária, integração e funcional
├── documents/               # Documentação técnica por camada
│   └── assets/              # GIF e imagem do fluxo
├── src/
│   ├── aplication/          # FastAPI, middleware, schemas e handlers
│   ├── auth/                # bcrypt e JWT
│   ├── cache/               # Redis
│   ├── config/              # .env, prompt e templates de e-mail
│   ├── controller/          # Docker Compose, imagens e requirements
│   ├── database/            # SQLAlchemy, modelos e repositórios
│   ├── logs/                # Logging por camada
│   ├── service/             # Orquestração e tarefas de domínio
│   ├── task/                # Celery
│   └── utils/               # OpenAI e SMTP
└── tests/
    ├── unit/
    ├── integration/
    └── functional/
```

## Segurança e limitações atuais

Antes de usar em produção, considere:

- Definir cookies com `secure=True` sob HTTPS e revisar política de domínio/expiração.
- Não versionar `.env`, tokens, senhas SMTP ou chaves OpenAI.
- Usar migrations versionadas em vez de depender apenas de `create_all`.
- Adicionar paginação às listagens de usuários, vagas e currículos.
- Revisar handlers que encapsulam `HTTPException` e podem devolver `501`.
- Extrair texto de PDFs de verdade; o agente atual executa `decode("utf-8")` nos bytes.
- Validar MIME type e tamanho do upload antes de armazenar o arquivo.
- Adicionar retry, timeout e observabilidade para OpenAI, SMTP e Celery.
- Tornar operações bloqueantes de Redis, bcrypt e SMTP compatíveis com o event loop.
- Adicionar healthchecks e política de restart no Compose.
- Garantir que somente administradores recebam currículos e dados sensíveis em listagens.

## Solução de problemas

### `Expeted enviroin <nome>`

A variável não foi encontrada. Confira `src/config/core/.env` e, no Compose, mantenha `--env-file` antes de `-f` ou conforme o comando completo documentado.

### Redis funciona no Docker, mas não localmente

Dentro do Compose use `redis_host=redis` e `redis_port=6379`. Fora dele use `redis_host=localhost` e a porta publicada `6350`.

### Alterei o código, mas o container continua antigo

Não existe bind mount. Reconstrua as imagens:

```bash
docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml \
  up -d --build api-agent agent
```

### `invalid reference format`

Use `usuario/repositorio:tag`, por exemplo:

```text
brayandevzn/agent_rh:api
```

Uma referência como `brayandevzn:agent_rh:api` é inválida porque possui dois separadores de tag.

### Upload pede `body.resume`

O cliente deve enviar `multipart/form-data`, e a rota deve receber `vancancie_id/status/reason` com `Form` e `pdf` com `File`. O teste funcional em `tests/functional/resumes.py` contém um exemplo executável.

### Teste retorna `409 ... exists`

Uma execução anterior criou dados e terminou antes da limpeza. Exclua o registro restante ou use identificadores únicos.

---

Documentação mantida junto ao código. Para detalhes internos, comece por [documentação da aplicação](https://github.com/BrayanDevZN/AgentRH/blob/develop/documents/application.md) e [serviços](https://github.com/BrayanDevZN/AgentRH/blob/develop/documents/service.md).
