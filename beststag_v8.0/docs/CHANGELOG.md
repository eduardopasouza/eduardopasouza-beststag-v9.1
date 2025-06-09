## [v8.0.0] - Estrutura inicial

- Criada a pasta beststag_v8.0/
- Adicionados arquivos de frontend (cadastro e chatbot)
- Criado schema do Supabase com RLS mínima
- Criado workflow n8n com integração Twilio, Supabase e OpenAI
- Adicionado teste básico com httpx
- Adicionado .env.example e README com instruções completas

## [v8.0.1] - Suporte a Chat Web
- Adicionado campo de envio em chatbot.html
- Criado webhook webchat para integração com frontend
- Adicionado fallback e logs no fluxo principal do WhatsApp

## [v8.0.2] - Ajustes finais
- Correção de estilo PEP8 nos arquivos Python
- Inclusão da dependência `httpx` para testes de API
- Teste básico de conectividade com a OpenAI
- README atualizado com instruções de lint, testes e variáveis de ambiente

## [v8.0.3] - Documentação aprimorada
- Adicionada dica para usar `black` ao formatar o código
