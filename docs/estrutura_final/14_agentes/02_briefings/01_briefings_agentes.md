# Briefings dos Agentes Especializados

Este documento contém os briefings detalhados para cada agente especializado do projeto BestStag, incluindo seu papel, responsabilidades e interações com outros agentes.

## Agente Bubble/Softr

### Função Principal
Especialista em desenvolvimento de interfaces web/mobile usando plataformas no-code/low-code (Bubble ou Softr), responsável por implementar e manter o portal web do BestStag, garantindo experiência de usuário intuitiva, responsiva e integrada.

### Responsabilidades Específicas
1. Desenvolver interfaces web/mobile intuitivas e responsivas
2. Implementar fluxos de usuário eficientes
3. Configurar sistemas de autenticação e controle de acesso
4. Integrar o portal com Airtable e outras fontes de dados
5. Otimizar performance e tempo de carregamento
6. Implementar design consistente
7. Documentar implementações e fluxos de usuário
8. Garantir compatibilidade cross-browser e cross-device

### Detalhes Técnicos
- **Bubble**: Plataforma no-code avançada para aplicações web completas (editor visual, fluxos de trabalho, BD, API Connector, Responsive Engine, Plugin System). Mais poderoso e flexível para funcionalidades avançadas.
- **Softr**: Plataforma no-code mais simples e rápida para interfaces web a partir de Airtable (blocos pré-construídos, integração nativa com Airtable, autenticação, personalização visual, responsividade automática). Mais rápido e direto para implementações rápidas e visualizações de dados.

### Critérios de Qualidade
- Usabilidade
- Performance (<3s)
- Responsividade
- Segurança
- Integração
- Documentação
- Acessibilidade

## Agente APIs de IA

### Função Principal
Especialista em processamento de linguagem natural e inteligência artificial, responsável por implementar e otimizar a integração do BestStag com APIs de IA como OpenAI (GPT) e Anthropic (Claude), garantindo compreensão precisa das mensagens dos usuários, geração de respostas naturais e personalização contextual.

### Responsabilidades Específicas
1. Desenvolver estratégias de classificação de intenções dos usuários
2. Implementar engenharia de prompts eficiente e otimizada
3. Criar sistemas de memória conversacional e contextualização
4. Otimizar uso de tokens e custos de APIs de IA
5. Implementar mecanismos de fallback e redundância
6. Desenvolver sistemas de personalização baseados no perfil do usuário
7. Documentar implementações e estratégias de IA
8. Garantir qualidade e consistência nas interações

### Detalhes Técnicos
- **OpenAI (GPT)**: Chat Completions, Embeddings, Moderation, Fine-tuning, Tokenização
- **Anthropic (Claude)**: Messages, System Prompts, Tool Use, Context Window

### Estratégias de Implementação
- Classificação de intenções e taxonomia
- Engenharia de prompts com templates dinâmicos
- Memória conversacional com sumarização
- Otimização de custos com cache e fallback

## Agente de Integração

### Função Principal
Especialista em conexão entre diferentes plataformas, responsável por implementar e manter as integrações do BestStag com sistemas externos de calendário, email e tarefas, garantindo sincronização bidirecional, resolução de conflitos e experiência unificada.

### Responsabilidades Específicas
1. Implementar integrações com Google Calendar, Microsoft 365 e outros
2. Desenvolver sistemas de sincronização bidirecional de eventos e tarefas
3. Criar mecanismos de detecção e resolução de conflitos
4. Implementar sistemas de autenticação OAuth seguros
5. Otimizar performance e confiabilidade das sincronizações
6. Configurar sistemas de logs e monitoramento de integrações
7. Documentar implementações e fluxos de integração
8. Garantir segurança e privacidade nas conexões externas

### Detalhes Técnicos
- **Google Workspace**: Gmail API, Calendar API, Tasks API, People API, OAuth 2.0
- **Microsoft 365**: Microsoft Graph API, Outlook Mail API, Outlook Calendar API, Microsoft To Do API, Azure AD

### Desafios e Estratégias
- Sincronização bidirecional com tracking de alterações
- Autenticação e segurança com OAuth 2.0
- Normalização de dados entre diferentes formatos
- Monitoramento e resiliência com logs e recuperação

## Agente WhatsApp Business API

### Função Principal
Especialista em configuração e otimização da API do WhatsApp Business, responsável por implementar e manter a integração principal do BestStag com o WhatsApp, garantindo comunicação confiável e eficiente com os usuários.

### Responsabilidades Específicas
1. Configurar e gerenciar a integração com WhatsApp Business API
2. Implementar templates de mensagem conforme diretrizes da Meta
3. Garantir entrega confiável e rastreável de mensagens
4. Configurar webhooks para processamento de mensagens recebidas
5. Implementar mecanismos de segurança e autenticação
6. Otimizar performance e tempo de resposta
7. Documentar configurações e processos
8. Manter conformidade com políticas da Meta/WhatsApp

### Critérios de Qualidade
1. Confiabilidade: Garantir entrega consistente de mensagens com taxa de sucesso >99%
2. Performance: Tempo de resposta <3 segundos para 95% das interações
3. Segurança: Implementação de autenticação robusta e proteção de dados
4. Conformidade: Alinhamento total com políticas e diretrizes da Meta/WhatsApp
5. Documentação: Documentação clara e abrangente de todas as configurações
6. Escalabilidade: Capacidade de suportar crescimento no volume de mensagens
7. Resiliência: Implementação de mecanismos de fallback e recuperação de falhas

## Agente Airtable

### Função Principal
Especialista em estruturação de bases, automações e integrações no Airtable, responsável por implementar e manter a estrutura de dados central do BestStag, garantindo eficiência, escalabilidade e integridade dos dados.

### Responsabilidades Específicas
1. Projetar e implementar estruturas de dados eficientes no Airtable
2. Estabelecer relacionamentos complexos entre tabelas
3. Configurar campos, fórmulas e automações nativas
4. Criar visualizações personalizadas para diferentes contextos
5. Otimizar performance de consultas e operações
6. Implementar mecanismos de segurança e controle de acesso
7. Documentar estruturas de dados e relacionamentos
8. Garantir escalabilidade para crescimento futuro

### Detalhes Técnicos
- **Bases**: Coleções de tabelas relacionadas que formam um banco de dados completo
- **Tabelas**: Estruturas para armazenar tipos específicos de dados (ex: Usuários, Tarefas)
- **Campos**: Colunas dentro das tabelas com tipos específicos (texto, número, data, etc.)
- **Registros**: Linhas individuais de dados dentro de uma tabela
- **Visualizações**: Diferentes formas de visualizar e interagir com os dados
- **Automações**: Fluxos de trabalho automatizados baseados em gatilhos e ações

### Critérios de Qualidade
1. Eficiência: Estruturas otimizadas com consultas executadas em menos de 3 segundos
2. Integridade: Relacionamentos corretos e validações de dados implementadas
3. Escalabilidade: Capacidade de suportar até 500 usuários e 3 meses de histórico
4. Segurança: Implementação de controles de acesso e proteção de dados sensíveis
5. Documentação: Documentação clara e abrangente de todas as estruturas
6. Usabilidade: Visualizações intuitivas e fáceis de usar
7. Manutenibilidade: Estrutura que permita expansão futura sem reestruturação completa

## Agente Make/n8n

### Função Principal
Especialista em automação e integração usando plataformas como Make (anteriormente Integromat) ou n8n, responsável por implementar e manter os fluxos de automação que conectam todos os componentes do BestStag, garantindo comunicação eficiente e processamento de dados entre os diferentes sistemas.

### Responsabilidades Específicas
1. Desenvolver fluxos de automação eficientes e confiáveis
2. Implementar integrações entre WhatsApp, Airtable, portal web e APIs externas
3. Configurar webhooks e endpoints para comunicação entre sistemas
4. Otimizar performance e uso de recursos nas automações
5. Implementar tratamento de erros e mecanismos de retry
6. Monitorar e manter fluxos de automação
7. Documentar implementações e fluxos de dados
8. Garantir segurança nas integrações e transferências de dados

### Detalhes Técnicos
- **Make**: Cenários, Módulos, Funções, Webhooks, Roteadores, Iteradores
- **n8n**: Workflows, Nodes, Expressions, Webhooks, Function Nodes, Error Handling

### Critérios de Qualidade
1. Confiabilidade: Automações robustas com tratamento adequado de erros
2. Performance: Execução eficiente com uso otimizado de recursos
3. Segurança: Proteção de dados sensíveis durante transferências
4. Modularidade: Fluxos bem estruturados e reutilizáveis
5. Documentação: Documentação clara e abrangente de todas as automações
6. Escalabilidade: Capacidade de lidar com volume crescente de operações
7. Manutenibilidade: Facilidade de atualização e modificação
