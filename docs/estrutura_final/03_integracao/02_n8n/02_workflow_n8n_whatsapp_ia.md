# Workflow Detalhado n8n: Conexão WhatsApp-IA

## Objetivo
Detalhar o fluxo de trabalho no n8n para estabelecer a comunicação básica entre o WhatsApp (via Twilio) e a API de IA (OpenAI/Claude), permitindo receber mensagens, processá-las com IA e enviar respostas.

## Pré-requisitos
- Conta Twilio configurada com WhatsApp Business API (Sandbox ou Produção)
- Conta n8n Cloud ou auto-hospedada
- Chave de API da OpenAI ou Anthropic
- URL pública para o webhook do n8n

## Componentes do Workflow (Nós n8n)

1.  **Webhook (Start Node)**
    - **Tipo**: Webhook
    - **Método HTTP**: POST
    - **Autenticação**: Nenhum (a validação será feita no próximo nó)
    - **Caminho (Path)**: `beststag/whatsapp/webhook` (ou similar)
    - **Ação**: Recebe a requisição POST do Twilio com os dados da mensagem.
    - **Observação**: A URL completa será `https://[seu-dominio-n8n]/webhook/[caminho]`.

2.  **Twilio Request Validator**
    - **Tipo**: Nó personalizado ou Função (JavaScript) para validação HMAC.
    - **Entrada**: Cabeçalho `X-Twilio-Signature` e corpo da requisição.
    - **Lógica**: Verifica se a assinatura da requisição é válida usando o Auth Token do Twilio.
    - **Saída**: Continua o fluxo se válido; para ou envia erro se inválido.
    - **Alternativa**: Usar o nó "Twilio Trigger" se disponível e configurado corretamente.

3.  **Set (Extrair Dados)**
    - **Tipo**: Set
    - **Ação**: Extrai informações relevantes do payload do Twilio:
        - `from_number`: Número do remetente (e.g., `{{ $json.body.From }}`)
        - `to_number`: Número do destinatário (e.g., `{{ $json.body.To }}`)
        - `message_body`: Conteúdo da mensagem (e.g., `{{ $json.body.Body }}`)
        - `message_sid`: ID da mensagem (e.g., `{{ $json.body.MessageSid }}`)
    - **Modo**: Manter apenas os dados definidos.

4.  **IF (Verificar Mensagem Vazia)**
    - **Tipo**: IF
    - **Condição**: `{{ $json.message_body }}` não está vazio.
    - **Saída Verdadeira**: Continua para processamento IA.
    - **Saída Falsa**: Termina o fluxo (ou loga/trata como erro).

5.  **OpenAI (Processamento IA)**
    - **Tipo**: OpenAI Chat Model (ou similar para Claude)
    - **Credenciais**: Chave de API da OpenAI.
    - **Modelo**: `gpt-3.5-turbo` (ou `gpt-4` / modelo Claude).
    - **Prompt (System)**: Define o papel do assistente BestStag (e.g., "Você é o BestStag, um assistente virtual prestativo...").
    - **Prompt (User)**: `{{ $json.message_body }}`.
    - **Parâmetros**: Ajustar `temperature`, `max_tokens` conforme necessário.
    - **Saída**: Armazena a resposta gerada pela IA (e.g., `{{ $json.choices[0].message.content }}`).

6.  **Set (Preparar Resposta)**
    - **Tipo**: Set
    - **Ação**: Prepara os dados para a API do Twilio:
        - `twilio_account_sid`: Seu Account SID do Twilio.
        - `twilio_auth_token`: Seu Auth Token do Twilio.
        - `recipient_number`: `{{ $node["Set (Extrair Dados)"].json.from_number }}` (número do usuário).
        - `sender_number`: `{{ $node["Set (Extrair Dados)"].json.to_number }}` (seu número Twilio).
        - `response_body`: `{{ $node["OpenAI"].json.choices[0].message.content }}` (resposta da IA).

7.  **HTTP Request (Enviar Resposta Twilio)**
    - **Tipo**: HTTP Request
    - **Método**: POST
    - **URL**: `https://api.twilio.com/2010-04-01/Accounts/{{ $json.twilio_account_sid }}/Messages.json`
    - **Autenticação**: Basic Auth
        - **Usuário**: `{{ $json.twilio_account_sid }}`
        - **Senha**: `{{ $json.twilio_auth_token }}`
    - **Corpo (Body)**: `application/x-www-form-urlencoded`
        - `To`: `{{ $json.recipient_number }}`
        - `From`: `{{ $json.sender_number }}`
        - `Body`: `{{ $json.response_body }}`
    - **Opções**: Desativar "SSL/TLS Certificate Verification" se necessário (não recomendado para produção).

8.  **Error Trigger (Opcional)**
    - **Tipo**: Error Trigger
    - **Ação**: Captura erros em qualquer ponto do fluxo para tratamento (log, notificação, etc.).

## Fluxo Lógico

1.  Webhook recebe a mensagem do Twilio.
2.  Validador verifica a autenticidade da requisição.
3.  Nó Set extrai os dados essenciais.
4.  Nó IF verifica se a mensagem não está vazia.
5.  Nó OpenAI processa a mensagem e gera uma resposta.
6.  Nó Set prepara os dados para a API do Twilio.
7.  Nó HTTP Request envia a resposta de volta ao usuário via Twilio.

## Considerações

- **Segurança**: A validação HMAC é crucial.
- **Custos**: Monitorar o uso de tokens da API de IA.
- **Escalabilidade**: Otimizar prompts e fluxos para performance.
- **Tratamento de Erros**: Implementar tratamento robusto para falhas.
- **Contexto**: Este fluxo inicial não inclui memória contextual, que será adicionada na Fase 2.

Este workflow detalhado serve como base para a implementação inicial da conexão WhatsApp-IA no n8n.
