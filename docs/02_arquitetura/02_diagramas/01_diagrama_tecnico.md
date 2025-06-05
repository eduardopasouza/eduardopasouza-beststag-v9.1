```mermaid
flowchart TB
    %% Definição de estilos
    classDef userInterface fill:#d8e8f9,stroke:#4a6da7,stroke-width:2px
    classDef communication fill:#e6e6e6,stroke:#666666,stroke-width:2px
    classDef processing fill:#d0e0f0,stroke:#3c78d8,stroke-width:2px
    classDef intelligence fill:#fff2cc,stroke:#d6b656,stroke-width:2px
    classDef dataStorage fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    classDef integration fill:#ffe6cc,stroke:#d79b00,stroke-width:2px
    
    %% CAMADA DE INTERFACE DO USUÁRIO
    subgraph UI[CAMADA DE INTERFACE DO USUÁRIO]
        WhatsApp[WhatsApp Business API\n- Mensagens de texto\n- Mensagens de voz\n- Anexos de mídia]
        WebPortal[Portal Web / PWA\n- Dashboard\n- Configurações\n- Visualizações avançadas]
        Email[Email\n- Comunicações formais\n- Anexos\n- Relatórios]
    end
    
    %% CAMADA DE COMUNICAÇÃO
    subgraph COMM[CAMADA DE COMUNICAÇÃO]
        Webhooks[Webhooks\n- WhatsApp Business Webhook\n- Portal Web Webhook\n- Email Webhook]
        APIGateway[API Gateway\n- Autenticação\n- Rate Limiting\n- Logging]
    end
    
    %% CAMADA DE PROCESSAMENTO
    subgraph PROC[CAMADA DE PROCESSAMENTO (Make/n8n)]
        MessageRouter[Roteador de Mensagens\n- Análise inicial\n- Distribuição para módulos]
        
        subgraph TaskModule[Módulo de Tarefas]
            TaskCreation[Criação de Tarefas]
            TaskUpdate[Atualização de Tarefas]
            TaskReminder[Lembretes de Tarefas]
            TaskQuery[Consulta de Tarefas]
        end
        
        subgraph CalendarModule[Módulo de Calendário]
            EventCreation[Criação de Eventos]
            EventUpdate[Atualização de Eventos]
            EventReminder[Lembretes de Eventos]
            EventQuery[Consulta de Eventos]
            ConflictCheck[Verificação de Conflitos]
        end
        
        subgraph EmailModule[Módulo de Email]
            EmailTriage[Triagem de Emails]
            EmailSearch[Busca de Emails]
            EmailSummary[Resumo de Emails]
            EmailNotification[Notificação de Emails]
        end
        
        subgraph InfoModule[Módulo de Informações]
            InfoCapture[Captura de Informações]
            InfoCategorize[Categorização]
            InfoSearch[Busca de Informações]
            InfoLink[Vinculação com Tarefas/Eventos]
        end
        
        subgraph FinanceModule[Módulo Financeiro]
            FinanceRecord[Registro de Transações]
            FinanceCategorize[Categorização]
            FinanceReport[Relatórios]
            FinanceAlert[Alertas de Orçamento]
        end
        
        ResponseFormatter[Formatador de Respostas\n- Estruturação\n- Personalização\n- Enriquecimento]
    end
    
    %% CAMADA DE INTELIGÊNCIA
    subgraph INTEL[CAMADA DE INTELIGÊNCIA (OpenAI/Claude)]
        IntentClassifier[Classificador de Intenção\n- Análise de mensagem\n- Identificação de objetivo\n- Extração de entidades]
        
        ContextManager[Gerenciador de Contexto\n- Histórico de interações\n- Preferências do usuário\n- Estado atual]
        
        ResponseGenerator[Gerador de Respostas\n- Criação de conteúdo\n- Formatação\n- Personalização]
        
        PatternAnalyzer[Analisador de Padrões\n- Comportamentos recorrentes\n- Sugestões proativas\n- Personalização]
    end
    
    %% CAMADA DE DADOS
    subgraph DATA[CAMADA DE DADOS (Airtable)]
        UserTable[Tabela de Usuários\n- Perfis\n- Preferências\n- Integrações]
        
        TaskTable[Tabela de Tarefas\n- Título\n- Descrição\n- Prazo\n- Prioridade\n- Status]
        
        EventTable[Tabela de Eventos\n- Título\n- Data/Hora\n- Participantes\n- Localização]
        
        InfoTable[Tabela de Informações\n- Conteúdo\n- Categorias\n- Tags\n- Vínculos]
        
        FinanceTable[Tabela Financeira\n- Tipo\n- Valor\n- Categoria\n- Data\n- Descrição]
        
        InteractionTable[Tabela de Interações\n- Mensagens\n- Timestamps\n- Contexto\n- Ações]
    end
    
    %% CAMADA DE INTEGRAÇÃO
    subgraph INTEG[CAMADA DE INTEGRAÇÃO]
        GoogleInteg[Google Workspace\n- Gmail\n- Google Calendar\n- Google Drive]
        
        MicrosoftInteg[Microsoft 365\n- Outlook\n- Office 365\n- OneDrive]
        
        PaymentInteg[Sistemas de Pagamento\n- Stripe\n- PagSeguro\n- PayPal]
        
        OtherInteg[Outras Integrações\n- CRMs\n- ERPs\n- Ferramentas específicas]
    end
    
    %% CONEXÕES ENTRE CAMADAS
    %% Interface -> Comunicação
    WhatsApp --> Webhooks
    WebPortal --> APIGateway
    Email --> Webhooks
    
    %% Comunicação -> Processamento
    Webhooks --> MessageRouter
    APIGateway --> MessageRouter
    
    %% Processamento -> Inteligência
    MessageRouter --> IntentClassifier
    TaskModule <--> ContextManager
    CalendarModule <--> ContextManager
    EmailModule <--> ContextManager
    InfoModule <--> ContextManager
    FinanceModule <--> ContextManager
    
    %% Inteligência -> Processamento
    IntentClassifier --> TaskModule
    IntentClassifier --> CalendarModule
    IntentClassifier --> EmailModule
    IntentClassifier --> InfoModule
    IntentClassifier --> FinanceModule
    ResponseGenerator --> ResponseFormatter
    
    %% Processamento -> Dados
    TaskModule <--> TaskTable
    CalendarModule <--> EventTable
    EmailModule <--> InteractionTable
    InfoModule <--> InfoTable
    FinanceModule <--> FinanceTable
    MessageRouter <--> UserTable
    ResponseFormatter <--> InteractionTable
    
    %% Inteligência -> Dados
    ContextManager <--> InteractionTable
    ContextManager <--> UserTable
    PatternAnalyzer <--> InteractionTable
    
    %% Processamento -> Integração
    EmailModule <--> GoogleInteg
    EmailModule <--> MicrosoftInteg
    CalendarModule <--> GoogleInteg
    CalendarModule <--> MicrosoftInteg
    InfoModule <--> GoogleInteg
    InfoModule <--> MicrosoftInteg
    FinanceModule <--> PaymentInteg
    
    %% Processamento -> Interface (Respostas)
    ResponseFormatter --> WhatsApp
    ResponseFormatter --> WebPortal
    ResponseFormatter --> Email
    
    %% Aplicar estilos
    class UI,WhatsApp,WebPortal,Email userInterface
    class COMM,Webhooks,APIGateway communication
    class PROC,MessageRouter,TaskModule,CalendarModule,EmailModule,InfoModule,FinanceModule,ResponseFormatter,TaskCreation,TaskUpdate,TaskReminder,TaskQuery,EventCreation,EventUpdate,EventReminder,EventQuery,ConflictCheck,EmailTriage,EmailSearch,EmailSummary,EmailNotification,InfoCapture,InfoCategorize,InfoSearch,InfoLink,FinanceRecord,FinanceCategorize,FinanceReport,FinanceAlert processing
    class INTEL,IntentClassifier,ContextManager,ResponseGenerator,PatternAnalyzer intelligence
    class DATA,UserTable,TaskTable,EventTable,InfoTable,FinanceTable,InteractionTable dataStorage
    class INTEG,GoogleInteg,MicrosoftInteg,PaymentInteg,OtherInteg integration
```
