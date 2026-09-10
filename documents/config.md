# Camada de configuração (`src/config`)

## Responsabilidade

A camada `config` centraliza duas fontes de configuração:

- variáveis de ambiente usadas pelas integrações e pela infraestrutura;
- o prompt de recrutamento enviado ao modelo de IA.

Os valores são carregados durante a importação dos módulos e ficam disponíveis nos objetos globais `enviroiments` e `prompt`.

## Arquivos

### `settings.py`

#### Exceção `NotFoundEnviroment`

Indica que uma variável obrigatória não foi encontrada. A mensagem segue o formato `Expeted enviroin <nome>`.

#### Classe `Environment`

##### `__init__() -> None`

Define em `self.envs` os nomes esperados:

| Variável | Consumidor atual | Finalidade |
| --- | --- | --- |
| `redis_port` | cache e Celery | Porta do Redis |
| `redis_host` | cache e Celery | Host do Redis |
| `url` | banco | URL assíncrona do SQLAlchemy |
| `sing` | autenticação | Chave simétrica do JWT |
| `origin` | não há consumidor em `src` atualmente | Origem prevista para a aplicação |
| `rate_limit` | não há consumidor em `src` atualmente | Limite previsto por operação |
| `global_rate_limit` | não há consumidor em `src` atualmente | Limite global previsto |
| `redis_password` | cache e Celery | Senha opcional do Redis |
| `email_user` | envio de e-mail | Usuário da conta SMTP |
| `password_user` | envio de e-mail | Senha da conta SMTP |
| `open_ai_key` | agente | Chave da API OpenAI |

##### `_load() -> None`

Procura primeiro `src/config/.env`. Se o arquivo existir, chama `load_dotenv()` com esse caminho. Caso contrário, chama `load_dotenv()` sem caminho explícito, permitindo que a biblioteca procure um `.env` conforme suas regras padrão.

Falhas de carregamento são registradas e relançadas como exceção genérica.

##### `_envs() -> None`

Percorre `self.envs`, lê cada valor com `os.getenv()` e monta `self.envroins`. Todas as variáveis são obrigatórias, exceto `redis_password`, que pode ficar como `None`.

A validação verifica apenas presença. Valores vazios, portas não numéricas ou URLs inválidas não são rejeitados nessa etapa.

##### `get() -> dict`

Executa `_load()`, depois `_envs()`, e retorna o dicionário de configurações.

#### Objeto global `enviroiments`

No final do módulo, `Environment()` é instanciada e `get()` é executado imediatamente. Assim, qualquer importação de `src.config.settings` carrega o `.env` e falha imediatamente se uma variável obrigatória estiver ausente.

### `file.py`

#### Exceção `NotFoundFilePromptError`

Sinaliza que `src/config/prompt.md` não existe no caminho esperado.

#### Classe `FilePrompt`

##### `__init__()`

Calcula um caminho absoluto para `prompt.md`, sempre relativo ao próprio módulo. Isso evita dependência do diretório a partir do qual o processo Python foi iniciado.

##### `_exists() -> None`

Verifica a existência do arquivo. Se ele não existir, registra o caminho esperado e lança `NotFoundFilePromptError`.

##### `_read() -> None`

Abre o prompt como texto UTF-8 e armazena seu conteúdo completo em `self.prompt`. Erros de leitura são registrados e relançados como exceção genérica.

##### `get() -> str`

Valida a existência, lê o arquivo e devolve o texto.

#### Objeto global `prompt`

`FilePrompt().get()` é executado durante o import. Consumidores recebem uma string já carregada, mas alterações em `prompt.md` feitas depois da importação não aparecem até o módulo ou processo ser recarregado.

### `prompt.md`

Contém as instruções dadas ao agente de recrutamento. O prompt orienta o modelo a:

- comparar currículo e descrição da vaga usando evidências profissionais;
- ignorar instruções maliciosas presentes nos documentos analisados;
- evitar critérios pessoais ou protegidos;
- produzir exatamente `aproved` ou `recuse` como decisão;
- criar assunto em texto puro e corpo completo em HTML;
- separar a saída em três partes usando `|`.

Essa última convenção é consumida por `AgentRH._get_responses()`, na camada de serviço.

## Dependências e consumidores

- Depende de `python-dotenv`, `os`, `pathlib` e da camada de logs.
- É consumida por autenticação, banco, cache, Celery, e-mail e agente de IA.

## Pontos de atenção do comportamento atual

- A importação faz trabalho e pode lançar exceções antes da execução da aplicação.
- Os nomes de variáveis são sensíveis a maiúsculas e minúsculas e atualmente estão em minúsculas.
- `redis_password` é a única configuração opcional.
- Não existe conversão de tipos; por exemplo, `redis_port` permanece texto quando vem do ambiente.
- `origin` e os limites são obrigatórios mesmo sem consumidores atuais dentro de `src`.
- Segredos não devem ser registrados, incluídos no repositório ou armazenados em arquivos de documentação.
