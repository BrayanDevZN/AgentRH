# Testes e integração contínua

## Organização

O projeto usa scripts Python executáveis diretamente com `python -m`.

| Nível | Diretório | Escopo |
| --- | --- | --- |
| Unitário | `tests/unit` | Configuração, logs, autenticação, tarefas, agente e e-mail |
| Integração | `tests/integration` | PostgreSQL, repositórios, Redis, serviços com cache e agente |
| Funcional | `tests/functional` | Fluxos HTTP completos contra a API em execução |

Os arquivos seguem um estilo linear e imprimem as respostas para facilitar diagnóstico no terminal e no GitHub Actions.

## Testes unitários

Com ambiente configurado e dependências instaladas:

```bash
python -m tests.unit.logs
python -m tests.unit.config
python -m tests.unit.sender
python -m tests.unit.tasks
python -m tests.unit.auth
python -m tests.unit.agent
```

Alguns módulos chamados de unitários ainda acessam serviços externos ou dependem de variáveis de ambiente. Eles devem ser executados com atenção ao ambiente ativo.

## Testes de integração

Exigem PostgreSQL acessível e, para cache/serviços, Redis:

```bash
python -m tests.integration.connect_db
python -m tests.integration.repository
python -m tests.integration.cache
python -m tests.integration.control_db
python -m tests.integration.agent
```

Os testes criam registros temporários, exercitam CRUD e removem os dados no final. Uma interrupção antes da limpeza pode deixar usuários, vagas ou candidaturas no banco.

## Testes funcionais

Primeiro suba o ambiente Docker. Depois execute, na ordem lógica:

```bash
python -m tests.functional.users
python -m tests.functional.auth
python -m tests.functional.admin
python -m tests.functional.vancancies
python -m tests.functional.resumes
```

O teste de currículos cobre:

1. login do admin;
2. criação de vaga;
3. criação do candidato;
4. upload multipart;
5. consulta individual e listagem administrativa;
6. leitura do relacionamento pela vaga;
7. exclusão de currículo, usuário e vaga.

Use `environment=test` para que os códigos de confirmação apareçam no JSON e para que o agente produza o HTML de teste no lugar de chamar a OpenAI.

## GitHub Actions

| Workflow | Arquivo | Gatilhos principais | Conteúdo |
| --- | --- | --- | --- |
| Unit | `.github/workflows/unit.yml` | Push/PR | Config, logs, e-mail, Celery e autenticação |
| Integration | `.github/workflows/integration.yml` | Push/PR | Banco, repositórios, Redis e serviços |
| Functional | `.github/workflows/functional.yml` | Push/PR | Compose e fluxos HTTP |

Os workflows usam Python 3.14 e leem credenciais pelo ambiente `develop` do GitHub. Segredos esperados: `REDIS_PORT`, `REDIS_HOST`, `URL`, `SING`, `ORIGIN`, `RATE_LIMIT`, `GLOBAL_RATE_LIMIT`, `EMAIL_USER`, `PASSWORD_USER`, `OPEN_AI_KEY` e `ENVIRONMENT`.

## Boas práticas ao ampliar a suíte

- Gere e-mails, CPF e nomes de vaga únicos para permitir repetição.
- Limpe dados em ordem: currículo, vaga e usuário.
- Atualize testes sempre que uma assinatura de repositório ou serviço mudar.
- Use `requests.Session()` para preservar cookies nos fluxos funcionais.
- Envie arquivos com `files={...}` e os demais campos com `data={...}`.
- Evite segredos e endereços pessoais fixos em fixtures versionadas.

## Limitações atuais

- Os scripts não usam assertions de forma consistente e podem encerrar cedo com `return`.
- Alguns fluxos usam dados fixos, o que pode causar `409` depois de uma execução interrompida.
- O workflow funcional depende de serviços externos configurados nos secrets.
- Não existe workflow de CD automático; a publicação das imagens é manual pelo Compose.

