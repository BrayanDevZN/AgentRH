# Camada de integrações (`src/utils`)

## Responsabilidade

`src/utils` contém adaptadores de baixo nível para serviços externos:

- OpenAI Responses API;
- envio SMTP via yagmail.

A orquestração e o registro no Celery ficam em `src/service/utils`.

## OpenAI

`analyze_agent(key, prompt, input) -> str`:

1. cria `AsyncOpenAI(api_key=key)`;
2. chama `client.responses.create()`;
3. passa o prompt em `instructions`;
4. passa vaga, candidato e currículo em `input`;
5. usa o modelo configurado diretamente no código;
6. devolve `response.output_text`.

O adaptador não interpreta nem valida a saída. O contrato é aplicado pelo prompt e separado posteriormente por `AgentRH`.

## Contrato da análise

```text
DECISION | SUBJECT_TEXT | COMPLETE_BODY_HTML_DOCUMENT
```

`DECISION` deve ser exatamente `aproved` ou `recuse`. O corpo começa com `<!DOCTYPE html>` e termina com `</html>`. Os dois delimitadores estruturais devem ser os únicos caracteres `|` da resposta.

## Modo de teste

Quando `environment=test`, `AgentRH` não chama `analyze_agent()`. Ele lê `resume_analysis_test.html` e monta:

```text
aproved | Candidatura aprovada para <vaga> | <!DOCTYPE html>...</html>
```

O mesmo parser e as mesmas atualizações são exercitados sem consumir a API externa.

## SMTP

`SenderEmail` cria `yagmail.SMTP(user, password)` e oferece:

```python
await sender.send(
    email="destino@example.com",
    subject="Assunto",
    body="<html>...</html>"
)
```

Internamente, o yagmail é síncrono. A interface assíncrona não impede bloqueio quando usada diretamente; no fluxo principal, o envio ocorre no worker Celery.

Para Gmail, `password_user` deve ser uma senha de aplicativo compatível com a política da conta, não uma credencial publicada no repositório.

## Templates

Os e-mails transacionais ficam em `src/config/sender` e são carregados no dicionário `senders`. O corpo produzido pela IA é entregue diretamente à tarefa de envio após a separação.

## Tratamento de erros

As integrações registram falhas e relançam exceções. Não existem classes específicas para erros da OpenAI; o SMTP usa `SenderEmailError`.

## Pontos de atenção

- O cliente OpenAI é recriado a cada análise.
- Não há retry ou timeout específicos nas integrações.
- O nome do modelo está fixado no adaptador.
- O destinatário aparece no log do envio.
- O conteúdo retornado pela IA depende da validação por prompt; não há parser estrutural além do `split`.
- O fluxo atual decodifica os bytes do currículo como UTF-8 antes da análise, o que não extrai texto de um PDF binário real.
