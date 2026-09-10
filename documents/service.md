# Camada de serviços (`src/service`)

## Responsabilidade

A camada `service` é a camada de composição e orquestração do AgentRH. Ela conecta configuração, autenticação, banco, cache, Celery, OpenAI e e-mail, oferecendo objetos prontos para o restante da aplicação.

Essa camada também implementa a estratégia cache-aside das entidades e o fluxo completo de avaliação de currículo.

## Módulos de composição

### `auth.py`

Lê `enviroiments["sing"]`, cria `AuthJwt` e `AuthHash` e expõe os objetos globais `auth_jwt` e `auth_hash`. Veja [auth.md](auth.md) para os métodos.

### `task.py`

Cria `task_app` com host, porta e senha do Redis e registra os módulos que contêm tarefas Celery. Veja [task.md](task.md).

### `manage.py`

Reexporta apenas `client_background` e `control_db`. É um ponto de importação reduzido para persistência e cache.

### `module.py`

É o agregador mais amplo. Reexporta autenticação, Celery, banco, cache, envio de e-mail e agente. Importá-lo aciona toda a cadeia de imports e inicializações associadas.

## Serviço de banco

### `db/connetion.py`

Cria `ConenctionDb` com a variável `url`, executa `run()` e expõe:

- `engine_session`: o `async_sessionmaker` usado nos repositórios;
- `engine`: a engine assíncrona.

Quando executado diretamente, chama `instance.test()` com `asyncio.run()`.

### `db/migration.py`

É um módulo de linha de comando que espera o argumento `make_migration_tables`. Se receber outro valor, lança `ValueError`. No código atual, `migration_db(engine=engine)` é chamado sem aguardar a coroutine; portanto, o fluxo não garante que a criação das tabelas seja executada.

### `db/change_types.py` — classe `ChangeTypes`

Converte tipos que não podem ser preservados diretamente em hashes Redis.

#### `to_cache(data: dict) -> dict`

Cria uma cópia serializável e um mapa de tipos:

| Tipo original | Valor no Redis | Marcador |
| --- | --- | --- |
| `None` | string vazia | `none` |
| `bool` | `"1"` ou `"0"` | `bool` |
| `int` | representação textual | `int` |
| `float` | representação textual | `float` |
| `UUID` | UUID textual | `uuid` |
| `datetime` | ISO 8601 | `datetime` |
| `bytes` | Base64 em ASCII | `bytes` |
| outros | valor original | sem marcador |

O mapa é salvo como JSON no campo reservado `__types__`.

#### `from_cache(data: dict) -> dict`

Copia o hash, remove e interpreta `__types__` e restaura cada valor marcado. Se o campo reservado não existir, assume `{}` e devolve os valores sem conversão adicional.

### `db/module.py` — classe `ControlDb`

Cria e reúne os serviços `ControlUsers`, `ControlResumes` e `ControlVancancies`. O objeto global `control_db` é a fachada usada por outros módulos.

## Serviços de entidade e estratégia de cache

Os três controladores seguem a mesma regra geral:

- `insert`: grava no banco e agenda cópias no cache;
- `select`: tenta cache, consulta banco quando necessário e agenda o preenchimento do cache;
- `update`: atualiza o banco e agenda invalidação do cache;
- `delete`: obtém a entidade, exclui do banco e agenda invalidação.

As gravações e remoções de cache são tarefas em segundo plano. O retorno principal não depende da conclusão dessas tarefas.

### `db/users.py` — classe `ControlUsers`

#### Construção

Cria `ControlDb(engine=engine_session).users`, obtendo um `UsersDb` ligado à fábrica global de sessões.

#### `insert(...) -> dict`

Aceita nome, idade, e-mail, senha, CPF, gênero, permissão e papel. Encaminha os dados ao repositório e agenda quatro hashes com o mesmo conteúdo:

- `user:public_id:<public_id>`;
- `user:email:<email>`;
- `user:cpf:<cpf>`;
- `user:id:<id>`.

Retorna o dicionário vindo do banco.

#### `select(search, value) -> dict | None`

Aceita busca por `public_id`, `email`, `id` ou `cpf`. Monta a chave correspondente, tenta o Redis e restaura tipos em caso de acerto. Em caso de falta, consulta o repositório; se encontrar, agenda as quatro chaves e retorna o usuário.

#### `update(search, field, set, value) -> dict | None`

Localiza o usuário conforme `search` e `field` e permite alterar `password`, `permission` ou `role`. Se não existir, retorna `None`; se existir, agenda a exclusão das quatro chaves e retorna o estado atualizado.

#### `delete(public_id) -> None`

Busca primeiro pelo identificador público para conhecer todas as chaves. Se existir, exclui no repositório e agenda a remoção das quatro entradas do cache.

### `db/vancancies.py` — classe `ControlVancancies`

#### Construção

Obtém o repositório `VancanciesDb` ligado a `engine_session`.

#### `insert(created_by, name, description) -> dict`

Grava a vaga e agenda cache por `id`, `name` e `created_by`.

#### `select(search, value) -> dict | None`

Aceita `name`, `id` ou `created_by`. Usa a chave correspondente; em cache miss, consulta o banco e agenda as três representações.

#### `update(search, field, set, value) -> dict | None`

Altera `name` ou `description` no banco. Em sucesso, agenda a remoção das chaves construídas com os valores retornados depois da atualização.

Quando o nome é alterado, a invalidação usa o nome novo. A chave baseada no nome antigo não é conhecida nesse ponto e pode permanecer até seu TTL expirar.

#### `delete(id) -> None`

Busca a vaga, exclui pelo ID e agenda a remoção das chaves por ID, criador e nome.

### `db/resumes.py` — classe `ControlResumes`

#### Construção

Obtém o repositório `ResumesDb` ligado a `engine_session`.

#### `insert(...) -> dict`

Grava usuário, vaga, conteúdo binário do currículo, status e motivo. Agenda cache por `id`, `user_id` e `vancancie_id`.

#### `select(search, value) -> dict | None`

Aceita `id`, `user_id` ou `vancancie_id`, tenta o cache e recorre ao banco em caso de falta.

#### `update(search, field, set, value) -> dict | None`

Altera `pdf`, `status` ou `reason`. Em sucesso, invalida as três chaves associadas.

#### `delete(id) -> None`

Busca por ID, exclui o registro e invalida as chaves por ID, usuário e vaga.

## Serviço de cache

### `cache/connection.py`

Cria o objeto global `client` chamando `cache_control()` com as configurações Redis. A chamada inclui `PING`, portanto importar esse módulo requer Redis acessível.

### `cache/task.py`

Registra `increment`, `hset` e `delete` como tarefas Celery síncronas. Cada função usa `asyncio.run()` para chamar o controlador de cache.

### `cache/control.py` — classe `ControlCacheBackground`

- `increment(name)`: enfileira incremento e não retorna o resultado da tarefa.
- `hset(name, data)`: enfileira gravação de hash.
- `get(name, hash=False)`: lê diretamente e retorna o valor.
- `delete(name)`: enfileira exclusão.

O objeto global `client_background` é compartilhado pelos serviços de entidade.

## Serviço de e-mail

### `utils/sender.py` — tarefa `sender`

Cria `SenderEmail` com as credenciais do ambiente e executa seu método `send()` dentro de `asyncio.run()`. Como é uma tarefa Celery, o chamador normalmente usa `sender.delay(...)`.

## Serviço do agente de RH

### `utils/agent.py` — classe `AgentRH`

Coordena toda a avaliação de uma candidatura.

#### `__init__(email, resume, description, name_vancancie, name_user, id)`

Armazena os dados do candidato e da vaga. O currículo deve chegar como `bytes` contendo texto UTF-8; ele é imediatamente convertido com `resume.decode("utf-8")`. Também guarda o controlador `control_db.resumes`.

#### `_response() -> None`

Monta uma única string contendo nome da vaga, descrição, nome do usuário e currículo. Chama `analyze_agent()` com a chave OpenAI e o prompt carregado de `src/config/prompt.md`. A saída textual fica em `self.res`.

#### `_get_responses() -> None`

Executa `self.res.split("|", 2)`, produzindo no máximo três partes:

- `self.result`: decisão;
- `self.sub`: assunto do e-mail;
- `self.body`: corpo HTML.

Espaços externos são removidos. Se a saída tiver menos de dois separadores, o acesso aos índices falha.

#### `_sender() -> None`

Enfileira a tarefa de e-mail com destinatário, assunto e corpo. O método não espera a entrega da mensagem.

#### `_update() -> None`

Executa duas atualizações separadas no currículo identificado por `self.id`:

1. define `reason` como a concatenação direta de assunto e corpo;
2. define `status` como a decisão retornada pela IA.

Cada atualização abre sua própria transação e invalida o cache. Não existe uma transação única envolvendo as duas alterações.

#### `run() -> None`

Executa sequencialmente geração da resposta, separação, enfileiramento do e-mail e atualização do currículo.

### Tarefa `run_agent(...)`

Captura os argumentos com `locals()`, cria `AgentRH` e executa `instance.run()` usando `asyncio.run()`.

## Fluxos completos

### Consulta com cache-aside

```text
consumidor -> ControlUsers/ControlVancancies/ControlResumes
           -> Redis
              -> encontrou: restaura tipos e retorna
              -> não encontrou: repositório -> banco -> agenda cache -> retorna
```

### Avaliação de candidatura

```text
run_agent.delay(...)
    -> worker Celery
    -> AgentRH.run()
    -> OpenAI gera decisão | assunto | HTML
    -> e-mail é enfileirado
    -> motivo é atualizado
    -> status é atualizado
    -> caches do currículo são invalidados em segundo plano
```

## Efeitos de importação

Importar o agregador `src.service.module` pode:

- validar todas as variáveis de ambiente;
- ler o prompt do disco;
- criar loggers e arquivos de log;
- criar a engine SQLAlchemy;
- conectar e testar o Redis;
- construir a aplicação Celery;
- instanciar controladores globais.

Esse acoplamento é relevante em testes: um teste que importa apenas um objeto do agregador ainda precisa preparar dependências e configurações das outras partes carregadas pela cadeia de imports.

## Pontos de atenção do comportamento atual

- Há dois agregadores chamados `ControlDb`: um na camada `database`, que reúne repositórios, e outro em `service/db/module.py`, que reúne serviços com cache.
- Cache é eventual porque gravações e invalidações são enfileiradas.
- Chaves associadas a consultas potencialmente múltiplas armazenam uma única entidade.
- O agente envia o e-mail antes de concluir as atualizações do currículo; falhas posteriores podem deixar a mensagem enfileirada e o banco parcialmente atualizado.
- A decisão da IA é gravada sem validação local contra `aproved` e `recuse`.
- Currículo precisa conter texto UTF-8 mesmo sendo chamado de `pdf`; bytes de um PDF binário real normalmente não podem ser decodificados diretamente dessa forma.
- A concatenação de assunto e corpo em `reason` não insere separador.
