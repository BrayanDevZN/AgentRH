# Camada de aplicação (`src/aplication`)

## Responsabilidade

A camada `aplication` é a interface HTTP do AgentRH. Ela cria a aplicação FastAPI, registra CORS e middleware, valida entradas com Pydantic, resolve o usuário autenticado e conecta cada endpoint aos serviços de domínio.

> O diretório usa atualmente o nome `aplication` e o middleware se chama `Midlleware`. A documentação preserva esses nomes porque eles fazem parte dos imports do projeto.

## Inicialização

`src/aplication/main.py` define `Aplication`, registra os routers e exporta `app`, usado pelo Uvicorn:

```bash
python -m uvicorn src.aplication.main:app --host 0.0.0.0 --port 8000
```

O Compose publica essa porta como `650` no host. Com a aplicação ativa, a documentação interativa fica em:

- Swagger UI: `http://localhost:650/docs`
- OpenAPI: `http://localhost:650/openapi.json`

O CORS permite credenciais e usa exclusivamente o valor de `origin` como origem autorizada.

## Middleware

`src/aplication/midlleware.py` aplica dois limites antes de encaminhar a requisição:

1. `global_rate_limit`: contador compartilhado por todas as chamadas;
2. `rate_limit`: contador por IP nas rotas públicas e por token nas demais.

As rotas públicas cadastradas são criação de usuário, envio de código, login e 2FA. Nas demais, a ausência do cookie `X-user_token` interrompe a requisição.

Os contadores são mantidos no Redis e expiram em aproximadamente 60 segundos. O limite global responde com `429`; o limite individual atual responde com `422`.

## Dependência de autenticação

`Depends(depends_user)` cria `UtilsDepends` e executa quatro etapas:

1. lê o cookie `X-user_token`;
2. decodifica o JWT;
3. valida a data armazenada em `expire`;
4. busca o usuário por `public_id` e verifica permissões da rota.

As operações administrativas e a criação, alteração e exclusão de vagas exigem papel `admin`. As demais rotas protegidas exigem um usuário autenticado.

## Routers e endpoints

Todos os endpoints atuais retornam JSON. A maioria das operações bem-sucedidas usa status `201`, inclusive consultas.

| Método | Rota | Entrada | Proteção | Função |
| --- | --- | --- | --- | --- |
| `POST` | `/sender/` | JSON | Pública | Gera código para cadastro |
| `PATCH` | `/sender/` | JSON | Pública | Gera código para troca de senha |
| `POST` | `/sender/2fa` | Cookie | Temporária | Envia código de autenticação |
| `POST` | `/users/` | JSON | Pública | Cria usuário e cookies de sessão |
| `GET` | `/users/` | Cookie | Usuário | Retorna o usuário autenticado |
| `PATCH` | `/users/` | JSON + cookie | Usuário | Altera idade, gênero ou permissão |
| `DELETE` | `/users/` | JSON + cookie | Usuário | Exclui a própria conta |
| `GET` | `/auth/` | JSON + cookies | Pública/2FA | Inicia ou conclui login |
| `PATCH` | `/auth/` | JSON | Variável | Atualiza senha |
| `PUT` | `/auth/` | Cookies | Usuário | Renova o token de acesso |
| `DELETE` | `/auth/` | Cookie | Usuário | Faz logout |
| `GET` | `/admin/` | JSON | Admin | Busca usuário ou solicita visão geral |
| `PATCH` | `/admin/` | JSON | Admin | Altera o papel de um usuário |
| `DELETE` | `/admin/` | JSON | Admin principal | Exclui um usuário |
| `POST` | `/vancancies/` | JSON | Admin | Cria vaga |
| `GET` | `/vancancies/` | JSON | Usuário | Busca uma vaga ou todas |
| `PATCH` | `/vancancies/` | JSON | Admin | Altera nome ou descrição |
| `DELETE` | `/vancancies/` | JSON | Admin | Exclui vaga |
| `POST` | `/resumes/` | Multipart | Usuário | Envia currículo e agenda análise |
| `GET` | `/resumes/` | JSON | Usuário/Admin | Busca candidatura ou todas |
| `DELETE` | `/resumes/` | Query + cookie | Usuário | Exclui candidatura própria |

## Upload de currículo

O endpoint de criação recebe `multipart/form-data`:

| Campo | Tipo | Padrão |
| --- | --- | --- |
| `vancancie_id` | inteiro | obrigatório |
| `pdf` | arquivo | obrigatório |
| `status` | `aproved`, `recuse` ou `pending` | `pending` |
| `reason` | texto | `null` |

Exemplo:

```bash
curl -X POST http://localhost:650/resumes/ \
  -b cookies.txt \
  -F 'vancancie_id=1' \
  -F 'status=pending' \
  -F 'reason=null' \
  -F 'pdf=@curriculo.pdf;type=application/pdf'
```

O arquivo é lido com `await pdf.read()` e persistido como `bytes`. Consultas convertem o conteúdo para Base64 para que ele possa fazer parte da resposta JSON.

## Schemas

Os modelos em `src/aplication/schema` validam:

- cadastro e senha forte;
- login, 2FA e atualização de senha;
- seleção e alteração administrativa;
- criação e seleção de vagas;
- seleção de currículos.

O upload usa `Form` e `File` diretamente na assinatura da rota. `GetResume` continua sendo um corpo JSON, inclusive no método `GET`.

## Cookies

| Cookie | Finalidade |
| --- | --- |
| `X-auth2_token` | Estado temporário da autenticação em duas etapas |
| `X-user_token` | Token de acesso usado pela dependência e middleware |
| `X-user_refresh_token` | Token usado pela rota de renovação |

Os cookies são definidos como `httponly` e `samesite="strict"`.

## Modo de teste

Quando `environment=test`, códigos de cadastro e 2FA são incluídos na resposta JSON. Isso permite que os testes funcionais concluam o fluxo sem ler uma caixa de e-mail. Em outros ambientes, os códigos são enviados pelas tarefas de e-mail.

## Pontos de atenção

- O projeto usa corpo JSON em métodos `GET`; alguns proxies e clientes não tratam esse padrão tão bem quanto query parameters.
- Diversos handlers capturam `HTTPException` dentro de `except Exception`, podendo transformar status específicos em `501`.
- O middleware autentica rotas pelo caminho literal e método; novas rotas precisam ser classificadas conscientemente.
- A resposta de vagas inclui candidaturas para admin; usuários comuns recebem os campos sensíveis removidos.
- Não há paginação nas listagens `all`/`get_all`.

