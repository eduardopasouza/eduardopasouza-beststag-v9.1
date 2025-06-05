# Estratégia de Memória Conversacional - BestStag

## Introdução

Este documento apresenta a estratégia de memória conversacional para o BestStag, detalhando como o sistema manterá, utilizará e gerenciará o contexto das conversas com os usuários. Uma memória conversacional eficiente é fundamental para proporcionar uma experiência personalizada e contextualizada, permitindo que o assistente compreenda referências a interações anteriores e mantenha a continuidade das conversas.

## Princípios Fundamentais

A estratégia de memória conversacional do BestStag é guiada pelos seguintes princípios:

1. **Relevância Contextual**: Priorizar informações mais relevantes para o contexto atual
2. **Eficiência de Armazenamento**: Otimizar o uso de recursos sem comprometer a qualidade
3. **Privacidade e Segurança**: Proteger dados sensíveis e garantir conformidade com regulamentações
4. **Acessibilidade Rápida**: Garantir recuperação ágil de informações históricas
5. **Adaptabilidade**: Ajustar dinamicamente o nível de detalhe conforme necessidade
6. **Persistência Seletiva**: Manter informações importantes por períodos apropriados
7. **Integração Fluida**: Conectar-se harmoniosamente com outros sistemas do BestStag

## Arquitetura da Memória Conversacional

A memória conversacional do BestStag será estruturada em múltiplas camadas, cada uma com propósito, escopo e duração específicos:

### 1. Memória de Curto Prazo (Sessão Atual)

- **Propósito**: Manter o contexto imediato da conversa em andamento
- **Conteúdo**: Mensagens completas da sessão atual (últimas 10-20 interações)
- **Duração**: Durante a sessão ativa (tipicamente algumas horas)
- **Implementação**: Armazenamento temporário em Airtable ou variáveis de sessão
- **Acesso**: Incluída integralmente nos prompts para a API de IA

### 2. Memória de Médio Prazo (Histórico Recente)

- **Propósito**: Manter contexto de conversas recentes para referência
- **Conteúdo**: Resumos de conversas dos últimos dias, decisões tomadas, preferências expressas
- **Duração**: 7-30 dias, dependendo da relevância
- **Implementação**: Armazenamento em Airtable com TTL (Time-To-Live)
- **Acesso**: Incluída seletivamente nos prompts, conforme relevância para o contexto atual

### 3. Memória de Longo Prazo (Conhecimento Persistente)

- **Propósito**: Manter informações essenciais sobre o usuário e suas preferências
- **Conteúdo**: Perfil do usuário, preferências estáveis, padrões de comportamento, informações críticas
- **Duração**: Persistente (meses a anos)
- **Implementação**: Armazenamento estruturado em Airtable
- **Acesso**: Incluída como metadados essenciais em todos os prompts

### 4. Memória Episódica (Eventos Significativos)

- **Propósito**: Registrar interações ou eventos importantes para referência futura
- **Conteúdo**: Decisões críticas, solicitações importantes, feedback explícito
- **Duração**: Longa (meses a anos)
- **Implementação**: Registros específicos em Airtable com metadados de importância
- **Acesso**: Recuperada quando relevante para o contexto atual

## Sistema de Armazenamento

### Estrutura de Dados

O sistema de armazenamento será implementado principalmente no Airtable, com a seguinte estrutura:

#### 1. Tabela de Conversas

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `conversation_id` | String | Identificador único da conversa |
| `user_id` | String | Identificador do usuário |
| `start_timestamp` | DateTime | Início da conversa |
| `last_timestamp` | DateTime | Última atualização |
| `channel` | String | Canal de comunicação (WhatsApp, web, email) |
| `status` | String | Status da conversa (ativa, encerrada) |
| `summary` | Text | Resumo gerado da conversa |
| `tags` | MultiSelect | Tópicos ou categorias relevantes |
| `importance` | Number | Nível de importância (1-5) |

#### 2. Tabela de Mensagens

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `message_id` | String | Identificador único da mensagem |
| `conversation_id` | String | Referência à conversa |
| `timestamp` | DateTime | Momento da mensagem |
| `role` | String | Origem da mensagem (usuário, assistente) |
| `content` | Text | Conteúdo da mensagem |
| `intent` | String | Intenção classificada |
| `entities` | JSON | Entidades extraídas |
| `importance` | Number | Relevância da mensagem (1-5) |
| `ttl` | DateTime | Data de expiração para retenção |

#### 3. Tabela de Perfil de Memória

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `user_id` | String | Identificador do usuário |
| `preference_key` | String | Tipo de preferência ou informação |
| `preference_value` | Text | Valor da preferência |
| `confidence` | Number | Nível de confiança (0-1) |
| `last_updated` | DateTime | Última atualização |
| `source` | String | Origem da informação (explícita, inferida) |
| `expiration` | DateTime | Data de validade da informação |

#### 4. Tabela de Eventos Significativos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `event_id` | String | Identificador único do evento |
| `user_id` | String | Identificador do usuário |
| `timestamp` | DateTime | Momento do evento |
| `event_type` | String | Tipo de evento (decisão, feedback, etc.) |
| `description` | Text | Descrição do evento |
| `related_entities` | JSON | Entidades relacionadas |
| `importance` | Number | Nível de importância (1-5) |

### Implementação no Ambiente No-Code/Low-Code

#### Usando Airtable:

1. **Configuração de Bases**:
   - Base principal para armazenamento estruturado
   - Relações entre tabelas para navegação eficiente
   - Campos calculados para métricas e indicadores

2. **Automações Internas**:
   - Gatilhos para atualização de timestamps
   - Cálculo automático de importância
   - Expiração e arquivamento de registros antigos

#### Usando Make/n8n:

1. **Fluxos de Processamento**:
   - Captura e registro de novas mensagens
   - Atualização de perfil de memória
   - Geração de resumos periódicos

2. **Integrações**:
   - Conexão com WhatsApp para registro de mensagens
   - Integração com APIs de IA para análise e resumo
   - Sincronização com outros sistemas do BestStag

## Mecanismos de Sumarização

Para manter a eficiência do armazenamento e uso de contexto, implementaremos técnicas avançadas de sumarização:

### 1. Sumarização Incremental

Resumos são atualizados progressivamente à medida que a conversa evolui:

1. Iniciar com resumo vazio
2. Após cada N mensagens, atualizar o resumo incorporando novas informações
3. Priorizar informações recentes e relevantes
4. Manter consistência com resumos anteriores

### 2. Sumarização Multi-nível

Diferentes níveis de detalhe para diferentes propósitos:

| Nível | Tamanho | Uso | Exemplo |
|-------|---------|-----|---------|
| Ultra-conciso | 1-2 frases | Metadados, tags | "Discussão sobre agendamento de reunião com cliente ABC para próxima semana" |
| Conciso | Parágrafo | Contexto rápido | "Usuário solicitou agendamento de reunião com cliente ABC. Discutidas opções para terça ou quarta-feira próxima. Preferência por período da manhã. Pendente confirmação do cliente." |
| Detalhado | Múltiplos parágrafos | Recuperação completa | Resumo extenso com pontos principais, decisões, próximos passos e contexto completo |

### 3. Sumarização Temática

Organização por tópicos ou temas para facilitar recuperação contextual:

- Identificar temas principais da conversa
- Agrupar informações relacionadas
- Criar índice temático para navegação
- Facilitar recuperação de contexto específico

### Implementação da Sumarização

#### Prompt para Sumarização Incremental

```
[DEFINIÇÃO DE PAPEL]
Você é um sistema especializado em resumir conversas para o assistente virtual BestStag.

[CONTEXTO]
Resumo atual da conversa: {resumo_existente}

Novas mensagens a incorporar:
{novas_mensagens}

[INSTRUÇÕES ESPECÍFICAS]
Atualize o resumo existente incorporando as informações relevantes das novas mensagens.
1. Mantenha a consistência com o resumo anterior
2. Priorize informações acionáveis e decisões
3. Inclua detalhes sobre entidades mencionadas (pessoas, datas, valores)
4. Preserve o contexto temporal (quando eventos ocorreram ou ocorrerão)
5. Limite o resumo a aproximadamente {tamanho_alvo} palavras

[FORMATO DE SAÍDA]
Um texto coeso que funcione como resumo atualizado da conversa completa.
```

#### Fluxo de Sumarização em Make/n8n

```
[Novas Mensagens] → [Verificar Contagem] → [Se atingir limiar] → [Recuperar Resumo Atual]
                                                                      ↓
[Atualizar Registro] ← [Armazenar Novo Resumo] ← [Chamar API de Sumarização]
```

## Estratégia de Recuperação de Contexto

A recuperação eficiente de contexto relevante é crucial para manter conversas naturais e personalizadas:

### 1. Recuperação Baseada em Relevância

Implementaremos um sistema que seleciona informações contextuais com base em:

- **Recência**: Priorizar informações mais recentes
- **Similaridade Semântica**: Selecionar contexto semanticamente relacionado à consulta atual
- **Importância Marcada**: Priorizar informações explicitamente marcadas como importantes
- **Referências Explícitas**: Identificar menções a conversas ou decisões anteriores

### 2. Embeddings para Busca Semântica

Utilizaremos embeddings vetoriais para busca eficiente de contexto relevante:

1. Gerar embeddings para mensagens e resumos de conversas
2. Armazenar vetores em estrutura adequada (pode ser implementado em Airtable)
3. Para cada nova mensagem, calcular similaridade com histórico
4. Recuperar contexto mais similar para inclusão no prompt

### 3. Sistema de Referência Cruzada

Implementar mecanismo para conectar informações relacionadas:

- Vincular menções a entidades comuns (pessoas, projetos, eventos)
- Conectar conversas sobre o mesmo tópico
- Relacionar decisões com suas implementações
- Rastrear evolução de tópicos ao longo do tempo

### Implementação da Recuperação

#### Pseudocódigo para Recuperação de Contexto

```javascript
async function recuperarContexto(mensagemAtual, perfilUsuario) {
  // Extrair entidades e tópicos da mensagem atual
  const { entidades, topicos } = analisarMensagem(mensagemAtual);
  
  // Recuperar contexto de curto prazo (sessão atual)
  const contextoCurtoPrazo = await obterUltimasMensagens(perfilUsuario.id, 10);
  
  // Gerar embedding da mensagem atual
  const embeddingAtual = await gerarEmbedding(mensagemAtual);
  
  // Buscar conversas semanticamente similares
  const conversasSimilares = await buscarConversasSimilares(
    perfilUsuario.id,
    embeddingAtual,
    topicos,
    5 // limite de conversas
  );
  
  // Recuperar eventos significativos relacionados
  const eventosRelacionados = await buscarEventosRelacionados(
    perfilUsuario.id,
    entidades,
    3 // limite de eventos
  );
  
  // Compilar contexto completo
  return {
    perfilUsuario,
    contextoCurtoPrazo,
    resumosConversasSimilares: conversasSimilares.map(c => c.resumo),
    eventosSignificativos: eventosRelacionados,
    entidadesRelevantes: entidades
  };
}
```

#### Fluxo em Make/n8n

```
[Nova Mensagem] → [Extrair Entidades/Tópicos] → [Gerar Embedding]
                                                      ↓
[Recuperar Mensagens Recentes] → [Buscar Conversas Similares] → [Buscar Eventos Relacionados]
                                                                      ↓
[Compilar Contexto Completo] → [Preparar Prompt para API de IA]
```

## Política de Retenção e Privacidade

### Diretrizes de Retenção

Implementaremos uma política de retenção em camadas, balanceando utilidade e privacidade:

| Tipo de Dado | Período de Retenção | Justificativa |
|--------------|---------------------|---------------|
| Mensagens completas | 30 dias | Contexto recente e resolução de problemas |
| Resumos de conversas | 180 dias | Referência de médio prazo |
| Perfil de preferências | Até solicitação de exclusão | Personalização contínua |
| Eventos significativos | 1 ano | Referência para decisões importantes |
| Logs de sistema | 90 dias | Diagnóstico técnico |

### Anonimização e Minimização

Para proteger a privacidade dos usuários:

1. **Minimização de Dados**:
   - Armazenar apenas informações necessárias
   - Descartar detalhes supérfluos após processamento
   - Resumir em vez de manter conteúdo completo

2. **Anonimização Seletiva**:
   - Mascarar informações sensíveis em armazenamento de longo prazo
   - Substituir identificadores diretos por tokens
   - Separar dados de identificação de conteúdo conversacional

3. **Agregação**:
   - Converter dados individuais em padrões agregados quando possível
   - Utilizar estatísticas em vez de exemplos específicos
   - Preservar insights sem preservar detalhes pessoais

### Controles de Acesso

Implementar controles rigorosos para acesso aos dados de memória:

1. **Segregação de Dados**:
   - Separar dados por usuário
   - Implementar isolamento lógico
   - Prevenir acesso cruzado entre contas

2. **Autenticação e Autorização**:
   - Exigir autenticação para acesso a qualquer dado
   - Limitar acesso baseado em funções e necessidade
   - Registrar todos os acessos para auditoria

3. **Transparência**:
   - Informar usuários sobre dados armazenados
   - Oferecer opções de visualização e exclusão
   - Documentar claramente políticas de retenção

### Implementação de Privacidade

#### Pseudocódigo para Anonimização

```javascript
function anonimizarMensagem(mensagem, nivel) {
  switch(nivel) {
    case 'baixo':
      // Manter a maioria do conteúdo, mascarar apenas dados sensíveis óbvios
      return mascaraDadosSensiveis(mensagem, ['cartao_credito', 'senha', 'documento']);
      
    case 'medio':
      // Substituir entidades específicas por categorias
      const entidades = extrairEntidades(mensagem);
      return substituirEntidadesPorCategorias(mensagem, entidades);
      
    case 'alto':
      // Manter apenas a intenção e tópicos gerais
      const { intencao, topicos } = analisarMensagem(mensagem);
      return `Mensagem sobre ${topicos.join(', ')} com intenção de ${intencao}`;
  }
}
```

#### Fluxo de Expiração em Make/n8n

```
[Agendamento Diário] → [Buscar Registros Expirados] → [Para Cada Registro]
                                                            ↓
                                                    [Verificar Política]
                                                            ↓
                                                  [Excluir ou Anonimizar]
```

## Integração com Outros Componentes

A memória conversacional se integrará com outros componentes do BestStag:

### 1. Integração com Classificação de Intenções

- Utilizar histórico para melhorar precisão da classificação
- Manter registro de intenções anteriores para detectar padrões
- Identificar mudanças de contexto ou tópico

### 2. Integração com Engenharia de Prompts

- Fornecer contexto relevante para inclusão em prompts
- Ajustar nível de detalhe baseado em necessidade do prompt
- Priorizar informações conforme tipo de interação

### 3. Integração com Otimização de Custos

- Implementar recuperação seletiva para reduzir tamanho de prompts
- Utilizar cache de respostas para consultas recorrentes
- Ajustar dinamicamente quantidade de contexto baseado em complexidade

### 4. Integração com WhatsApp Business API

- Sincronizar histórico de mensagens do WhatsApp
- Manter consistência entre diferentes sessões
- Preservar contexto mesmo após interrupções

## Métricas e Monitoramento

Para avaliar a eficácia da memória conversacional:

### 1. Métricas de Qualidade

- **Precisão Contextual**: Frequência com que o sistema utiliza corretamente o contexto
- **Taxa de Recuperação**: Capacidade de encontrar informações relevantes no histórico
- **Continuidade Percebida**: Avaliação da naturalidade das transições entre sessões

### 2. Métricas de Eficiência

- **Tempo de Recuperação**: Latência para acessar informações históricas
- **Uso de Armazenamento**: Volume de dados mantidos por usuário
- **Eficiência de Tokens**: Redução no uso de tokens através de sumarização

### 3. Métricas de Privacidade

- **Taxa de Retenção**: Percentual de dados retidos vs. descartados
- **Nível de Anonimização**: Eficácia das técnicas de anonimização
- **Conformidade**: Aderência a políticas de privacidade e regulamentações

## Protótipo de Implementação

### Exemplo de Fluxo Completo em Make/n8n

1. **Recebimento de Mensagem**:
   - Trigger: Nova mensagem do WhatsApp
   - Ação: Registrar mensagem na tabela de Mensagens
   - Ação: Atualizar timestamp da conversa

2. **Processamento de Contexto**:
   - Ação: Recuperar mensagens recentes
   - Ação: Verificar necessidade de sumarização
   - Condicional: Se atingir limiar, gerar/atualizar resumo

3. **Preparação de Prompt**:
   - Ação: Recuperar perfil do usuário
   - Ação: Buscar contexto relevante
   - Ação: Compilar prompt com contexto selecionado

4. **Processamento de Resposta**:
   - Ação: Enviar prompt para API de IA
   - Ação: Registrar resposta na tabela de Mensagens
   - Ação: Extrair insights para atualização de perfil

5. **Manutenção de Memória**:
   - Agendamento: Diariamente
   - Ação: Identificar registros expirados
   - Ação: Aplicar política de retenção (excluir ou anonimizar)

### Exemplo de Estrutura de Prompt com Contexto

```
[DEFINIÇÃO DE PAPEL]
Você é o assistente virtual BestStag, ajudando {nome_usuario}, um {profissao}.

[CONTEXTO DO USUÁRIO]
Preferências conhecidas:
- {preferencia_1}
- {preferencia_2}
- {preferencia_3}

[CONTEXTO DA CONVERSA ATUAL]
{ultimas_5_mensagens}

[CONTEXTO HISTÓRICO RELEVANTE]
Resumo de conversa anterior sobre {topico_relacionado}:
{resumo_conversa_relacionada}

Decisão importante registrada em {data_evento}:
{descricao_evento_significativo}

[INSTRUÇÕES ESPECÍFICAS]
{instrucoes_baseadas_em_intencao}

[RESTRIÇÕES]
{restricoes_e_limitacoes}
```

## Considerações Técnicas

### Limitações do Ambiente No-Code/Low-Code

1. **Capacidade de Armazenamento**:
   - Airtable tem limites por base/tabela
   - Implementar estratégia de arquivamento para histórico antigo
   - Considerar múltiplas bases para diferentes tipos de memória

2. **Complexidade de Consultas**:
   - Limitações nas capacidades de consulta do Airtable
   - Implementar lógica adicional em Make/n8n quando necessário
   - Utilizar campos calculados e fórmulas para otimizar

3. **Latência**:
   - Considerar tempo de resposta em integrações múltiplas
   - Implementar cache para dados frequentemente acessados
   - Otimizar fluxos para minimizar chamadas desnecessárias

### Escalabilidade

Para suportar crescimento no volume de usuários e interações:

1. **Particionamento de Dados**:
   - Separar dados por períodos (mensal, trimestral)
   - Implementar arquivamento automático
   - Utilizar múltiplas bases para diferentes segmentos de usuários

2. **Otimização de Consultas**:
   - Criar índices e campos de busca otimizados
   - Implementar cache para consultas frequentes
   - Utilizar técnicas de paginação para grandes conjuntos de dados

3. **Processamento Assíncrono**:
   - Executar sumarizações em background
   - Implementar filas para processamento de picos
   - Priorizar operações críticas para tempo de resposta

## Próximos Passos

1. **Validação de Conceito**: Implementar protótipo básico para testar fluxos
2. **Refinamento de Esquemas**: Ajustar estrutura de dados baseado em testes iniciais
3. **Desenvolvimento de Prompts**: Criar e testar prompts para sumarização
4. **Testes de Integração**: Validar conexão com outros componentes
5. **Avaliação de Performance**: Medir tempos de resposta e eficiência
6. **Documentação Técnica**: Preparar guias detalhados de implementação

## Conclusão

A estratégia de memória conversacional apresentada fornece uma base sólida para o BestStag oferecer interações contextualizadas e personalizadas. A abordagem em camadas, combinando diferentes tipos de memória e técnicas de sumarização, permite um equilíbrio entre riqueza contextual e eficiência operacional.

Esta estratégia será refinada continuamente com base em feedback e dados de uso real, garantindo que o BestStag mantenha conversas cada vez mais naturais e eficazes com seus usuários, enquanto respeita princípios de privacidade e otimização de recursos.
