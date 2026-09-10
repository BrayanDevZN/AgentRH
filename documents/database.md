# Camada de banco de dados (`src/database`)

## Responsabilidade

A camada `database` implementa persistência relacional com SQLAlchemy assíncrono. Ela contém:

- a base declarativa dos modelos;
- a criação da engine e da fábrica de sessões;
- os modelos `Users`, `Vancancies` e `Resumes`;
- a criação inicial das tabelas;
- repositórios com operações de inserção, consulta, atualização e exclusão;
- um agregador que reúne os repositórios.

Os repositórios não conhecem Redis, Celery, OpenAI ou e-mail. Cache e regras de orquestração ficam na camada `service`.

## Base declarativa

### `base.py`

#### Classe `Base`

Herda de `sqlalchemy.orm.DeclarativeBase`. Todos os modelos herdam dela, permitindo que o SQLAlchemy reúna seus metadados em `Base.metadata`. A migração usa esses metadados para criar as tabelas.

## Conexão e sessões

### `connection/engine.py`

#### Exceção `ConenctionDbError`

Está declarada como erro específico da conexão, mas os métodos atuais lançam exceções genéricas. O nome `Conenction` faz parte da nomenclatura atual do código.

#### Classe `ConenctionDb`

##### `__init__(url: str)`

Armazena a URL assíncrona do banco. Ela deve usar um driver compatível com `create_async_engine()`.

##### `_engine() -> None`

Cria `self.engine` com `create_async_engine(self.url)`. A engine administra pool, dialeto e futuras conexões; sua criação não garante, sozinha, que o servidor esteja acessível.

##### `_session() -> None`

Cria `self.make_session` com `async_sessionmaker(bind=self.engine, expire_on_commit=False)`. O valor `expire_on_commit=False` mantém atributos carregados disponíveis depois do commit.

##### `test() -> None`

Abre uma transação com `self.make_session.begin()` e executa `SELECT 1;`. Se concluir, registra sucesso. Esse é o teste efetivo de comunicação com o banco.

##### `run() -> ConenctionDb`

Chama `_engine()` e `_session()`. Apesar da anotação indicar `ConenctionDb`, o método atual não possui `return`; seu resultado real é `None`. Os objetos úteis ficam nos atributos `engine` e `make_session`.

## Modelos

### `models/users.py` — classe `Users`

Representa a tabela `users`.

| Coluna | Tipo e restrições | Finalidade |
| --- | --- | --- |
| `id` | inteiro, chave primária, indexado | Identificador interno |
| `public_id` | UUID, único, indexado, padrão `uuid.uuid4` | Identificador público |
| `name` | string de até 50, obrigatório | Nome do usuário |
| `email` | string de até 50, obrigatório, único e indexado | E-mail |
| `cpf` | string de até 12, obrigatório, único e indexado | CPF |
| `age` | inteiro, obrigatório | Idade |
| `gender` | string de até 15, obrigatório | Esperado: `male`, `female` ou `other` |
| `password` | string de até 50, obrigatório | Senha armazenada pela aplicação |
| `permission` | booleano, padrão `False` | Indicador de permissão |
| `role` | string de até 20, padrão `user` | Esperado: `admin` ou `user` |
| `created_at` | data/hora, padrão `datetime.now` | Momento de criação |

Os `Literal` ajudam ferramentas de tipo, mas não criam automaticamente uma restrição `CHECK` no banco. O campo `password` tem limite 50; um hash bcrypt normalmente excede esse tamanho, o que pode provocar truncamento ou erro conforme o banco.

### `models/vancancies.py` — classe `Vancancies`

Representa a tabela `vancancies`.

| Coluna/relação | Tipo e restrições | Finalidade |
| --- | --- | --- |
| `id` | inteiro, chave primária, indexado | Identificador da vaga |
| `created_by` | inteiro, FK para `users.id` | Usuário criador |
| `name` | string de até 50, obrigatório, único e indexado | Nome da vaga |
| `description` | texto, obrigatório | Descrição completa |
| `resumes` | relacionamento, lista | Currículos associados |
| `created_at` | data/hora, padrão `datetime.now` | Momento de criação |

O relacionamento `resumes` usa `back_populates="vancancie"` e `cascade="all, delete-orphan"`. A intenção é que currículos dependentes acompanhem o ciclo de vida da vaga quando a exclusão ocorre pelo ORM.

### `models/resumes.py` — classe `Resumes`

Representa a tabela `resumes`.

| Coluna/relação | Tipo e restrições | Finalidade |
| --- | --- | --- |
| `id` | inteiro, chave primária, indexado | Identificador da candidatura/currículo |
| `user_id` | inteiro, FK para `users.id` | Candidato |
| `vancancie_id` | inteiro, FK para `vancancies.id` | Vaga relacionada |
| `pdf` | binário grande, obrigatório | Conteúdo recebido como bytes |
| `status` | string de até 12, obrigatório | `aproved`, `recuse` ou `pending` |
| `reason` | texto, padrão literal `"null"` | Justificativa/resultado |
| `vancancie` | relacionamento | Vaga associada |
| `created_at` | data/hora, padrão `datetime.now` | Momento de criação |

O valor padrão de `reason` é a string `"null"`, não o valor SQL `NULL`. Não há relacionamento ORM de volta para `Users` no modelo atual.

## Migração

### `migration/tables.py`

#### Exceção `MigrationDbError`

Encapsula falhas na criação das tabelas.

#### Função `migration_db(engine: AsyncEngine) -> None`

Abre uma transação na engine e chama `Base.metadata.create_all` por meio de `run_sync()`. Isso cria tabelas ausentes conforme os metadados importados, mas não versiona nem altera de forma controlada esquemas já existentes como uma ferramenta de migrations faria.

Para que todas as tabelas façam parte de `Base.metadata`, seus módulos de modelo precisam ter sido importados no processo. O caminho atual passa por `src.database.manage`, que importa os três repositórios e, por consequência, os modelos.

## Serialização

### `repository/serializer.py`

#### Função `model_to_dict(instance) -> dict`

Usa a inspeção do SQLAlchemy para percorrer apenas `mapper.column_attrs`. Retorna um dicionário com colunas simples e seus valores atuais. Relacionamentos, como `Vancancies.resumes`, não entram no resultado.

## Repositórios

Todos recebem uma `async_sessionmaker`, armazenada em `self.eng`, e usam `async with self.eng.begin() as session`. Ao sair sem erro, a transação é confirmada; em falha, é revertida pelo contexto.

### `repository/users.py`

#### Exceção `UsersDbError`

Encapsula qualquer falha nas operações do repositório de usuários.

#### Classe `UsersDb`

- `insert(...) -> dict`: cria `Users`, adiciona à sessão, executa `flush`, atualiza com `refresh` e retorna suas colunas como dicionário.
- `select(search, value) -> dict | None`: aceita `public_id`, `email`, `id` ou `cpf`, monta a coluna a partir de um mapa e retorna o primeiro resultado ou `None`.
- `update(search, field, set, value) -> dict`: localiza com `SELECT ... FOR UPDATE`, aceita alterar apenas `password`, `permission` ou `role`, e retorna o usuário atualizado. Retorna `{}` se não encontrar.
- `delete(public_id) -> dict`: executa exclusão direta e retorna `{"deleted": bool}` com base em `rowcount`.

O parâmetro `field` de `update` é o valor usado na busca, enquanto `set` indica a coluna alterada.

### `repository/vancancies.py`

#### Exceção `VancanciesDbError`

Encapsula falhas nas operações de vagas.

#### Classe `VancanciesDb`

- `insert(created_by, name, description) -> dict`: cria e retorna uma vaga.
- `select(search, value) -> dict | None`: aceita `name`, `id` ou `created_by`; carrega `resumes` com `selectinload`, mas a serialização final inclui apenas colunas.
- `update(search, field, set, value) -> dict`: bloqueia a linha com `FOR UPDATE` e altera `name` ou `description`. Retorna `{}` se não encontrar.
- `delete(id) -> dict`: exclui diretamente por ID e retorna `{"deleted": bool}`.

Buscas por `created_by` usam `.first()`, portanto devolvem apenas uma vaga mesmo que o usuário tenha criado várias.

### `repository/resumes.py`

#### Exceção `ResumesDbError`

Encapsula falhas nas operações de currículos.

#### Classe `ResumesDb`

- `insert(user_id, vancancie_id, pdf, status="pending", reason="null") -> dict`: cria a candidatura e retorna suas colunas.
- `select(search, value) -> dict | None`: aceita `id`, `user_id` ou `vancancie_id`; carrega a vaga relacionada, mas retorna apenas as colunas do currículo.
- `update(search, field, set, value) -> dict`: bloqueia a linha e altera `pdf`, `status` ou `reason`. Retorna `{}` se não encontrar.
- `delete(id) -> dict`: exclui diretamente por ID e informa se alguma linha foi removida.

Buscas por `user_id` e `vancancie_id` retornam somente o primeiro currículo encontrado.

## Agregador

### `manage.py` — classe `ControlDb`

Recebe o criador de sessões usado pelos repositórios, apesar de a anotação do parâmetro indicar `AsyncEngine`. Expõe:

- `self.users`, instância de `UsersDb`;
- `self.vancancies`, instância de `VancanciesDb`;
- `self.resumes`, instância de `ResumesDb`.

O mesmo módulo reexporta `ConenctionDb`, `migration_db` e os modelos importados pelos repositórios.

## Fluxo de uma operação

```text
serviço de entidade
    -> ControlDb
        -> repositório
            -> async_sessionmaker.begin()
                -> SQLAlchemy
                    -> banco relacional
            -> model_to_dict()
    -> dicionário
```

## Pontos de atenção do comportamento atual

- As escolhas recebidas em `search` e `set` dependem de mapas e `match`; valores fora do contrato podem gerar erro ou não atualizar campo algum.
- `FOR UPDATE` protege atualizações concorrentes até o fim da transação.
- Exclusões usam `delete()` do SQLAlchemy diretamente; comportamentos de cascade ORM podem diferir de excluir uma instância pela sessão.
- Não há paginação nem métodos que retornem listas.
- Erros de integridade, conexão e validação são agrupados na exceção específica de cada repositório.
- `src/service/db/migration.py` chama a função assíncrona `migration_db()` sem `await` ou `asyncio.run()` no estado atual; executar esse módulo dessa forma apenas cria a coroutine e pode não criar as tabelas.
