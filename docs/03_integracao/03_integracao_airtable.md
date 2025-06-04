# Integração Airtable para BestStag: Armazenamento e Recuperação

## Objetivo
Este documento detalha a integração do Airtable com o workflow n8n do BestStag para armazenamento e recuperação de mensagens, permitindo a construção de memória contextual básica.

## Estrutura da Base Airtable

### Tabela: Usuários
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Autonumber | ID único do usuário |
| `phone_number` | Single line text | Número de telefone do usuário (chave primária) |
| `name` | Single line text | Nome do usuário |
| `email` | Email | Email do usuário |
| `created_at` | Date & Time | Data de criação do registro |
| `last_interaction` | Date & Time | Data da última interação |
| `interaction_count` | Number | Contador de interações |
| `preferences` | Long text | Preferências do usuário (JSON) |
| `tags` | Multiple select | Tags para categorização |
| `status` | Single select | Status do usuário (Ativo, Inativo, Bloqueado) |

### Tabela: Interações
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Autonumber | ID único da interação |
| `user` | Link | Link para tabela Usuários |
| `direction` | Single select | Entrada (do usuário) ou Saída (do BestStag) |
| `channel` | Single select | Canal de comunicação (WhatsApp, Portal, Email) |
| `message` | Long text | Conteúdo da mensagem |
| `timestamp` | Date & Time | Data e hora da interação |
| `message_id` | Single line text | ID externo da mensagem (ex: Twilio SID) |
| `context` | Long text | Contexto da mensagem (JSON) |
| `intent` | Single select | Intenção detectada |
| `sentiment` | Single select | Sentimento detectado |
| `has_attachment` | Checkbox | Indica se há anexos |

### Tabela: Anexos
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Autonumber | ID único do anexo |
| `interaction` | Link | Link para tabela Interações |
| `file_name` | Single line text | Nome do arquivo |
| `file_type` | Single line text | Tipo MIME do arquivo |
| `file_url` | URL | URL para o arquivo |
| `file_size` | Number | Tamanho do arquivo em bytes |
| `created_at` | Date & Time | Data de upload |

### Tabela: Contexto
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Autonumber | ID único do contexto |
| `user` | Link | Link para tabela Usuários |
| `context_key` | Single line text | Chave do contexto |
| `context_value` | Long text | Valor do contexto (pode ser JSON) |
| `created_at` | Date & Time | Data de criação |
| `updated_at` | Date & Time | Data de atualização |
| `expires_at` | Date & Time | Data de expiração (opcional) |
| `priority` | Number | Prioridade do contexto (1-10) |

## Workflow n8n para Integração Airtable

### 1. Armazenamento de Mensagens

#### Nós Adicionais para o Workflow Existente:

1. **Airtable: Buscar Usuário**
   - **Tipo**: Airtable
   - **Operação**: Buscar registro
   - **Base**: BestStag
   - **Tabela**: Usuários
   - **Filtro**: `{phone_number} = {{ $node["Set (Extrair Dados)"].json.from_number }}`

2. **IF: Usuário Existe**
   - **Tipo**: IF
   - **Condição**: `{{ $node["Airtable: Buscar Usuário"].json.id }} != undefined`

3. **Airtable: Criar Usuário**
   - **Tipo**: Airtable
   - **Operação**: Criar registro
   - **Base**: BestStag
   - **Tabela**: Usuários
   - **Campos**:
     - `phone_number`: `{{ $node["Set (Extrair Dados)"].json.from_number }}`
     - `created_at`: `{{ $now.toISOString() }}`
     - `last_interaction`: `{{ $now.toISOString() }}`
     - `interaction_count`: 1
     - `status`: "Ativo"

4. **Airtable: Atualizar Usuário**
   - **Tipo**: Airtable
   - **Operação**: Atualizar registro
   - **Base**: BestStag
   - **Tabela**: Usuários
   - **ID**: `{{ $node["Airtable: Buscar Usuário"].json.id }}`
   - **Campos**:
     - `last_interaction`: `{{ $now.toISOString() }}`
     - `interaction_count`: `{{ $node["Airtable: Buscar Usuário"].json.interaction_count + 1 }}`

5. **Merge: Usuário**
   - **Tipo**: Merge
   - **Modo**: Merge by position
   - **Entradas**: Saídas de "Airtable: Criar Usuário" e "Airtable: Atualizar Usuário"

6. **Airtable: Salvar Mensagem Recebida**
   - **Tipo**: Airtable
   - **Operação**: Criar registro
   - **Base**: BestStag
   - **Tabela**: Interações
   - **Campos**:
     - `user`: `{{ $node["Merge: Usuário"].json.id }}`
     - `direction`: "Entrada"
     - `channel`: "WhatsApp"
     - `message`: `{{ $node["Set (Extrair Dados)"].json.message_body }}`
     - `timestamp`: `{{ $now.toISOString() }}`
     - `message_id`: `{{ $node["Set (Extrair Dados)"].json.message_sid }}`

7. **Airtable: Salvar Resposta**
   - **Tipo**: Airtable
   - **Operação**: Criar registro
   - **Base**: BestStag
   - **Tabela**: Interações
   - **Campos**:
     - `user`: `{{ $node["Merge: Usuário"].json.id }}`
     - `direction`: "Saída"
     - `channel`: "WhatsApp"
     - `message`: `{{ $node["OpenAI"].json.text }}`
     - `timestamp`: `{{ $now.toISOString() }}`
     - `message_id`: `{{ $node["HTTP Request (Enviar Resposta Twilio)"].json.sid }}`

### 2. Recuperação de Contexto

#### Nós para Recuperação de Contexto:

1. **Airtable: Buscar Interações Recentes**
   - **Tipo**: Airtable
   - **Operação**: Buscar registros
   - **Base**: BestStag
   - **Tabela**: Interações
   - **Filtro**: `{user} = {{ $node["Merge: Usuário"].json.id }}`
   - **Ordenar**: `timestamp DESC`
   - **Limite**: 5

2. **Function: Preparar Contexto**
   - **Tipo**: Function
   - **Código**:
   ```javascript
   // Extrair mensagens recentes
   const interacoes = $input.item.json;
   let contexto = "";
   
   if (Array.isArray(interacoes)) {
     // Formatar histórico de conversa para o prompt
     contexto = interacoes.reverse().map(i => {
       const prefixo = i.direction === "Entrada" ? "Usuário" : "BestStag";
       return `${prefixo}: ${i.message}`;
     }).join("\n");
   }
   
   // Adicionar ao contexto atual
   return {
     contexto_conversa: contexto,
     usuario_id: $node["Merge: Usuário"].json.id,
     interacao_count: $node["Merge: Usuário"].json.interaction_count
   };
   ```

3. **Set: Atualizar Prompt com Contexto**
   - **Tipo**: Set
   - **Ação**: Atualizar o prompt para o OpenAI
   - **Campo**: `prompt`
   - **Valor**:
   ```
   Histórico de conversa recente:
   {{ $node["Function: Preparar Contexto"].json.contexto_conversa }}
   
   Usuário: {{ $node["Set (Extrair Dados)"].json.message_body }}
   ```

## Fluxo Lógico Atualizado

1. Webhook recebe a mensagem do Twilio
2. Validador verifica a autenticidade da requisição
3. Nó Set extrai os dados essenciais
4. Busca usuário no Airtable pelo número de telefone
5. Cria novo usuário ou atualiza usuário existente
6. Salva a mensagem recebida no Airtable
7. Busca interações recentes para contexto
8. Prepara o prompt com contexto para a IA
9. OpenAI processa a mensagem com contexto e gera resposta
10. Salva a resposta no Airtable
11. Envia a resposta de volta ao usuário via Twilio

## Considerações de Implementação

1. **Índices**: Criar índices no Airtable para `phone_number` e `user` para melhor performance
2. **Limpeza de Dados**: Implementar rotina para arquivar interações antigas
3. **Backup**: Configurar backup regular da base Airtable
4. **Limites de API**: Monitorar uso da API do Airtable para evitar limites
5. **Tratamento de Erros**: Implementar tratamento robusto para falhas de API

## Próximos Passos

1. Implementar este workflow no n8n
2. Testar o armazenamento e recuperação de mensagens
3. Validar a construção de contexto
4. Avançar para implementação de comandos básicos
