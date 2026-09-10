# Camada de autenticação (`src/auth`)

## Responsabilidade

A camada `auth` contém as operações criptográficas do projeto. Ela não consulta usuários, não valida permissões e não implementa um fluxo completo de login. Sua função atual é:

- transformar uma senha em hash usando bcrypt;
- comparar uma senha em texto puro com um hash bcrypt;
- gerar um token JWT a partir de um payload;
- validar e decodificar um token JWT.

A instanciação dessas classes com as configurações da aplicação acontece em `src/service/auth.py`.

## Arquivos

### `hash.py`

Implementa a classe `AuthHash`. O módulo cria um logger da camada `auth` durante a importação.

#### Classe `AuthHash`

A classe não mantém estado. Seus métodos são estáticos e assíncronos.

##### `encode(password: str) -> str`

Cria um hash para a senha recebida.

Fluxo interno:

1. Registra que a senha será criptografada.
2. Codifica o texto em UTF-8.
3. Cria um salt aleatório com `bcrypt.gensalt()`.
4. Gera o hash com `bcrypt.hashpw()`.
5. Decodifica o resultado binário para texto UTF-8.
6. Retorna o hash como `str`.

Como o salt é aleatório, chamadas diferentes para a mesma senha normalmente geram hashes diferentes. A validação deve ser feita com `check`, nunca comparando hashes diretamente.

Em caso de falha, o erro original é registrado e relançado dentro de uma exceção genérica.

##### `check(password: str, hashed_passowrd: str) -> bool`

Compara a senha em texto puro com um hash armazenado.

Os dois valores são convertidos em bytes e enviados para `bcrypt.checkpw()`. O método retorna `True` se a senha corresponder ao hash e `False` caso contrário. O nome `hashed_passowrd` contém um erro ortográfico, mas deve ser usado exatamente assim em chamadas nomeadas enquanto a assinatura atual permanecer.

### `jwt.py`

Implementa a classe `AuthJwt` usando a biblioteca PyJWT e cria um logger `auth` durante a importação.

#### Classe `AuthJwt`

##### `__init__(sing: str) -> None`

Recebe a chave usada para assinar e verificar tokens. A chave é armazenada em `self.sing`. O algoritmo é fixado em `HS256` e armazenado em `self.alg`.

Como HS256 é simétrico, a mesma chave deve ser usada para gerar e validar o token. No serviço, ela vem da variável de ambiente `sing`.

##### `encode(payload: str) -> str`

Entrega `payload`, algoritmo e chave para `jwt.encode()` e retorna o token produzido. Embora a anotação declare `payload: str`, o uso atual do projeto passa um dicionário, que é o formato esperado para um conjunto de claims JWT.

O método não adiciona automaticamente claims como `exp`, `iat`, `sub` ou `iss`. Portanto, validade temporal, identidade do titular e emissor só existirão se o chamador os incluir no payload.

##### `decode(token: str) -> dict`

Chama `jwt.decode()` com a chave configurada e restringe a validação ao algoritmo `HS256`. Se assinatura, formato ou claims validados pela biblioteca forem inválidos, registra e relança o erro dentro de uma exceção genérica.

### `module.py`

É um módulo de conveniência. Apenas reexporta `AuthHash` e `AuthJwt`, permitindo que a camada de serviço importe as duas classes de um único local.

## Integração com a camada de serviço

`src/service/auth.py` cria dois objetos globais:

```python
auth_jwt = AuthJwt(sing=enviroiments["sing"])
auth_hash = AuthHash()
```

Ao importar esse serviço, `src.config.settings` também é importado e todas as variáveis obrigatórias são validadas. Mesmo que o consumidor queira apenas usar bcrypt, a importação de `src.service.auth` depende do conjunto completo de configurações exigido por `Environment`.

## Fluxo de autenticação demonstrado nos testes

O teste atual executa este fluxo:

1. Monta um payload com e-mail e senha.
2. Substitui a senha em texto puro pelo hash bcrypt.
3. Coloca o payload completo dentro de um JWT.
4. Decodifica o token.
5. Compara uma senha em texto puro com o hash extraído.

Esse teste comprova geração e leitura do token e comparação do hash. Ele não consulta o banco, não autentica um usuário cadastrado e não testa expiração ou autorização.

## Dependências

- `bcrypt`: geração e comparação de hashes.
- `PyJWT`, importada como `jwt`: codificação e decodificação de tokens.
- `src.logs.log`: registro das operações.
- `src.config.settings`: fornecimento da chave, quando acessada pela camada de serviço.

## Pontos de atenção do comportamento atual

- A senha com hash está sendo incluída no payload do JWT no teste. Mesmo sendo um hash, credenciais não devem ser usadas como conteúdo de sessão sem necessidade.
- Tokens não recebem expiração automaticamente.
- Métodos são assíncronos, mas bcrypt e PyJWT são chamados de forma síncrona internamente.
- A coluna `Users.password` está limitada a 50 caracteres, enquanto hashes bcrypt normalmente são maiores; consulte a documentação da camada de banco.
- A classe fornece primitivas criptográficas, mas regras de login, bloqueio, renovação e autorização ainda precisam existir em uma camada superior.
