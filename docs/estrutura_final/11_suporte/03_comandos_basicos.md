# Guia de Implementação - Fase 4: Comandos Básicos

## 🎯 Objetivo

Implementar um sistema robusto de comandos básicos que permite aos usuários interagir com o BestStag de forma estruturada e eficiente, oferecendo funcionalidades essenciais de produtividade através de comandos intuitivos.

## 📦 Comandos Implementados

### 1. Sistema de Detecção Inteligente
**Funcionalidade**: Detecta comandos tanto explícitos (iniciados com /) quanto implícitos (palavras-chave na conversa natural).

**Características**:
- Detecção de comandos diretos (/ajuda, /status, etc.)
- Reconhecimento de aliases (help, ajuda, h)
- Detecção implícita em conversas naturais
- Extração automática de parâmetros e flags

### 2. Comandos de Sistema

#### /ajuda (aliases: /help, /h, ajuda, help)
**Funcionalidade**: Mostra lista de comandos disponíveis e instruções de uso.

**Uso**:
```
/ajuda                    # Lista todos os comandos
/ajuda tarefa            # Ajuda específica para comando tarefa
```

**Características**:
- Ajuda geral com comandos organizados por categoria
- Ajuda específica para cada comando
- Exemplos práticos de uso
- Dicas de uso avançado

#### /status (aliases: /s, status, situação)
**Funcionalidade**: Mostra status atual do usuário e sistema.

**Uso**:
```
/status                  # Status completo do usuário
```

**Informações exibidas**:
- Tarefas pendentes (top 5)
- Próximos eventos (24 horas)
- Interações recentes
- Memórias importantes
- Estatísticas de produtividade

### 3. Comandos de Produtividade

#### /tarefa (aliases: /task, /t, tarefa, task, fazer)
**Funcionalidade**: Gerencia tarefas e atividades do usuário.

**Subcomandos**:
- `criar`: Cria nova tarefa
- `listar`: Lista tarefas (todas, pendentes, concluídas, hoje, atrasadas)
- `completar`: Marca tarefa como concluída
- `deletar`: Remove tarefa

**Exemplos de uso**:
```
/tarefa criar Revisar relatório mensal urgente para amanhã
/tarefa listar pendentes
/tarefa completar 1
/tarefa deletar 2
```

**Características avançadas**:
- Extração automática de prioridade (urgente, alta, média, baixa)
- Detecção de datas de vencimento (hoje, amanhã, DD/MM)
- Categorização automática por tags
- Filtros inteligentes para listagem

#### /agenda (aliases: /calendar, /cal, /a, agenda, calendário)
**Funcionalidade**: Gerencia eventos e compromissos.

**Subcomandos**:
- `criar`: Cria novo evento
- `listar`: Lista eventos por período
- `hoje`: Eventos de hoje
- `semana`: Eventos da semana

**Exemplos de uso**:
```
/agenda criar Reunião com cliente ABC amanhã às 14h na sala 201
/agenda hoje
/agenda semana
/agenda listar mês
```

**Características avançadas**:
- Extração automática de horários (14h, 14:30, 2pm)
- Detecção de datas (hoje, amanhã, dias da semana, DD/MM)
- Extração de localização (em, no, na, sala, online)
- Organização cronológica automática

### 4. Comandos de Configuração

#### /perfil (aliases: /profile, /p, perfil, profile)
**Funcionalidade**: Gerencia informações do perfil do usuário.

**Subcomandos**:
- `ver`: Exibe informações do perfil
- `editar`: Edita campos do perfil
- `preferências`: Gerencia preferências do usuário

**Exemplos de uso**:
```
/perfil ver
/perfil editar nome João Silva
/perfil editar email joao@empresa.com
/perfil preferências notificação ativar horário 9h às 18h
```

**Campos editáveis**:
- Nome, email, telefone, empresa, cargo
- Preferências de notificação
- Horário de trabalho
- Idioma e formato de data

### 5. Comandos de Análise

#### /relatório (aliases: /report, /r, relatório, report)
**Funcionalidade**: Gera relatórios de produtividade e atividades.

**Subcomandos**:
- `diário`: Relatório do dia atual
- `semanal`: Relatório da semana atual
- `mensal`: Relatório do mês atual

**Exemplos de uso**:
```
/relatório diário
/relatório semanal
/relatório mensal
```

**Métricas incluídas**:
- Tarefas concluídas vs criadas
- Eventos realizados
- Interações com o sistema
- Produtividade e tendências

## 🔧 Configuração e Implementação

### Pré-requisitos
- Workflows das Fases 1, 2 e 3 funcionando
- Estrutura completa do Airtable
- Credenciais configuradas no n8n

### Passo 1: Importar Workflow de Comandos

1. **Acessar n8n Cloud**
   ```
   URL: https://beststag25.app.n8n.cloud
   ```

2. **Importar Workflow**
   - Clique em "New Workflow"
   - Selecione "Import from file"
   - Faça upload do arquivo: `beststag_comandos_basicos.json`
   - Renomeie para: "BestStag - Comandos Básicos"

### Passo 2: Configurar Webhook

#### Webhook Principal de Comandos
```
Endpoint: /webhook/comandos/processar
Método: POST
Função: Processar e executar comandos do usuário
```

**Parâmetros de entrada**:
```json
{
  "user_id": "user_123",
  "message": "/tarefa criar Revisar relatório urgente para amanhã"
}
```

### Passo 3: Integrar com Workflow Principal

#### Modificar Workflow da Fase 1
Adicione verificação de comandos antes do processamento OpenAI:

```javascript
// Verificar se é um comando
const commandRequest = {
  user_id: userData.user_id,
  message: userData.message_body
};

const commandResponse = await fetch('https://beststag25.app.n8n.cloud/webhook/comandos/processar', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(commandRequest)
});

const commandResult = await commandResponse.json();

if (commandResult.success && commandResult.data.is_command) {
  // É um comando, retornar resposta do comando
  return commandResult.data.response;
} else {
  // Não é comando, continuar processamento normal
  // ... resto do workflow
}
```

## 🧪 Testes e Validação

### Teste 1: Comando de Ajuda
```bash
curl -X POST https://beststag25.app.n8n.cloud/webhook/comandos/processar \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "/ajuda"
  }'
```

### Teste 2: Criação de Tarefa
```bash
curl -X POST https://beststag25.app.n8n.cloud/webhook/comandos/processar \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "/tarefa criar Revisar relatório mensal urgente para amanhã"
  }'
```

### Teste 3: Status do Usuário
```bash
curl -X POST https://beststag25.app.n8n.cloud/webhook/comandos/processar \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "/status"
  }'
```

### Teste 4: Comando Implícito
```bash
curl -X POST https://beststag25.app.n8n.cloud/webhook/comandos/processar \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "Preciso criar uma tarefa para ligar para o cliente"
  }'
```

## 📊 Estruturas de Dados

### Tabela "Tarefas"
```
- user: Link para Usuários
- title: Título da tarefa
- description: Descrição detalhada
- status: Pendente, Em Progresso, Concluída
- priority: Baixa, Média, Alta, Urgente
- due_date: Data de vencimento
- created_at: Data de criação
- completed_at: Data de conclusão
- tags: Tags categorizadas
```

### Tabela "Eventos"
```
- user: Link para Usuários
- title: Título do evento
- description: Descrição
- start_date: Data do evento
- start_time: Horário de início
- end_time: Horário de fim
- location: Local do evento
- created_at: Data de criação
```

## 🎯 Algoritmos Inteligentes

### Detecção de Prioridade
```javascript
function extractPriority(text) {
  const lowerText = text.toLowerCase();
  if (lowerText.includes('urgente') || lowerText.includes('crítico')) return 'Urgente';
  if (lowerText.includes('alta') || lowerText.includes('importante')) return 'Alta';
  if (lowerText.includes('baixa') || lowerText.includes('simples')) return 'Baixa';
  return 'Média';
}
```

### Extração de Datas
```javascript
function extractDueDate(text) {
  const lowerText = text.toLowerCase();
  const today = new Date();
  
  if (lowerText.includes('hoje')) return today.toISOString().split('T')[0];
  if (lowerText.includes('amanhã')) {
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  }
  
  // Padrão DD/MM/YYYY
  const dateMatch = text.match(/(\d{1,2})\/(\d{1,2})(?:\/(\d{2,4}))?/);
  if (dateMatch) {
    const day = parseInt(dateMatch[1]);
    const month = parseInt(dateMatch[2]) - 1;
    const year = dateMatch[3] ? parseInt(dateMatch[3]) : today.getFullYear();
    return new Date(year, month, day).toISOString().split('T')[0];
  }
  
  return null;
}
```

### Extração de Horários
```javascript
function extractTime(text) {
  const timePatterns = [
    /(\d{1,2})h(\d{2})?/g,           // 14h30, 14h
    /(\d{1,2}):(\d{2})/g,            // 14:30
    /(\d{1,2})\s*(am|pm)/gi          // 2pm, 2 pm
  ];
  
  for (const pattern of timePatterns) {
    const match = text.match(pattern);
    if (match) return match[0];
  }
  
  return null;
}
```

## 🔄 Fluxos de Trabalho

### Fluxo de Detecção de Comandos
```
Mensagem → Command Detector → Is Command? → Route Command → Handler Específico → Response
```

### Fluxo de Criação de Tarefa
```
/tarefa criar → Task Handler → Extract Parameters → Create Task → Airtable → Success Response
```

### Fluxo de Status
```
/status → Status Handler → Query Multiple Tables → Consolidate Data → Format Response
```

## 📈 Benefícios Implementados

### Produtividade
- **Criação rápida** de tarefas e eventos
- **Organização automática** por prioridade e data
- **Visão consolidada** do status atual
- **Relatórios automáticos** de produtividade

### Usabilidade
- **Comandos intuitivos** em português
- **Detecção inteligente** de parâmetros
- **Aliases múltiplos** para flexibilidade
- **Ajuda contextual** sempre disponível

### Eficiência
- **Processamento rápido** de comandos
- **Integração seamless** com memória contextual
- **Validação automática** de dados
- **Feedback imediato** ao usuário

## 🚨 Tratamento de Erros

### Validações Implementadas
- Verificação de parâmetros obrigatórios
- Validação de formatos de data e hora
- Verificação de permissões de edição
- Tratamento de comandos não reconhecidos

### Mensagens de Erro Amigáveis
```javascript
// Exemplo de tratamento de erro
if (args.length === 0) {
  return {
    error: 'Por favor, especifique o título da tarefa. Exemplo: /tarefa criar Revisar relatório mensal'
  };
}
```

## 🔄 Próximos Passos

Após implementação da Fase 4:
1. **Testar todos os comandos** com diferentes variações
2. **Monitorar uso** e identificar comandos mais utilizados
3. **Otimizar detecção** baseada em padrões de uso
4. **Adicionar comandos** baseados em feedback
5. **Avançar para Fase 5**: Integração com Portal Web

---

**Status**: ✅ **FASE 4 PRONTA PARA IMPLEMENTAÇÃO**  
**Próxima Fase**: Integração com Portal Web  
**Tempo Estimado**: 2-3 horas para implementação completa

