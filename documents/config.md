# Camada de configuração (`src/config`)

## Responsabilidade

A camada `config` carrega variáveis de ambiente, templates HTML e o prompt que governa a análise de currículos.

## Variáveis de ambiente

`src/config/core/settings.py` procura primeiro `src/config/core/.env`. Se o arquivo não existir, `python-dotenv` procura um `.env` pelos caminhos convencionais. A configuração é carregada durante o import e fica no dicionário global `enviroiments`.

| Variável | Obrigatória | Uso |
| --- | --- | --- |
| `redis_port` | Sim | Cache e Celery |
| `redis_host` | Sim | Cache e Celery |
| `redis_password` | Não | Autenticação Redis |
| `url` | Sim | DSN assíncrona do SQLAlchemy |
| `sing` | Sim | Assinatura JWT HS256 |
| `origin` | Sim | Origem autorizada no CORS |
| `rate_limit` | Sim | Limite individual por janela |
| `global_rate_limit` | Sim | Limite global por janela |
| `email_user` | Sim | Conta SMTP e admin inicial |
| `password_user` | Sim | Credencial SMTP |
| `open_ai_key` | Sim | OpenAI Responses API |
| `environment` | Sim | Alterna fluxo normal e teste |
| `test_email` | Não | Campo opcional para testes |

Exemplo sem valores reais:

```dotenv
redis_port=6379
redis_host=redis
redis_password=
url=postgresql+asyncpg://USER:PASSWORD@HOST:5432/DATABASE
sing=troque-por-uma-chave-longa-e-aleatoria
origin=http://localhost:3000
rate_limit=100
global_rate_limit=1000
email_user=conta@gmail.com
password_user=senha-de-aplicativo
open_ai_key=chave-da-api
environment=test
test_email=
```

Não versione o `.env`. O `.gitignore` dentro de `src` exclui `config/core/.env`.

## Ambiente local e Docker

Fora do Docker, `redis_host` normalmente é `localhost` e a porta publicada é `6350`. Dentro do Compose, os serviços recebem `redis_host=redis` e `redis_port=6379`.

Use `--env-file` para alimentar a interpolação do Compose:

```bash
docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml up -d --build
```

## Prompt da IA

`src/config/prompt/file_prompt.py` lê `src/config/prompt/prompt.md` e exporta seu conteúdo em `prompt`. O contrato exige uma única string:

```text
aproved | Assunto profissional | <!DOCTYPE html><html>...</html>
```

ou:

```text
recuse | Assunto profissional | <!DOCTYPE html><html>...</html>
```

Os únicos caracteres `|` permitidos são os dois separadores.

## Templates de e-mail

`src/config/sender/file.py` descobre os arquivos `.html` e cria `senders`, usando o nome sem extensão como chave.

| Chave | Template |
| --- | --- |
| `create_account` | Código de criação da conta |
| `two_factor_authentication` | Código de 2FA |
| `update_password` | Código de alteração de senha |
| `resume_analysis_test` | Resultado simulado do agente |

## Comportamento de teste

Com `environment=test`, códigos temporários retornam no JSON e o agente monta `aproved | assunto | HTML` com `resume_analysis_test.html`, sem chamar a OpenAI.

## Pontos de atenção

- A configuração é avaliada no import; variável ausente pode impedir módulos de carregar.
- Todos os valores chegam como texto e são convertidos apenas no ponto de uso.
- Templates usam placeholders; mudanças devem preservar a quantidade e ordem esperadas.
- Alterações em prompt/templates exigem reinício do processo ou container.
- Segredos devem existir apenas em `.env`, secrets do CI ou secret manager.
