# Camada de logs (`src/logs`)

## Responsabilidade

A camada `logs` fornece uma configuração padronizada de logging para todo o sistema. Cada camada cria seu logger chamando `LayerLogger(<nome>).build()`.

## Arquivo `log.py`

### Classe `LayerLogger`

#### `__init__(layer_name: str)`

Normaliza o nome recebido removendo espaços nas extremidades e convertendo-o para minúsculas. Em seguida:

- cria o formatador padrão;
- define o arquivo como `src/logs/<layer_name>.log`;
- recupera um logger do registro global do Python com o nome `layer.<layer_name>`.

Exemplo: `LayerLogger("database")` usa o logger `layer.database` e grava em `src/logs/database.log`.

#### `_create_formatter() -> logging.Formatter`

Define o formato:

```text
[AAAA-MM-DD HH:MM:SS] [NÍVEL] [NOME_DO_LOGGER]: mensagem
```

#### `_add_console_handler()`

Cria um `StreamHandler` direcionado a `sys.stderr`, aplica o formatador e adiciona o handler ao logger. A escolha de `stderr` mantém logs separados da saída normal da aplicação.

#### `_add_file_handler()`

Cria um `FileHandler` com UTF-8 apontando para o arquivo da camada. O arquivo é criado ou aberto quando o logger é configurado.

#### `_configure_logger()`

Configura nível `INFO`, desativa propagação para loggers ancestrais, remove handlers já existentes e adiciona novamente os handlers de console e arquivo.

A limpeza impede duplicação de mensagens quando o mesmo logger é reconstruído. Como loggers de mesmo nome são globais dentro do processo, uma nova construção substitui os handlers configurados anteriormente para aquela camada.

#### `build() -> logging.Logger`

Executa a configuração completa e retorna um `logging.Logger` padrão, pronto para chamadas como `info`, `warning` e `error`.

## Loggers usados pelo projeto

| Nome passado | Arquivo produzido | Principais consumidores |
| --- | --- | --- |
| `auth` | `src/logs/auth.log` | Hash e JWT |
| `cache` | `src/logs/cache.log` | Conexão e operações Redis |
| `config` | `src/logs/config.log` | Ambiente e leitura do prompt |
| `database` | `src/logs/database.log` | Engine, migração e repositórios |
| `tasks` | `src/logs/tasks.log` | Configuração do Celery |
| `utils` | `src/logs/utils.log` | OpenAI e e-mail |

## Ciclo de uso

Os módulos geralmente criam o logger no topo do arquivo. Portanto, importar a camada já configura seus handlers e pode criar ou abrir o arquivo correspondente. Durante uma operação, a mensagem inicial é registrada; em caso de erro, a exceção é registrada antes de ser relançada.

## Pontos de atenção do comportamento atual

- Os arquivos ficam dentro de `src/logs`, misturando código-fonte e artefatos de execução.
- Não há rotação ou limite de tamanho; os arquivos podem crescer continuamente.
- O nível está fixo em `INFO`, sem configuração por ambiente.
- Vários módulos da mesma camada constroem o mesmo logger. A limpeza de handlers evita duplicação, mas reconfigura o objeto compartilhado.
- Dados incluídos diretamente nas mensagens podem ir para disco; informações sensíveis devem ser evitadas.
