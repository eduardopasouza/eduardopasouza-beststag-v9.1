# Guia de Integração com WhatsApp Business API

Este documento detalha a integração do BestStag com a WhatsApp Business API, incluindo configuração, templates de mensagem, webhooks e considerações de implementação.

## 1. Visão Geral da Integração

A integração com WhatsApp Business API é um componente crítico do BestStag, pois o WhatsApp é o canal principal de comunicação com os usuários. Esta integração permite:

- Receber mensagens dos usuários
- Enviar respostas e notificações
- Utilizar templates de mensagem pré-aprovados
- Processar mídia e anexos
- Manter conversas contextuais

## 2. Configuração da WhatsApp Business API

### 2.1 Provedores Recomendados

O BestStag utiliza a WhatsApp Business API através de provedores certificados pela Meta:

- **Twilio**: Solução robusta com ampla documentação
- **MessageBird**: Alternativa com bom custo-benefício
- **Gupshup**: Opção com recursos adicionais para chatbots

A implementação atual utiliza o Twilio como provedor principal.

### 2.2 Requisitos de Configuração

Para configurar a integração, são necessários:

1. **Conta de Negócios no Facebook**: Para solicitar acesso à API
2. **Processo de Verificação**: Aprovação pela Meta
3. **Número de Telefone Dedicado**: Para envio e recebimento de mensagens
4. **Conta no Provedor Escolhido**: Para acesso à API

### 2.3 Processo de Aprovação

O processo de aprovação pela Meta inclui:

1. Criação de conta Business no Facebook
2. Verificação de identidade do negócio
3. Solicitação de acesso à WhatsApp Business API
4. Aprovação dos templates de mensagem
5. Configuração do número de telefone

## 3. Templates de Mensagem

### 3.1 Visão Geral

Templates de mensagem são formatos pré-aprovados pela Meta que permitem iniciar conversas ou enviar notificações proativas aos usuários.

### 3.2 Categorias de Templates

O BestStag utiliza templates nas seguintes categorias:

- **Boas-vindas**: Primeira mensagem após opt-in
- **Notificações**: Alertas sobre eventos, tarefas, emails
- **Atualizações**: Informações sobre mudanças em compromissos
- **Lembretes**: Avisos sobre eventos próximos
- **Confirmações**: Confirmação de ações realizadas

### 3.3 Estrutura de Templates

Cada template inclui:

- **Nome**: Identificador único
- **Categoria**: Classificação do propósito
- **Idioma**: Idioma do template
- **Conteúdo**: Texto com variáveis entre chaves
- **Exemplo**: Demonstração com valores reais
- **Botões** (opcional): Ações rápidas para o usuário

### 3.4 Exemplos de Templates

#### Template de Boas-vindas
```
Nome: welcome_message
Categoria: UTILITY
Idioma: pt_BR
Conteúdo: Olá {{1}}! Bem-vindo ao BestStag, seu assistente virtual. Estou aqui para ajudar com sua agenda, tarefas, emails e muito mais. Como posso ajudar hoje?
Exemplo: Olá João! Bem-vindo ao BestStag, seu assistente virtual. Estou aqui para ajudar com sua agenda, tarefas, emails e muito mais. Como posso ajudar hoje?
```

#### Template de Lembrete de Compromisso
```
Nome: appointment_reminder
Categoria: APPOINTMENT_UPDATE
Idioma: pt_BR
Conteúdo: Lembrete: Você tem {{1}} agendado para {{2}} às {{3}}. Local: {{4}}
Exemplo: Lembrete: Você tem Reunião com Cliente agendado para amanhã às 15:00. Local: Escritório Central
Botões: [Confirmar, Reagendar, Cancelar]
```

## 4. Webhooks e Processamento de Mensagens

### 4.1 Configuração de Webhooks

O BestStag utiliza webhooks para receber mensagens e eventos do WhatsApp:

```javascript
// Exemplo de configuração no Twilio
const express = require('express');
const app = express();
app.use(express.json());

app.post('/webhook/whatsapp', (req, res) => {
  // Processar mensagem recebida
  const message = req.body;
  
  // Encaminhar para processamento
  processMessage(message)
    .then(() => {
      res.status(200).send('OK');
    })
    .catch(error => {
      console.error('Erro ao processar mensagem:', error);
      res.status(500).send('Erro ao processar mensagem');
    });
});

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});
```

### 4.2 Estrutura de Mensagens Recebidas

As mensagens recebidas seguem esta estrutura (exemplo do Twilio):

```json
{
  "SmsMessageSid": "SM123456789",
  "NumMedia": "0",
  "ProfileName": "João Silva",
  "SmsSid": "SM123456789",
  "WaId": "5511999999999",
  "SmsStatus": "received",
  "Body": "Agende uma reunião com Maria amanhã às 15h",
  "To": "whatsapp:+14155238886",
  "NumSegments": "1",
  "MessageSid": "SM123456789",
  "AccountSid": "AC123456789",
  "From": "whatsapp:+5511999999999",
  "ApiVersion": "2010-04-01"
}
```

### 4.3 Processamento de Mensagens

O fluxo de processamento de mensagens inclui:

1. **Recebimento**: Webhook recebe a mensagem
2. **Extração**: Dados relevantes são extraídos
3. **Normalização**: Formato é padronizado
4. **Classificação**: Intenção é identificada
5. **Processamento**: Ação correspondente é executada
6. **Resposta**: Mensagem de retorno é enviada

```javascript
// Exemplo de processamento no Make/n8n
async function processMessage(message) {
  // Extrair informações
  const text = message.Body;
  const userId = message.From.replace('whatsapp:', '');
  
  // Chamar API de processamento
  const response = await fetch('https://api.beststag.com/process', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      text,
      userId,
      channel: 'whatsapp'
    })
  });
  
  // Obter resultado
  const result = await response.json();
  
  // Enviar resposta
  await sendWhatsAppMessage(userId, result.response);
  
  return result;
}
```

## 5. Envio de Mensagens

### 5.1 Mensagens de Resposta

Para mensagens de resposta dentro da janela de 24 horas:

```javascript
// Exemplo com Twilio
async function sendWhatsAppMessage(to, text) {
  const client = require('twilio')(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);
  
  try {
    const message = await client.messages.create({
      body: text,
      from: `whatsapp:${process.env.TWILIO_PHONE_NUMBER}`,
      to: `whatsapp:${to}`
    });
    
    return message.sid;
  } catch (error) {
    console.error('Erro ao enviar mensagem:', error);
    throw error;
  }
}
```

### 5.2 Mensagens com Templates

Para mensagens fora da janela de 24 horas ou notificações proativas:

```javascript
// Exemplo com Twilio
async function sendTemplateMessage(to, templateName, variables) {
  const client = require('twilio')(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);
  
  try {
    const message = await client.messages.create({
      from: `whatsapp:${process.env.TWILIO_PHONE_NUMBER}`,
      to: `whatsapp:${to}`,
      contentSid: templateName,
      contentVariables: JSON.stringify(variables)
    });
    
    return message.sid;
  } catch (error) {
    console.error('Erro ao enviar template:', error);
    throw error;
  }
}
```

### 5.3 Envio de Mídia

Para envio de imagens, documentos ou outros tipos de mídia:

```javascript
// Exemplo com Twilio
async function sendMediaMessage(to, mediaUrl, caption) {
  const client = require('twilio')(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);
  
  try {
    const message = await client.messages.create({
      from: `whatsapp:${process.env.TWILIO_PHONE_NUMBER}`,
      to: `whatsapp:${to}`,
      body: caption,
      mediaUrl: [mediaUrl]
    });
    
    return message.sid;
  } catch (error) {
    console.error('Erro ao enviar mídia:', error);
    throw error;
  }
}
```

## 6. Integração com Make/n8n

### 6.1 Fluxo de Integração

A integração com Make/n8n segue este fluxo:

1. **Webhook** recebe mensagem do WhatsApp
2. **HTTP Request** envia mensagem para API de processamento
3. **Router** direciona fluxo com base na intenção
4. **Módulos específicos** executam ações correspondentes
5. **HTTP Request** envia resposta de volta para WhatsApp

### 6.2 Exemplo de Cenário no Make

```
Trigger: Webhook (POST /webhook/whatsapp)
↓
HTTP Request (POST https://api.beststag.com/process)
↓
Router (baseado em result.intent)
├─ agenda.criar → Google Calendar (Create Event)
├─ agenda.consultar → Google Calendar (Search Events)
├─ tarefa.criar → Airtable (Create Record)
├─ tarefa.listar → Airtable (Search Records)
└─ outros → Text Parser (Default Response)
↓
HTTP Request (POST https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json)
```

### 6.3 Tratamento de Erros

O sistema implementa tratamento de erros em múltiplos níveis:

1. **Retry automático**: Para falhas temporárias
2. **Fallback de resposta**: Mensagens genéricas em caso de erro
3. **Logging**: Registro detalhado de erros para análise
4. **Alertas**: Notificações para erros críticos

```javascript
// Exemplo de tratamento de erros no Make
try {
  // Processar mensagem
} catch (error) {
  if (error.status >= 500) {
    // Erro de servidor, tentar novamente
    $trigger.retry = true;
    $trigger.retryIn = 60; // segundos
  } else {
    // Erro de cliente ou outro, enviar resposta de fallback
    await sendWhatsAppMessage(
      userId,
      "Desculpe, estou com dificuldades para processar sua solicitação no momento. Por favor, tente novamente mais tarde."
    );
    
    // Registrar erro
    await logError(error, userId, message);
  }
}
```

## 7. Considerações de Segurança

### 7.1 Autenticação de Webhooks

Para garantir que apenas o provedor possa enviar mensagens ao webhook:

```javascript
// Exemplo de validação de assinatura do Twilio
const validateTwilioRequest = (req) => {
  const signature = req.headers['x-twilio-signature'];
  const url = 'https://seu-dominio.com/webhook/whatsapp';
  const params = req.body;
  
  const twilio = require('twilio');
  const requestIsValid = twilio.validateRequest(
    process.env.TWILIO_AUTH_TOKEN,
    signature,
    url,
    params
  );
  
  return requestIsValid;
};

app.post('/webhook/whatsapp', (req, res) => {
  if (!validateTwilioRequest(req)) {
    return res.status(403).send('Forbidden');
  }
  
  // Processar mensagem
});
```

### 7.2 Proteção de Dados

Medidas para proteger dados dos usuários:

1. **Criptografia em trânsito**: HTTPS para todas as comunicações
2. **Armazenamento seguro**: Credenciais em variáveis de ambiente
3. **Minimização de dados**: Armazenar apenas o necessário
4. **Expiração de dados**: Política de retenção definida

### 7.3 Conformidade com Políticas da Meta

Para manter conformidade com as políticas da Meta:

1. **Opt-in explícito**: Consentimento do usuário antes do primeiro contato
2. **Respeito à janela de 24h**: Uso de templates fora da janela
3. **Conteúdo apropriado**: Seguir diretrizes de conteúdo
4. **Qualidade de serviço**: Manter métricas de qualidade aceitáveis

## 8. Métricas e Monitoramento

### 8.1 Métricas Principais

O sistema monitora as seguintes métricas:

- **Taxa de entrega**: Porcentagem de mensagens entregues
- **Tempo de resposta**: Tempo médio para responder mensagens
- **Taxa de opt-out**: Usuários que bloqueiam ou saem
- **Engajamento**: Frequência e duração das interações
- **Qualidade**: Avaliações e feedback dos usuários

### 8.2 Implementação de Monitoramento

```javascript
// Exemplo de registro de métricas
async function trackMetrics(messageId, type, status, responseTime) {
  await fetch('https://api.beststag.com/metrics', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      messageId,
      type,
      status,
      responseTime,
      timestamp: new Date().toISOString()
    })
  });
}

// Uso
app.post('/webhook/whatsapp', async (req, res) => {
  const startTime = Date.now();
  
  try {
    // Processar mensagem
    const result = await processMessage(req.body);
    
    // Registrar métricas
    const responseTime = Date.now() - startTime;
    await trackMetrics(
      req.body.MessageSid,
      'inbound',
      'processed',
      responseTime
    );
    
    res.status(200).send('OK');
  } catch (error) {
    // Registrar erro
    await trackMetrics(
      req.body.MessageSid,
      'inbound',
      'error',
      Date.now() - startTime
    );
    
    res.status(500).send('Error');
  }
});
```

## 9. Próximos Passos

### 9.1 Melhorias Planejadas

1. **Implementação de Rich Messages**: Utilizar recursos avançados como botões e listas
2. **Otimização de Templates**: Expandir biblioteca de templates para mais casos de uso
3. **Integração com CRM**: Sincronizar conversas com sistema de CRM
4. **Análise de Sentimento**: Detectar tom e emoção nas mensagens dos usuários
5. **Suporte a Múltiplos Idiomas**: Expandir para outros idiomas além do português

### 9.2 Roadmap de Implementação

| Fase | Funcionalidade | Prazo Estimado |
|------|---------------|----------------|
| 1    | Integração básica com WhatsApp API | Concluído |
| 2    | Templates essenciais | Concluído |
| 3    | Processamento de mídia | Em andamento |
| 4    | Rich Messages (botões, listas) | Planejado |
| 5    | Análise de sentimento | Futuro |
| 6    | Suporte multilíngue | Futuro |

---

*Esta documentação foi preparada pelo Agente APIs de IA como parte do backup completo do projeto BestStag.*
