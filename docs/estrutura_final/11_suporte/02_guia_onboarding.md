# Guia de Onboarding para o Projeto BestStag

## Introdução

Este documento serve como guia de onboarding para novos agentes de IA ou equipes que assumirão o desenvolvimento do projeto BestStag. Ele contém informações essenciais sobre a estrutura organizacional, arquitetura técnica, componentes implementados e próximos passos planejados.

## Como Usar Esta Documentação

A documentação está organizada em seções temáticas para facilitar a compreensão e navegação:

1. **Visão Geral do Projeto**: Entenda o propósito, pilares e funcionalidades do BestStag
2. **Estrutura Organizacional**: Conheça a hierarquia de agentes e seus papéis
3. **Arquitetura Técnica**: Compreenda os componentes e suas interações
4. **Implementações Atuais**: Explore os módulos já desenvolvidos
5. **Próximos Passos**: Identifique as prioridades para continuidade

Recomendamos que você leia este guia na ordem apresentada para obter uma compreensão completa do projeto.

## Primeiros Passos

### 1. Familiarize-se com a Visão do Projeto

O BestStag é um MicroSaaS que funciona como assistente virtual inteligente e serviço de análise de dados, acessível via WhatsApp, aplicativo web/mobile e email. O sistema é projetado para atender freelancers, pequenas e médias empresas, indivíduos e diversos profissionais (médicos, advogados, etc.) globalmente.

Os pilares fundamentais do projeto são:
- **Simplicidade Extrema**: Interface intuitiva e fluxos de interação naturais
- **Integração Verdadeira**: Conexão fluida entre canais e serviços externos
- **Personalização Contextual**: Adaptação às necessidades específicas de cada perfil profissional
- **Escalabilidade Gradual**: Evolução progressiva de funcionalidades conforme adoção

### 2. Entenda a Estrutura Organizacional

O BestStag é desenvolvido com uma estrutura hierárquica de agentes de IA:

1. **Dono do BestStag**: Visão estratégica e decisões fundamentais
2. **Agente Diretor**: Gerencia operação e coordena Gerentes de Área
3. **Gerentes de Área (13)**: Responsáveis por domínios específicos
4. **Coordenador de Equipe**: Intermediário entre gerentes e agentes executores
5. **Agentes Especializados**: Executores de tarefas específicas

Como novo agente ou equipe, você se integrará nesta estrutura, recebendo instruções do Coordenador de Equipe e potencialmente colaborando com outros agentes especializados.

### 3. Explore a Arquitetura Técnica

O BestStag utiliza uma arquitetura baseada em ferramentas no-code/low-code:

- **Airtable**: Base de dados central
- **Make/n8n**: Automações e fluxos de integração
- **Bubble/Softr**: Interface web/mobile
- **WhatsApp Business API**: Canal principal de comunicação
- **APIs de IA (OpenAI/Claude)**: Processamento de linguagem natural

Os componentes principais incluem:
1. Sistema de Processamento de Linguagem Natural
2. Integração com WhatsApp Business API
3. Automação com Make/n8n
4. Armazenamento com Airtable
5. Interface Web/Mobile

### 4. Revise as Implementações Atuais

Os seguintes módulos já foram implementados:

- **Sistema de Classificação de Intenções**: Taxonomia, fallback, prompts
- **Extração de Entidades**: Reconhecimento de datas, pessoas, valores, etc.
- **Sistema de Contexto**: Armazenamento de histórico de interações
- **Integração com n8n e WhatsApp**: Estrutura inicial

Revise a documentação detalhada de cada módulo para entender sua implementação e funcionamento.

### 5. Identifique os Próximos Passos

As prioridades atuais para o desenvolvimento são:

1. Integração com APIs reais da OpenAI e Claude
2. Refinamento dos prompts de classificação
3. Aprimoramento da extração de entidades críticas
4. Desenvolvimento de mecanismos de feedback
5. Testes com volumes maiores de dados reais

## Fluxo de Trabalho

Como novo agente ou equipe, você seguirá este fluxo de trabalho:

1. **Recebimento de Instruções**: O Coordenador de Equipe fornecerá instruções específicas
2. **Análise e Planejamento**: Avalie as instruções e planeje sua execução
3. **Desenvolvimento**: Implemente as funcionalidades solicitadas
4. **Testes**: Valide as implementações com testes apropriados
5. **Documentação**: Documente todas as implementações e decisões
6. **Entrega**: Submeta os resultados ao Coordenador de Equipe

## Boas Práticas

Para manter a qualidade e consistência do projeto, siga estas boas práticas:

1. **Documentação Detalhada**: Documente todas as implementações e decisões
2. **Testes Abrangentes**: Valide todas as funcionalidades com testes apropriados
3. **Modularidade**: Mantenha a arquitetura modular para facilitar manutenção
4. **Otimização**: Busque eficiência no uso de recursos e APIs
5. **Foco no Usuário**: Priorize a experiência do usuário em todas as decisões
6. **Comunicação Clara**: Mantenha o Coordenador informado sobre progresso e bloqueios

## Recursos Adicionais

Para aprofundar seu conhecimento sobre o projeto, consulte:

- **Resumo do Projeto**: Visão geral detalhada do BestStag
- **Documentação de Agentes**: Informações sobre cada agente especializado
- **Arquitetura Técnica**: Detalhes sobre componentes e suas interações
- **Implementações**: Documentação técnica dos módulos implementados
- **Resultados de Testes**: Análises de testes realizados

## Suporte

Se você tiver dúvidas ou precisar de esclarecimentos adicionais:

1. Consulte a documentação detalhada disponível
2. Solicite informações ao Coordenador de Equipe
3. Peça esclarecimentos sobre interações com outros agentes

---

*Este guia de onboarding foi preparado pelo Agente APIs de IA como parte do backup completo do projeto BestStag.*
