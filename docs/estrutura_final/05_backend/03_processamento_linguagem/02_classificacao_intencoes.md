# Estratégia de Classificação de Intenções - BestStag

## Introdução

Este documento apresenta a estratégia de classificação de intenções para o processamento de mensagens dos usuários do BestStag via WhatsApp e outros canais. A classificação precisa de intenções é fundamental para garantir respostas adequadas e ações corretas do sistema.

## Taxonomia de Intenções

A taxonomia de intenções foi desenvolvida considerando os principais casos de uso do BestStag e as necessidades típicas dos usuários-alvo (freelancers, pequenas empresas e profissionais). As intenções são organizadas em categorias principais e subcategorias.

### 1. Gerenciamento de Agenda

| Intenção | Descrição | Exemplos de Mensagens |
|----------|-----------|------------------------|
| `agenda.consultar` | Consultar compromissos agendados | "Quais são meus compromissos de hoje?", "Tenho reuniões amanhã?" |
| `agenda.criar` | Criar novo compromisso | "Agende uma reunião com João amanhã às 15h", "Marque consulta com dentista" |
| `agenda.atualizar` | Modificar compromisso existente | "Mude a reunião de amanhã para 16h", "Atualize o local da consulta" |
| `agenda.cancelar` | Cancelar compromisso | "Cancele a reunião de hoje", "Desmarque o almoço de amanhã" |
| `agenda.lembrete` | Configurar lembretes | "Me lembre da reunião 30 minutos antes", "Configure alerta para consulta" |

### 2. Gerenciamento de Tarefas

| Intenção | Descrição | Exemplos de Mensagens |
|----------|-----------|------------------------|
| `tarefa.listar` | Listar tarefas pendentes | "Quais são minhas tarefas para hoje?", "Mostre minha lista de afazeres" |
| `tarefa.criar` | Criar nova tarefa | "Adicione 'enviar proposta' à minha lista", "Crie tarefa para ligar para cliente" |
| `tarefa.atualizar` | Modificar tarefa existente | "Mude o prazo da tarefa para sexta", "Atualize a prioridade da proposta" |
| `tarefa.concluir` | Marcar tarefa como concluída | "Marque 'enviar email' como concluído", "Finalizei a tarefa de ontem" |
| `tarefa.priorizar` | Definir prioridades | "Coloque 'finalizar relatório' como prioridade alta", "Qual minha tarefa mais urgente?" |

### 3. Gerenciamento de Email

| Intenção | Descrição | Exemplos de Mensagens |
|----------|-----------|------------------------|
| `email.resumo` | Solicitar resumo de emails | "Tenho emails importantes hoje?", "Resuma meus emails não lidos" |
| `email.ler` | Ler conteúdo de email específico | "Leia o email do cliente ABC", "O que diz o email sobre o projeto X?" |
| `email.responder` | Responder a email | "Responda ao email de João confirmando presença", "Envie resposta agradecendo" |
| `email.criar` | Criar novo email | "Envie email para Maria sobre o orçamento", "Crie email para o cliente sobre atraso" |
| `email.arquivar` | Arquivar ou organizar emails | "Arquive os emails do projeto concluído", "Marque como spam" |

### 4. Gerenciamento de Clientes/Contatos

| Intenção | Descrição | Exemplos de Mensagens |
|----------|-----------|------------------------|
| `contato.consultar` | Buscar informações de contato | "Qual o telefone do cliente ABC?", "Me dê os dados de contato de João" |
| `contato.adicionar` | Adicionar novo contato | "Adicione Maria como nova cliente", "Salve este contato: João Silva, tel..." |
| `contato.atualizar` | Atualizar informações de contato | "Atualize o email do cliente ABC", "Mude o telefone de contato de Maria" |
| `contato.historico` | Consultar histórico de interações | "Quando foi minha última reunião com cliente ABC?", "Histórico do projeto X" |
| `contato.lembrete` | Configurar lembretes de follow-up | "Me lembre de ligar para o cliente em 3 dias", "Agende follow-up com João" |

### 5. Gerenciamento Financeiro

| Intenção | Descrição | Exemplos de Mensagens |
|----------|-----------|------------------------|
| `financeiro.registrar` | Registrar transação | "Registre pagamento de R$1000 do cliente ABC", "Anote despesa de R$150 com material" |
| `financeiro.consultar` | Consultar informações financeiras | "Quanto recebi este mês?", "Qual o total de despesas da semana?" |
| `financeiro.pendente` | Verificar pagamentos pendentes | "Quais clientes estão com pagamento atrasado?", "Tenho contas a pagar hoje?" |
| `financeiro.relatorio` | Solicitar relatórios financeiros | "Gere relatório financeiro do mês", "Me envie balanço do trimestre" |
| `financeiro.lembrete` | Configurar lembretes financeiros | "Me lembre de cobrar cliente ABC amanhã", "Alerta para pagamento de imposto" |

### 6. Assistência Geral

| Intenção | Descrição | Exemplos de Mensagens |
|----------|-----------|------------------------|
| `assistencia.ajuda` | Solicitar ajuda sobre funcionalidades | "Como faço para agendar reunião?", "Quais são suas funcionalidades?" |
| `assistencia.configurar` | Configurar preferências | "Mude meu fuso horário para Brasília", "Configure notificações diárias às 8h" |
| `assistencia.feedback` | Fornecer feedback | "Isso não funcionou bem", "Gostei muito dessa função" |
| `assistencia.status` | Verificar status do sistema | "Você está funcionando normalmente?", "Por que está demorando para responder?" |
| `assistencia.saudacao` | Saudações e conversas informais | "Olá", "Bom dia", "Como vai?" |

### 7. Integração com Outros Sistemas

| Intenção | Descrição | Exemplos de Mensagens |
|----------|-----------|------------------------|
| `integracao.consultar` | Consultar dados de sistemas integrados | "Qual o status do projeto no Trello?", "Verifique meu saldo no banco" |
| `integracao.atualizar` | Atualizar informações em sistemas integrados | "Mova o card para 'Em Progresso' no Trello", "Atualize status no CRM" |
| `integracao.conectar` | Conectar novos sistemas | "Conecte minha conta do Google Calendar", "Integre com meu Dropbox" |
| `integracao.compartilhar` | Compartilhar informações entre sistemas | "Compartilhe este arquivo no Drive", "Envie este relatório por email" |

## Sistema de Detecção de Entidades

Para complementar a classificação de intenções, é essencial identificar entidades relevantes nas mensagens dos usuários. Estas entidades fornecem contexto e parâmetros necessários para executar as ações solicitadas.

### Entidades Principais

| Tipo de Entidade | Descrição | Exemplos |
|------------------|-----------|----------|
| `pessoa` | Nomes de pessoas, clientes, contatos | "João Silva", "Maria", "cliente ABC" |
| `data` | Datas, períodos, prazos | "amanhã", "próxima sexta", "15/06/2025" |
| `hora` | Horários específicos | "15h", "às 9 da manhã", "14:30" |
| `duracao` | Períodos de tempo | "30 minutos", "2 horas", "uma semana" |
| `local` | Locais físicos ou virtuais | "escritório", "café central", "via Zoom" |
| `valor` | Valores monetários | "R$1000", "mil reais", "€50" |
| `projeto` | Nomes de projetos | "Projeto Redesign", "campanha de marketing" |
| `tarefa` | Descrições de tarefas | "enviar proposta", "ligar para cliente" |
| `prioridade` | Níveis de prioridade | "urgente", "alta prioridade", "pode esperar" |
| `status` | Estados de tarefas/projetos | "pendente", "concluído", "em andamento" |
| `contato` | Informações de contato | "email@exemplo.com", "(11) 98765-4321" |
| `documento` | Tipos de documentos | "contrato", "proposta", "relatório" |
| `servico` | Tipos de serviços | "consultoria", "design", "desenvolvimento" |

## Fluxo de Decisão para Classificação

O processo de classificação de intenções seguirá um fluxo estruturado para garantir precisão e eficiência:

1. **Pré-processamento da Mensagem**
   - Normalização de texto (remoção de acentos, padronização de caixa)
   - Correção ortográfica básica
   - Expansão de abreviações comuns

2. **Classificação Primária**
   - Análise inicial para identificar a categoria principal da intenção
   - Utilização de palavras-chave e padrões para classificação rápida

3. **Extração de Entidades**
   - Identificação de entidades relevantes na mensagem
   - Normalização e validação de entidades (datas, valores, etc.)

4. **Classificação Refinada**
   - Determinação da intenção específica dentro da categoria
   - Consideração do contexto da conversa e histórico recente

5. **Resolução de Ambiguidades**
   - Aplicação de regras para resolver casos ambíguos
   - Consideração de probabilidades para múltiplas intenções possíveis

6. **Validação Final**
   - Verificação de consistência entre intenção e entidades
   - Confirmação de que todos os parâmetros necessários estão presentes

### Diagrama de Fluxo

```
Mensagem do Usuário
       ↓
Pré-processamento
       ↓
Classificação Primária
       ↓
Extração de Entidades
       ↓
Classificação Refinada
       ↓
Resolução de Ambiguidades
       ↓
Validação Final
       ↓
Intenção Classificada + Entidades
```

## Abordagem para Ambiguidades e Casos Especiais

### 1. Intenções Múltiplas

Quando uma mensagem contém múltiplas intenções, o sistema seguirá estas estratégias:

- **Priorização por Ordem**: Processar intenções na ordem em que aparecem na mensagem
- **Priorização por Importância**: Priorizar intenções com maior impacto ou urgência
- **Confirmação Sequencial**: Confirmar e processar uma intenção por vez
- **Agrupamento Lógico**: Agrupar intenções relacionadas para processamento conjunto

Exemplo: "Agende uma reunião com João amanhã às 15h e me lembre de preparar a apresentação"
- Intenções: `agenda.criar` e `tarefa.criar`
- Abordagem: Processar primeiro a criação do compromisso e depois a criação da tarefa relacionada

### 2. Ambiguidade de Intenção

Para casos onde a intenção não está clara:

- **Análise de Contexto**: Utilizar histórico recente da conversa para inferir intenção
- **Probabilidade Ponderada**: Calcular probabilidades para diferentes intenções possíveis
- **Confirmação Explícita**: Solicitar clarificação do usuário quando necessário
- **Ação Padrão Segura**: Escolher a interpretação mais segura quando não for possível confirmar

Exemplo: "Verifique o status"
- Ambiguidade: Pode referir-se a status de tarefa, projeto, pagamento, etc.
- Abordagem: Verificar contexto recente ou solicitar clarificação

### 3. Entidades Incompletas ou Ambíguas

Quando entidades necessárias estão ausentes ou ambíguas:

- **Valores Padrão**: Utilizar valores padrão baseados em preferências do usuário
- **Inferência Contextual**: Deduzir valores a partir do contexto da conversa
- **Solicitação de Complemento**: Pedir informações adicionais ao usuário
- **Confirmação de Suposições**: Sugerir valores e confirmar antes de prosseguir

Exemplo: "Agende reunião com João"
- Entidades faltantes: data, hora, duração
- Abordagem: Sugerir próximo horário disponível baseado em padrões anteriores

### 4. Linguagem Informal e Variações Regionais

Para lidar com diferentes formas de expressão:

- **Normalização Semântica**: Mapear variações linguísticas para termos padronizados
- **Dicionário de Sinônimos**: Manter lista de sinônimos e expressões equivalentes
- **Adaptação Regional**: Considerar variações regionais do português
- **Aprendizado Contínuo**: Atualizar base de conhecimento com novas expressões

Exemplo: "Marca um papo com o João" vs "Agende uma reunião com João"
- Abordagem: Reconhecer que ambas expressões indicam `agenda.criar`

## Implementação Técnica

A implementação da classificação de intenções será realizada utilizando uma combinação de técnicas:

### 1. Abordagem Principal: Prompt Engineering com GPT/Claude

Utilizaremos engenharia de prompts avançada com modelos como GPT-4 ou Claude para classificação de intenções e extração de entidades. Esta abordagem oferece flexibilidade e precisão sem necessidade de treinamento específico.

**Estrutura do Prompt:**
```
[CONTEXTO]
Você é o assistente do BestStag, analisando mensagens de usuários.
Histórico recente da conversa: {histórico}
Perfil do usuário: {perfil}

[TAREFA]
Classifique a intenção da seguinte mensagem e extraia as entidades relevantes.
Mensagem: "{mensagem_do_usuário}"

[FORMATO DE SAÍDA]
{
  "intenção_primária": "categoria.subcategoria",
  "intenção_secundária": "categoria.subcategoria", // se aplicável
  "confiança": 0.95, // nível de confiança de 0 a 1
  "entidades": {
    "tipo_entidade1": "valor1",
    "tipo_entidade2": "valor2"
  },
  "requer_clarificação": false, // true se informações essenciais estiverem faltando
  "pergunta_clarificação": "" // pergunta para obter informações faltantes
}
```

### 2. Abordagem de Fallback: Regras e Palavras-chave

Como sistema de fallback, implementaremos um conjunto de regras baseadas em palavras-chave e padrões para casos simples ou quando a API de IA não estiver disponível.

**Exemplo de Regras:**
- Mensagens começando com "agende", "marque", "crie reunião" → `agenda.criar`
- Mensagens contendo "lembrar" + "reunião/compromisso" → `agenda.lembrete`
- Mensagens começando com "adicione tarefa", "crie tarefa" → `tarefa.criar`

### 3. Sistema Híbrido

O sistema final combinará ambas abordagens:
1. Tentar classificação via API de IA (GPT/Claude)
2. Em caso de falha ou baixa confiança, utilizar sistema de regras
3. Se ambos falharem, solicitar clarificação ao usuário

## Métricas de Avaliação

Para garantir a qualidade da classificação de intenções, monitoraremos as seguintes métricas:

1. **Precisão Geral**: Percentual de intenções corretamente classificadas
2. **Precisão por Categoria**: Desempenho específico para cada categoria de intenção
3. **Taxa de Solicitação de Clarificação**: Frequência com que o sistema precisa pedir mais informações
4. **Tempo de Classificação**: Latência do processo de classificação
5. **Satisfação do Usuário**: Feedback explícito e implícito sobre a precisão das respostas

## Considerações de Implementação

### Limitações Técnicas

- **Latência da API**: Considerar o tempo de resposta das APIs de IA
- **Custo por Token**: Otimizar prompts para reduzir custos de API
- **Limitações de Contexto**: Gerenciar eficientemente o histórico da conversa
- **Ferramentas No-Code/Low-Code**: Adaptar a implementação para plataformas como Make/n8n

### Privacidade e Segurança

- **Minimização de Dados**: Enviar apenas informações essenciais para APIs externas
- **Anonimização**: Remover ou mascarar dados sensíveis antes do processamento
- **Retenção**: Definir políticas claras de retenção para histórico de conversas
- **Consentimento**: Garantir transparência sobre o processamento de mensagens

### Evolução e Manutenção

- **Monitoramento Contínuo**: Acompanhar desempenho e identificar padrões de erro
- **Atualização de Taxonomia**: Revisar e expandir categorias conforme necessário
- **Feedback Loop**: Incorporar feedback dos usuários para melhorar classificação
- **Documentação**: Manter documentação atualizada para facilitar manutenção

## Próximos Passos

1. **Validação da Taxonomia**: Revisar categorias com stakeholders
2. **Prototipagem**: Implementar versão inicial para testes
3. **Avaliação de Desempenho**: Testar com conjunto diversificado de mensagens
4. **Refinamento**: Ajustar baseado nos resultados dos testes
5. **Integração**: Preparar para integração com outros componentes do BestStag

## Conclusão

A estratégia de classificação de intenções apresentada fornece uma base sólida para o processamento de linguagem natural no BestStag. A abordagem híbrida, combinando modelos avançados de IA com sistemas de regras, oferece um equilíbrio entre precisão, custo e resiliência.

Esta estratégia será refinada continuamente com base em feedback e dados de uso real, garantindo que o BestStag compreenda cada vez melhor as necessidades de seus usuários.
