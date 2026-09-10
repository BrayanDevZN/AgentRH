# Camada de tarefas (`src/task`)

## Responsabilidade

A camada `task` cria a aplicação Celery usada para executar operações em segundo plano. Ela define conexão e backend, mas as tarefas concretas são declaradas na camada `service`.

## Arquivo `celery.py`

### Classe `TaskControl`

#### `__init__(port, host, password=None) -> None`

Armazena os dados de acesso ao Redis. O tipo aceito para porta é `str | int`; a senha está anotada como `str | int | None`.

#### `_formated() -> None`

Monta duas URLs Redis:

- `self.broker`: banco lógico 1, usado como fila de mensagens;
- `self.back`: banco lógico 2, usado como backend de resultados.

Sem senha:

```text
redis://<host>:<port>/1
redis://<host>:<port>/2
```

Com senha:

```text
redis://<password>@<host>:<port>/1
redis://<password>@<host>:<port>/2
```

#### `_connect() -> None`

Cria `Celery(broker=self.broker, backend=self.back)` e guarda a aplicação em `self.con`. Essa etapa cria o objeto de configuração; a conexão efetiva com o broker pode acontecer posteriormente, quando uma tarefa for enviada ou quando o worker iniciar.

Falhas são registradas e relançadas como exceção genérica.

#### `run() -> Celery`

Formata as URLs, cria a aplicação e retorna a instância Celery.

## Configuração na camada de serviço

`src/service/task.py` lê as configurações do Redis, executa `TaskControl.run()` e expõe `task_app`.

Depois, define os módulos que o worker deve importar:

```python
task_app.conf.imports = (
    "src.service.cache.task",
    "src.service.utils.sender",
    "src.service.utils.agent",
)
```

Esses imports registram cinco tarefas:

| Tarefa | Módulo | Função |
| --- | --- | --- |
| `increment` | `service.cache.task` | Incrementar contador Redis |
| `hset` | `service.cache.task` | Gravar hash Redis |
| `delete` | `service.cache.task` | Remover chave Redis |
| `sender` | `service.utils.sender` | Enviar e-mail |
| `run_agent` | `service.utils.agent` | Avaliar currículo e concluir o fluxo |

## Adaptação entre Celery e código assíncrono

As funções registradas no Celery são síncronas. Dentro delas, `asyncio.run()` cria um event loop temporário para executar os métodos assíncronos das outras camadas. Cada execução da tarefa abre e encerra seu próprio loop.

Exemplo conceitual:

```text
chamador -> tarefa.delay(...) -> Redis broker -> worker Celery
worker -> função síncrona -> asyncio.run(...) -> função assíncrona
```

## Relação entre os bancos lógicos Redis

- O cliente de cache de dados não informa um número de banco e, portanto, usa o padrão do Redis, normalmente `/0`.
- O broker Celery usa `/1`.
- O backend de resultados usa `/2`.

Essa separação reduz colisões entre chaves de aplicação, mensagens da fila e resultados de tarefas.

## Pontos de atenção do comportamento atual

- Enfileirar com `.delay()` confirma o envio ao broker, não a conclusão da operação.
- Os controladores de serviço não guardam o identificador retornado por `.delay()`, então não acompanham status ou resultado.
- Não há configuração explícita de retry, timeout, serializador, fila ou política de falha.
- `bytes` é aceito por `run_agent`; o serializador Celery configurado no ambiente precisa suportar esse argumento.
- A URL com senha segue o formato atual do código. Senhas com caracteres reservados podem precisar de codificação para URL.
- Worker e processo chamador precisam compartilhar as mesmas variáveis de ambiente e alcançar o mesmo Redis e banco.
