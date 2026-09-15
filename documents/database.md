# Camada de banco de dados (`src/database`)

## Responsabilidade

A camada `database` implementa persistência relacional assíncrona com SQLAlchemy. Ela define base declarativa, engine, sessões, modelos, criação inicial de tabelas, serialização e repositórios CRUD.

Redis, autenticação, Celery, OpenAI e regras HTTP ficam fora desta camada.

## Conexão e sessões

`ConenctionDb` usa `create_async_engine(url)` e cria `async_sessionmaker` com `expire_on_commit=False`.

```python
connection = ConenctionDb(url=database_url)
connection.run()
await connection.test()
```

`test()` abre uma sessão e executa `SELECT 1;`. `run()` prepara `engine` e `make_session`, mas não retorna a própria instância no código atual.

O DSN precisa usar um driver assíncrono, por exemplo:

```text
postgresql+asyncpg://user:password@host:5432/database
```

## Modelos

### `Users`

| Campo | Tipo | Regras atuais |
| --- | --- | --- |
| `id` | inteiro | PK, indexado |
| `public_id` | UUID | único, indexado, `uuid4` |
| `name` | string(50) | opcional |
| `email` | string(50) | obrigatório, único, indexado |
| `cpf` | string(12) | opcional, único, indexado |
| `age` | inteiro | opcional |
| `gender` | string(15) | opcional |
| `password` | string(100) | opcional; admin inicial pode não possuir senha |
| `permission` | booleano | padrão `False` |
| `role` | string(20) | padrão `user` |
| `created_at` | datetime | padrão `datetime.now` |

### `Vancancies`

| Campo | Tipo | Regras atuais |
| --- | --- | --- |
| `id` | inteiro | PK, indexado |
| `created_by` | inteiro | FK para `users.id` |
| `name` | string(50) | obrigatório, único, indexado |
| `description` | texto | obrigatório |
| `created_at` | datetime | padrão `datetime.now` |
| `resumes` | relacionamento | lista com `delete-orphan` |

### `Resumes`

| Campo | Tipo | Regras atuais |
| --- | --- | --- |
| `id` | inteiro | PK, indexado |
| `user_id` | inteiro | FK para `users.id` |
| `vancancie_id` | inteiro | FK para `vancancies.id` |
| `pdf` | LargeBinary | obrigatório |
| `status` | string(12) | `pending`, `aproved` ou `recuse` |
| `reason` | texto | padrão literal `"null"` |
| `created_at` | datetime | padrão `datetime.now` |
| `vancancie` | relacionamento | volta para a vaga |

```mermaid
erDiagram
    USERS ||--o{ VANCANCIES : creates
    USERS ||--o{ RESUMES : submits
    VANCANCIES ||--o{ RESUMES : receives

    USERS {
      int id PK
      uuid public_id UK
      string email UK
      string role
    }
    VANCANCIES {
      int id PK
      int created_by FK
      string name UK
    }
    RESUMES {
      int id PK
      int user_id FK
      int vancancie_id FK
      bytes pdf
      string status
    }
```

O relacionamento entre usuário e currículo existe pela foreign key, mas não está declarado como `relationship()` no model `Users`.

## Criação das tabelas

`migration_db(engine)` executa `Base.metadata.create_all`. O comando usado pelo container é:

```bash
python -m src.service.db.migration make_migration_tables
```

Esse mecanismo cria tabelas ausentes, mas não mantém histórico nem executa migrações incrementais como Alembic.

## Serialização

`model_to_dict(instance)` usa `inspect(instance).mapper.column_attrs`. Portanto, converte somente colunas mapeadas e não inclui relacionamentos automaticamente.

`VancanciesDb` possui `_to_dict_with_resumes()` para complementar essa regra: adiciona os currículos relacionados, transforma datas em texto e PDFs em Base64.

## Repositório de usuários

`UsersDb` oferece:

- `insert(...)`: cria e retorna o usuário;
- `select(search, value, is_all, is_admin)`: busca por `public_id`, `email`, `id` ou `cpf`;
- `update(...)`: altera senha, permissão, papel, idade ou gênero com `FOR UPDATE`;
- `delete(public_id)`: exclui e retorna `{"deleted": bool}`.

No estado atual, o caminho `is_all` monta um `SELECT` amplo, mas ainda finaliza com `.first()`. Portanto, retorna somente um usuário e não uma lista.

## Repositório de vagas

`VancanciesDb` oferece:

- `insert(created_by, name, description)`;
- `select(search, value)` por `name`, `id`, `created_by` ou `all`;
- `update(...)` para `name` ou `description` com bloqueio da linha;
- `delete(id)`.

`search="all"` usa `.all()` e retorna `list[dict]`. As demais buscas retornam `dict | None`. Todas as vagas selecionadas carregam `resumes` por `selectinload`; a serialização inclui somente as candidaturas cujo `vancancie_id` pertence à vaga consultada.

## Repositório de currículos

`ResumesDb` oferece:

- `insert(user_id, vancancie_id, pdf, status, reason)`;
- `select(user_id=None, vancancie_id=None, id=None, get_all=False)`;
- `update(...)` para `pdf`, `status` ou `reason`;
- `delete(id)`.

Filtros fornecidos à consulta individual são combinados com `AND`. `get_all=True` ignora filtros, usa `.all()` e retorna uma lista de dicionários. A relação `vancancie` é carregada, mas `model_to_dict()` não a inclui no retorno de currículo.

## Agregador

`src/database/manage.py` cria `ControlDb`, que reúne:

```python
db.users
db.vancancies
db.resumes
```

Apesar do parâmetro se chamar `engine` e estar anotado como `AsyncEngine`, os repositórios recebem na prática uma `async_sessionmaker`.

## Transações e concorrência

Cada operação usa `async with self.eng.begin()`. Atualizações selecionam com `with_for_update()` para proteger a linha até o fim da transação. Exclusões usam `delete()` diretamente.

## Pontos de atenção

- `create_all` não substitui migrações versionadas.
- Não existem constraints SQL `CHECK` para `role`, `gender` e `status`; `Literal` atua apenas na tipagem Python.
- A combinação usuário/vaga não possui constraint única no banco; a aplicação impede duplicidade antes de inserir.
- Exclusão direta pode ter comportamento diferente do cascade ORM quando não carrega a instância.
- Listagens não têm paginação.
- O nome público `Vancancies` e `vancancie_id` contém a grafia usada pelo código e pela API.
