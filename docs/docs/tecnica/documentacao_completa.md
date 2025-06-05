# Documentação Técnica Completa - BestStag v9.0

## 📋 Índice

1. [Visão Geral do Sistema](#visão-geral-do-sistema)
2. [Arquitetura](#arquitetura)
3. [Componentes Principais](#componentes-principais)
4. [APIs e Integrações](#apis-e-integrações)
5. [Workflows n8n](#workflows-n8n)
6. [Portal Web](#portal-web)
7. [Sistema de Memória](#sistema-de-memória)
8. [Configurações](#configurações)
9. [Deployment](#deployment)
10. [Monitoramento](#monitoramento)
11. [Troubleshooting](#troubleshooting)
12. [Roadmap](#roadmap)

---

## 🎯 Visão Geral do Sistema

### Propósito
O BestStag v9.0 é um assistente virtual inteligente que integra múltiplos canais de comunicação (WhatsApp, Portal Web, Email) com sistemas de produtividade (gestão de tarefas, agenda, relatórios) através de uma arquitetura baseada em workflows automatizados.

### Características Principais
- **Multicanal**: WhatsApp, Portal Web, Email, API REST
- **Inteligência Contextual**: Sistema de memória em camadas (MCP, MMP, MLP)
- **Automação Completa**: Workflows n8n para todas as operações
- **Interface Moderna**: Portal web React com dashboard em tempo real
- **Escalabilidade**: Arquitetura containerizada com Docker
- **Monitoramento**: Métricas e logs integrados

### Tecnologias Utilizadas
- **Backend**: n8n (workflows), FastAPI (API), Python 3.11
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Database**: Airtable (principal), SQLite/PostgreSQL (cache)
- **Cache**: Redis
- **Comunicação**: Twilio WhatsApp API, SendGrid
- **Containerização**: Docker, Docker Compose
- **Monitoramento**: Prometheus, Grafana, Loki

---

## 🏗️ Arquitetura

### Diagrama de Arquitetura

```mermaid
graph TB
    subgraph "Canais de Entrada"
        WA[WhatsApp]
        PW[Portal Web]
        EM[Email]
        API[API REST]
    end
    
    subgraph "Camada de Processamento"
        N8N[n8n Workflows]
        FAST[FastAPI]
        REDIS[Redis Cache]
    end
    
    subgraph "Camada de Dados"
        AT[Airtable]
        DB[SQLite/PostgreSQL]
        MEM[Sistema Memória]
    end
    
    subgraph "Serviços Externos"
        TW[Twilio]
        SG[SendGrid]
        GC[Google Calendar]
    end
    
    WA --> N8N
    PW --> FAST
    EM --> N8N
    API --> FAST
    
    N8N --> AT
    N8N --> REDIS
    N8N --> TW
    N8N --> SG
    
    FAST --> AT
    FAST --> DB
    FAST --> REDIS
    
    N8N --> MEM
    FAST --> MEM
    
    N8N --> GC
```

### Fluxo de Dados

1. **Entrada**: Usuário interage via WhatsApp, Portal ou API
2. **Roteamento**: n8n ou FastAPI processa a requisição
3. **Processamento**: Workflows executam lógica de negócio
4. **Persistência**: Dados salvos no Airtable/Database
5. **Memória**: Contexto armazenado no sistema de memória
6. **Resposta**: Resultado enviado de volta ao usuário

---

## 🔧 Componentes Principais

### 1. n8n Workflows Engine

**Responsabilidades:**
- Processamento de mensagens WhatsApp
- Automações de tarefas e agenda
- Integrações com serviços externos
- Sistema de memória contextual

**Workflows Principais:**
- `01_whatsapp_principal.json`: Processamento WhatsApp
- `02_gestao_tarefas.json`: CRUD de tarefas
- `03_gestao_agenda.json`: Gestão de eventos
- `04_memoria_contextual.json`: Sistema de memória

### 2. Portal Web (React)

**Funcionalidades:**
- Dashboard interativo
- Gestão de tarefas e eventos
- Relatórios e analytics
- Configurações do usuário

**Estrutura:**
```
portal_web/
├── src/
│   ├── components/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Tasks.tsx
│   │   │   └── Calendar.tsx
│   │   └── ui/
│   ├── hooks/
│   ├── services/
│   └── utils/
├── public/
└── package.json
```

### 3. FastAPI Backend

**Endpoints Principais:**
- `/api/dashboard/stats`: Estatísticas do dashboard
- `/api/tarefas`: CRUD de tarefas
- `/api/eventos`: CRUD de eventos
- `/api/usuarios`: Gestão de usuários
- `/api/relatorios`: Geração de relatórios

### 4. Sistema de Memória Contextual

**Camadas:**
- **MCP (Memória Curto Prazo)**: 24 horas
- **MMP (Memória Médio Prazo)**: 30 dias
- **MLP (Memória Longo Prazo)**: 1 ano

**Algoritmo de Classificação:**
```python
def classificar_memoria(conteudo, contexto):
    score = calcular_relevancia(conteudo)
    
    if score >= 80:
        return "MLP"
    elif score >= 60:
        return "MMP"
    else:
        return "MCP"
```

---

## 🔌 APIs e Integrações

### Airtable API

**Configuração:**
```python
AIRTABLE_API_KEY = "seu_api_key"
AIRTABLE_BASE_ID = "seu_base_id"
BASE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}"
```

**Tabelas:**
- `Usuarios`: Dados dos usuários
- `Tarefas`: Gestão de tarefas
- `Eventos`: Agenda e calendário
- `Interacoes`: Log de interações
- `Configuracoes`: Preferências do usuário

### Twilio WhatsApp API

**Webhook Configuration:**
```json
{
  "url": "https://seu-dominio.com/webhook/whatsapp",
  "method": "POST",
  "events": ["message.received"]
}
```

**Envio de Mensagens:**
```python
def enviar_whatsapp(para, mensagem):
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    message = client.messages.create(
        from_=f'whatsapp:{TWILIO_NUMBER}',
        body=mensagem,
        to=f'whatsapp:{para}'
    )
    return message.sid
```

### Google Calendar API

**Sincronização de Eventos:**
```python
def sincronizar_evento(evento):
    service = build('calendar', 'v3', credentials=creds)
    
    google_event = {
        'summary': evento['titulo'],
        'start': {'dateTime': evento['data_inicio']},
        'end': {'dateTime': evento['data_fim']},
    }
    
    result = service.events().insert(
        calendarId='primary',
        body=google_event
    ).execute()
    
    return result['id']
```

---

## ⚙️ Workflows n8n

### Estrutura dos Workflows

Cada workflow segue o padrão:
1. **Trigger**: Webhook ou Schedule
2. **Validação**: Verificar dados de entrada
3. **Processamento**: Lógica de negócio
4. **Persistência**: Salvar no Airtable
5. **Resposta**: Retornar resultado

### Workflow WhatsApp Principal

**Fluxo:**
```
Webhook → Verificar Comando → Processar → Salvar Interação → Responder
```

**Comandos Suportados:**
- `/ajuda`: Lista de comandos
- `/status`: Resumo geral
- `/tarefa`: Gestão de tarefas
- `/agenda`: Gestão de eventos
- `/perfil`: Configurações

### Workflow Gestão de Tarefas

**Operações:**
- `criar`: Nova tarefa
- `listar`: Listar tarefas
- `concluir`: Marcar como concluída
- `atualizar`: Editar tarefa
- `deletar`: Remover tarefa

### Sistema de Memória

**Operações:**
- `armazenar`: Salvar nova memória
- `buscar`: Recuperar memórias relevantes
- `sumarizar`: Resumir período
- `limpar`: Remover memórias expiradas
- `migrar`: Mover entre camadas

---

## 🌐 Portal Web

### Tecnologias

**Core:**
- React 18 com TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Radix UI (componentes)

**Estado e Dados:**
- TanStack Query (server state)
- Zustand (client state)
- React Hook Form (formulários)

**Funcionalidades:**
- Dashboard responsivo
- Gestão de tarefas drag-and-drop
- Calendário interativo
- Relatórios com gráficos
- Configurações avançadas

### Estrutura de Componentes

```typescript
// Dashboard Principal
const Dashboard: React.FC = () => {
  const { data: stats } = useQuery(['dashboard-stats']);
  
  return (
    <div className="dashboard">
      <StatsCards stats={stats} />
      <TasksList />
      <UpcomingEvents />
      <ActivityFeed />
    </div>
  );
};

// Gestão de Tarefas
const TaskManager: React.FC = () => {
  const { data: tasks } = useQuery(['tasks']);
  const createTask = useMutation(createTaskAPI);
  
  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <TaskBoard tasks={tasks} />
    </DragDropContext>
  );
};
```

### API Integration

```typescript
// Service Layer
class BestStagAPI {
  async getTasks(filters?: TaskFilters): Promise<Task[]> {
    const response = await fetch('/api/tarefas', {
      method: 'GET',
      headers: this.getHeaders(),
    });
    return response.json();
  }
  
  async createTask(task: CreateTaskRequest): Promise<Task> {
    const response = await fetch('/api/tarefas', {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(task),
    });
    return response.json();
  }
}
```

---

## 🧠 Sistema de Memória

### Arquitetura da Memória

O sistema implementa um modelo de memória em três camadas inspirado na neurociência:

**MCP (Memória Curto Prazo)**
- Duração: 24 horas
- Uso: Contexto imediato da conversa
- Critério: Todas as interações recentes

**MMP (Memória Médio Prazo)**
- Duração: 30 dias
- Uso: Padrões e preferências
- Critério: Relevância score > 60

**MLP (Memória Longo Prazo)**
- Duração: 1 ano
- Uso: Configurações e dados importantes
- Critério: Relevância score > 80

### Algoritmo de Relevância

```python
def calcular_relevancia(conteudo, contexto):
    score = 50  # Base score
    
    # Palavras-chave importantes
    palavras_alta = ['importante', 'urgente', 'projeto', 'cliente']
    for palavra in palavras_alta:
        if palavra in conteudo.lower():
            score += 20
    
    # Frequência de acesso
    if contexto.get('frequencia', 0) > 3:
        score += 15
    
    # Tipo de informação
    if 'configuração' in conteudo.lower():
        score += 25
    
    # Recência
    dias_atras = (datetime.now() - contexto['data']).days
    if dias_atras <= 1:
        score += 10
    
    return min(100, max(0, score))
```

### Migração Automática

```python
def migrar_memorias():
    # MCP → MMP (score alto + frequência)
    candidatas_mmp = buscar_memorias(
        camada='MCP',
        score_min=70,
        frequencia_min=3
    )
    
    for memoria in candidatas_mmp:
        migrar_memoria(memoria, 'MCP', 'MMP')
    
    # MMP → MLP (score muito alto + tempo)
    candidatas_mlp = buscar_memorias(
        camada='MMP',
        score_min=85,
        idade_min_dias=7
    )
    
    for memoria in candidatas_mlp:
        migrar_memoria(memoria, 'MMP', 'MLP')
```

---

## ⚙️ Configurações

### Variáveis de Ambiente

**Essenciais:**
```env
# Airtable
AIRTABLE_API_KEY=keyXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX

# Twilio
TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# n8n
N8N_WEBHOOK_URL=http://localhost:5678/webhook
N8N_USER=admin
N8N_PASSWORD=beststag2025

# Portal
PORTAL_URL=http://localhost:3000
JWT_SECRET_KEY=your-secret-key-here
```

**Opcionais:**
```env
# Email
SENDGRID_API_KEY=SG.XXXXXXXXXXXXXXXX
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Monitoramento
SENTRY_DSN=https://xxx@sentry.io/xxx
PROMETHEUS_ENABLED=true

# Backup
S3_BACKUP_BUCKET=beststag-backups
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Configuração do Airtable

**Schema das Tabelas:**

```json
{
  "Usuarios": {
    "fields": {
      "nome": "Single line text",
      "email": "Email",
      "telefone": "Phone number",
      "status": "Single select",
      "plano": "Single select",
      "configuracoes": "Long text",
      "fuso_horario": "Single line text",
      "idioma": "Single line text"
    }
  },
  "Tarefas": {
    "fields": {
      "usuario": "Link to Usuarios",
      "titulo": "Single line text",
      "descricao": "Long text",
      "status": "Single select",
      "prioridade": "Single select",
      "categoria": "Single select",
      "data_vencimento": "Date",
      "estimativa_horas": "Number",
      "progresso": "Number",
      "tags": "Multiple select"
    }
  }
}
```

---

## 🚀 Deployment

### Opções de Deployment

**1. Docker Compose (Recomendado)**
```bash
# Produção completa
docker-compose --profile production up -d

# Com monitoramento
docker-compose --profile monitoring up -d

# Com backup automático
docker-compose --profile backup up -d
```

**2. Kubernetes**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: beststag-n8n
spec:
  replicas: 2
  selector:
    matchLabels:
      app: beststag-n8n
  template:
    metadata:
      labels:
        app: beststag-n8n
    spec:
      containers:
      - name: n8n
        image: n8nio/n8n:latest
        ports:
        - containerPort: 5678
        env:
        - name: N8N_BASIC_AUTH_ACTIVE
          value: "true"
```

**3. Cloud Providers**

**AWS:**
- ECS Fargate para containers
- RDS para PostgreSQL
- ElastiCache para Redis
- S3 para backups

**Google Cloud:**
- Cloud Run para containers
- Cloud SQL para PostgreSQL
- Memorystore para Redis
- Cloud Storage para backups

**Azure:**
- Container Instances
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Blob Storage para backups

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy BestStag v9.0

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: |
          python -m pytest tests/
          cd portal_web && npm test

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker Images
        run: |
          docker build -t beststag:${{ github.sha }} .
          docker build -t beststag-portal:${{ github.sha }} portal_web/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Production
        run: |
          docker-compose -f docker-compose.prod.yml up -d
```

---

## 📊 Monitoramento

### Métricas Principais

**Sistema:**
- CPU e Memória dos containers
- Latência das APIs
- Taxa de erro dos workflows
- Uptime dos serviços

**Negócio:**
- Número de interações por dia
- Taxa de conclusão de tarefas
- Tempo médio de resposta
- Usuários ativos

### Dashboards Grafana

**Dashboard Sistema:**
```json
{
  "dashboard": {
    "title": "BestStag v9.0 - Sistema",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total[5m])"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "container_memory_usage_bytes"
          }
        ]
      }
    ]
  }
}
```

**Dashboard Negócio:**
```json
{
  "dashboard": {
    "title": "BestStag v9.0 - Negócio",
    "panels": [
      {
        "title": "Interações por Hora",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(beststag_interactions_total[1h])"
          }
        ]
      },
      {
        "title": "Tarefas Concluídas",
        "type": "stat",
        "targets": [
          {
            "expr": "beststag_tasks_completed_total"
          }
        ]
      }
    ]
  }
}
```

### Alertas

**Prometheus Rules:**
```yaml
groups:
  - name: beststag.rules
    rules:
      - alert: HighErrorRate
        expr: rate(beststag_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Alta taxa de erro no BestStag"
          
      - alert: ServiceDown
        expr: up{job="beststag"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Serviço BestStag está down"
```

---

## 🔧 Troubleshooting

### Problemas Comuns

**1. n8n não inicia**
```bash
# Verificar logs
docker logs beststag-n8n

# Verificar porta
netstat -tulpn | grep 5678

# Limpar dados corrompidos
docker volume rm beststag_n8n_data
```

**2. Webhook WhatsApp não funciona**
```bash
# Testar webhook manualmente
curl -X POST http://localhost:5678/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"Body": "/ajuda", "From": "whatsapp:+5511999999999"}'

# Verificar configuração Twilio
curl -X GET "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_SID/Messages.json" \
  -u "$TWILIO_SID:$TWILIO_TOKEN"
```

**3. Portal web não carrega**
```bash
# Verificar build
cd portal_web
npm run build

# Verificar dependências
npm install

# Verificar variáveis de ambiente
echo $REACT_APP_API_URL
```

**4. Airtable API errors**
```bash
# Testar conexão
curl -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  "https://api.airtable.com/v0/$AIRTABLE_BASE_ID/Usuarios"

# Verificar rate limits
curl -I -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  "https://api.airtable.com/v0/$AIRTABLE_BASE_ID/Usuarios"
```

### Logs e Debugging

**Estrutura de Logs:**
```
logs/
├── n8n/
│   ├── workflow-executions.log
│   ├── errors.log
│   └── debug.log
├── api/
│   ├── access.log
│   ├── error.log
│   └── debug.log
└── portal/
    ├── build.log
    └── runtime.log
```

**Comandos Úteis:**
```bash
# Logs em tempo real
docker-compose logs -f beststag-n8n

# Logs específicos
docker logs beststag-n8n --since 1h

# Logs com filtro
docker logs beststag-n8n 2>&1 | grep ERROR

# Exportar logs
docker logs beststag-n8n > debug.log 2>&1
```

---

## 🗺️ Roadmap

### v9.1 (Q2 2025)
- [ ] Integração com Microsoft Teams
- [ ] Sistema de plugins
- [ ] API GraphQL
- [ ] Mobile app (React Native)

### v9.2 (Q3 2025)
- [ ] IA generativa integrada (GPT-4)
- [ ] Análise de sentimento
- [ ] Automações baseadas em ML
- [ ] Dashboard preditivo

### v9.3 (Q4 2025)
- [ ] Multi-tenancy
- [ ] Marketplace de workflows
- [ ] Integração com Slack
- [ ] Sistema de billing

### v10.0 (Q1 2026)
- [ ] Arquitetura microserviços
- [ ] Kubernetes nativo
- [ ] Edge computing
- [ ] Realidade aumentada

---

## 📞 Suporte e Contribuição

### Canais de Suporte
- **GitHub Issues**: [Reportar bugs](https://github.com/beststag/beststag-v9/issues)
- **Discussions**: [Discussões gerais](https://github.com/beststag/beststag-v9/discussions)
- **Email**: suporte@beststag.com
- **Discord**: [Comunidade BestStag](https://discord.gg/beststag)

### Como Contribuir
1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Adicione testes
5. Submeta um Pull Request

### Padrões de Código
- **Python**: Black + isort + flake8
- **TypeScript**: ESLint + Prettier
- **Commits**: Conventional Commits
- **Documentação**: Markdown + Mermaid

---

**BestStag v9.0** - Documentação Técnica Completa
*Desenvolvido com ❤️ pela Manus AI*

*Última atualização: 03/06/2025*

