# Design da Estrutura de Dados - BestStag MVP
## Documento Técnico de Planejamento

### Visão Geral
Este documento detalha o design da estrutura de dados no Airtable para o MVP do BestStag, um MicroSaaS que funciona como assistente virtual inteligente acessível via WhatsApp, aplicativo web/mobile e email.

### Objetivos da Estrutura
- Suportar até 500 usuários no MVP
- Armazenar pelo menos 3 meses de histórico
- Garantir consultas em menos de 3 segundos
- Permitir expansão futura sem reestruturação completa
- Facilitar integração com Make/n8n

### Arquitetura de Tabelas

## 1. TABELA: Usuários
**Propósito:** Armazenar perfis, preferências e configurações de acesso dos usuários

### Campos Principais:
- **ID_Usuario** (Primary Key, Auto Number)
- **Nome_Completo** (Single Line Text, Required)
- **Email** (Email, Required, Unique)
- **Telefone_WhatsApp** (Phone Number, Required, Unique)
- **Fuso_Horario** (Single Select: UTC-12 a UTC+14)
- **Idioma_Preferido** (Single Select: PT-BR, EN, ES)
- **Status_Conta** (Single Select: Ativo, Inativo, Suspenso, Trial)
- **Plano_Assinatura** (Single Select: Free, Basic, Premium)
- **Data_Cadastro** (Date, Auto-populated)
- **Data_Ultimo_Acesso** (Date)
- **Configuracoes_Notificacao** (Long Text, JSON format)
- **Preferencias_Pessoais** (Long Text, JSON format)

### Campos Calculados:
- **Dias_Desde_Cadastro** (Formula: DATETIME_DIFF(TODAY(), {Data_Cadastro}, 'days'))
- **Usuario_Ativo** (Formula: IF(DATETIME_DIFF(TODAY(), {Data_Ultimo_Acesso}, 'days') <= 7, "Ativo", "Inativo"))

## 2. TABELA: Emails
**Propósito:** Armazenar metadados de emails importantes (sem conteúdo completo por privacidade)

### Campos Principais:
- **ID_Email** (Primary Key, Auto Number)
- **Usuario** (Link to Usuarios, Required)
- **Remetente** (Email)
- **Assunto** (Single Line Text)
- **Data_Recebimento** (Date & Time)
- **Prioridade** (Single Select: Alta, Média, Baixa)
- **Categoria** (Single Select: Trabalho, Pessoal, Financeiro, Saúde, Outros)
- **Status_Leitura** (Single Select: Não Lido, Lido, Arquivado)
- **Requer_Acao** (Checkbox)
- **Data_Acao_Necessaria** (Date)
- **Resumo_IA** (Long Text)
- **Tags** (Multiple Select)
- **Email_ID_Externo** (Single Line Text, para integração)

### Campos Calculados:
- **Dias_Sem_Acao** (Formula: IF({Requer_Acao}, DATETIME_DIFF(TODAY(), {Data_Recebimento}, 'days'), 0))
- **Status_Urgencia** (Formula: IF(AND({Requer_Acao}, {Dias_Sem_Acao} > 3), "Urgente", "Normal"))

## 3. TABELA: Eventos
**Propósito:** Armazenar compromissos de calendário e metadados associados

### Campos Principais:
- **ID_Evento** (Primary Key, Auto Number)
- **Usuario** (Link to Usuarios, Required)
- **Titulo** (Single Line Text, Required)
- **Descricao** (Long Text)
- **Data_Inicio** (Date & Time, Required)
- **Data_Fim** (Date & Time)
- **Local** (Single Line Text)
- **Tipo_Evento** (Single Select: Reunião, Compromisso, Lembrete, Tarefa Agendada)
- **Status** (Single Select: Agendado, Confirmado, Cancelado, Concluído)
- **Prioridade** (Single Select: Alta, Média, Baixa)
- **Participantes** (Long Text)
- **Link_Reuniao** (URL)
- **Lembrete_Antecedencia** (Number, em minutos)
- **Evento_ID_Externo** (Single Line Text, para integração)
- **Recorrencia** (Single Select: Única, Diária, Semanal, Mensal, Anual)

### Campos Calculados:
- **Duracao_Minutos** (Formula: DATETIME_DIFF({Data_Fim}, {Data_Inicio}, 'minutes'))
- **Status_Temporal** (Formula: IF({Data_Inicio} > NOW(), "Futuro", IF({Data_Fim} < NOW(), "Passado", "Em Andamento")))
- **Dias_Ate_Evento** (Formula: DATETIME_DIFF({Data_Inicio}, NOW(), 'days'))

## 4. TABELA: Tarefas
**Propósito:** Lista de tarefas com categorias, prazos e status

### Campos Principais:
- **ID_Tarefa** (Primary Key, Auto Number)
- **Usuario** (Link to Usuarios, Required)
- **Titulo** (Single Line Text, Required)
- **Descricao** (Long Text)
- **Status** (Single Select: Pendente, Em Andamento, Concluída, Cancelada)
- **Prioridade** (Single Select: Alta, Média, Baixa)
- **Categoria** (Single Select: Trabalho, Pessoal, Financeiro, Saúde, Estudos, Outros)
- **Data_Criacao** (Date, Auto-populated)
- **Data_Prazo** (Date)
- **Data_Conclusao** (Date)
- **Tempo_Estimado** (Number, em horas)
- **Tempo_Gasto** (Number, em horas)
- **Tags** (Multiple Select)
- **Evento_Relacionado** (Link to Eventos)
- **Email_Origem** (Link to Emails)
- **Notas** (Long Text)

### Campos Calculados:
- **Dias_Ate_Prazo** (Formula: IF({Data_Prazo}, DATETIME_DIFF({Data_Prazo}, TODAY(), 'days'), ""))
- **Status_Prazo** (Formula: IF({Status} = "Concluída", "Concluída", IF({Dias_Ate_Prazo} < 0, "Atrasada", IF({Dias_Ate_Prazo} <= 1, "Urgente", "No Prazo"))))
- **Tempo_Execucao** (Formula: IF({Data_Conclusao}, DATETIME_DIFF({Data_Conclusao}, {Data_Criacao}, 'days'), ""))

## 5. TABELA: Interações
**Propósito:** Histórico de comandos e respostas para memória contextual

### Campos Principais:
- **ID_Interacao** (Primary Key, Auto Number)
- **Usuario** (Link to Usuarios, Required)
- **Data_Hora** (Date & Time, Auto-populated)
- **Canal** (Single Select: WhatsApp, Web, Email, API)
- **Tipo_Interacao** (Single Select: Comando, Consulta, Notificação, Resposta)
- **Comando_Usuario** (Long Text)
- **Resposta_Sistema** (Long Text)
- **Contexto** (Long Text, JSON format)
- **Objeto_Relacionado_Tipo** (Single Select: Email, Evento, Tarefa, Configuração, Nenhum)
- **Email_Relacionado** (Link to Emails)
- **Evento_Relacionado** (Link to Eventos)
- **Tarefa_Relacionada** (Link to Tarefas)
- **Sucesso** (Checkbox)
- **Tempo_Resposta** (Number, em segundos)
- **Sessao_ID** (Single Line Text)

### Campos Calculados:
- **Hora_Formatada** (Formula: DATETIME_FORMAT({Data_Hora}, 'DD/MM/YYYY HH:mm'))
- **Dia_Semana** (Formula: DATETIME_FORMAT({Data_Hora}, 'dddd'))

## 6. TABELA: Configurações
**Propósito:** Regras de classificação e preferências do sistema

### Campos Principais:
- **ID_Configuracao** (Primary Key, Auto Number)
- **Usuario** (Link to Usuarios, Required)
- **Tipo_Configuracao** (Single Select: Email_Filter, Task_Category, Notification_Rule, AI_Preference)
- **Nome_Regra** (Single Line Text, Required)
- **Descricao** (Long Text)
- **Condicoes** (Long Text, JSON format)
- **Acoes** (Long Text, JSON format)
- **Ativa** (Checkbox, Default: true)
- **Prioridade_Execucao** (Number)
- **Data_Criacao** (Date, Auto-populated)
- **Data_Modificacao** (Date)
- **Contador_Uso** (Number, Default: 0)

### Campos Calculados:
- **Status_Uso** (Formula: IF({Contador_Uso} > 10, "Muito Usada", IF({Contador_Uso} > 5, "Usada", "Pouco Usada")))

### Relacionamentos Entre Tabelas

## Relacionamentos Principais:
1. **Usuários → Emails** (1:N) - Um usuário pode ter muitos emails
2. **Usuários → Eventos** (1:N) - Um usuário pode ter muitos eventos
3. **Usuários → Tarefas** (1:N) - Um usuário pode ter muitas tarefas
4. **Usuários → Interações** (1:N) - Um usuário pode ter muitas interações
5. **Usuários → Configurações** (1:N) - Um usuário pode ter muitas configurações

## Relacionamentos Secundários:
6. **Eventos → Tarefas** (1:N) - Um evento pode gerar várias tarefas
7. **Emails → Tarefas** (1:N) - Um email pode gerar várias tarefas
8. **Interações → Emails** (N:1) - Várias interações podem referenciar um email
9. **Interações → Eventos** (N:1) - Várias interações podem referenciar um evento
10. **Interações → Tarefas** (N:1) - Várias interações podem referenciar uma tarefa

### Considerações de Performance

## Índices Recomendados:
- Usuários: Email, Telefone_WhatsApp
- Emails: Usuario + Data_Recebimento
- Eventos: Usuario + Data_Inicio
- Tarefas: Usuario + Status + Data_Prazo
- Interações: Usuario + Data_Hora
- Configurações: Usuario + Tipo_Configuracao

## Estratégias de Otimização:
1. Usar campos de lookup apenas quando necessário
2. Limitar campos de rollup para evitar recálculos excessivos
3. Implementar arquivamento automático de dados antigos
4. Usar visualizações filtradas para reduzir carga de dados
5. Configurar automações com gatilhos específicos

### Limitações do Plano Airtable

## Plano Gratuito:
- 1.200 registros por base
- 2GB de anexos
- Histórico de revisão de 2 semanas
- Automações limitadas

## Plano Plus (Recomendado para MVP):
- 5.000 registros por base
- 5GB de anexos
- Histórico de revisão de 6 meses
- Automações ilimitadas
- Campos de sincronização

## Estratégia para MVP:
- Iniciar com Plano Plus
- Implementar arquivamento automático após 3 meses
- Monitorar uso de registros e anexos
- Planejar migração para plano superior conforme crescimento

