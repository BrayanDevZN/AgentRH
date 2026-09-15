# Camada de autenticação (`src/auth`)

## Responsabilidade

A camada `auth` fornece duas primitivas independentes:

- hash e comparação de senha com bcrypt;
- criação e leitura de JWT com HS256.

Ela não acessa banco, cookies ou permissões. O fluxo HTTP completo é implementado em `src/aplication/handles/auth.py`, enquanto `src/service/auth.py` injeta a chave de assinatura e expõe instâncias prontas.

## `AuthHash`

Arquivo: `src/auth/hash.py`.

### `encode(password: str) -> str`

Converte a senha para UTF-8, cria um salt aleatório com `bcrypt.gensalt()`, gera o hash e retorna uma string. Por causa do salt, duas chamadas para a mesma senha normalmente produzem valores diferentes.

```python
hashed = await AuthHash.encode(password="Senha123")
```

### `check(password: str, hashed_passowrd: str) -> bool`

Compara texto puro e hash por `bcrypt.checkpw()`. A validação correta é sempre feita por esse método, nunca comparando duas strings de hash.

```python
valid = await AuthHash.check(
    password="Senha123",
    hashed_passowrd=hashed
)
```

O nome `hashed_passowrd` está grafado assim na assinatura atual e precisa ser preservado em argumentos nomeados.

## `AuthJwt`

Arquivo: `src/auth/jwt.py`.

### Construção

```python
auth = AuthJwt(sing="chave-secreta")
```

`sing` é a chave simétrica usada para assinar e verificar tokens. O algoritmo é fixo em `HS256`.

### `encode(payload) -> str`

Encaminha o payload para `jwt.encode()`. O projeto usa dicionários, apesar de a anotação atual indicar `str`.

### `decode(token: str) -> dict`

Valida assinatura e algoritmo e devolve o payload. Datas do projeto são armazenadas como texto e validadas manualmente na aplicação; o código atual não usa automaticamente uma claim JWT `exp` numérica.

## Instâncias de serviço

`src/service/auth.py` cria:

```python
auth_jwt = AuthJwt(sing=enviroiments["sing"])
auth_hash = AuthHash()
```

Importar esse módulo exige que as configurações obrigatórias estejam disponíveis.

## Fluxo de login

O login usa até três cookies:

```text
Credenciais
   ↓
GET /auth/
   ├── sem 2FA → X-user_token + X-user_refresh_token
   └── com 2FA → X-auth2_token
                       ↓
                 POST /sender/2fa
                       ↓
                 GET /auth/ + code
                       ↓
             tokens de acesso e renovação
```

Usuários comuns fornecem senha. O admin inicial pode ter `password=None`, possui `permission=True` e entra pelo código de autenticação.

## Política de senha

`ValidPassword` exige no mínimo oito caracteres e pelo menos:

- uma letra maiúscula;
- uma letra minúscula;
- uma letra;
- um dígito.

A regra é aplicada na criação e na alteração de senha.

## Proteção de rotas

`UtilsDepends` lê `X-user_token`, valida `expire`, busca o usuário por `public_id` e verifica o papel exigido. Alterações administrativas e mutações de vagas requerem `role="admin"`.

## Pontos de atenção

- HS256 exige proteção rigorosa da variável `sing`.
- Tokens não usam atualmente a claim padrão `exp`; a aplicação interpreta um campo textual próprio.
- Os métodos são `async`, mas bcrypt e PyJWT executam trabalho síncrono internamente.
- Alguns handlers transformam exceções HTTP em `501`; consumidores devem observar o corpo `detail` durante a depuração.
- Cookies não definem `secure=True` no código atual; produção HTTPS deve revisar essa configuração.
