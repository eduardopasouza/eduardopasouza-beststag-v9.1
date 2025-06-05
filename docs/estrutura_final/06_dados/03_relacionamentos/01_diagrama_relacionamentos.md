# Diagrama de Relacionamentos - BestStag MVP
## Mapa Conceitual da Estrutura de Dados

```
┌─────────────────┐
│    USUÁRIOS     │ (Tabela Central)
│                 │
│ • ID_Usuario    │
│ • Nome_Completo │
│ • Email         │
│ • Telefone_WA   │
│ • Fuso_Horario  │
│ • Status_Conta  │
│ • Plano         │
└─────────┬───────┘
          │
          │ (1:N - Um usuário tem muitos registros)
          │
    ┌─────┴─────┬─────────┬─────────┬─────────┐
    │           │         │         │         │
    ▼           ▼         ▼         ▼         ▼
┌───────┐  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────┐
│EMAILS │  │ EVENTOS │ │ TAREFAS │ │INTERAÇÕES│ │CONFIGURAÇÕES │
└───┬───┘  └────┬────┘ └────┬────┘ └─────┬────┘ └──────────────┘
    │           │           │            │
    │           │           │            │
    │           └───────────┼────────────┼─── Relacionamentos
    │                       │            │    Secundários
    └───────────────────────┼────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ RELACIONAMENTOS│
                    │   CRUZADOS     │
                    │                │
                    │ • Tarefas ←→   │
                    │   Eventos      │
                    │ • Tarefas ←→   │
                    │   Emails       │
                    │ • Interações ←→│
                    │   Todos Objetos│
                    └───────────────┘
```

## Detalhamento dos Relacionamentos

### 1. USUÁRIOS (Hub Central)
```
USUÁRIOS (1) ←→ (N) EMAILS
USUÁRIOS (1) ←→ (N) EVENTOS  
USUÁRIOS (1) ←→ (N) TAREFAS
USUÁRIOS (1) ←→ (N) INTERAÇÕES
USUÁRIOS (1) ←→ (N) CONFIGURAÇÕES
```

### 2. Relacionamentos Secundários
```
EVENTOS (1) ←→ (N) TAREFAS
- Um evento pode gerar várias tarefas relacionadas
- Campo: Evento_Relacionado em Tarefas

EMAILS (1) ←→ (N) TAREFAS  
- Um email pode gerar várias tarefas
- Campo: Email_Origem em Tarefas

INTERAÇÕES (N) ←→ (1) EMAILS
- Várias interações podem referenciar um email
- Campo: Email_Relacionado em Interações

INTERAÇÕES (N) ←→ (1) EVENTOS
- Várias interações podem referenciar um evento  
- Campo: Evento_Relacionado em Interações

INTERAÇÕES (N) ←→ (1) TAREFAS
- Várias interações podem referenciar uma tarefa
- Campo: Tarefa_Relacionada em Interações
```

### 3. Fluxo de Dados Típico

```
1. USUÁRIO faz login/cadastro
   ↓
2. CONFIGURAÇÕES são carregadas
   ↓
3. EMAILS são processados → podem gerar TAREFAS
   ↓
4. EVENTOS são sincronizados → podem gerar TAREFAS
   ↓
5. INTERAÇÕES são registradas com contexto
   ↓
6. Sistema aprende e atualiza CONFIGURAÇÕES
```

### 4. Campos de Lookup Principais

```
EMAILS:
- Usuario_Nome (lookup de Usuários.Nome_Completo)
- Usuario_Fuso (lookup de Usuários.Fuso_Horario)

EVENTOS:
- Usuario_Nome (lookup de Usuários.Nome_Completo)
- Usuario_Fuso (lookup de Usuários.Fuso_Horario)

TAREFAS:
- Usuario_Nome (lookup de Usuários.Nome_Completo)
- Evento_Titulo (lookup de Eventos.Titulo)
- Email_Assunto (lookup de Emails.Assunto)

INTERAÇÕES:
- Usuario_Nome (lookup de Usuários.Nome_Completo)
- Email_Assunto (lookup de Emails.Assunto)
- Evento_Titulo (lookup de Eventos.Titulo)
- Tarefa_Titulo (lookup de Tarefas.Titulo)
```

### 5. Campos de Rollup para Estatísticas

```
USUÁRIOS:
- Total_Emails (count de Emails)
- Total_Eventos (count de Eventos)  
- Total_Tarefas (count de Tarefas)
- Total_Interações (count de Interações)
- Tarefas_Pendentes (count de Tarefas onde Status = "Pendente")
- Emails_Nao_Lidos (count de Emails onde Status_Leitura = "Não Lido")
- Eventos_Hoje (count de Eventos onde Data_Inicio = TODAY())
```

### 6. Visualizações Recomendadas

```
USUÁRIOS:
- Visão Geral (todos os campos principais)
- Usuários Ativos (filtro: Usuario_Ativo = "Ativo")
- Por Plano (agrupado por Plano_Assinatura)

EMAILS:
- Por Usuário (agrupado por Usuario)
- Não Lidos (filtro: Status_Leitura = "Não Lido")
- Requer Ação (filtro: Requer_Acao = true)
- Por Prioridade (agrupado por Prioridade)

EVENTOS:
- Por Usuário (agrupado por Usuario)
- Hoje (filtro: Data_Inicio = TODAY())
- Esta Semana (filtro: Data_Inicio entre hoje e +7 dias)
- Por Status (agrupado por Status)

TAREFAS:
- Por Usuário (agrupado por Usuario)
- Pendentes (filtro: Status = "Pendente")
- Atrasadas (filtro: Status_Prazo = "Atrasada")
- Por Prioridade (agrupado por Prioridade)
- Por Categoria (agrupado por Categoria)

INTERAÇÕES:
- Por Usuário (agrupado por Usuario)
- Últimas 24h (filtro: Data_Hora >= DATEADD(NOW(), -1, 'day'))
- Por Canal (agrupado por Canal)
- Erros (filtro: Sucesso = false)

CONFIGURAÇÕES:
- Por Usuário (agrupado por Usuario)
- Ativas (filtro: Ativa = true)
- Por Tipo (agrupado por Tipo_Configuracao)
```

### 7. Automações Planejadas

```
1. NOTIFICAÇÃO DE TAREFAS:
   Gatilho: Data_Prazo = DATEADD(TODAY(), 1, 'day')
   Ação: Criar registro em Interações com notificação

2. ATUALIZAÇÃO DE STATUS:
   Gatilho: Data_Fim de Evento < NOW()
   Ação: Atualizar Status para "Concluído"

3. LOG DE ALTERAÇÕES:
   Gatilho: Qualquer alteração em registros importantes
   Ação: Criar registro em Interações com log

4. LIMPEZA DE DADOS:
   Gatilho: Dados com mais de 90 dias
   Ação: Arquivar ou marcar para exclusão
```

### 8. Considerações de Integração

```
MAKE/N8N:
- Webhooks configurados para cada tabela
- Endpoints de API para operações CRUD
- Sincronização bidirecional com serviços externos
- Processamento de dados em lote

WHATSAPP API:
- Interações registradas em tempo real
- Contexto mantido via Sessao_ID
- Respostas baseadas em histórico

PORTAL WEB:
- Visualizações filtradas por usuário
- Dashboards com rollups e estatísticas
- Interface para configurações avançadas
```

