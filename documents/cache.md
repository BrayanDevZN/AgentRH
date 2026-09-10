# Camada de cache (`src/cache`)

## Responsabilidade

A camada `cache` encapsula a conexão com Redis e as operações usadas pelo sistema. Ela conhece Redis, pipelines, transações e expiração, mas não conhece usuários, vagas ou currículos. A definição de chaves por entidade fica na camada `service`.

## Arquivos

### `connection.py`

#### Exceção `RedisConnectionError`

Representa falhas ocorridas ao construir o cliente Redis. O teste de conexão possui tratamento próprio descrito abaixo.

#### Classe `RedisConnection`

##### `__init__(port: int | str, host: str, password: str = None)`

Armazena endereço, porta e senha. A conexão ainda não é aberta nesse momento.

##### `_con() -> None`

Cria `redis.Redis` com:

- host e porta recebidos;
- senha opcional;
- `decode_responses=True`, fazendo o cliente retornar texto em vez de bytes para respostas comuns.

O cliente é salvo em `self.con`. Falhas nessa criação são registradas e convertidas em `RedisConnectionError`.

##### `_test() -> None`

Executa `PING` para verificar se o Redis responde. Em caso de falha, tenta novamente enquanto o contador for menor que três. Considerando a tentativa inicial e as repetições, o fluxo pode realizar até quatro chamadas a `ping()`.

Quando o limite é excedido, o código atual tenta lançar `RedisConnection(e)`, isto é, uma nova instância da classe de conexão, e não `RedisConnectionError`. Esse é o comportamento implementado e pode fazer o erro final diferir do pretendido.

##### `run() -> Redis`

Orquestra `_con()` e `_test()` e retorna o cliente Redis somente depois de um `PING` bem-sucedido.

### `control.py`

#### Classe `RedisCache`

Recebe um cliente `Redis` já configurado e o armazena em `self.client`.

##### `hset(name: str, data: dict) -> None`

Armazena `data` como hash Redis:

1. Abre um pipeline transacional.
2. Observa a chave com `WATCH`.
3. Inicia a transação com `MULTI`.
4. agenda `HSET` com `mapping=data`;
5. agenda expiração de 70 segundos;
6. executa a transação.

Se ocorrer `WatchError`, reinicia o ciclo e tenta novamente, sem limite explícito de repetições.

##### `get(name: str, hash: bool = False) -> dict | None`

Lê uma chave dentro de pipeline transacional. Com `hash=True`, agenda `HGETALL`; caso contrário, agenda `GET`. O resultado de `pipeline.execute()` é uma lista, e o método retorna seu primeiro item.

Para hash inexistente, o cliente Redis normalmente retorna um dicionário vazio. Para valor simples inexistente, retorna `None`. Em caso de `WatchError`, tenta novamente sem limite explícito.

O parâmetro se chama `hash`, o que oculta o nome da função nativa `hash()` apenas dentro desse escopo.

##### `delete(name: str) -> None`

Remove a chave com `client.delete()`. A operação é executada diretamente, sem pipeline. Erros são registrados e relançados como exceção genérica.

##### `increment(name: str) -> None`

Executa `INCR` e define expiração de 70 segundos dentro de um pipeline transacional. Pode ser usado para contadores temporários, como limites de uso. Erros são registrados e relançados.

Embora os métodos estejam declarados com `async def`, o cliente Redis utilizado é síncrono. Assim, as chamadas internas bloqueiam a thread enquanto aguardam o Redis.

### `manage.py`

#### Função `cache_control(port, host, password=None) -> RedisCache`

É a fábrica da camada:

1. Cria `RedisConnection`.
2. Executa `run()`, incluindo o teste com `PING`.
3. Injeta o cliente resultante em `RedisCache`.
4. Retorna o controlador pronto.

## Integração com a camada de serviço

`src/service/cache/connection.py` lê `redis_host`, `redis_port` e `redis_password`, chama `cache_control()` e expõe o objeto global `client`. Isso significa que importar o módulo tenta conectar ao Redis imediatamente.

`src/service/cache/task.py` transforma `increment`, `hset` e `delete` em tarefas Celery. A leitura permanece direta porque precisa devolver um valor imediatamente.

`ControlCacheBackground`, em `src/service/cache/control.py`, oferece a interface consumida pelos serviços de banco:

- escrita, incremento e remoção usam `.delay()` e ocorrem em segundo plano;
- leitura chama `client.get()` diretamente e aguarda o resultado.

## Padrão de chaves

| Entidade | Chaves atuais |
| --- | --- |
| Usuário | `user:id:<id>`, `user:public_id:<uuid>`, `user:email:<email>`, `user:cpf:<cpf>` |
| Vaga | `vancancie:id:<id>`, `vancancie:name:<nome>`, `vancancie:created_by:<user_id>` |
| Currículo | `resume:id:<id>`, `resume:user_id:<user_id>`, `resume:vancancie_id:<vaga_id>` |

Todos os hashes recebem TTL de 70 segundos. Atualizações e exclusões agendam a remoção das chaves conhecidas da entidade.

## Serialização

Hashes Redis não preservam automaticamente tipos Python. Antes de gravar dados de banco, a camada de serviço usa `ChangeTypes.to_cache()`. Um campo especial `__types__` registra como reconstruir `None`, booleanos, números, UUID, datas e bytes. Na leitura, `ChangeTypes.from_cache()` restaura esses tipos.

## Pontos de atenção do comportamento atual

- A escrita no banco pode terminar antes da tarefa de cache; durante esse intervalo, uma leitura pode consultar o banco novamente.
- A invalidação também é assíncrona; uma leitura imediatamente após atualização pode observar cache antigo até a tarefa executar.
- Chaves baseadas em campos não únicos, como `created_by`, `user_id` e `vancancie_id`, guardam apenas um hash, enquanto o banco pode possuir várias linhas correspondentes.
- A política de repetição para `WatchError` não possui limite nem espera progressiva.
- `json` é importado em `control.py`, mas não é usado nesse arquivo.
