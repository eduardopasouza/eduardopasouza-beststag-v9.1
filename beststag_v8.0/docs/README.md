# BestStag v8.0 - MVP Simplificado

Esta é a versão **MVP (Minimum Viable Product) v8.0** do BestStag. Ela oferece uma versão retroativa **simplificada** do assistente virtual, criada para pilotos iniciais com usuários reais. **Importante:** Esta versão *não substitui* a BestStag v9.1; trata-se de uma alternativa paralela, de menor complexidade, para validação rápida de conceitos com baixo custo e esforço.

## ✨ Visão Geral
- **WhatsApp (Twilio)** como principal interface de usuário – os usuários interagem via mensagens de WhatsApp.
- **Supabase** como backend _low-code_ (banco de dados & autenticação simples) – armazena usuários e mensagens.
- **n8n** como orquestrador de fluxos – integra WhatsApp/Twilio, consulta/cria registros no Supabase e chama a API do **OpenAI GPT-4** para gerar respostas.
- **OpenAI GPT-4** para processamento de linguagem natural – gera respostas inteligentes às mensagens dos usuários.

Esta arquitetura simplificada reutiliza integrações existentes da v9.1 (Twilio, OpenAI, etc.), mas sem a complexidade de sistemas adicionais. O objetivo é fornecer um assistente funcional de forma **100% low-code**, facilitando testes rápidos com usuários.

## ⚙️ Configuração do Ambiente
Antes de executar, configure as variáveis de ambiente no arquivo `.env` (ou configure diretamente nos serviços SaaS utilizados). Use o arquivo `.env.example` como referência. Principais variáveis:
- **Credenciais do Twilio:** SID da conta, Auth Token e número de WhatsApp configurado.
- **Dados do Supabase:** URL do projeto e chaves (pública e service role).
- **Chave da API OpenAI:** chave secreta para acessar o GPT-4 (ou modelo escolhido).
- **URL do Webhook (n8n):** endpoint público do fluxo no n8n que receberá mensagens do Twilio.

Edite o arquivo `.env` local com esses valores. *Nunca* comite suas chaves secretas.

## 🗄️ Inicialização do Banco de Dados (Supabase)
Em seu projeto Supabase, crie as tabelas necessárias usando os scripts em `supabase_schema/`:
- Execute `usuarios.sql` para criar a tabela de usuários e definir regras de acesso (RLS).
- Execute `mensagens.sql` para criar a tabela de mensagens e definir RLS.

## 🤖 Configuração do Workflow n8n
Importe o fluxo `n8n_workflows/whatsapp_fluxo_base.json` em sua instância do n8n. Ajuste as credenciais do Twilio, Supabase e OpenAI conforme suas chaves. Publique o webhook e configure a URL resultante no Twilio.

## 💻 Testando o MVP
1. Abra `frontend/cadastro.html` e cadastre um usuário de teste.
2. Envie uma mensagem WhatsApp para o número configurado. Você receberá a resposta gerada pelo GPT-4.
3. Acompanhe o histórico em `frontend/chatbot.html` consultando as mensagens salvas no Supabase.

## ⚠️ Notas Importantes
- Esta versão é apenas para testes e validação rápida. Reforce políticas de segurança antes de uso em produção.
