# Camada de tarefas (`src/task`)

## Responsabilidade

A camada `task` cria a aplicação Celery. As tarefas concretas ficam em `src/service/cache` e `src/service/utils`.

## `TaskControl`

`src/task/celery.py` recebe host, porta e senha opcional do Redis. `_formated()` separa broker e backend:

```text
redis://<host>:<port>/1   # broker
redis://<host>:<port>/2   # backend
```

Com senha, o código atual usa:

```text
redis://<password>@<host>:<port>/<db>
```

`_connect()` cria `Celery(broker=..., backend=...)`, e `run()` devolve a instância.

## Registro das tarefas

`src/service/task.py` exporta `task_app` e define os módulos importados pelo worker:

```python
task_app.conf.imports = (
    "src.service.cache.task",
    "src.service.utils.sender",
    "src.service.utils.agent"
)
```

Tarefas registradas:

| Tarefa | Responsabilidade |
| --- | --- |
| `increment` | Incrementar contador Redis |
| `hset` | Gravar hash com TTL |
| `delete` | Invalidar chave |
| `set` | Gravar valor temporário |
| `sender` | Enviar e-mail HTML |
| `run_agent` | Analisar currículo e atualizar candidatura |

## Ponte síncrono/assíncrono

As funções Celery são síncronas e chamam os serviços assíncronos com `asyncio.run()`:

```text
API → task.delay() → Redis /1 → worker Celery
                                   ↓
                              asyncio.run()
                                   ↓
                        banco, cache, OpenAI ou SMTP
```

## Worker

Localmente:

```bash
python -m celery \
  -A src.service.task:task_app \
  worker --loglevel=INFO
```

No Docker, `Dockerfile.worker` usa esse comando como `CMD`, e o serviço se chama `agent`.

## Resultado e acompanhamento

O backend usa Redis `/2`, mas os chamadores atuais não armazenam o `AsyncResult` retornado por `.delay()`. O sistema trabalha em fire-and-forget: confirma que a tarefa foi enviada, sem expor endpoint de progresso.

## Pontos de atenção

- `.delay()` não significa que a tarefa terminou.
- Não há política explícita de retry, timeout, fila, prioridade ou dead-letter.
- Bytes enviados à tarefa dependem do serializador Celery configurado.
- Worker, API e migration precisam compartilhar banco, Redis e variáveis de ambiente.
- Senhas Redis com caracteres reservados podem exigir URL encoding.
- Escalar workers pode aumentar concorrência sobre SMTP, OpenAI e banco.
