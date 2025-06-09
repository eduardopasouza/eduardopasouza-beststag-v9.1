# BestStag v8.0 - Guia Rápido

Este diretório contém uma versão simplificada (MVP) do BestStag, mantida apenas
para testes rápidos com usuários reais. **Não substitui a versão 9.1**.

## Pré-requisitos

- Conta no **Twilio** para envio de mensagens WhatsApp
- Projeto **Supabase** configurado
- Chave de API da **OpenAI**
- Instância do **n8n** executando os workflows

## Configuração

1. Copie o arquivo `.env.example` para `.env` e preencha com suas chaves:

   ```bash
   cp docs/.env.example docs/.env
   ```
   As principais variáveis são:
   - `SUPABASE_URL`, `SUPABASE_ANON_KEY` e `SUPABASE_SERVICE_ROLE_KEY`
   - `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` e `TWILIO_WHATSAPP_NUMBER`
   - `OPENAI_API_KEY`

### Variáveis de ambiente necessárias

Defina no `.env` todas as chaves usadas no projeto para que o frontend e os
testes funcionem corretamente:

```text
SUPABASE_URL=<url do seu projeto>
SUPABASE_ANON_KEY=<chave anon>
SUPABASE_SERVICE_ROLE_KEY=<chave service role>
TWILIO_ACCOUNT_SID=<sid twilio>
TWILIO_AUTH_TOKEN=<token twilio>
TWILIO_WHATSAPP_NUMBER=whatsapp:+5511999999999
OPENAI_API_KEY=<sua chave openai>
```

2. Importe os workflows `n8n_workflows/whatsapp_fluxo_base.json` e
   `n8n_workflows/webchat_fluxo_base.json` em sua instância do n8n.

3. Instale as dependências Python (inclui `httpx` para testes):

   ```bash
   pip install -r requirements.txt
   ```

## Como rodar o lint

Executar `make lint` na raiz do projeto (usa `flake8`). Também é possível rodar
manualmente:

```bash
flake8 beststag_v8.0/ --max-line-length=100 --ignore=E203,W503
```

Para ajustar a formatação automaticamente, utilize o comando:

```bash
black beststag_v8.0 --line-length 100
```

## Como executar os testes

1. Garanta que a variável `OPENAI_API_KEY` esteja definida no `.env`.
2. Rode os testes utilizando `pytest`:

   ```bash
   pytest beststag_v8.0/tests -v
   ```

## Teste de Cadastro

Abra `frontend/cadastro.html` em um navegador. Preencha nome, telefone e email e
clique em "Cadastrar" para gravar o usuário no Supabase.

## Teste de Chat

Abra `frontend/chatbot.html`, insira o telefone e clique em "Carregar" para
listar as mensagens deste usuário. O campo de pergunta permite enviar
mensagens diretamente pelo navegador. O frontend faz uma requisição para o
webhook `/webhook/webchat` no n8n e exibe a resposta abaixo da pergunta.

