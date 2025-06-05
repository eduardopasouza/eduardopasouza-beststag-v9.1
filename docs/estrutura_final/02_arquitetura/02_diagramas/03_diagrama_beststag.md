```mermaid
flowchart TD
    %% Definição dos estilos
    classDef userInterface fill:#f9d5e5,stroke:#333,stroke-width:1px
    classDef dataStorage fill:#eeeeee,stroke:#333,stroke-width:1px
    classDef integration fill:#d0e8f2,stroke:#333,stroke-width:1px
    classDef processing fill:#d5f5e3,stroke:#333,stroke-width:1px
    classDef external fill:#fdebd0,stroke:#333,stroke-width:1px
    
    %% Interfaces de Usuário
    User((Usuário)) --> WhatsApp
    User --> Portal
    
    WhatsApp[WhatsApp Business API\nTwilio] :::userInterface
    Portal[Portal Web\nLovable/Bubble] :::userInterface
    
    %% Armazenamento de Dados
    Airtable[Airtable\nBase de Dados Central] :::dataStorage
    
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
        ResponseFormatter[Formatador de Respostas]
    end
    
    %% Conexões Principais
    
    %% Fluxo de Entrada via WhatsApp
    WhatsApp -->|1. Mensagem recebida| n8n
    n8n -->|2. Processa mensagem| MessageProcessor
    MessageProcessor -->|3a. Comando detectado| IntentRouter
    MessageProcessor -->|3b. Texto livre| EntityExtractor
    
    %% Processamento de IA
    EntityExtractor -->|4. Extração de entidades| OpenAI
    OpenAI -->|5. Entidades extraídas| IntentRouter
    IntentRouter -->|6. Classificação de intenção| Claude
    Claude -->|7. Intenção classificada| IntentRouter
    
    %% Sistema de Contexto
    IntentRouter <-->|8. Consulta/atualiza contexto| ContextSystem
    ContextSystem <-->|9. Armazena contexto| Airtable
    
    %% Roteamento para Handlers
    IntentRouter -->|10a. Tarefa identificada| TaskHandler
    IntentRouter -->|10b. Evento de agenda| CalendarHandler
    IntentRouter -->|10c. Contato| ContactHandler
    IntentRouter -->|10d. Email| EmailHandler
    
    %% Handlers para Airtable
    TaskHandler <-->|11a. CRUD tarefas| Airtable
    CalendarHandler <-->|11b. CRUD eventos| Airtable
    ContactHandler <-->|11c. CRUD contatos| Airtable
    EmailHandler <-->|11d. CRUD emails| Airtable
    
    %% Integração com Sistemas Externos
    CalendarHandler <-->|12a. Sincronização| GCalendar
    CalendarHandler <-->|12b. Sincronização| MSCalendar
    EmailHandler <-->|12c. Sincronização| Gmail
    EmailHandler <-->|12d. Sincronização| Outlook
    
    %% Formatação e Resposta
    TaskHandler -->|13a. Resultado| ResponseFormatter
    CalendarHandler -->|13b. Resultado| ResponseFormatter
    ContactHandler -->|13c. Resultado| ResponseFormatter
    EmailHandler -->|13d. Resultado| ResponseFormatter
    
    %% Resposta ao Usuário
    ResponseFormatter -->|14. Formata resposta| n8n
    n8n -->|15. Envia resposta| WhatsApp
    
    %% Portal Web
    Portal <-->|16. Sincronização bidirecional| n8n
    n8n <-->|17. CRUD operações| Airtable
    
    %% Aplicação de estilos
    class MessageProcessor,IntentRouter,EntityExtractor,ContextSystem,TaskHandler,CalendarHandler,ContactHandler,EmailHandler,ResponseFormatter processing
```
