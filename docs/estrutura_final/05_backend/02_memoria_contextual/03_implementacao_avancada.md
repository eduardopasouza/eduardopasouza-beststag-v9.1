# Implementação de Camadas de Memória Contextual Avançada para BestStag

## Objetivo
Este documento detalha o planejamento e implementação de camadas avançadas de memória contextual para o BestStag, permitindo personalização profunda e continuidade conversacional entre sessões e canais.

## Arquitetura de Memória Contextual em Camadas

### Visão Geral das Camadas

1. **Memória de Curto Prazo (MCP)**
   - Contexto imediato da conversa atual
   - Alta prioridade, acesso rápido
   - Duração: Sessão atual (até 1 hora de inatividade)

2. **Memória de Médio Prazo (MMP)**
   - Contexto de interações recentes
   - Prioridade média, acesso moderado
   - Duração: 7-14 dias

3. **Memória de Longo Prazo (MLP)**
   - Informações persistentes sobre o usuário
   - Prioridade baseada em relevância, acesso indexado
   - Duração: Permanente (com arquivamento)

4. **Memória Episódica**
   - Eventos significativos e interações importantes
   - Prioridade alta para eventos marcantes
   - Duração: Permanente (com sumarização)

5. **Memória Semântica**
   - Conhecimento estruturado sobre preferências e padrões
   - Prioridade baseada em frequência de uso
   - Duração: Permanente (com atualização contínua)

### Estrutura de Dados no Airtable

#### Tabela: Memória Contextual
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Autonumber | ID único da entrada de memória |
| `user` | Link | Link para tabela Usuários |
| `type` | Single select | Tipo de memória (MCP, MMP, MLP, Episódica, Semântica) |
| `key` | Single line text | Chave de identificação da memória |
| `value` | Long text | Valor da memória (pode ser JSON) |
| `priority` | Number | Prioridade da memória (1-10) |
| `created_at` | Date & Time | Data de criação |
| `updated_at` | Date & Time | Data de atualização |
| `expires_at` | Date & Time | Data de expiração (opcional) |
| `access_count` | Number | Contador de acessos |
| `last_accessed` | Date & Time | Última vez que foi acessada |
| `embedding` | Long text | Vetor de embedding para busca semântica |
| `tags` | Multiple select | Tags para categorização |

#### Tabela: Perfil Cognitivo
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Autonumber | ID único do perfil |
| `user` | Link | Link para tabela Usuários |
| `preference_key` | Single line text | Chave da preferência |
| `preference_value` | Long text | Valor da preferência |
| `confidence` | Number | Nível de confiança (0-1) |
| `observation_count` | Number | Número de observações que levaram a esta preferência |
| `created_at` | Date & Time | Data de criação |
| `updated_at` | Date & Time | Data de atualização |

## Implementação no n8n

### 1. Sistema de Gerenciamento de Memória Contextual

```javascript
// Função principal para gerenciar memória contextual
const userId = $input.item.json.userId;
const currentMessage = $input.item.json.message || "";
const channel = $input.item.json.channel || "WhatsApp";

// Configurações
const MAX_MCP_TOKENS = 2000;  // Limite para Memória de Curto Prazo
const MAX_MMP_INTERACTIONS = 20;  // Número máximo de interações para Memória de Médio Prazo
const MCP_EXPIRY_HOURS = 1;  // Expiração da Memória de Curto Prazo em horas
const MMP_EXPIRY_DAYS = 14;  // Expiração da Memória de Médio Prazo em dias

// 1. Recuperar memórias existentes
// Código para buscar memórias do Airtable omitido por brevidade

// 2. Processar e organizar memórias por tipo
const memories = {
  shortTerm: [], // MCP
  mediumTerm: [], // MMP
  longTerm: [], // MLP
  episodic: [], // Episódica
  semantic: [] // Semântica
};

// Organizar memórias recuperadas nas categorias apropriadas
// Código omitido por brevidade

// 3. Calcular relevância para o contexto atual
function calculateRelevance(memory, currentMessage) {
  let score = memory.priority || 5;
  
  // Fatores de relevância
  const recencyFactor = getRecencyFactor(memory.updated_at);
  const semanticFactor = getSemanticSimilarity(memory.value, currentMessage);
  const usageFactor = Math.log(memory.access_count + 1) / 10;
  
  // Calcular pontuação final
  score = score * (0.4 * recencyFactor + 0.4 * semanticFactor + 0.2 * usageFactor);
  
  return Math.min(10, score);
}

// 4. Selecionar memórias mais relevantes para cada camada
const selectedMemories = {
  shortTerm: selectTopMemories(memories.shortTerm, 5),
  mediumTerm: selectTopMemories(memories.mediumTerm, 3),
  longTerm: selectTopMemories(memories.longTerm, 2),
  episodic: selectTopMemories(memories.episodic, 2),
  semantic: selectTopMemories(memories.semantic, 3)
};

// 5. Construir contexto para o modelo de IA
let contextPrompt = "";

// Adicionar memória semântica (preferências e informações do usuário)
if (selectedMemories.semantic.length > 0) {
  contextPrompt += "Informações importantes sobre o usuário:\n";
  selectedMemories.semantic.forEach(memory => {
    contextPrompt += `- ${memory.key}: ${memory.value}\n`;
  });
  contextPrompt += "\n";
}

// Adicionar memória episódica (eventos importantes)
if (selectedMemories.episodic.length > 0) {
  contextPrompt += "Eventos importantes a lembrar:\n";
  selectedMemories.episodic.forEach(memory => {
    contextPrompt += `- ${memory.value}\n`;
  });
  contextPrompt += "\n";
}

// Adicionar memória de longo prazo
if (selectedMemories.longTerm.length > 0) {
  contextPrompt += "Contexto de longo prazo:\n";
  selectedMemories.longTerm.forEach(memory => {
    contextPrompt += `- ${memory.value}\n`;
  });
  contextPrompt += "\n";
}

// Adicionar memória de médio prazo
if (selectedMemories.mediumTerm.length > 0) {
  contextPrompt += "Interações recentes relevantes:\n";
  selectedMemories.mediumTerm.forEach(memory => {
    contextPrompt += `- ${memory.value}\n`;
  });
  contextPrompt += "\n";
}

// Adicionar memória de curto prazo (conversa atual)
if (selectedMemories.shortTerm.length > 0) {
  contextPrompt += "Conversa atual:\n";
  selectedMemories.shortTerm.forEach(memory => {
    contextPrompt += `${memory.value}\n`;
  });
}

// 6. Preparar dados para atualização de memória após resposta
const memoryUpdateData = {
  userId,
  currentMessage,
  channel,
  timestamp: new Date().toISOString()
};

return {
  contextPrompt,
  memoryUpdateData,
  selectedMemories
};
```

### 2. Sistema de Atualização de Memória

```javascript
// Função para atualizar memória após interação
const userId = $input.item.json.userId;
const userMessage = $input.item.json.userMessage;
const aiResponse = $input.item.json.aiResponse;
const channel = $input.item.json.channel;
const timestamp = new Date().toISOString();

// 1. Atualizar Memória de Curto Prazo
const mcpEntry = {
  user: userId,
  type: "MCP",
  key: `conversation_${timestamp}`,
  value: `Usuário: ${userMessage}\nBestStag: ${aiResponse}`,
  priority: 10,
  created_at: timestamp,
  updated_at: timestamp,
  expires_at: new Date(Date.now() + 3600000).toISOString(), // 1 hora
  access_count: 1,
  last_accessed: timestamp,
  tags: ["conversation"]
};

// 2. Analisar para possível Memória de Médio Prazo
const shouldCreateMMP = analyzeForMMP(userMessage, aiResponse);
let mmpEntry = null;

if (shouldCreateMMP) {
  mmpEntry = {
    user: userId,
    type: "MMP",
    key: `interaction_${timestamp}`,
    value: summarizeInteraction(userMessage, aiResponse),
    priority: 7,
    created_at: timestamp,
    updated_at: timestamp,
    expires_at: new Date(Date.now() + 14 * 24 * 3600000).toISOString(), // 14 dias
    access_count: 1,
    last_accessed: timestamp,
    tags: detectTags(userMessage, aiResponse)
  };
}

// 3. Analisar para possível Memória Episódica
const isSignificantEvent = detectSignificantEvent(userMessage, aiResponse);
let episodicEntry = null;

if (isSignificantEvent) {
  episodicEntry = {
    user: userId,
    type: "Episodica",
    key: `event_${timestamp}`,
    value: createEventSummary(userMessage, aiResponse),
    priority: 8,
    created_at: timestamp,
    updated_at: timestamp,
    expires_at: null, // Não expira
    access_count: 1,
    last_accessed: timestamp,
    tags: ["significant_event"].concat(detectTags(userMessage, aiResponse))
  };
}

// 4. Atualizar Memória Semântica (preferências e informações)
const extractedPreferences = extractPreferences(userMessage, aiResponse);
const semanticEntries = [];

if (extractedPreferences.length > 0) {
  extractedPreferences.forEach(pref => {
    semanticEntries.push({
      user: userId,
      type: "Semantica",
      key: pref.key,
      value: pref.value,
      priority: 6,
      created_at: timestamp,
      updated_at: timestamp,
      expires_at: null, // Não expira
      access_count: 1,
      last_accessed: timestamp,
      tags: ["preference", pref.category]
    });
  });
}

// 5. Preparar entradas para salvar no Airtable
const entriesToSave = [mcpEntry];
if (mmpEntry) entriesToSave.push(mmpEntry);
if (episodicEntry) entriesToSave.push(episodicEntry);
semanticEntries.forEach(entry => entriesToSave.push(entry));

// 6. Atualizar Perfil Cognitivo
const cognitiveUpdates = updateCognitiveProfile(userId, extractedPreferences);

return {
  memoryEntries: entriesToSave,
  cognitiveUpdates
};

// Funções auxiliares (implementações simplificadas)

function analyzeForMMP(userMessage, aiResponse) {
  // Determina se a interação deve ser salva na memória de médio prazo
  const combinedText = userMessage + " " + aiResponse;
  
  // Critérios para salvar na MMP
  const containsQuestion = userMessage.includes("?");
  const containsImportantKeywords = /\b(lembrar|importante|não esquecer|anotar|salvar)\b/i.test(combinedText);
  const isLongInteraction = combinedText.length > 200;
  
  return containsQuestion || containsImportantKeywords || isLongInteraction;
}

function summarizeInteraction(userMessage, aiResponse) {
  // Cria um resumo da interação para MMP
  // Implementação simplificada
  return `Usuário perguntou sobre "${userMessage.substring(0, 50)}..." e recebeu resposta relacionada a ${detectMainTopic(aiResponse)}.`;
}

function detectSignificantEvent(userMessage, aiResponse) {
  // Detecta se a interação representa um evento significativo
  const combinedText = userMessage + " " + aiResponse;
  
  // Palavras-chave que indicam eventos significativos
  const significantKeywords = [
    "marcar", "agendar", "reunião", "importante", "prazo", "deadline",
    "entrega", "cliente", "contrato", "projeto", "proposta"
  ];
  
  // Verifica se pelo menos 2 palavras-chave estão presentes
  let keywordCount = 0;
  significantKeywords.forEach(keyword => {
    if (combinedText.toLowerCase().includes(keyword)) keywordCount++;
  });
  
  return keywordCount >= 2;
}

function createEventSummary(userMessage, aiResponse) {
  // Cria um resumo de evento para memória episódica
  // Implementação simplificada
  return `Evento: ${detectEventType(userMessage, aiResponse)} - ${extractEventDetails(userMessage, aiResponse)}`;
}

function extractPreferences(userMessage, aiResponse) {
  // Extrai preferências do usuário da interação
  // Implementação simplificada
  const preferences = [];
  
  // Detectar preferências de comunicação
  if (/\b(prefiro|gosto|melhor)\b.*\b(email|whatsapp|mensagem|ligação)\b/i.test(userMessage)) {
    preferences.push({
      key: "communication_preference",
      value: extractCommunicationPreference(userMessage),
      category: "communication"
    });
  }
  
  // Detectar preferências de horário
  if (/\b(manhã|tarde|noite|horário)\b/i.test(userMessage)) {
    preferences.push({
      key: "time_preference",
      value: extractTimePreference(userMessage),
      category: "scheduling"
    });
  }
  
  return preferences;
}

function updateCognitiveProfile(userId, extractedPreferences) {
  // Atualiza o perfil cognitivo com novas preferências
  const updates = [];
  
  extractedPreferences.forEach(pref => {
    updates.push({
      user: userId,
      preference_key: pref.key,
      preference_value: pref.value,
      confidence: 0.7, // Valor inicial
      observation_count: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    });
  });
  
  return updates;
}

function detectTags(userMessage, aiResponse) {
  // Detecta tags relevantes para categorização
  const tags = [];
  const combinedText = userMessage + " " + aiResponse;
  
  // Categorias principais
  if (/\b(tarefa|task|todo|fazer|pendente)\b/i.test(combinedText)) tags.push("tarefa");
  if (/\b(agenda|calendário|evento|reunião|appointment)\b/i.test(combinedText)) tags.push("agenda");
  if (/\b(email|mensagem|comunicação)\b/i.test(combinedText)) tags.push("comunicacao");
  if (/\b(cliente|customer|contato)\b/i.test(combinedText)) tags.push("cliente");
  if (/\b(projeto|project|trabalho)\b/i.test(combinedText)) tags.push("projeto");
  
  return tags;
}
```

### 3. Sistema de Busca Semântica de Memória

```javascript
// Função para busca semântica de memória
const userId = $input.item.json.userId;
const query = $input.item.json.query;
const maxResults = $input.item.json.maxResults || 5;

// 1. Gerar embedding para a consulta
// Nota: Requer integração com API de embeddings (OpenAI, etc.)
const queryEmbedding = await generateEmbedding(query);

// 2. Buscar todas as memórias do usuário
// Código para buscar memórias do Airtable omitido por brevidade

// 3. Calcular similaridade com cada memória
const scoredMemories = memories.map(memory => {
  // Se a memória tem embedding, calcular similaridade coseno
  if (memory.embedding) {
    const similarity = calculateCosineSimilarity(queryEmbedding, JSON.parse(memory.embedding));
    return {
      ...memory,
      similarity
    };
  }
  
  // Caso contrário, usar busca de texto simples
  const textSimilarity = calculateTextSimilarity(query, memory.value);
  return {
    ...memory,
    similarity: textSimilarity
  };
});

// 4. Ordenar por similaridade e selecionar os mais relevantes
const sortedMemories = scoredMemories
  .sort((a, b) => b.similarity - a.similarity)
  .slice(0, maxResults);

// 5. Incrementar contadores de acesso para as memórias recuperadas
const memoryIds = sortedMemories.map(memory => memory.id);
// Código para atualizar contadores no Airtable omitido por brevidade

return {
  memories: sortedMemories,
  query,
  timestamp: new Date().toISOString()
};

// Funções auxiliares

async function generateEmbedding(text) {
  // Integração com API de embeddings
  // Implementação depende da API escolhida (OpenAI, etc.)
  // Retorna vetor de embedding
}

function calculateCosineSimilarity(vec1, vec2) {
  // Calcula similaridade coseno entre dois vetores
  let dotProduct = 0;
  let mag1 = 0;
  let mag2 = 0;
  
  for (let i = 0; i < vec1.length; i++) {
    dotProduct += vec1[i] * vec2[i];
    mag1 += vec1[i] * vec1[i];
    mag2 += vec2[i] * vec2[i];
  }
  
  mag1 = Math.sqrt(mag1);
  mag2 = Math.sqrt(mag2);
  
  return dotProduct / (mag1 * mag2);
}

function calculateTextSimilarity(text1, text2) {
  // Implementação simplificada de similaridade de texto
  // Baseada em palavras comuns
  const words1 = new Set(text1.toLowerCase().split(/\W+/));
  const words2 = new Set(text2.toLowerCase().split(/\W+/));
  
  let intersection = 0;
  for (const word of words1) {
    if (words2.has(word)) intersection++;
  }
  
  return intersection / (words1.size + words2.size - intersection);
}
```

## Fluxo de Trabalho Completo no n8n

### 1. Fluxo de Processamento de Mensagem com Memória Contextual Avançada

1. **Webhook recebe mensagem**
2. **Validação e extração de dados**
3. **Buscar usuário no Airtable**
4. **Sistema de Gerenciamento de Memória Contextual**
   - Recupera memórias de todas as camadas
   - Calcula relevância para o contexto atual
   - Seleciona memórias mais relevantes
   - Constrói prompt contextualizado
5. **OpenAI processa mensagem com contexto avançado**
6. **Sistema de Atualização de Memória**
   - Atualiza Memória de Curto Prazo
   - Analisa para Memória de Médio Prazo
   - Detecta eventos significativos para Memória Episódica
   - Extrai preferências para Memória Semântica
   - Atualiza Perfil Cognitivo
7. **Salvar resposta e interação no Airtable**
8. **Enviar resposta ao usuário**

### 2. Fluxo de Recuperação de Memória Específica

1. **Webhook recebe comando de busca**
   - Ex: `/lembrar reunião cliente`
2. **Sistema de Busca Semântica de Memória**
   - Gera embedding para a consulta
   - Busca memórias relevantes
   - Calcula similaridade
   - Seleciona resultados mais relevantes
3. **Formatar resultados da busca**
4. **Enviar resposta ao usuário**

## Estratégias de Otimização

### 1. Gerenciamento de Tokens

Para otimizar o uso de tokens nos modelos de IA:

1. **Sumarização Progressiva**
   - Memórias de médio e longo prazo são sumarizadas
   - Detalhes menos importantes são removidos com o tempo
   - Preservação de informações essenciais

2. **Priorização Dinâmica**
   - Ajuste automático de prioridades baseado em padrões de uso
   - Memórias frequentemente acessadas recebem prioridade maior
   - Decaimento natural de prioridade com o tempo

3. **Compressão Semântica**
   - Representação de memórias como embeddings
   - Agrupamento de memórias similares
   - Eliminação de redundâncias

### 2. Arquivamento e Recuperação

Para gerenciar o crescimento do banco de dados:

1. **Arquivamento Automático**
   - Memórias de médio prazo não acessadas são arquivadas após o período de expiração
   - Memórias arquivadas são mantidas em formato comprimido
   - Metadados são preservados para busca

2. **Recuperação Sob Demanda**
   - Memórias arquivadas podem ser recuperadas quando relevantes
   - Sistema de busca inclui memórias arquivadas quando necessário
   - Recuperação baseada em similaridade semântica

## Métricas de Avaliação

Para avaliar a eficácia do sistema de memória contextual:

1. **Relevância Contextual**
   - Porcentagem de respostas que utilizam corretamente o contexto
   - Avaliação manual de amostras de conversas

2. **Continuidade Conversacional**
   - Capacidade de retomar conversas anteriores
   - Tempo médio de "memória" efetiva entre sessões

3. **Personalização**
   - Precisão na aplicação de preferências do usuário
   - Adaptação a padrões de uso individuais

4. **Performance**
   - Tempo de recuperação de memória
   - Uso de recursos (tokens, armazenamento)
   - Latência de resposta

## Próximos Passos

1. **Implementação Inicial**
   - Configurar tabelas no Airtable
   - Implementar Sistema de Gerenciamento de Memória Contextual
   - Integrar com o fluxo existente

2. **Testes e Refinamento**
   - Testar com conversas reais
   - Ajustar parâmetros de relevância e prioridade
   - Otimizar uso de tokens

3. **Expansão**
   - Implementar busca semântica avançada
   - Adicionar suporte para memória multimodal (imagens, documentos)
   - Desenvolver mecanismos de aprendizado contínuo

4. **Documentação**
   - Documentar arquitetura completa
   - Criar guias de manutenção e expansão
   - Preparar materiais de treinamento
