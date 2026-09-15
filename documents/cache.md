# Camada de cache (`src/cache`)

## Responsabilidade

A camada `cache` encapsula conexão e operações Redis. Ela não conhece entidades de negócio. A definição de chaves para usuários, vagas e currículos fica em `src/service/db`.

## Conexão

`RedisConnection` recebe `host`, `port` e senha opcional. `run()` cria `redis.Redis(..., decode_responses=True)`, executa `PING`, repete a tentativa em falhas transitórias e devolve o cliente conectado.

A fábrica `cache_control()` combina `RedisConnection` e `RedisCache`.

## Operações

`RedisCache` oferece métodos assíncronos sobre o cliente Redis síncrono:

| Método | Operação Redis | Expiração |
| --- | --- | --- |
| `hset(name, data)` | Hash com `HSET` | 70 segundos |
| `get(name, hash=True)` | `HGETALL` | Mantém TTL atual |
| `get(name)` | `GET` | Mantém TTL atual |
| `set(name, data, ttl)` | `SET` | 60 segundos ou `ttl` |
| `increment(name, time)` | `INCR` | 60 segundos ou `time` |
| `delete(name)` | `DEL` | — |

`hset`, `get` e `set` usam pipelines e repetem em `WatchError`.

## Cache assíncrono de serviço

`src/service/cache/control.py` expõe `client_background`:

- leituras são imediatas porque precisam devolver um valor;
- `hset`, `delete`, `increment` e `set` são enfileirados no Celery;
- `set_immediate` grava diretamente e é usado quando o código de confirmação precisa estar disponível na requisição seguinte.

Essa combinação implementa cache-aside com consistência eventual.

## Bancos Redis

| Banco | Uso |
| --- | --- |
| `/0` | Cache e códigos temporários |
| `/1` | Broker Celery |
| `/2` | Backend de resultados Celery |

## Serialização

`ChangeTypes` converte dados para hashes Redis:

| Python | Representação | Marcador |
| --- | --- | --- |
| `None` | string vazia | `none` |
| `bool` | `0` ou `1` | `bool` |
| `int` | string | `int` |
| `float` | string | `float` |
| `UUID` | string | `uuid` |
| `datetime` | ISO 8601 | `datetime` |
| `bytes` | Base64 | `bytes` |
| `dict`/`list` | JSON | `json` |

O mapa fica no campo reservado `__types__`. Listagens de currículos convertem cada item antes de empacotar a lista, preservando bytes e datas.

## Chaves atuais

### Usuários

- `user:id:<id>`
- `user:public_id:<uuid>`
- `user:email:<email>`
- `user:cpf:<cpf>`
- `users` para a visão geral administrativa

### Vagas

- `vancancie:id:<id>`
- `vancancie:name:<name>`
- `vancancie:created_by:<user_id>`
- `vancancies` para a lista completa

### Currículos

- `resume:id:<id>`
- `resume:user_id:<user_id>`
- `resume:vancancie_id:<vancancie_id>`
- `resume:user_id+vancancie_id:<user_id>:<vancancie_id>`
- chave combinada de ID, usuário e vaga para consulta autorizada
- `resumes` para a lista administrativa

### Códigos e limites

- `email_sender:create:<email>`
- `email_sender:auth:<email>`
- `user_sender:update:<email>`
- `rate_limit:<identificador>`
- `global_rate_limit`

## Invalidação

Mutações removem as chaves conhecidas da entidade. Alterações em currículos também invalidam a vaga relacionada e as listagens gerais, pois a resposta de uma vaga pode conter `resumes`.

## Pontos de atenção

- Escrita e invalidação em segundo plano criam uma pequena janela de cache desatualizado.
- O cliente Redis interno é síncrono, apesar da interface `async`, e pode bloquear o event loop.
- Loops de retry para `WatchError` não possuem limite nem backoff.
- Chaves simples baseadas em campos não únicos representam somente um item; listagens usam chaves próprias.
- O Compose publica Redis na porta `6350` do host e não configura senha.
