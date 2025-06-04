# TEMPLATE DE CREDENCIAIS - BESTSTAG

**IMPORTANTE**: Este arquivo contém templates das credenciais necessárias. 
Substitua os valores entre [colchetes] pelas credenciais reais.

---

## N8N CLOUD CREDENTIALS

### Twilio BestStag
```
Name: Twilio BestStag
Type: Twilio
Account SID: [ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]
Auth Token: [xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]
```

### OpenAI BestStag
```
Name: OpenAI BestStag
Type: OpenAI
API Key: [sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]
Organization ID: [org-xxxxxxxxxxxxxxxxxxxxxxxx] (opcional)
```

### Airtable BestStag
```
Name: Airtable BestStag
Type: Airtable
API Key: [keyxxxxxxxxxxxxxxx]
```

---

## N8N ENVIRONMENT VARIABLES

Acesse Settings > Environment Variables no n8n Cloud:

```
AIRTABLE_BASE_ID=[appxxxxxxxxxxxxxxx]
TWILIO_WHATSAPP_NUMBER=[+5511999999999]
OPENAI_MODEL=gpt-4
SYSTEM_TIMEZONE=America/Sao_Paulo
DEBUG_MODE=false
HMAC_SECRET=[seu_secret_para_validacao_opcional]
JWT_SECRET=[seu_secret_para_jwt_opcional]
```

---

## TWILIO CONFIGURATION

### Account Information
```
Account SID: [ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]
Auth Token: [xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]
WhatsApp Number: [+5511999999999]
```

### Webhook Configuration
```
Webhook URL: https://beststag25.app.n8n.cloud/webhook/whatsapp/receive
HTTP Method: POST
Events: message-received, message-status
```

### WhatsApp Business Profile
```
Business Name: [Nome da sua empresa]
Business Description: [Descrição do negócio]
Business Category: [Categoria apropriada]
Business Website: [URL do site]
```

---

## AIRTABLE CONFIGURATION

### Base Information
```
Base Name: BestStag Production
Base ID: [appxxxxxxxxxxxxxxx]
API Key: [keyxxxxxxxxxxxxxxx]
Region: US (recomendado)
```

### API Settings
```
API Endpoint: https://api.airtable.com/v0/[BASE_ID]
Rate Limit: 5 requests per second
Authentication: Bearer [API_KEY]
```

---

## OPENAI CONFIGURATION

### API Settings
```
API Key: [sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]
Organization ID: [org-xxxxxxxxxxxxxxxxxxxxxxxx] (opcional)
Model: gpt-4
Max Tokens: 500
Temperature: 0.7
```

### Usage Limits
```
Tier: [Pay-as-you-go / Tier 1 / Tier 2]
Rate Limit: [Verificar no dashboard OpenAI]
Monthly Budget: [Definir limite de gastos]
```

---

## PORTAL WEB CONFIGURATION

### Environment Variables (.env.production)
```
VITE_API_BASE_URL=https://beststag25.app.n8n.cloud
VITE_APP_NAME=BestStag Portal
VITE_SUPPORT_EMAIL=[seu_email_de_suporte]
VITE_COMPANY_NAME=[Nome da sua empresa]
```

### Deploy Configuration
```
Platform: [Vercel / Netlify / AWS S3]
Domain: [seu_dominio.com]
SSL: Enabled
CDN: Enabled
```

---

## SECURITY CONFIGURATION

### HMAC Validation (Opcional mas Recomendado)
```
HMAC Secret: [string_aleatoria_segura_32_chars]
Algorithm: SHA-256
Header: X-Hub-Signature-256
```

### JWT Authentication (Portal Web)
```
JWT Secret: [string_aleatoria_segura_64_chars]
Expiration: 24h
Refresh Token: 7d
Algorithm: HS256
```

### CORS Configuration
```
Allowed Origins: 
- https://[seu_dominio].com
- https://[seu_dominio].vercel.app
- http://localhost:5173 (desenvolvimento)

Allowed Methods: GET, POST, PUT, DELETE, OPTIONS
Allowed Headers: Content-Type, Authorization, X-Hub-Signature-256
```

---

## MONITORING CONFIGURATION

### Alerting
```
Email Alerts: [seu_email_admin]
Slack Webhook: [webhook_url_slack] (opcional)
SMS Alerts: [numero_telefone] (emergências)
```

### Logging
```
Log Level: INFO (produção) / DEBUG (desenvolvimento)
Log Retention: 90 days
Error Tracking: [Sentry DSN] (opcional)
```

---

## BACKUP CONFIGURATION

### Airtable Backup
```
Frequency: Daily at 03:00 UTC
Retention: 30 days
Format: CSV + JSON
Storage: [Local / S3 / Google Drive]
```

### n8n Backup
```
Workflows: Export JSON monthly
Credentials: Backup encrypted
Executions: Keep 1000 last executions
```

---

## TESTING CONFIGURATION

### Test User
```
Test User ID: test_user_automated
Test Phone: [numero_teste_whatsapp]
Test Email: [email_teste]
```

### Test Environment
```
n8n Instance: [URL_instancia_teste] (opcional)
Airtable Base: [base_id_teste] (opcional)
OpenAI Key: [chave_teste_com_limite] (opcional)
```

---

## CHECKLIST DE CONFIGURAÇÃO

### Pré-requisitos
- [ ] Conta Twilio ativa com WhatsApp Business aprovado
- [ ] Conta n8n Cloud ativa (plano Pro recomendado)
- [ ] Conta Airtable ativa
- [ ] Conta OpenAI com créditos suficientes
- [ ] Domínio para portal web (opcional)

### Configuração Inicial
- [ ] Credenciais configuradas no n8n
- [ ] Variáveis de ambiente definidas
- [ ] Workflows importados na ordem correta
- [ ] Webhooks ativados e testados
- [ ] Estrutura Airtable criada
- [ ] Portal web deployado

### Testes de Validação
- [ ] Teste de mensagem WhatsApp
- [ ] Teste de comandos básicos
- [ ] Teste de criação de tarefas
- [ ] Teste de portal web
- [ ] Teste de sincronização
- [ ] Teste de performance

### Monitoramento
- [ ] Alertas configurados
- [ ] Logs funcionando
- [ ] Backup automático ativo
- [ ] Métricas sendo coletadas

---

## CONTATOS DE SUPORTE

### Documentação
- Conhecimento Completo: `00_CONHECIMENTO_COMPLETO.md`
- Instalação Rápida: `guias-instalacao/INSTALACAO_RAPIDA.md`
- Troubleshooting: `documentacao/documentacao_tecnica_completa.md`

### Recursos Externos
- n8n Documentation: https://docs.n8n.io/
- Twilio WhatsApp API: https://www.twilio.com/docs/whatsapp
- Airtable API: https://airtable.com/developers/web/api/introduction
- OpenAI API: https://platform.openai.com/docs/

---

**SEGURANÇA**: Nunca commite este arquivo com credenciais reais em repositórios públicos!
**BACKUP**: Mantenha backup seguro de todas as credenciais.
**ROTAÇÃO**: Rotacione credenciais periodicamente por segurança.

