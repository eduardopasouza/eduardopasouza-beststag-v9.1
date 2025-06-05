```mermaid
flowchart TD
    %% Definição dos estilos
    classDef userInterface fill:#f9d5e5,stroke:#333,stroke-width:1px
    classDef dataStorage fill:#eeeeee,stroke:#333,stroke-width:1px
    classDef integration fill:#d0e8f2,stroke:#333,stroke-width:1px
    classDef processing fill:#d5f5e3,stroke:#333,stroke-width:1px
    classDef external fill:#fdebd0,stroke:#333,stroke-width:1px
    classDef finance fill:#e8daef,stroke:#333,stroke-width:1px
    
    %% Título
    title["FLUXOGRAMA TÉCNICO COMPLETO DO BESTSTAG"]
    
    %% Interfaces de Usuário
    User((Usuário)) --> WhatsApp
    User --> Portal
    User --> Email
    
    WhatsApp[WhatsApp Business API\nTwilio] :::userInterface
    Portal[Portal Web\nLovable/Bubble/Softr] :::userInterface
    Email[Email\nGmail/Outlook] :::userInterface
    
    %% Armazenamento de Dados
    Airtable[Airtable\nBase de Dados Central] :::dataStorage
    Supabase[Supabase\nArmazenamento Complementar] :::dataStorage
    
    %% Backbone de Integração
    n8n[n8n\nBackbone de Integração] :::integration
    
    %% Processamento de IA
    OpenAI[OpenAI API\nGPT-4] :::processing
    Claude[Claude API\nAnthropica] :::processing
    
    %% Sistemas Externos
    Gmail[Gmail API] :::external
    GCalendar[Google Calendar API] :::external
    Outlook[Outlook API] :::external
    MSCalendar[Microsoft Calendar API] :::external
    
    %% Componentes Internos do n8n
    subgraph "n8n Workflows"
        MessageProcessor[Processador de Mensagens]
        IntentRouter[Router de Intenções]
        EntityExtractor[Extrator de Entidades]
        ContextSystem[Sistema de Contexto]
        TaskHandler[Gerenciador de Tarefas]
        CalendarHandler[Gerenciador de Agenda]
        ContactHandler[Gerenciador de Contatos]
        EmailHandler[Gerenciador de Emails]
        FinanceHandler[Gerenciador Financeiro] :::finance
        ResponseFormatter[Formatador de Respostas]
        WebhookManager[Gerenciador de Webhooks]
        Scheduler[Agendador de Tarefas]
    end
    
    %% Fluxos de Entrada
    
    %% 1. Fluxo de Entrada via WhatsApp
    WhatsApp -->|1. Mensagem recebida| WebhookManager
    WebhookManager -->|2. Webhook processado| n8n
    n8n -->|3. Processa mensagem| MessageProcessor
    MessageProcessor -->|4a. Comando detectado| IntentRouter
    MessageProcessor -->|4b. Texto livre| EntityExtractor
    
    %% 2. Fluxo de Entrada via Portal Web
    Portal -->|1. Interação do usuário| WebhookManager
    
    %% 3. Fluxo de Entrada via Email
    Email -->|1. Email recebido| WebhookManager
    
    %% 4. Fluxo de Tarefas Agendadas
    Scheduler -->|1. Execução programada| n8n
    
    %% Processamento de IA
    EntityExtractor -->|5. Extração de entidades| OpenAI
    OpenAI -->|6. Entidades extraídas| IntentRouter
    IntentRouter -->|7. Classificação de intenção| Claude
    Claude -->|8. Intenção classificada| IntentRouter
    
    %% Sistema de Contexto
    IntentRouter <-->|9. Consulta/atualiza contexto| ContextSystem
    ContextSystem <-->|10. Armazena contexto| Airtable
    
    %% Roteamento para Handlers
    IntentRouter -->|11a. Tarefa identificada| TaskHandler
    IntentRouter -->|11b. Evento de agenda| CalendarHandler
    IntentRouter -->|11c. Contato| ContactHandler
    IntentRouter -->|11d. Email| EmailHandler
    IntentRouter -->|11e. Finanças| FinanceHandler
    
    %% Handlers para Armazenamento
    TaskHandler <-->|12a. CRUD tarefas| Airtable
    CalendarHandler <-->|12b. CRUD eventos| Airtable
    ContactHandler <-->|12c. CRUD contatos| Airtable
    EmailHandler <-->|12d. CRUD emails| Airtable
    FinanceHandler <-->|12e. CRUD finanças| Airtable
    
    %% Armazenamento Complementar
    TaskHandler <-->|13a. Dados complementares| Supabase
    CalendarHandler <-->|13b. Dados complementares| Supabase
    ContactHandler <-->|13c. Dados complementares| Supabase
    
    %% Integração com Sistemas Externos
    CalendarHandler <-->|14a. Sincronização| GCalendar
    CalendarHandler <-->|14b. Sincronização| MSCalendar
    EmailHandler <-->|14c. Sincronização| Gmail
    EmailHandler <-->|14d. Sincronização| Outlook
    
    %% Formatação e Resposta
    TaskHandler -->|15a. Resultado| ResponseFormatter
    CalendarHandler -->|15b. Resultado| ResponseFormatter
    ContactHandler -->|15c. Resultado| ResponseFormatter
    EmailHandler -->|15d. Resultado| ResponseFormatter
    FinanceHandler -->|15e. Resultado| ResponseFormatter
    
    %% Resposta ao Usuário
    ResponseFormatter -->|16. Formata resposta| n8n
    n8n -->|17a. Envia resposta| WhatsApp
    n8n -->|17b. Atualiza interface| Portal
    n8n -->|17c. Envia email| Email
    
    %% Sincronização Bidirecional
    Portal <-->|18. Sincronização bidirecional| n8n
    n8n <-->|19. CRUD operações| Airtable
    
    %% Fluxos de Funcionalidades Principais
    
    %% A. Fluxo de Gestão de Tarefas
    subgraph "Fluxo: Gestão de Tarefas"
        A1[Receber comando/texto]
        A2[Identificar intenção]
        A3[Extrair detalhes da tarefa]
        A4[Consultar/Criar/Atualizar]
        A5[Notificar usuário]
    end
    
    %% B. Fluxo de Gerenciamento de Agenda
    subgraph "Fluxo: Gerenciamento de Agenda"
        B1[Receber comando/texto]
        B2[Identificar intenção]
        B3[Extrair detalhes do evento]
        B4[Verificar conflitos]
        B5[Agendar/Atualizar evento]
        B6[Sincronizar calendários]
        B7[Notificar usuário]
    end
    
    %% C. Fluxo de Triagem de Email
    subgraph "Fluxo: Triagem de Email"
        C1[Receber email]
        C2[Classificar importância]
        C3[Extrair informações]
        C4[Armazenar metadados]
        C5[Notificar usuário]
    end
    
    %% D. Fluxo de Gestão de Contatos
    subgraph "Fluxo: Gestão de Contatos"
        D1[Receber comando/texto]
        D2[Identificar intenção]
        D3[Extrair detalhes do contato]
        D4[Consultar/Criar/Atualizar]
        D5[Notificar usuário]
    end
    
    %% E. Fluxo de Assistente Financeiro
    subgraph "Fluxo: Assistente Financeiro"
        E1[Receber comando/texto]
        E2[Identificar intenção]
        E3[Extrair detalhes financeiros]
        E4[Registrar transação]
        E5[Atualizar saldos]
        E6[Gerar relatório]
        E7[Notificar usuário]
    end
    
    %% Aplicação de estilos
    class MessageProcessor,IntentRouter,EntityExtractor,ContextSystem,TaskHandler,CalendarHandler,ContactHandler,EmailHandler,ResponseFormatter,WebhookManager,Scheduler processing
```
