# Modelo de Dados do Airtable para o BestStag

## 1. Visão Geral da Estrutura de Dados

Este documento detalha o modelo de dados completo para o BestStag no Airtable, projetado para suportar todas as funcionalidades do MVP e permitir escalabilidade futura. A estrutura foi concebida para atender diferentes perfis profissionais (advogados, médicos, freelancers, etc.), garantir segurança e privacidade dos dados, e otimizar a performance das integrações.

### 1.1 Princípios de Design

- **Modularidade**: Separação clara de domínios de dados para facilitar manutenção
- **Flexibilidade**: Capacidade de adaptação a diferentes perfis profissionais
- **Segurança**: Proteção de dados sensíveis e conformidade com LGPD
- **Performance**: Otimização para consultas frequentes e integrações
- **Escalabilidade**: Estrutura que suporta crescimento sem redesenho significativo

### 1.2 Bases de Dados

Para otimizar performance e respeitar limites do Airtable, o modelo utiliza múltiplas bases:

1. **Base Principal**: Núcleo do sistema com dados de usuários, configurações e metadados
2. **Base de Comunicações**: Histórico de mensagens, templates e interações
3. **Base de Produtividade**: Tarefas, projetos, eventos e lembretes
4. **Base Financeira**: Transações, categorias e relatórios financeiros
5. **Base de Conhecimento**: Documentos, FAQs e recursos de aprendizado

## 2. Diagrama do Modelo de Dados

```
┌─────────────────────────┐      ┌─────────────────────────┐
│                         │      │                         │
│      BASE PRINCIPAL     │      │   BASE COMUNICAÇÕES     │
│                         │      │                         │
│ ┌─────────────────────┐ │      │ ┌─────────────────────┐ │
│ │      Usuários       │ │      │ │     Mensagens       │ │
│ └─────────────────────┘ │      │ └─────────────────────┘ │
│           │             │      │           │             │
│ ┌─────────────────────┐ │      │ ┌─────────────────────┐ │
│ │      Contatos       │ │      │ │     Templates       │ │
│ └─────────────────────┘ │      │ └─────────────────────┘ │
│           │             │      │           │             │
│ ┌─────────────────────┐ │      │ ┌─────────────────────┐ │
│ │    Configurações    │ │      │ │    Conversações     │ │
│ └─────────────────────┘ │      │ └─────────────────────┘ │
│                         │      │                         │
└─────────────────────────┘      └─────────────────────────┘

┌─────────────────────────┐      ┌─────────────────────────┐
│                         │      │                         │
│   BASE PRODUTIVIDADE    │      │     BASE FINANCEIRA     │
│                         │      │                         │
│ ┌─────────────────────┐ │      │ ┌─────────────────────┐ │
│ │       Tarefas       │ │      │ │     Transações      │ │
│ └─────────────────────┘ │      │ └─────────────────────┘ │
│           │             │      │           │             │
│ ┌─────────────────────┐ │      │ ┌─────────────────────┐ │
│ │      Projetos       │ │      │ │     Categorias      │ │
│ └─────────────────────┘ │      │ └─────────────────────┘ │
│           │             │      │           │             │
│ ┌─────────────────────┐ │      │ ┌─────────────────────┐ │
│ │       Eventos       │ │      │ │      Relatórios     │ │
│ └─────────────────────┘ │      │ └─────────────────────┘ │
│                         │      │                         │
└─────────────────────────┘      └─────────────────────────┘
```

## 3. Base Principal

### 3.1 Tabela: Usuários

**Propósito**: Armazenar informações dos usuários do sistema

**Campos**:
- `ID` (Chave Primária, Autonumeração)
- `Nome` (Texto)
- `Email` (Email, Único)
- `Telefone` (Texto, Único)
- `Perfil_Profissional` (Seleção Única: Advogado, Médico, Freelancer, Empresário, Outro)
- `Área_Atuação` (Texto)
- `Data_Cadastro` (Data/Hora)
- `Último_Acesso` (Data/Hora)
- `Status` (Seleção Única: Ativo, Inativo, Pendente, Bloqueado)
- `Plano` (Seleção Única: Gratuito, Básico, Profissional, Empresarial)
- `Data_Expiração_Plano` (Data)
- `Preferências_Notificação` (Múltipla Seleção: WhatsApp, Email, Push)
- `Fuso_Horário` (Texto)
- `Idioma` (Seleção Única: Português, Inglês, Espanhol)
- `Foto_Perfil` (Anexo)
- `Notas_Internas` (Texto Longo)
- `ID_WhatsApp` (Texto)
- `Opt_In_WhatsApp` (Checkbox)
- `Data_Opt_In` (Data/Hora)
- `Método_Opt_In` (Texto)

**Índices**:
- Email (para login)
- Telefone (para integração WhatsApp)
- Status (para filtragem)

**Considerações de Segurança**:
- Dados pessoais protegidos com permissões restritas
- Não armazenar senhas (autenticação via OAuth)
- Registros de opt-in para conformidade legal

### 3.2 Tabela: Contatos

**Propósito**: Armazenar contatos dos usuários (clientes, fornecedores, etc.)

**Campos**:
- `ID` (Chave Primária, Autonumeração)
- `ID_Usuário` (Link para Usuários)
- `Nome` (Texto)
- `Email` (Email)
- `Telefone` (Texto)
- `Telefone_Secundário` (Texto)
- `Empresa` (Texto)
- `Cargo` (Texto)
- `Tipo` (Seleção Única: Cliente, Fornecedor, Parceiro, Pessoal)
- `Grupo` (Múltipla Seleção, personalizável por usuário)
- `Endereço` (Texto Longo)
- `Cidade` (Texto)
- `Estado` (Texto)
- `País` (Texto)
- `CEP` (Texto)
- `Data_Nascimento` (Data)
- `Data_Cadastro` (Data/Hora)
- `Última_Interação` (Data/Hora)
- `Status` (Seleção Única: Ativo, Inativo, Potencial, Arquivado)
- `Notas` (Texto Longo)
- `Tags` (Múltipla Seleção, personalizável)
- `Foto` (Anexo)
- `Campos_Personalizados` (JSON)
- `Opt_In_Comunicação` (Checkbox)

**Índices**:
- ID_Usuário + Nome (para busca rápida)
- Telefone (para integração WhatsApp)
- Status (para filtragem)

**Considerações de Segurança**:
- Visibilidade restrita ao usuário proprietário
- Campos personalizados para adaptação a diferentes perfis profissionais
- Registro de consentimento para comunicações

### 3.3 Tabela: Configurações

**Propósito**: Armazenar configurações personalizadas por usuário

**Campos**:
- `ID` (Chave Primária, Autonumeração)
- `ID_Usuário` (Link para Usuários)
- `Categoria` (Seleção Única: Geral, Notificações, Privacidade, Integrações, Aparência)
- `Chave` (Texto)
- `Valor` (Texto Longo)
- `Tipo_Dado` (Seleção Única: Texto, Número, Booleano, JSON, Data)
- `Descrição` (Texto)
- `Data_Modificação` (Data/Hora)
- `Versão` (Número)

**Índices**:
- ID_Usuário + Categoria + Chave (para busca rápida)

**Considerações de Segurança**:
- Não armazenar credenciais em texto claro
- Valores sensíveis devem ser criptografados

## 4. Base de Comunicações

### 4.1 Tabela: Mensagens

**Propósito**: Armazenar histórico de mensagens enviadas e recebidas

**Campos**:
- `ID` (Chave Primária, Autonumeração)
- `ID_Usuário` (Link para Usuários)
- `ID_Contato` (Link para Contatos)
- `ID_Conversação` (Link para Conversações)
- `Direção` (Seleção Única: Entrada, Saída)
- `Canal` (Seleção Única: WhatsApp, Email, SMS, Portal)
- `Tipo` (Seleção Única: Texto, Imagem, Áudio, Vídeo, Documento, Localização, Contato)
- `Conteúdo` (Texto Longo)
- `Mídia_URL` (Texto)
- `Mídia_Tipo` (Texto)
- `Mídia_Tamanho` (Número)
- `Data_Envio` (Data/Hora)
- `Data_Entrega` (Data/Hora)
- `Data_Leitura` (Data/Hora)
- `Status` (Seleção Única: Enviado, Entregue, Lido, Falha)
- `Código_Erro` (Texto)
- `Mensagem_Erro` (Texto)
- `ID_Template` (Link para Templates)
- `Variáveis_Template` (JSON)
- `Metadados` (JSON)
- `Tags` (Múltipla Seleção)
- `Intenção_Detectada` (Texto)
- `Sentimento` (Seleção Única: Positivo, Neutro, Negativo)

**Índices**:
- ID_Usuário + ID_Contato + Data_Envio (para histórico)
- ID_Conversação (para agrupamento)
- Status (para monitoramento)

**Considerações de Segurança**:
- Conteúdo sensível deve ser protegido
- Retenção de dados conforme política de privacidade
- Não armazenar dados de cartão de crédito ou senhas

### 4.2 Tabela: Templates

**Propósito**: Armazenar templates de mensagens para uso no WhatsApp

**Campos**:
- `ID` (Chave Primária, Autonumeração)
- `ID_Usuário` (Link para Usuários)
- `Nome` (Texto)
- `Categoria` (Seleção Única: Marketing, Transacional, Serviço, Autenticação)
- `Conteúdo` (Texto Longo)
- `Variáveis` (JSON)
- `Botões` (JSON)
- `Mídia_URL` (Texto)
- `Mídia_Tipo` (Texto)
- `Status_Aprovação` (Seleção Única: Rascunho, Enviado, Aprovado, Rejeitado)
- `Feedback_Rejeição` (Texto Longo)
- `Data_Criação` (Data/Hora)
- `Data_Modificação` (Data/Hora)
- `Data_Aprovação` (Data/Hora)
- `ID_WhatsApp` (Texto)
- `Idioma` (Seleção Única: Português, Inglês, Espanhol)
- `Tags` (Múltipla Seleção)
- `Notas` (Texto Longo)

**Índices**:
- ID_Usuário + Categoria (para filtragem)
- Status_Aprovação (para monitoramento)

**Considerações de Segurança**:
- Validação de conteúdo conforme diretrizes do WhatsApp
- Controle de versão para templates aprovados

### 4.3 Tabela: Conversações

**Propósito**: Agrupar mensagens em conversações lógicas

**Campos**:
- `ID` (Chave Primária, Autonumeração)
- `ID_Usuário` (Link para Usuários)
- `ID_Contato` (Link para Contatos)
- `Canal` (Seleção Única: WhatsApp, Email, SMS, Portal)
- `Assunto` (Texto)
- `Status` (Seleção Única: Ativa, Resolvida, Pendente, Arquivada)
- `Prioridade` (Seleção Única: Baixa, Média, Alta, Urgente)
- `Data_Início` (Data/Hora)
- `Data_Última_Mensagem` (Data/Hora)
- `Data_Resolução` (Data/Hora)
- `Atribuído_A` (Texto)
- `Tags` (Múltipla Seleção)
- `Contexto` (JSON)
- `Notas_Internas` (Texto Longo)
- `ID_Projeto` (Link para Projetos)
- `ID_Tarefa` (Link para Tarefas)

**Índices**:
- ID_Usuário + ID_Contato (para busca)
- Status (para filtragem)
- Data_Última_Mensagem (para ordenação)

**Considerações de Segurança**:
- Acesso restrito a conversações por usuário
- Proteção de contexto sensível

## 5. Base de Produtividade

### 5.1 Tabela: Tarefas

**Propósito**: Gerenciar tarefas e pendências do usuário

**Campos**:
- `ID` (Chave Primária, Autonumeração)
- `ID_Usuário` (Link para Usuários)
- `Título` (Texto)
- `Descrição` (Texto Longo)
- `Status` (Seleção Única: Não Iniciada, Em Andamento, Concluída, Adiada, Cancelada)
- `Prioridade` (Seleção Única: Baixa, Média, Alta, Urgente)
- `Data_Criação` (Data/Hora)
- `Data_Vencimento` (Data/Hora)
- `Data_Conclusão` (Data/Hora)
- `Tempo_Estimado` (Número, minutos)
- `Tempo_Real` (Número, minutos)
- `Recorrência` (Seleção Única: Nenhuma, Diária, Semanal, Mensal, Personalizada)
- `Padrão_Recorrência` (Texto)
- `ID_Projeto` (Link para Projetos)
- `ID_Contato` (Link para Contatos)
- `Tags` (Múltipla Seleção)
- `Categoria` (Seleção Única, personalizável)
- `Notas` (Texto Longo)
- `Anexos` (Anexos)
- `Lembrete` (Data/Hora)
- `Tipo_Lembrete` (Seleção Única: Nenhum, WhatsApp, Email, Push)
- `Subtarefas` (JSON)
- `Progresso` (Número, percentual)

**Índices**:
- ID_Usuário + Status (para filtragem)
- Data_Vencimento (para lembretes)
- ID_Projeto (para agrupamento)

**Considerações de Segurança**:
- Acesso restrito por usuário
- Proteção de anexos sensíveis

### 5.2 Tabela: Projetos

**Propósito**: Organizar tarefas em projetos ou grupos lógicos

**Campos**:
- `ID` (Chave Primária, Autonumeração)
- `ID_Usuário` (Link para Usuários)
- `Nome` (Texto)
- `Descrição` (Texto Longo)
- `Status` (Seleção Única: Planejamento, Em Andamento, Concluído, Em Pausa, Cancelado)
- `Data_Início` (Data)
- `Data_Previsão_Término` (Data)
- `Data_Término_Real` (Data)
- `Progresso` (Número, percentual)
- `Orçamento` (Número)
- `Custo_Real` (Número)
- `Moeda` (Seleção Única: BRL, USD, EUR)
- `ID_Cliente` (Link para Contatos)
- `Equipe` (Múltipla Seleção)
- `Cor` (Texto)
- `Ícone` (Texto)
- `Tags` (Múltipla Seleção)
- `Notas` (Texto Longo)
- `Anexos` (Anexos)
- `Campos_Personalizados` (JSON)

**Índices**:
- ID_Usuário + Status (para filtragem)
- ID_Cliente (para agrupamento)

**Considerações de Segurança**:
- Acesso restrito por usuário
- Proteção de informações financeiras

### 5.3 Tabela: Eventos

**Propósito**: Gerenciar agenda e compromissos

**Campos**:
- `ID` (Chave Primária, Autonumeração)
- `ID_Usuário` (Link para Usuários)
- `Título` (Texto)
- `Descrição` (Texto Longo)
- `Local` (Texto)
- `Local_Virtual` (Texto)
- `Data_Início` (Data/Hora)
- `Data_Fim` (Data/Hora)
- `Dia_Todo` (Checkbox)
- `Recorrência` (Seleção Única: Nenhuma, Diária, Semanal, Mensal, Anual, Personalizada)
- `Padrão_Recorrência` (Texto)
- `Status` (Seleção Única: Confirmado, Tentativo, Cancelado)
- `Visibilidade` (Seleção Única: Público, Privado, Confidencial)
- `Participantes` (JSON)
- `ID_Contato` (Link para Contatos)
- `ID_Projeto` (Link para Projetos)
- `Categoria` (Seleção Única, personalizável)
- `Cor` (Texto)
- `Lembrete` (Múltipla Seleção: 5min, 15min, 30min, 1h, 1d)
- `Tipo_Lembrete` (Seleção Única: Nenhum, WhatsApp, Email, Push)
- `Notas` (Texto Longo)
- `Anexos` (Anexos)
- `ID_Calendário_Externo` (Texto)
- `URL_Calendário_Externo` (Texto)

**Índices**:
- ID_Usuário + Data_Início (para agenda)
- ID_Contato (para relacionamento)
- ID_Projeto (para agrupamento)

**Considerações de Segurança**:
- Respeito à configuração de visibilidade
- Proteção de detalhes de eventos confidenciais

## 6. Base Financeira

### 6.1 Tabela: Transações

**Propósito**: Registrar transações financeiras (manual)

**Campos**:
- `ID` (Chave Primária, Autonumeração)
- `ID_Usuário` (Link para Usuários)
- `Tipo` (Seleção Única: Receita, Despesa, Transferência)
- `Descrição` (Texto)
- `Valor` (Número)
- `Moeda` (Seleção Única: BRL, USD, EUR)
- `Data` (Data)
- `Data_Pagamento` (Data)
- `Status` (Seleção Única: Pendente, Pago, Recebido, Atrasado, Cancelado)
- `Método_Pagamento` (Seleção Única: Dinheiro, Cartão Crédito, Cartão Débito, Transferência, Boleto, Outro)
- `ID_Categoria` (Link para Categorias)
- `ID_Contato` (Link para Contatos)
- `ID_Projeto` (Link para Projetos)
- `Recorrência` (Seleção Única: Nenhuma, Diária, Semanal, Mensal, Anual)
- `Padrão_Recorrência` (Texto)
- `Comprovante` (Anexo)
- `Notas` (Texto Longo)
- `Tags` (Múltipla Seleção)
- `Campos_Personalizados` (JSON)

**Índices**:
- ID_Usuário + Tipo + Data (para relatórios)
- ID_Categoria (para agrupamento)
- Status (para monitoramento)

**Considerações de Segurança**:
- Acesso altamente restrito a dados financeiros
- Proteção de comprovantes e detalhes de pagamento
- Não armazenar dados completos de cartão

### 6.2 Tabela: Categorias

**Propósito**: Classificar transações financeiras

**Campos**:
- `ID` (Chave Primária, Autonumeração)
- `ID_Usuário` (Link para Usuários)
- `Nome` (Texto)
- `Tipo` (Seleção Única: Receita, Despesa, Ambos)
- `Categoria_Pai` (Link para Categorias)
- `Descrição` (Texto)
- `Cor` (Texto)
- `Ícone` (Texto)
- `Orçamento_Mensal` (Número)
- `Sistema` (Checkbox)
- `Ordem` (Número)

**Índices**:
- ID_Usuário + Tipo (para filtragem)
- Categoria_Pai (para hierarquia)

**Considerações de Segurança**:
- Acesso restrito por usuário
- Categorias de sistema protegidas contra exclusão

### 6.3 Tabela: Relatórios

**Propósito**: Armazenar configurações de relatórios financeiros

**Campos**:
- `ID` (Chave Primária, Autonumeração)
- `ID_Usuário` (Link para Usuários)
- `Nome` (Texto)
- `Descrição` (Texto)
- `Tipo` (Seleção Única: Fluxo de Caixa, Orçamento, Categoria, Projeto, Personalizado)
- `Configuração` (JSON)
- `Filtros` (JSON)
- `Período` (Seleção Única: Diário, Semanal, Mensal, Trimestral, Anual, Personalizado)
- `Data_Início` (Data)
- `Data_Fim` (Data)
- `Agrupamento` (Seleção Única: Nenhum, Dia, Semana, Mês, Categoria, Projeto, Contato)
- `Visualização` (Seleção Única: Tabela, Gráfico de Barras, Gráfico de Linha, Pizza)
- `Programação` (Seleção Única: Nenhuma, Diária, Semanal, Mensal)
- `Destinatários` (Texto)
- `Última_Execução` (Data/Hora)
- `Última_Modificação` (Data/Hora)

**Índices**:
- ID_Usuário + Tipo (para filtragem)
- Programação (para automação)

**Considerações de Segurança**:
- Acesso restrito por usuário
- Proteção de configurações com dados sensíveis

## 7. Adaptação para Diferentes Perfis Profissionais

### 7.1 Campos Personalizados

Para atender diferentes perfis profissionais, o sistema utiliza campos personalizados armazenados em formato JSON. Cada perfil profissional terá um conjunto predefinido de campos personalizados que serão renderizados dinamicamente na interface.

**Exemplos por Perfil**:

**Advogados**:
- Contatos: Número OAB, Área de Atuação, Foro Principal
- Projetos: Número Processo, Vara, Comarca, Tipo de Ação
- Tarefas: Prazo Legal, Tipo de Petição, Urgência Judicial

**Médicos**:
- Contatos: CRM, Especialidade, Convênios
- Projetos: Tipo de Tratamento, Duração Prevista
- Tarefas: Tipo de Procedimento, Preparação Necessária

**Freelancers**:
- Contatos: Área de Interesse, Fonte de Captação
- Projetos: Tipo de Entrega, Formato de Cobrança
- Tarefas: Habilidades Necessárias, Entregáveis

### 7.2 Implementação Técnica

Os campos personalizados são implementados através de:

1. **Metatabela de Definições**:
   - Define estrutura, validação e renderização dos campos
   - Associa campos a perfis profissionais
   - Permite configuração pelo usuário

2. **Armazenamento Eficiente**:
   - Campos personalizados armazenados em JSON
   - Índices criados para campos de busca frequente
   - Validação de esquema antes da persistência

3. **Renderização Dinâmica**:
   - Interface adapta-se ao perfil do usuário
   - Campos obrigatórios vs. opcionais claramente indicados
   - Agrupamento lógico de campos relacionados

## 8. Segurança e Privacidade de Dados

### 8.1 Estratégia de Proteção de Dados Sensíveis

1. **Classificação de Dados**:
   - Dados públicos: Visíveis sem restrições
   - Dados internos: Visíveis apenas para o usuário
   - Dados sensíveis: Proteção adicional necessária
   - Dados críticos: Máxima proteção, acesso limitado

2. **Técnicas de Proteção**:
   - **Mascaramento**: Exibição parcial de dados sensíveis (ex: cartões)
   - **Criptografia**: Para dados altamente sensíveis
   - **Tokenização**: Substituição de dados sensíveis por tokens
   - **Isolamento**: Separação física de dados críticos

3. **Controle de Acesso**:
   - Permissões granulares por tabela e campo
   - Registro de acesso a dados sensíveis
   - Autenticação forte para operações críticas

### 8.2 Conformidade com LGPD

1. **Base Legal para Processamento**:
   - Registro claro da base legal para cada tipo de dado
   - Consentimento explícito quando necessário
   - Finalidade específica documentada

2. **Direitos do Titular**:
   - Estrutura para exportação de dados (portabilidade)
   - Mecanismo para correção de informações
   - Processo para exclusão de dados (direito ao esquecimento)

3. **Medidas Técnicas**:
   - Minimização de dados coletados
   - Limitação de retenção com políticas de expiração
   - Anonimização quando possível

## 9. Otimização de Performance

### 9.1 Estratégias de Indexação

1. **Índices Primários**:
   - Chaves de busca frequente
   - Campos de filtragem comum
   - Campos de ordenação padrão

2. **Índices Compostos**:
   - Combinações frequentes de filtros
   - Otimizados para consultas específicas
   - Balanceados para evitar sobrecarga

3. **Campos Calculados**:
   - Pré-computação de valores frequentemente consultados
   - Atualização via automações
   - Documentação clara da fonte de verdade

### 9.2 Particionamento de Dados

1. **Particionamento Horizontal**:
   - Separação por período (dados históricos vs. ativos)
   - Arquivamento automático de dados antigos
   - Links entre bases para referências cruzadas

2. **Particionamento Vertical**:
   - Separação de dados frequentemente acessados
   - Isolamento de campos grandes (texto longo, anexos)
   - Otimização para padrões de acesso específicos

### 9.3 Estratégias de Cache

1. **Cache de Consultas Frequentes**:
   - Resultados armazenados temporariamente
   - Invalidação baseada em eventos
   - Balanceamento entre atualidade e performance

2. **Materialização de Visões**:
   - Snapshots pré-calculados para relatórios
   - Atualização programada em horários de baixo uso
   - Documentação clara de frequência de atualização

## 10. Plano de Implementação

### 10.1 Fases de Implementação

1. **Fase 1: Estrutura Core (Dias 1-2)**
   - Base Principal (Usuários, Contatos)
   - Base de Comunicações (Mensagens, Conversações)
   - Configurações básicas de segurança

2. **Fase 2: Funcionalidades Essenciais (Dias 3-4)**
   - Base de Produtividade (Tarefas, Eventos)
   - Templates de mensagens
   - Campos personalizados por perfil

3. **Fase 3: Funcionalidades Complementares (Dias 5-6)**
   - Base Financeira
   - Relatórios e dashboards
   - Otimizações de performance

4. **Fase 4: Refinamento e Testes (Dia 7)**
   - Validação de integridade referencial
   - Testes de performance
   - Documentação final

### 10.2 Considerações para Escalabilidade Futura

1. **Limites do Airtable**:
   - Plano para particionamento quando próximo de limites
   - Estratégia de arquivamento para dados históricos
   - Monitoramento de uso de recursos

2. **Evolução do Modelo**:
   - Áreas identificadas para expansão futura
   - Campos reservados para funcionalidades planejadas
   - Documentação de intenções de design

3. **Migração Potencial**:
   - Caminhos para migração para banco de dados dedicado
   - Estrutura compatível com SQL quando necessário
   - Pontos de decisão para reavaliação da plataforma

## 11. Conclusão

O modelo de dados do BestStag no Airtable foi projetado para equilibrar flexibilidade, segurança e performance, atendendo às necessidades de diferentes perfis profissionais enquanto mantém a escalabilidade para crescimento futuro. A estrutura modular permite implementação incremental e adaptação contínua, com foco inicial nas funcionalidades essenciais do MVP.

A separação em múltiplas bases otimiza a performance dentro dos limites do Airtable, enquanto as estratégias de campos personalizados garantem adaptabilidade sem redesenho significativo. As considerações de segurança e privacidade foram incorporadas desde o início, garantindo conformidade com requisitos regulatórios.

Este modelo serve como fundação sólida para todas as integrações e automações do BestStag, permitindo a construção de um assistente virtual verdadeiramente útil e contextual para profissionais de diversos segmentos.

---

*Documento preparado por: Gerente de Backend do BestStag*  
*Data: 30 de maio de 2025*  
*Versão: 1.0*
