# BestStag v9.1 + Abacus.AI - Fase 1: Integração Inicial

## 📋 Visão Geral

Esta é a **Fase 1** da integração do BestStag v9.1 com Abacus.AI, focando na integração inicial com os componentes essenciais:

- ✅ Nó customizado n8n para Abacus.AI
- ✅ Workflow WhatsApp inteligente
- ✅ Cliente Python robusto
- ✅ Sistema de cache e retry
- ✅ Testes de validação

## 🚀 Instalação e Configuração

### 1. Pré-requisitos

- Python 3.8+
- n8n instalado e funcionando
- Conta Abacus.AI com API key
- Conta Twilio configurada para WhatsApp

### 2. Instalação das Dependências

```bash
# Instalar dependências Python
pip install -r requirements.txt

# Instalar dependências do n8n (se necessário)
npm install -g n8n
```

### 3. Configuração de Ambiente

```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar .env com suas credenciais
nano .env
```

**Variáveis obrigatórias:**
- `ABACUS_API_KEY`: Sua chave da API Abacus.AI
- `TWILIO_ACCOUNT_SID`: SID da conta Twilio
- `TWILIO_AUTH_TOKEN`: Token de autenticação Twilio
- `TWILIO_WHATSAPP_NUMBER`: Número WhatsApp do Twilio

### 4. Configuração do n8n

#### 4.1 Instalar Nó Customizado

```bash
# Copiar arquivos para diretório n8n
mkdir -p ~/.n8n/custom/
cp nodes/AbacusAI.node.ts ~/.n8n/custom/
cp credentials/AbacusApi.credentials.ts ~/.n8n/custom/

# Compilar TypeScript (se necessário)
cd ~/.n8n/custom/
tsc AbacusAI.node.ts
tsc AbacusApi.credentials.ts
```

#### 4.2 Reiniciar n8n

```bash
# Parar n8n
pkill -f n8n

# Iniciar n8n
n8n start
```

#### 4.3 Configurar Credenciais

1. Acesse n8n em `http://localhost:5678`
2. Vá em **Credentials** → **Add Credential**
3. Selecione **Abacus.AI API**
4. Insira sua API key
5. Salve as credenciais

#### 4.4 Importar Workflow

1. Vá em **Workflows** → **Import from File**
2. Selecione `workflows/whatsapp_abacus_workflow.json`
3. Configure as credenciais nos nós:
   - **Abacus.AI**: Selecione as credenciais criadas
   - **Twilio**: Configure com suas credenciais Twilio
4. Ative o workflow

### 5. Configuração do WhatsApp

#### 5.1 Webhook Twilio

1. Acesse o Console Twilio
2. Vá em **Messaging** → **Settings** → **WhatsApp sandbox settings**
3. Configure o webhook URL: `http://seu-dominio.com/webhook/whatsapp-in`
4. Método: **POST**

#### 5.2 Teste do WhatsApp

1. Envie `join <sandbox-code>` para o número sandbox
2. Envie uma mensagem de teste
3. Verifique se recebe resposta inteligente

## 🧪 Testes e Validação

### Teste Automático

```bash
# Executar todos os testes
python test_integration.py
```

### Teste Manual

#### 1. Teste do Cliente Python

```python
from python.abacus_client import AbacusClient

client = AbacusClient()
response = client.generate_text("Olá, como você pode me ajudar?")
print(response)
```

#### 2. Teste do Workflow n8n

1. Acesse o workflow no n8n
2. Clique em **Execute Workflow**
3. Simule uma mensagem WhatsApp
4. Verifique a resposta

#### 3. Teste do WhatsApp

1. Envie: "Olá BestStag"
2. Esperado: Resposta personalizada e inteligente
3. Envie: "Estou triste hoje"
4. Esperado: Resposta empática

## 📊 Funcionalidades Implementadas

### ✅ Nó n8n Abacus.AI

- **Operações**: Chat, DeepAgent, Sentiment Analysis
- **Modelos**: ChatGLM, GPT-4, Claude
- **Configuração**: Visual no n8n
- **Tratamento de erros**: Retry automático

### ✅ Workflow WhatsApp Inteligente

- **Análise de sentimento**: Detecta emoções
- **Roteamento inteligente**: Resposta empática vs normal
- **Processamento IA**: Classificação de intenções
- **Execução de ações**: DeepAgent para tarefas complexas
- **Fallback**: Tratamento de erros

### ✅ Cliente Python Robusto

- **Cache inteligente**: TTL configurável
- **Retry automático**: Backoff exponencial
- **Estatísticas**: Monitoramento de uso
- **Health check**: Verificação de status
- **Múltiplas operações**: Chat, Agent, Sentiment

## 🔧 Configurações Avançadas

### Cache Redis (Opcional)

```bash
# Instalar Redis
sudo apt install redis-server

# Configurar no .env
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Monitoramento

```python
# Verificar estatísticas
client = AbacusClient()
stats = client.get_stats()
print(f"Requests: {stats['requests_made']}")
print(f"Cache hits: {stats['cache_hits']}")
print(f"Hit rate: {stats['cache_hit_rate']:.1f}%")
```

### Logs

```bash
# Verificar logs do n8n
tail -f ~/.n8n/logs/n8n.log

# Logs do Python
export LOG_LEVEL=DEBUG
python test_integration.py
```

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. "API key não encontrada"
```bash
# Verificar variável de ambiente
echo $ABACUS_API_KEY

# Ou verificar arquivo .env
cat .env | grep ABACUS_API_KEY
```

#### 2. "Nó Abacus.AI não encontrado no n8n"
```bash
# Verificar se arquivos foram copiados
ls ~/.n8n/custom/

# Reiniciar n8n
pkill -f n8n && n8n start
```

#### 3. "Webhook WhatsApp não funciona"
- Verificar URL do webhook no Twilio
- Verificar se n8n está acessível externamente
- Usar ngrok para desenvolvimento local

#### 4. "Timeout nas requisições"
```python
# Aumentar timeout
client = AbacusClient(max_retries=5)
```

### Logs de Debug

```bash
# Ativar logs detalhados
export LOG_LEVEL=DEBUG
export ABACUS_DEBUG=true

# Executar testes
python test_integration.py
```

## 📈 Próximos Passos

Após validar a Fase 1, prossiga para:

- **Fase 2**: IA Contextual e Front-end Inteligente
  - Sistema de memória com embeddings
  - Hooks React inteligentes
  - Dashboard adaptativo
  - Relatórios automáticos

## 📞 Suporte

- **Documentação**: Consulte os comentários no código
- **Testes**: Execute `python test_integration.py`
- **Logs**: Verifique logs do n8n e Python
- **Issues**: Documente problemas encontrados

---

**✅ Fase 1 Concluída com Sucesso!**

A integração básica entre BestStag v9.1 e Abacus.AI está funcionando. O sistema agora possui:
- Conversação natural via WhatsApp
- Análise de sentimento automática
- Respostas empáticas e contextuais
- Execução de ações inteligentes
- Sistema robusto com cache e retry

Pronto para avançar para a Fase 2! 🚀

