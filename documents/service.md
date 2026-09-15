# Camada de serviços (`src/service`)

## Responsabilidade

A camada `service` compõe autenticação, banco, cache, Celery e integrações externas. Ela oferece fachadas prontas à camada HTTP e implementa os fluxos cache-aside, criação do admin e análise assíncrona de currículo.

## Pontos de composição

| Módulo | Exportação principal |
| --- | --- |
| `service/auth.py` | `auth_hash`, `auth_jwt` |
| `service/task.py` | `task_app` |
| `service/db/connetion.py` | `engine`, `engine_session` |
| `service/db/module.py` | `control_db` |
| `service/cache/control.py` | `client_background` |
| `service/module.py` | fachada ampla usada pelos handlers |

Importar `src.service.module` carrega configurações, prompt/templates, engine SQLAlchemy, Redis, Celery, autenticação e controladores. Redis e variáveis obrigatórias precisam estar disponíveis durante o import.

## Serviços de entidades

### Usuários

`ControlUsers` grava no repositório e distribui o resultado entre chaves por `public_id`, e-mail, CPF e ID. Consultas usam cache-aside; atualizações e exclusões invalidam as chaves conhecidas.

O nome `users` é escolhido quando não há campo de busca, mas a listagem administrativa ainda herda o retorno único do repositório atual.

### Vagas

`ControlVancancies` mantém caches individuais e a lista `vancancies`.

```text
select(search="all")
    ├── cache vancancies → items → list[dict]
    └── banco → serializa vagas + resumes → salva lista → retorna
```

Criação, atualização e exclusão invalidam a lista geral. Buscas individuais só aceitam cache que já possua o campo `resumes`, impedindo reutilização do formato antigo.

### Currículos

`ControlResumes` aceita seleção por combinação de `id`, `user_id` e `vancancie_id`, além de `get_all=True`.

As chaves combinadas evitam que uma consulta autorizada por usuário/vaga reutilize diretamente uma entrada incompatível. A lista administrativa fica em `resumes`; cada item é convertido separadamente por `ChangeTypes` antes de ser empacotado.

Mutações de currículo invalidam:

- caches individuais e combinados do currículo;
- lista geral `resumes`;
- caches da vaga relacionada;
- lista geral `vancancies`.

Isso é necessário porque a representação da vaga inclui suas candidaturas.

## Conversão para cache

`ChangeTypes.to_cache()` e `from_cache()` preservam valores que um hash Redis não representa nativamente: `None`, booleanos, números, UUID, datetime, bytes, listas e dicionários.

Listas de currículos seguem duas camadas de conversão:

1. cada currículo converte bytes/datetime;
2. a lista convertida é serializada como JSON no hash geral.

## Criação do admin

O comando:

```bash
python -m src.service.admin create_admin
```

busca `email_user`. Se não existir, cria um usuário com `role="admin"`, `permission=True` e campos opcionais sem preenchimento. Esse comando é executado pelo serviço `migration` depois da criação das tabelas.

## Tarefas de cache

`service/cache/task.py` registra operações Celery que executam métodos assíncronos por `asyncio.run()`:

- `increment`;
- `hset`;
- `delete`;
- `set`.

`ControlCacheBackground` escolhe quando enfileirar e quando executar imediatamente.

## E-mail

`service/utils/sender.py` registra a tarefa `sender`. O worker cria `SenderEmail` com `email_user`/`password_user` e envia assunto e HTML pelo yagmail.

## Agente de recrutamento

`AgentRH` recebe candidato, vaga, bytes do currículo e ID da candidatura. O fluxo de `run()` é:

```text
montar entrada
   ↓
OpenAI ou resposta HTML de teste
   ↓
separar decisão | assunto | corpo
   ↓
enfileirar e-mail
   ↓
atualizar reason
   ↓
atualizar status
```

Em produção, `_response()` chama `analyze_agent()`. Em `environment=test`, usa `resume_analysis_test.html` e produz uma resposta `aproved` no mesmo contrato da IA.

`_get_responses()` usa `split("|", 2)` e atribui:

- `result`: `aproved` ou `recuse`;
- `sub`: assunto;
- `body`: documento HTML.

`_update()` grava assunto + HTML em `reason` e a decisão em `status`.

## Migração e conexão

`service/db/connetion.py` cria a engine e a fábrica de sessões globais. `service/db/migration.py` fornece o comando de criação das tabelas e executa corretamente a coroutine com `asyncio.run()`.

## Consistência

O banco é a fonte principal. A resposta HTTP não espera tarefas de cache ou e-mail terminarem. Assim:

- o CRUD principal pode concluir antes do cache;
- o upload pode responder antes da análise;
- o status começa como `pending` e é atualizado pelo worker;
- falha no worker não reverte a criação original da candidatura.

## Pontos de atenção

- `AgentRH.__init__` executa `resume.decode("utf-8")`; um PDF binário real pode não ser texto UTF-8 válido.
- O envio de e-mail ocorre antes das duas atualizações do currículo e não faz parte de uma transação única.
- Não há retry/timeout específico para OpenAI ou SMTP.
- Operações de cache são eventual-consistent por serem tarefas Celery.
- Objetos globais e trabalho durante imports aumentam requisitos para testes isolados.
