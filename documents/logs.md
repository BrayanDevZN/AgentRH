# Camada de logs (`src/logs`)

## Responsabilidade

A camada `logs` centraliza a configuração do logging do AgentRH. Cada módulo obtém um logger com:

```python
logger = LayerLogger("database").build()
```

## Formato

As mensagens seguem:

```text
[AAAA-MM-DD HH:MM:SS] [NÍVEL] [layer.nome]: mensagem
```

Cada logger possui dois destinos:

- `StreamHandler` em `stderr`, visível no terminal e nos logs Docker;
- `FileHandler` UTF-8 em `src/logs/<camada>.log`.

## `LayerLogger`

`src/logs/log.py` normaliza o nome da camada, cria o formatador, remove handlers anteriores do mesmo logger e instala os dois novos handlers. A propagação para o logger raiz é desativada para evitar duplicação.

## Loggers atuais

| Logger | Arquivo | Consumidores |
| --- | --- | --- |
| `layer.aplication` | `aplication.log` | Handlers HTTP |
| `layer.auth` | `auth.log` | bcrypt e JWT |
| `layer.cache` | `cache.log` | Redis |
| `layer.config` | `config.log` | Ambiente, prompt e templates |
| `layer.database` | `database.log` | Conexão, tabelas e repositórios |
| `layer.service` | `service.log` | Admin e serviços |
| `layer.tasks` | `tasks.log` | Celery |
| `layer.utils` | `utils.log` | OpenAI e SMTP |

Os arquivos `.log` são ignorados por `src/logs/.gitignore`.

## Uso recomendado

```python
logger.info("Operação iniciada")
logger.warning("Tentativa será repetida")
logger.error(error)
logger.exception("Falha com traceback")
```

Use `exception()` dentro de um `except` quando o traceback for necessário. Não registre senhas, tokens, chaves da API, conteúdo integral de currículos ou códigos temporários.

## Docker

Para acompanhar os processos principais:

```bash
docker compose --env-file src/config/core/.env \
  -f src/controller/compose.yml \
  logs -f api-agent agent migration
```

Como os Dockerfiles não montam volume persistente para `src/logs`, arquivos gravados dentro do container são perdidos quando ele é removido; a saída em `stderr` permanece disponível pelo driver de logs do Docker enquanto o container existir.

## Pontos de atenção

- Não há rotação, retenção ou limite de tamanho dos arquivos.
- O nível está fixo em `INFO`.
- Criar um logger acontece no import e abre o arquivo correspondente.
- Reconstruir um logger remove e adiciona seus handlers novamente.
- Logs estruturados em JSON e correlação por requisição ainda não estão configurados.
