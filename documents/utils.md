# Camada de utilitários (`src/utils`)

## Responsabilidade

A camada `utils` contém adaptadores para serviços externos. Atualmente existem dois: análise de currículo com OpenAI e envio de e-mail com yagmail.

Esses módulos implementam a chamada externa de baixo nível. A orquestração, as configurações e o registro como tarefa Celery ficam em `src/service/utils`.

## Arquivo `agent.py`

### Função `analyze_agent(key: str, prompt: str, input: str) -> str`

Executa uma solicitação assíncrona à API OpenAI:

1. Cria `AsyncOpenAI(api_key=key)`.
2. Chama `client.responses.create()`.
3. Envia o prompt no campo `instructions`.
4. Envia os dados da vaga e do currículo no campo `input`.
5. Usa o modelo `gpt-5.6-luna`.
6. Retorna `response.output_text`.

A função não interpreta a resposta. Ela apenas devolve o texto produzido. Erros de autenticação, rede, limite, validação ou resposta são registrados e relançados como exceção genérica.

O cliente é criado a cada chamada, em vez de ser mantido como objeto global.

## Arquivo `sender.py`

### Exceção `SenderEmailError`

Encapsula falhas ocorridas durante o envio de e-mail.

### Classe `SenderEmail`

#### `__init__(user: str, password: str) -> None`

Cria uma sessão `yagmail.SMTP` com usuário e senha e guarda a instância em `self.instance`. A criação pode iniciar a preparação da conexão ou autenticação conforme o comportamento da biblioteca.

#### `send(email: str, subject: str, body: str) -> None`

Envia uma mensagem chamando:

```python
self.instance.send(to=email, subject=subject, contents=body)
```

Em caso de sucesso, registra a conclusão. Em caso de falha, registra o erro e lança `SenderEmailError`.

O método é assíncrono na interface, mas `yagmail` é usado de forma síncrona internamente, portanto a chamada pode bloquear a thread até o envio terminar.

## Integração com os serviços

### Serviço de e-mail

`src/service/utils/sender.py` registra a função `sender` como tarefa Celery. Quando o worker a executa:

1. Lê `email_user` e `password_user` das configurações já carregadas.
2. Cria `SenderEmail`.
3. Executa `send()` por meio de `asyncio.run()`.

### Serviço do agente de RH

`src/service/utils/agent.py` define `AgentRH` e a tarefa `run_agent`. O fluxo completo está documentado em [service.md](service.md), pois essa classe coordena banco, e-mail, prompt, OpenAI e Celery.

## Contrato da resposta da IA

O prompt exige três componentes separados por `|`:

```text
decisão | assunto | corpo HTML
```

A decisão deve ser exatamente `aproved` ou `recuse`. O assunto deve ser texto simples e o corpo deve ser um documento HTML completo. A camada `utils.agent` não aplica esse contrato; quem o interpreta é `AgentRH._get_responses()`.

## Dependências

- SDK `openai` para a Responses API.
- `yagmail` para envio SMTP.
- Camada `logs` para observabilidade.

## Pontos de atenção do comportamento atual

- O nome do modelo está fixo no código.
- Não há timeout, retry ou tratamento específico por tipo de falha nas chamadas externas.
- O e-mail é entregue ao yagmail como `contents`; a renderização do HTML depende do reconhecimento feito pela biblioteca.
- O endereço do destinatário aparece na mensagem de log de envio.
- As funções não validam localmente formato de e-mail, tamanho do currículo ou estrutura da resposta da IA.
- Segredos chegam como argumentos de construção, mas não são registrados explicitamente pelo código atual.
