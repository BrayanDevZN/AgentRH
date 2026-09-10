# Documentação técnica do AgentRH

Esta pasta descreve a arquitetura e o funcionamento atual das camadas existentes em `src`. A documentação reflete o código implementado no repositório; nomes como `sing`, `ConenctionDb` e `Vancancies` foram preservados porque fazem parte da API atual do projeto.

## Visão geral da arquitetura

O sistema é dividido em oito camadas:

| Camada | Responsabilidade principal | Documentação |
| --- | --- | --- |
| `auth` | Gerar hash de senha, comparar senhas e criar/ler tokens JWT | [auth.md](auth.md) |
| `cache` | Abrir a conexão com Redis e executar operações básicas de cache | [cache.md](cache.md) |
| `config` | Carregar variáveis de ambiente e o prompt usado pela IA | [config.md](config.md) |
| `database` | Definir modelos, criar tabelas, abrir sessões e acessar os dados | [database.md](database.md) |
| `logs` | Padronizar logs no terminal e em arquivos | [logs.md](logs.md) |
| `service` | Integrar as demais camadas e expor os serviços usados pela aplicação | [service.md](service.md) |
| `task` | Configurar o Celery e seus backends Redis | [task.md](task.md) |
| `utils` | Integrar OpenAI e envio de e-mail | [utils.md](utils.md) |

## Fluxo geral

O ponto central de composição é `src/service`. Essa camada lê as configurações, instancia autenticação, banco, cache e tarefas e oferece objetos prontos para os consumidores da aplicação.

```text
config ──────────────┬──────────────┬──────────────┐
                    │              │              │
                    v              v              v
auth <────────── service ───────> task ────────> Redis
                    │              │
                    │              └────────────> utils
                    v
              database <────────> cache
                    │
                    v
                 SQLAlchemy

Todas as camadas ───────────────────────────────> logs
```

Um fluxo típico de leitura de dados passa primeiro pela camada de serviço. Ela tenta obter a entidade no Redis; se não houver cache, consulta o repositório SQLAlchemy, converte o modelo em dicionário e agenda a gravação desse resultado no cache.

Um fluxo típico de avaliação de currículo é executado como tarefa Celery: o currículo e a descrição da vaga são enviados à OpenAI, a resposta é separada em decisão, assunto e corpo, o e-mail é enfileirado e a candidatura é atualizada no banco.

## Inicialização e efeitos de importação

Alguns módulos constroem objetos globais assim que são importados:

- `src.config.settings` carrega e valida as variáveis de ambiente.
- `src.config.file` lê `src/config/prompt.md`.
- `src.service.auth` cria os objetos de autenticação.
- `src.service.db.connetion` cria a engine e o gerenciador de sessões.
- `src.service.cache.connection` conecta ao Redis e executa `PING`.
- `src.service.task` cria a aplicação Celery.
- `src.service.db.module` cria os controladores de banco e cache.

Isso significa que importar `src.service.module`, por exemplo, exige que as variáveis obrigatórias estejam disponíveis e pode tentar acessar o Redis antes que qualquer função seja chamada.

## Convenções atuais

- Operações de domínio e infraestrutura são majoritariamente declaradas com `async def`.
- Repositórios retornam dicionários, e não instâncias SQLAlchemy.
- Ausência em consultas retorna `None`; alguns métodos de atualização retornam `{}` quando nada é encontrado.
- Erros de infraestrutura são registrados e normalmente encapsulados em exceções específicas da camada.
- Dados mantidos no Redis expiram depois de 70 segundos.
- As chaves de cache incluem o tipo da entidade, o campo de busca e seu valor, como `user:id:10`.

## Ordem sugerida de leitura

Para entender o projeto do nível mais baixo ao mais alto, leia: `config`, `logs`, `auth`, `database`, `cache`, `task`, `utils` e, por último, `service`.
