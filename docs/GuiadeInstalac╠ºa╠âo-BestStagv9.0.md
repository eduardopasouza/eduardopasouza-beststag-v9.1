# Guia de Instalação - BestStag v9.0

## 📋 Visão Geral

Este guia fornece instruções detalhadas para instalar e configurar o BestStag v9.0, um assistente virtual inteligente que integra WhatsApp, gestão de tarefas, agenda e muito mais.

## 🎯 Pré-requisitos

### Sistema Operacional
- **Linux**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **macOS**: 10.15+ (Catalina ou superior)
- **Windows**: 10/11 com WSL2

### Software Necessário
- **Node.js**: 18.0.0 ou superior
- **Python**: 3.8.0 ou superior
- **Git**: 2.25.0 ou superior
- **Docker**: 20.10.0 ou superior (opcional)

### Contas de Serviços Externos
- **Airtable**: Conta Pro ou superior
- **Twilio**: Conta com WhatsApp Business API
- **n8n**: Instância local ou cloud

## 🚀 Instalação Rápida

### Opção 1: Script Automatizado (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/beststag/beststag-v9.git
cd beststag-v9

# 2. Execute o script de instalação
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Opção 2: Instalação Manual

#### Passo 1: Preparar o Ambiente

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y nodejs npm python3 python3-pip git curl docker.io

# CentOS/RHEL
sudo yum install -y nodejs npm python3 python3-pip git curl docker

# macOS (com Homebrew)
brew install node python3 git curl docker
```

#### Passo 2: Configurar Variáveis de Ambiente

```bash
# Copiar template de configuração
cp configs/.env.example .env

# Editar configurações
nano .env
```

**Configurações obrigatórias no .env:**

```env
# Airtable
AIRTABLE_API_KEY=seu_api_key_aqui
AIRTABLE_BASE_ID=seu_base_id_aqui

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=seu_account_sid
TWILIO_AUTH_TOKEN=seu_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+5511999999999

# n8n
N8N_WEBHOOK_URL=http://localhost:5678/webhook
N8N_USER=admin
N8N_PASSWORD=beststag2025

# Portal Web
PORTAL_URL=http://localhost:3000
PORTAL_SECRET_KEY=sua_chave_secreta_aqui

# Email (opcional)
SENDGRID_API_KEY=seu_sendgrid_key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
```

#### Passo 3: Instalar Dependências Python

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
```

#### Passo 4: Configurar Airtable

```bash
# Executar script de setup
python scripts/python/setup_airtable.py
```

#### Passo 5: Configurar n8n

```bash
# Instalar n8n globalmente
npm install -g n8n

# Configurar variáveis de ambiente
export N8N_BASIC_AUTH_ACTIVE=true
export N8N_BASIC_AUTH_USER=admin
export N8N_BASIC_AUTH_PASSWORD=beststag2025

# Iniciar n8n
n8n start
```

#### Passo 6: Importar Workflows

1. Acesse n8n em `http://localhost:5678`
2. Faça login com as credenciais configuradas
3. Importe os workflows da pasta `workflows/n8n/`

#### Passo 7: Configurar Portal Web

```bash
cd portal_web

# Instalar dependências
npm install

# Build do projeto
npm run build

# Iniciar servidor de desenvolvimento
npm run dev
```

## 🔧 Configuração Detalhada

### Airtable Setup

1. **Criar Base no Airtable**
   - Acesse [airtable.com](https://airtable.com)
   - Crie uma nova base chamada "BestStag v9.0"
   - Use o schema em `configs/airtable_schema.json`

2. **Obter API Key**
   - Vá em Account → API
   - Copie sua API Key
   - Cole no arquivo `.env`

3. **Configurar Tabelas**
   - Execute o script: `python scripts/python/setup_airtable.py`
   - Verifique se todas as tabelas foram criadas

### Twilio WhatsApp Setup

1. **Configurar Sandbox**
   - Acesse [Twilio Console](https://console.twilio.com)
   - Vá em Messaging → Try it out → Send a WhatsApp message
   - Configure o webhook: `https://seu-dominio.com/webhook/whatsapp`

2. **Configurar Webhook**
   ```
   URL: http://localhost:5678/webhook/whatsapp
   Método: POST
   ```

### n8n Workflows

1. **Workflow Principal WhatsApp**
   - Arquivo: `workflows/n8n/01_whatsapp_principal.json`
   - Webhook: `/webhook/whatsapp`

2. **Gestão de Tarefas**
   - Arquivo: `workflows/n8n/02_gestao_tarefas.json`
   - API: `/api/tarefas`

3. **Gestão de Agenda**
   - Arquivo: `workflows/n8n/03_gestao_agenda.json`
   - API: `/api/agenda`

4. **Sistema de Memória**
   - Arquivo: `workflows/n8n/04_memoria_contextual.json`
   - API: `/api/memoria`

## 🐳 Instalação com Docker

### Docker Compose (Recomendado)

```yaml
# docker-compose.yml
version: '3.8'

services:
  beststag-n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=beststag2025
    volumes:
      - n8n_data:/home/node/.n8n
      - ./workflows:/workflows

  beststag-portal:
    build: ./portal_web
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - beststag-n8n

volumes:
  n8n_data:
```

```bash
# Iniciar com Docker Compose
docker-compose up -d
```

### Docker Manual

```bash
# Build da imagem
docker build -t beststag:v9.0 .

# Executar container
docker run -d \
  --name beststag \
  -p 5678:5678 \
  -p 3000:3000 \
  -v $(pwd)/.env:/app/.env \
  beststag:v9.0
```

## 🔍 Verificação da Instalação

### Testes Básicos

```bash
# Testar conexão Airtable
python -c "
import os
import requests
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('AIRTABLE_API_KEY')
base_id = os.getenv('AIRTABLE_BASE_ID')
response = requests.get(f'https://api.airtable.com/v0/{base_id}/Usuarios', 
                       headers={'Authorization': f'Bearer {api_key}'})
print('✅ Airtable OK' if response.status_code == 200 else '❌ Airtable ERRO')
"

# Testar n8n
curl -s http://localhost:5678 && echo "✅ n8n OK" || echo "❌ n8n ERRO"

# Testar portal web
curl -s http://localhost:3000 && echo "✅ Portal OK" || echo "❌ Portal ERRO"
```

### Teste WhatsApp

1. Envie uma mensagem para o número configurado
2. Digite: `/ajuda`
3. Verifique se recebe a resposta com comandos disponíveis

### Teste Portal Web

1. Acesse `http://localhost:3000`
2. Faça login com suas credenciais
3. Verifique se o dashboard carrega corretamente

## 🚨 Solução de Problemas

### Problemas Comuns

#### Erro: "Airtable API Key inválida"
```bash
# Verificar se a API Key está correta
echo $AIRTABLE_API_KEY

# Testar manualmente
curl -H "Authorization: Bearer $AIRTABLE_API_KEY" \
     "https://api.airtable.com/v0/$AIRTABLE_BASE_ID/Usuarios"
```

#### Erro: "n8n não inicia"
```bash
# Verificar logs
n8n start --log-level debug

# Verificar porta
netstat -tulpn | grep 5678

# Limpar cache
rm -rf ~/.n8n/cache
```

#### Erro: "Portal web não carrega"
```bash
# Verificar dependências
cd portal_web
npm install

# Verificar build
npm run build

# Verificar logs
npm run dev
```

### Logs e Debugging

```bash
# Logs do n8n
tail -f ~/.n8n/logs/n8n.log

# Logs do sistema
journalctl -u beststag-n8n -f

# Logs do portal
cd portal_web
npm run dev
```

## 🔄 Atualizações

### Atualizar para Nova Versão

```bash
# Backup dos dados
cp .env .env.backup
cp -r ~/.n8n ~/.n8n.backup

# Baixar nova versão
git pull origin main

# Atualizar dependências
pip install -r requirements.txt
cd portal_web && npm install && cd ..

# Executar migrações
python scripts/python/migrate.py

# Reiniciar serviços
sudo systemctl restart beststag-n8n
```

## 📊 Monitoramento

### Métricas Importantes

- **Uptime do n8n**: `systemctl status beststag-n8n`
- **Uso de memória**: `htop` ou `ps aux | grep n8n`
- **Logs de erro**: `tail -f ~/.n8n/logs/n8n.log | grep ERROR`
- **Webhooks ativos**: Verificar no painel do n8n

### Alertas Recomendados

- Falha na conexão com Airtable
- Webhook WhatsApp inativo
- Alto uso de CPU/memória
- Erros nos workflows

## 🔐 Segurança

### Configurações de Segurança

```bash
# Configurar firewall
sudo ufw allow 22    # SSH
sudo ufw allow 5678  # n8n (apenas se necessário externamente)
sudo ufw allow 3000  # Portal web
sudo ufw enable

# Configurar SSL (produção)
sudo certbot --nginx -d seu-dominio.com

# Backup automático
crontab -e
# Adicionar: 0 2 * * * /path/to/backup-script.sh
```

### Variáveis Sensíveis

- Nunca commitar o arquivo `.env`
- Usar secrets manager em produção
- Rotacionar API keys regularmente
- Monitorar acessos suspeitos

## 📞 Suporte

### Recursos de Ajuda

- **Documentação**: `docs/`
- **Issues**: [GitHub Issues](https://github.com/beststag/beststag-v9/issues)
- **Discussões**: [GitHub Discussions](https://github.com/beststag/beststag-v9/discussions)
- **Email**: suporte@beststag.com

### Informações para Suporte

Ao reportar problemas, inclua:

```bash
# Informações do sistema
uname -a
node --version
python3 --version
docker --version

# Logs relevantes
tail -n 50 ~/.n8n/logs/n8n.log

# Configuração (sem dados sensíveis)
cat .env | grep -v "API_KEY\|PASSWORD\|SECRET"
```

## 🎉 Próximos Passos

Após a instalação bem-sucedida:

1. **Configurar usuários**: Adicione usuários no Airtable
2. **Personalizar comandos**: Edite os workflows conforme necessário
3. **Configurar notificações**: Configure emails e alertas
4. **Treinar usuários**: Compartilhe o guia de uso
5. **Monitorar performance**: Configure dashboards de monitoramento

---

**BestStag v9.0** - Desenvolvido com ❤️ pela Manus AI

Para mais informações, visite: [https://beststag.com](https://beststag.com)

