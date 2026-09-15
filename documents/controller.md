# Camada de execução (`src/controller`)

## Responsabilidade

A camada `controller` empacota e executa o AgentRH com Docker. Ela contém um Compose, três Dockerfiles e a lista de dependências Python compartilhada pelas imagens.

## Serviços do Compose

| Serviço | Imagem | Papel | Porta |
| --- | --- | --- | --- |
| `redis` | `redis:alpine` | Cache, broker Celery e backend de resultados | `6350:6379` |
| `migration` | `brayandevzn/agent_rh:migration` | Cria tabelas e o admin inicial | Apenas rede interna |
| `api-agent` | `brayandevzn/agent_rh:api` | API FastAPI/Uvicorn | `650:8000` |
| `agent` | `brayandevzn/agent_rh:agent` | Worker Celery | Apenas rede interna |

O Compose não cria um PostgreSQL. A variável `url` deve apontar para uma instância acessível pelos containers.

## Ordem de inicialização

```text
redis
  └── migration
        ├── cria as tabelas
        └── cria o admin inicial
              └── api-agent
                    └── agent
```

`depends_on` organiza a ordem de criação, mas não substitui um healthcheck de prontidão. O código de conexão ao Redis possui tentativas próprias; a conexão PostgreSQL depende da disponibilidade indicada em `url`.

## Imagens

Os três Dockerfiles partem de `python:3.14.7`, usam `/app` como diretório de trabalho, copiam `src` e instalam `src/controller/dependences/requirements.txt`.

- `Dockerfile.api`: imagem da API; o comando vem do Compose.
- `Dockerfile.worker`: inicia o worker Celery por padrão.
- `Dockerfile.migration`: imagem de inicialização; o comando vem do Compose.

Não há volume de código configurado. Mudanças locais exigem reconstrução das imagens, mesmo com `--reload` no comando do Uvicorn.

## Comandos operacionais

Subir e reconstruir:

```bash
docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml \
  up -d --build
```

Ver estado:

```bash
docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml \
  ps
```

Acompanhar logs:

```bash
docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml \
  logs -f api-agent agent migration
```

Parar os containers:

```bash
docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml \
  down
```

## Publicação das imagens

O formato dos nomes é `namespace/repository:tag`. Depois de autenticar com `docker login`:

```bash
docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml \
  build

docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml \
  push
```

As tags atuais são `migration`, `api` e `agent` no repositório `brayandevzn/agent_rh`.

## Dependências

O arquivo `requirements.txt` fixa bibliotecas de aplicação, banco, cache, filas, autenticação, OpenAI, SMTP, testes HTTP e multipart. Ao adicionar uma dependência usada em runtime, reconstrua todas as imagens que compartilham esse arquivo.

## Pontos de atenção

- A lista de dependências possui atualmente um bloco duplicado; mantenha as versões sincronizadas até ela ser normalizada.
- Segredos chegam ao Compose por interpolação de ambiente; não devem ser gravados na imagem.
- O Redis publica a porta no host sem senha por padrão.
- Não há healthchecks, limites de recursos nem política explícita de restart.
- `--reload` não observa alterações do host porque não existe bind mount.

