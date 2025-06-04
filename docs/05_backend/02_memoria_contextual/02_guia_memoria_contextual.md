# Guia de Implementação - Fase 3: Sistema de Memória Contextual

## 🧠 Objetivo

Implementar um sistema avançado de memória contextual que permite ao BestStag "lembrar" de conversas anteriores, aprender com as interações e fornecer respostas cada vez mais personalizadas através de camadas inteligentes de memória (MCP, MMP, MLP).

## 📦 Componentes Implementados

### 1. Analisador de Contexto
**Funcionalidade**: Analisa mensagens recebidas para determinar relevância temporal, importância e tipo de conteúdo, direcionando para a camada de memória apropriada.

**Características**:
- Análise temporal (imediato, recente, distante)
- Classificação de importância (alta, média, baixa)
- Identificação de tipo de conteúdo (pessoal, profissional, tarefa, evento)
- Extração automática de palavras-chave e entidades

### 2. Sistema de Camadas de Memória
**Funcionalidade**: Implementa três camadas distintas de memória com diferentes características de retenção e acesso.

**Camadas implementadas**:
- **MCP (Memória de Curto Prazo)**: Últimas 24 horas, acesso rápido
- **MMP (Memória de Médio Prazo)**: Última semana, contexto recente
- **MLP (Memória de Longo Prazo)**: Último mês, informações importantes

### 3. Recuperador de Memória Inteligente
**Funcionalidade**: Busca e consolida informações relevantes de múltiplas camadas de memória baseado no contexto atual.

**Características**:
- Busca multi-camada com priorização
- Pontuação de relevância baseada em palavras-chave
- Consolidação inteligente de resultados
- Atualização automática de contadores de acesso

### 4. Armazenador Contextual
**Funcionalidade**: Processa e armazena novas informações nas camadas apropriadas com extração automática de dados estruturados.

**Características**:
- Extração de entidades (pessoas, emails, telefones, datas)
- Identificação de ações e preferências
- Geração automática de chaves de memória
- Configuração de TTL baseada na importância

### 5. Sumarizador Inteligente
**Funcionalidade**: Cria resumos contextuais para memórias importantes usando IA.

**Características**:
- Sumarização automática para conteúdo de alta prioridade
- Integração com OpenAI para resumos inteligentes
- Armazenamento de resumos como memórias especiais
- Contexto de memórias relacionadas

### 6. Priorizador Dinâmico
**Funcionalidade**: Ajusta prioridades de memórias baseado em padrões de acesso e relevância temporal.

**Características**:
- Rebalanceamento automático de prioridades
- Limpeza de memórias expiradas
- Promoção entre camadas baseada em uso
- Análise de padrões de acesso

## 🔧 Configuração e Implementação

### Pré-requisitos
- Workflows das Fases 1 e 2 funcionando
- Estrutura do Airtable com tabela "Memória Contextual"
- Credenciais OpenAI configuradas
- Acesso aos webhooks do n8n

### Passo 1: Importar Workflow de Memória Contextual

1. **Acessar n8n Cloud**
   ```
   URL: https://beststag25.app.n8n.cloud
   ```

2. **Importar Workflow**
   - Clique em "New Workflow"
   - Selecione "Import from file"
   - Faça upload do arquivo: `beststag_memoria_contextual.json`
   - Renomeie para: "BestStag - Sistema de Memória Contextual"

### Passo 2: Configurar Webhooks

#### 2.1 Webhook Principal de Memória
```
Endpoint: /webhook/memoria/contextual
Método: POST
Função: Gerenciar armazenamento e recuperação de memória
```

**Parâmetros para recuperação**:
```json
{
  "operation": "retrieve",
  "user_id": "user_123",
  "message": "Lembra da reunião que mencionei ontem?",
  "memory_type": "auto"
}
```

**Parâmetros para armazenamento**:
```json
{
  "operation": "store",
  "user_id": "user_123",
  "message": "Tenho uma reunião importante amanhã às 14h com o cliente ABC",
  "memory_type": "auto"
}
```

#### 2.2 Webhook de Priorização
```
Endpoint: /webhook/memoria/prioritize
Método: POST
Função: Analisar e rebalancear prioridades de memória
```

**Parâmetros**:
```json
{
  "operation": "rebalance",
  "user_id": "user_123",
  "time_range": "7d"
}
```

### Passo 3: Integrar com Workflow Principal

#### 3.1 Modificar Workflow da Fase 1
Adicione recuperação de contexto antes do processamento OpenAI:

```javascript
// Recuperar contexto relevante
const memoryRequest = {
  operation: 'retrieve',
  user_id: userData.user_id,
  message: userData.message_body,
  memory_type: 'auto'
};

const memoryResponse = await fetch('https://beststag25.app.n8n.cloud/webhook/memoria/contextual', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(memoryRequest)
});

const contextualMemories = await memoryResponse.json();
```

#### 3.2 Armazenar Nova Memória
Após processar a resposta, armazene a nova interação:

```javascript
// Armazenar nova memória
const storeRequest = {
  operation: 'store',
  user_id: userData.user_id,
  message: userData.message_body,
  memory_type: 'auto'
};

await fetch('https://beststag25.app.n8n.cloud/webhook/memoria/contextual', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(storeRequest)
});
```

### Passo 4: Configurar Automações de Manutenção

#### 4.1 Priorização Automática
Configure execução diária para rebalancear prioridades:

```javascript
// Executar diariamente às 02:00
const prioritizationRequest = {
  operation: 'rebalance',
  time_range: '7d'
};

// Para todos os usuários ou usuário específico
const response = await fetch('https://beststag25.app.n8n.cloud/webhook/memoria/prioritize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(prioritizationRequest)
});
```

#### 4.2 Limpeza Automática
Configure limpeza semanal de memórias expiradas:

```javascript
// Executar semanalmente
const cleanupRequest = {
  operation: 'analyze',
  time_range: '30d'
};
```

## 🧪 Testes e Validação

### Teste 1: Armazenamento de Memória
```bash
# Teste de armazenamento
curl -X POST https://beststag25.app.n8n.cloud/webhook/memoria/contextual \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "store",
    "user_id": "test_user",
    "message": "Tenho uma reunião importante com o cliente ABC amanhã às 14h para discutir o projeto XYZ",
    "memory_type": "auto"
  }'
```

### Teste 2: Recuperação de Contexto
```bash
# Teste de recuperação
curl -X POST https://beststag25.app.n8n.cloud/webhook/memoria/contextual \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "retrieve",
    "user_id": "test_user",
    "message": "Como foi a reunião com o cliente ABC?",
    "memory_type": "auto"
  }'
```

### Teste 3: Priorização Dinâmica
```bash
# Teste de priorização
curl -X POST https://beststag25.app.n8n.cloud/webhook/memoria/prioritize \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "analyze",
    "user_id": "test_user",
    "time_range": "7d"
  }'
```

## 📊 Estrutura de Dados da Memória

### Campos da Tabela "Memória Contextual"
```
- user: Link para tabela Usuários
- type: MCP, MMP, MLP, Resumo
- key: Chave única gerada automaticamente
- value: Dados estruturados em JSON
- priority: 1-10 (calculado dinamicamente)
- created_at: Data de criação
- expires_at: Data de expiração
- access_count: Contador de acessos
- last_accessed: Último acesso
```

### Exemplo de Valor Armazenado
```json
{
  "original_message": "Tenho reunião com cliente ABC amanhã às 14h",
  "structured_info": {
    "entities": [
      {"type": "person", "value": "cliente ABC"},
      {"type": "time", "value": "14h"}
    ],
    "actions": ["reunir"],
    "temporal_refs": ["amanhã"],
    "preferences": [],
    "facts": ["reunião agendada"]
  },
  "context_analysis": {
    "temporal_scope": "immediate",
    "importance_level": "high",
    "content_type": "professional",
    "keywords": ["reunião", "cliente", "amanhã"]
  },
  "processing_timestamp": "2024-12-03T10:30:00Z"
}
```

## 🎯 Algoritmos de Inteligência

### Algoritmo de Relevância
```javascript
function calculateRelevance(memory, context) {
  let score = 0;
  
  // Pontuação por palavras-chave (40%)
  const keywordMatches = context.keywords.filter(k => 
    memory.value.toLowerCase().includes(k)
  ).length;
  score += (keywordMatches / context.keywords.length) * 4;
  
  // Pontuação por tipo de conteúdo (30%)
  if (memory.key.includes(context.content_type)) {
    score += 3;
  }
  
  // Pontuação por acesso recente (30%)
  const daysSinceAccess = (Date.now() - new Date(memory.last_accessed)) / (1000 * 60 * 60 * 24);
  if (daysSinceAccess < 1) score += 3;
  else if (daysSinceAccess < 7) score += 2;
  else if (daysSinceAccess < 30) score += 1;
  
  return Math.min(score, 10);
}
```

### Algoritmo de Priorização Dinâmica
```javascript
function calculateNewPriority(memory, config) {
  const accessScore = Math.min(memory.access_count / 5, 1) * 10;
  const recencyScore = calculateRecencyScore(memory.last_accessed);
  const importanceScore = memory.priority;
  
  return Math.round(
    accessScore * 0.4 +
    recencyScore * 0.3 +
    importanceScore * 0.3
  );
}
```

## 🔄 Fluxos de Trabalho

### Fluxo de Armazenamento
```
Mensagem → Context Analyzer → Memory Storer → Store Memory Record → Summarization? → Generate Summary → Store Summary
```

### Fluxo de Recuperação
```
Consulta → Context Analyzer → Memory Retriever → Query Layers → Memory Processor → Return Results
```

### Fluxo de Priorização
```
Trigger → Priority Analyzer → Get Memories → Priority Processor → Execute Actions → Update/Delete Records
```

## 📈 Métricas e Monitoramento

### Métricas de Memória
- **Total de memórias por usuário**
- **Distribuição por camadas (MCP/MMP/MLP)**
- **Taxa de acesso por tipo de memória**
- **Efetividade da recuperação contextual**

### Métricas de Performance
- **Tempo de recuperação de contexto**
- **Precisão da relevância**
- **Taxa de sumarização**
- **Eficiência da priorização**

### Alertas Configurados
- Memórias não acessadas > 30 dias
- Taxa de recuperação < 70%
- Tempo de resposta > 3 segundos
- Falhas na sumarização

## 🚀 Benefícios Implementados

### Personalização Avançada
- **Contexto contínuo** entre conversas
- **Aprendizado progressivo** sobre preferências
- **Respostas personalizadas** baseadas no histórico
- **Antecipação de necessidades** do usuário

### Eficiência Operacional
- **Redução de repetições** de informações
- **Continuidade natural** das conversas
- **Priorização automática** de informações importantes
- **Limpeza automática** de dados irrelevantes

### Inteligência Contextual
- **Compreensão temporal** de eventos
- **Relacionamento entre informações** diferentes
- **Sumarização inteligente** de conversas longas
- **Busca semântica** por conceitos

## 🔄 Próximos Passos

Após implementação da Fase 3:
1. **Monitorar métricas** de uso da memória por 1 semana
2. **Ajustar algoritmos** de relevância baseado no feedback
3. **Otimizar TTL** das diferentes camadas
4. **Configurar automações** de manutenção
5. **Avançar para Fase 4**: Implementação de Comandos Básicos

---

**Status**: ✅ **FASE 3 PRONTA PARA IMPLEMENTAÇÃO**  
**Próxima Fase**: Implementação de Comandos Básicos  
**Tempo Estimado**: 3-4 horas para implementação completa

