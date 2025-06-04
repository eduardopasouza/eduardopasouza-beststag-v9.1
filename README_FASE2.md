# BestStag v9.1 + Abacus.AI - Fase 2: IA Contextual e Front-end Inteligente

## 📋 Visão Geral

A **Fase 2** implementa funcionalidades avançadas de IA contextual e componentes inteligentes para o frontend, transformando o BestStag em um assistente verdadeiramente inteligente:

- ✅ Sistema de memória contextual com embeddings vetoriais
- ✅ Hooks React inteligentes para IA
- ✅ Componentes React com funcionalidades de IA
- ✅ Sistema de relatórios inteligentes automáticos
- ✅ Análise de produtividade e bem-estar

## 🧠 Sistema de Memória Contextual

### Funcionalidades

- **Embeddings Vetoriais**: Usa sentence-transformers para representação semântica
- **Busca Semântica**: Encontra informações relevantes por similaridade
- **Categorização Automática**: Organiza memórias por tipo e importância
- **Políticas de Retenção**: Limpa automaticamente dados antigos
- **Contexto Personalizado**: Mantém histórico específico por usuário

### Uso Básico

```python
from contextual_memory import ContextualMemorySystem

# Inicializar sistema
memory = ContextualMemorySystem()

# Adicionar memória
memory_id = memory.add_memory(
    content="Usuário tem reunião importante na sexta às 14h",
    user_id="user123",
    category="agenda",
    importance=0.8,
    metadata={"type": "meeting", "day": "friday"}
)

# Buscar memórias
results = memory.search_memory("reunião sexta", user_id="user123", top_k=3)
for result in results:
    print(f"- {result.content} (score: {result.metadata['similarity_score']:.3f})")

# Obter contexto completo do usuário
context = memory.get_user_context("user123", days=7)
print(f"Total de itens: {context['total_items']}")
```

### Configuração Avançada

```python
# Configuração personalizada
memory = ContextualMemorySystem(
    model_name='all-MiniLM-L6-v2',  # Modelo de embeddings
    max_items=10000,                # Máximo de itens na memória
    cache_ttl=300                   # TTL do cache em segundos
)

# Salvar/carregar memória
memory.save_memory()  # Salva em disco
memory.load_memory()  # Carrega do disco
```

## ⚛️ Hooks React Inteligentes

### Hooks Disponíveis

#### `useSentiment(text, debounceMs)`
Análise de sentimento em tempo real:

```tsx
import { useSentiment } from '../hooks/useAI';

const MyComponent = () => {
  const [text, setText] = useState('');
  const { sentiment, loading, error } = useSentiment(text);
  
  return (
    <div>
      <input value={text} onChange={(e) => setText(e.target.value)} />
      {sentiment && (
        <div>Sentimento: {sentiment.sentiment} ({sentiment.confidence}%)</div>
      )}
    </div>
  );
};
```

#### `useIntelligentChat(userId)`
Chat inteligente com contexto:

```tsx
const ChatComponent = ({ userId }) => {
  const { messages, sendMessage, loading } = useIntelligentChat(userId);
  
  const handleSend = async (message) => {
    await sendMessage(message, { context: 'additional_context' });
  };
  
  return (
    <div>
      {messages.map(msg => (
        <div key={msg.id}>{msg.content}</div>
      ))}
    </div>
  );
};
```

#### `useAIInsights(data, refreshInterval)`
Insights automáticos baseados em dados:

```tsx
const InsightsPanel = ({ userData }) => {
  const { insights, loading, refresh } = useAIInsights(userData, 30000);
  
  return (
    <div>
      <button onClick={refresh}>Atualizar Insights</button>
      {insights.map(insight => (
        <div key={insight.title}>
          <h4>{insight.title}</h4>
          <p>{insight.description}</p>
        </div>
      ))}
    </div>
  );
};
```

#### `useProductivityAnalysis(userId, timeframe)`
Análise de produtividade:

```tsx
const ProductivityDashboard = ({ userId }) => {
  const { analysis, trends, loading } = useProductivityAnalysis(userId, '7d');
  
  return (
    <div>
      <h3>Score: {Math.round(analysis?.overallScore * 100)}</h3>
      <div>Tarefas: {analysis?.tasksCompleted}</div>
      <div>Foco: {analysis?.focusTime}</div>
    </div>
  );
};
```

### Outros Hooks

- `useSmartAutocomplete(input, category)`: Autocomplete inteligente
- `useContextualAssistant(userId)`: Assistente contextual
- `usePersonalizedRecommendations(userId)`: Recomendações personalizadas
- `useWellbeingMonitor(userId)`: Monitoramento de bem-estar
- `useSmartCache(key, fetcher, ttl)`: Cache inteligente

## 🎨 Componentes React Inteligentes

### Componentes Disponíveis

#### `<IntelligentChat userId={string} />`
Chat completo com análise de sentimento:

```tsx
import { IntelligentChat } from '../components/AIComponents';

<IntelligentChat userId="user123" />
```

**Funcionalidades:**
- Interface de chat responsiva
- Análise de sentimento em tempo real
- Indicador visual de emoções
- Histórico de conversas
- Loading states e tratamento de erros

#### `<AIInsightsPanel data={any} />`
Painel de insights automáticos:

```tsx
<AIInsightsPanel data={userProductivityData} />
```

**Funcionalidades:**
- Insights gerados automaticamente
- Categorização por tipo e prioridade
- Ações sugeridas
- Atualização em tempo real

#### `<ProductivityDashboard userId={string} />`
Dashboard de produtividade:

```tsx
<ProductivityDashboard userId="user123" />
```

**Funcionalidades:**
- Score visual de produtividade
- Métricas principais
- Tendências e comparações
- Filtros por período

#### `<RecommendationsPanel userId={string} />`
Painel de recomendações personalizadas:

```tsx
<RecommendationsPanel userId="user123" />
```

**Funcionalidades:**
- Recomendações baseadas em IA
- Marcação de recomendações usadas
- Categorização automática
- Feedback de utilização

#### `<SentimentIndicator text={string} />`
Indicador de sentimento:

```tsx
<SentimentIndicator text={userInput} />
```

**Funcionalidades:**
- Análise em tempo real
- Indicador visual colorido
- Percentual de confiança
- Debounce automático

## 📊 Sistema de Relatórios Inteligentes

### Funcionalidades

- **Relatórios Automáticos**: Geração semanal/mensal automática
- **Análise com IA**: Insights narrativos gerados por LLM
- **Métricas Avançadas**: Produtividade, bem-estar, tendências
- **Recomendações Acionáveis**: Sugestões específicas e práticas
- **Formatos Múltiplos**: JSON, PDF, HTML

### Uso Básico

```python
from intelligent_reports import IntelligentReportGenerator
from abacus_client import AbacusClient
from contextual_memory import ContextualMemorySystem

# Inicializar componentes
abacus = AbacusClient()
memory = ContextualMemorySystem()
generator = IntelligentReportGenerator(abacus, memory)

# Gerar relatório semanal
report = await generator.generate_weekly_report("user123")

print(f"Score de Produtividade: {report.productivity_score:.2f}")
print(f"Score de Bem-estar: {report.wellbeing_score:.2f}")
print(f"Insights: {len(report.insights)}")
print(f"Recomendações: {len(report.recommendations)}")

# Salvar relatório
filename = generator.save_report(report, format="json")
```

### Tipos de Relatórios

#### Relatório Semanal
- Resumo executivo da semana
- Métricas principais
- Insights e padrões identificados
- Recomendações para próxima semana
- Comparação com semanas anteriores

#### Relatório Mensal
- Visão geral do mês
- Análise detalhada por semana
- Conquistas e desafios
- Insights estratégicos
- Plano para próximo mês

#### Relatório de Projeto
- Status atual do projeto
- Performance da equipe
- Riscos e oportunidades
- Próximos passos

### Personalização

```python
# Templates personalizados
custom_template = """
Analise os dados e gere um relatório focado em:
1. Eficiência energética
2. Qualidade do sono
3. Impacto no trabalho

Dados: {data}
Contexto: {context}
"""

# Usar template personalizado
generator.report_templates["custom"] = custom_template
```

## 🚀 Instalação e Configuração

### 1. Dependências

```bash
# Instalar dependências da Fase 2
pip install -r requirements_fase2.txt

# Principais dependências:
# - sentence-transformers: Embeddings vetoriais
# - faiss-cpu: Busca vetorial eficiente
# - numpy: Computação numérica
# - aiohttp: Requisições assíncronas
```

### 2. Configuração de Ambiente

```bash
# Adicionar ao .env
EMBEDDING_MODEL=all-MiniLM-L6-v2
MEMORY_MAX_ITEMS=10000
MEMORY_CACHE_TTL=300
REPORTS_AUTO_GENERATE=true
REPORTS_SCHEDULE=weekly
```

### 3. Inicialização

```python
# Inicializar sistemas
memory_system = ContextualMemorySystem()
abacus_client = AbacusClient()
report_generator = IntelligentReportGenerator(abacus_client, memory_system)

# Carregar dados existentes
memory_system.load_memory()
```

## 🧪 Testes e Validação

### Teste Automático

```bash
# Executar todos os testes da Fase 2
python test_fase2.py
```

### Testes Individuais

#### Teste de Memória Contextual

```python
# Teste básico
memory = ContextualMemorySystem()
memory_id = memory.add_memory("Teste de memória", "user123", "test")
results = memory.search_memory("teste", user_id="user123")
assert len(results) > 0
```

#### Teste de Relatórios

```python
# Teste de geração
generator = IntelligentReportGenerator(abacus_client, memory_system)
report = await generator.generate_weekly_report("user123")
assert report.productivity_score >= 0.0
assert report.wellbeing_score >= 0.0
```

#### Teste de Hooks React

```bash
# Verificar estrutura dos arquivos
ls frontend/hooks/useAI.ts
ls frontend/components/AIComponents.tsx

# Verificar exports
grep -n "export" frontend/hooks/useAI.ts
```

## 📈 Métricas e Monitoramento

### Métricas de Performance

- **Latência de busca**: < 100ms para busca semântica
- **Precisão de embeddings**: > 85% de relevância
- **Cache hit rate**: > 70% para consultas repetidas
- **Tempo de geração de relatórios**: < 30s

### Monitoramento

```python
# Estatísticas da memória
stats = memory_system.get_stats()
print(f"Total de itens: {stats['total_items']}")
print(f"Cache hit rate: {stats.get('cache_hit_rate', 0):.1f}%")

# Estatísticas do cliente Abacus
client_stats = abacus_client.get_stats()
print(f"Requests feitos: {client_stats['requests_made']}")
print(f"Tokens usados: {client_stats['total_tokens']}")
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. "sentence-transformers não encontrado"
```bash
pip install sentence-transformers
# Ou para CPU apenas:
pip install sentence-transformers[cpu]
```

#### 2. "FAISS não instalado"
```bash
# Para CPU:
pip install faiss-cpu

# Para GPU (se disponível):
pip install faiss-gpu
```

#### 3. "Embeddings muito lentos"
```python
# Usar modelo menor
memory = ContextualMemorySystem(model_name='all-MiniLM-L6-v2')

# Ou usar cache mais agressivo
memory = ContextualMemorySystem(cache_ttl=3600)  # 1 hora
```

#### 4. "Memória crescendo muito"
```python
# Reduzir limite de itens
memory = ContextualMemorySystem(max_items=5000)

# Ou limpar manualmente
memory._cleanup_memory()
```

#### 5. "Relatórios muito genéricos"
```python
# Adicionar mais contexto
context = memory.get_user_context(user_id, days=30)  # Mais histórico

# Ou personalizar templates
generator.report_templates["weekly"] = custom_template
```

## 📚 Exemplos Avançados

### Integração Completa

```tsx
// Componente React completo
import React from 'react';
import {
  IntelligentChat,
  AIInsightsPanel,
  ProductivityDashboard,
  RecommendationsPanel
} from '../components/AIComponents';

const BestStagDashboard = ({ userId }) => {
  const [productivityData, setProductivityData] = useState(null);
  
  useEffect(() => {
    // Carregar dados de produtividade
    fetchProductivityData(userId).then(setProductivityData);
  }, [userId]);
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <IntelligentChat userId={userId} />
      <ProductivityDashboard userId={userId} />
      <AIInsightsPanel data={productivityData} />
      <RecommendationsPanel userId={userId} />
    </div>
  );
};
```

### Pipeline de Dados Completo

```python
# Pipeline completo de dados
async def process_user_interaction(user_id: str, message: str):
    # 1. Adicionar à memória contextual
    memory.add_memory(
        content=message,
        user_id=user_id,
        category="interaction",
        importance=0.6
    )
    
    # 2. Gerar resposta inteligente
    context = memory.get_user_context(user_id)
    response = abacus.generate_text(
        prompt=f"Contexto: {context}\nMensagem: {message}\nResposta:",
        model="gpt-4"
    )
    
    # 3. Atualizar métricas
    update_user_metrics(user_id, message, response)
    
    # 4. Gerar insights se necessário
    if should_generate_insights(user_id):
        insights = await generate_insights(user_id)
        send_insights_to_user(user_id, insights)
    
    return response
```

## 🎯 Próximos Passos

Após validar a Fase 2, prossiga para:

- **Fase 3**: Consolidação v9.1 e Documentação
  - Integração completa de todos os componentes
  - Documentação técnica abrangente
  - Testes de integração ponta a ponta
  - Preparação para deployment

---

**✅ Fase 2 Concluída com Sucesso!**

O BestStag v9.1 agora possui:
- 🧠 Memória contextual inteligente
- ⚛️ Componentes React com IA
- 📊 Relatórios automáticos
- 🎯 Recomendações personalizadas
- 📈 Análise de produtividade avançada

Pronto para a consolidação final! 🚀

