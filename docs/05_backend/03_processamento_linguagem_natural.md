# Documentação de Implementação do Sistema de Processamento de Linguagem Natural

Este documento detalha a implementação do Sistema de Processamento de Linguagem Natural do BestStag, incluindo o sistema de classificação de intenções, extração de entidades, análise contextual e memória conversacional.

## 1. Sistema de Classificação de Intenções

### 1.1 Visão Geral

O Sistema de Classificação de Intenções é responsável por identificar o objetivo do usuário em mensagens recebidas via WhatsApp e outros canais. Ele utiliza uma combinação de técnicas de processamento de linguagem natural e engenharia de prompts para classificar mensagens em categorias predefinidas.

### 1.2 Taxonomia de Intenções

A taxonomia segue uma estrutura hierárquica de domínio.ação:

**Domínios Principais:**
- **agenda**: Relacionado a compromissos e eventos
- **tarefa**: Relacionado a tarefas e lembretes
- **financeiro**: Relacionado a finanças e pagamentos
- **contato**: Relacionado a contatos e clientes
- **assistencia**: Relacionado a ajuda e suporte

**Ações por Domínio:**
- **agenda**: criar, atualizar, cancelar, consultar, lembrete
- **tarefa**: criar, atualizar, concluir, listar, priorizar
- **financeiro**: registrar, consultar, categorizar, relatorio
- **contato**: adicionar, atualizar, consultar, remover
- **assistencia**: ajuda, saudacao, feedback, configurar

### 1.3 Implementação Técnica

O classificador utiliza uma abordagem baseada em LLMs (Large Language Models) com engenharia de prompts otimizada:

```python
class ClassificadorIntencoes:
    def __init__(self, api_client, cache_size=100):
        self.api_client = api_client
        self.cache = LRUCache(cache_size)
        self.fallback_system = FallbackHierarquico()
        
    def classificar(self, mensagem, contexto=None):
        # Verificar cache
        cache_key = self._generate_cache_key(mensagem, contexto)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Preparar prompt
        prompt = self._prepare_prompt(mensagem, contexto)
        
        # Chamar API
        try:
            resultado = self.api_client.completar(prompt)
            intencao = self._parse_resultado(resultado)
            confianca = self._calcular_confianca(resultado)
            
            # Aplicar fallback se necessário
            if confianca < LIMIAR_CONFIANCA:
                intencao, confianca = self.fallback_system.aplicar_fallback(
                    mensagem, intencao, confianca, contexto
                )
            
            # Armazenar no cache
            resultado_final = {
                'intencao': intencao,
                'confianca': confianca,
                'timestamp': time.time()
            }
            self.cache[cache_key] = resultado_final
            
            return resultado_final
            
        except Exception as e:
            # Aplicar fallback de emergência
            return self.fallback_system.fallback_emergencia(mensagem, contexto)
```

### 1.4 Sistema de Fallback Hierárquico

O sistema de fallback implementa uma estratégia em camadas para garantir robustez:

```python
class FallbackHierarquico:
    def __init__(self):
        self.palavras_chave = self._carregar_palavras_chave()
        
    def aplicar_fallback(self, mensagem, intencao_primaria, confianca, contexto=None):
        if confianca >= LIMIAR_CONFIANCA:
            return intencao_primaria, confianca
            
        # Fallback 1: Tentar classificar apenas o domínio
        dominio, confianca_dominio = self._classificar_dominio(mensagem, contexto)
        
        if confianca_dominio >= LIMIAR_DOMINIO:
            # Tentar inferir ação baseado em palavras-chave
            acao = self._inferir_acao(mensagem, dominio)
            return f"{dominio}.{acao}", confianca_dominio * 0.9
            
        # Fallback 2: Usar análise de palavras-chave
        intencao_keywords, confianca_keywords = self._classificar_por_keywords(mensagem)
        
        if confianca_keywords >= LIMIAR_KEYWORDS:
            return intencao_keywords, confianca_keywords
            
        # Fallback final: Retornar intenção genérica
        return "assistencia.ajuda", 0.3
```

### 1.5 Engenharia de Prompts

Os prompts foram otimizados com técnicas de few-shot learning:

```
Você é um assistente especializado em classificar mensagens de usuários do BestStag, um assistente virtual acessível via WhatsApp.

Sua tarefa é identificar a intenção do usuário na mensagem abaixo, seguindo a taxonomia de intenções do BestStag.

A taxonomia segue o formato dominio.acao, onde:
- Domínios: agenda, tarefa, financeiro, contato, assistencia
- Ações específicas para cada domínio

Exemplos:
Mensagem: "Agende uma reunião com João amanhã às 15h"
Intenção: agenda.criar

Mensagem: "Mude a reunião de amanhã para 16h"
Intenção: agenda.atualizar

Mensagem: "Cancele a reunião de hoje"
Intenção: agenda.cancelar

Mensagem: "Adicione 'enviar proposta' à minha lista"
Intenção: tarefa.criar

Mensagem: "Quais são minhas tarefas para hoje?"
Intenção: tarefa.listar

Mensagem: "Registre pagamento de R$1.500,00 do cliente XYZ"
Intenção: financeiro.registrar

Mensagem: "Quanto recebi este mês?"
Intenção: financeiro.consultar

Mensagem: "Adicione o contato de Maria: maria@email.com"
Intenção: contato.adicionar

Mensagem: "Como faço para agendar reunião?"
Intenção: assistencia.ajuda

Mensagem: "Bom dia, como você está?"
Intenção: assistencia.saudacao

Agora, classifique a seguinte mensagem:
"{mensagem}"

Responda apenas com a intenção no formato dominio.acao e um valor de confiança entre 0 e 1.
Formato: {"intencao": "dominio.acao", "confianca": 0.XX}
```

### 1.6 Métricas e Avaliação

O sistema é avaliado com as seguintes métricas:

- **Precisão**: Porcentagem de intenções classificadas corretamente
- **Recall**: Capacidade de identificar todas as instâncias de uma intenção
- **F1-Score**: Média harmônica entre precisão e recall
- **Tempo de Resposta**: Tempo médio para classificar uma mensagem
- **Taxa de Fallback**: Porcentagem de mensagens que acionam o sistema de fallback

## 2. Extração de Entidades e Parâmetros

### 2.1 Visão Geral

O sistema de Extração de Entidades é responsável por identificar e extrair informações relevantes das mensagens dos usuários, como datas, horas, pessoas, valores monetários, etc.

### 2.2 Tipos de Entidades Suportadas

- **data**: Datas absolutas e relativas
- **hora**: Horários em diferentes formatos
- **duracao**: Períodos de tempo
- **pessoa**: Nomes de pessoas e títulos
- **local**: Locais de encontro ou eventos
- **valor**: Valores monetários em diferentes moedas
- **tarefa**: Descrições de tarefas
- **prioridade**: Níveis de prioridade
- **status**: Estados de tarefas ou compromissos
- **categoria_financeira**: Categorias de receitas ou despesas

### 2.3 Implementação Técnica

O extrator utiliza uma combinação de expressões regulares e processamento de linguagem natural:

```python
class ExtratorEntidades:
    def __init__(self, api_client=None):
        self.api_client = api_client
        self.cache = {}
        self.regex_patterns = self._carregar_patterns()
        
    def extrair_entidades(self, mensagem, intencao=None):
        # Verificar cache
        cache_key = f"{mensagem}_{intencao}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Inicializar resultado
        entidades = {}
        
        # Extrair entidades com base na intenção
        if intencao:
            dominio, acao = intencao.split(".", 1) if "." in intencao else (intencao, None)
            
            # Extrair entidades específicas por domínio
            if dominio == "agenda":
                entidades.update(self._extrair_entidades_agenda(mensagem))
            elif dominio == "tarefa":
                entidades.update(self._extrair_entidades_tarefa(mensagem))
            elif dominio == "financeiro":
                entidades.update(self._extrair_entidades_financeiro(mensagem))
            elif dominio == "contato":
                entidades.update(self._extrair_entidades_contato(mensagem))
        
        # Extrair entidades comuns independente da intenção
        entidades.update(self._extrair_entidades_comuns(mensagem))
        
        # Usar LLM para entidades complexas se disponível
        if self.api_client and self._requer_llm(entidades, intencao):
            entidades_llm = self._extrair_com_llm(mensagem, intencao, entidades)
            entidades.update(entidades_llm)
        
        # Armazenar no cache
        self.cache[cache_key] = entidades
        
        return entidades
        
    def _extrair_entidades_agenda(self, mensagem):
        entidades = {}
        
        # Extrair data
        data = self._extrair_data(mensagem)
        if data:
            entidades["data"] = data
        
        # Extrair hora
        hora = self._extrair_hora(mensagem)
        if hora:
            entidades["hora"] = hora
        
        # Extrair duração
        duracao = self._extrair_duracao(mensagem)
        if duracao:
            entidades["duracao"] = duracao
        
        # Extrair local
        local = self._extrair_local(mensagem)
        if local:
            entidades["local"] = local
        
        # Extrair pessoas
        pessoas = self._extrair_pessoas(mensagem)
        if pessoas:
            entidades["pessoa"] = pessoas
        
        return entidades
```

### 2.4 Normalização e Validação

O sistema inclui mecanismos de normalização para garantir consistência:

```python
class AnalisadorContextual:
    def __init__(self):
        pass
        
    def analisar_e_normalizar(self, entidades, intencao, mensagem, contexto=None):
        entidades_refinadas = entidades.copy()
        
        # Iterar sobre as entidades extraídas
        for tipo_entidade, valor_entidade in entidades.items():
            if isinstance(valor_entidade, list):
                # Se for uma lista de entidades
                entidades_refinadas[tipo_entidade] = [
                    self._aplicar_refinamentos(item, tipo_entidade, intencao, mensagem, contexto)
                    for item in valor_entidade
                ]
            else:
                # Se for uma única entidade
                entidades_refinadas[tipo_entidade] = self._aplicar_refinamentos(
                    valor_entidade, tipo_entidade, intencao, mensagem, contexto
                )
        
        # Adicionar validações baseadas na intenção
        entidades_refinadas = self._enriquecer_baseado_intencao(entidades_refinadas, intencao, mensagem)
        
        return entidades_refinadas
        
    def _aplicar_refinamentos(self, entidade, tipo_entidade, intencao, mensagem, contexto):
        if tipo_entidade == "data" or tipo_entidade == "hora":
            entidade = self._resolver_tempo_relativo(entidade, contexto)
        elif tipo_entidade == "tarefa":
            entidade = self._refinar_descricao_tarefa(entidade, mensagem)
        elif tipo_entidade == "valor":
            entidade = self._normalizar_valor_financeiro(entidade)
        
        return entidade
```

## 3. Sistema de Contexto e Histórico

### 3.1 Visão Geral

O Sistema de Contexto e Histórico é responsável por manter o contexto conversacional entre interações, permitindo uma experiência mais natural e personalizada.

### 3.2 Estrutura de Dados

```python
class SistemaContextoHistorico:
    def __init__(self, tamanho_janela=10, tamanho_cache=100):
        self.cache = LRUCache(tamanho_cache)
        self.tamanho_janela = tamanho_janela
        self.db_connector = None  # Conector para armazenamento persistente
        
    def adicionar_interacao(self, usuario_id, canal, mensagem, resposta, intencao, entidades):
        # Gerar ID único para a interação
        interacao_id = str(uuid.uuid4())
        
        # Criar registro da interação
        interacao = {
            "id": interacao_id,
            "timestamp": time.time(),
            "usuario_id": usuario_id,
            "canal": canal,
            "mensagem": mensagem,
            "resposta": resposta,
            "intencao": intencao,
            "entidades": entidades
        }
        
        # Obter histórico atual
        historico = self.obter_historico(usuario_id, canal)
        
        # Adicionar nova interação
        historico.append(interacao)
        
        # Limitar tamanho do histórico
        if len(historico) > self.tamanho_janela:
            historico = historico[-self.tamanho_janela:]
        
        # Atualizar cache
        cache_key = f"{usuario_id}_{canal}"
        self.cache[cache_key] = historico
        
        # Persistir se disponível
        if self.db_connector:
            self.db_connector.salvar_interacao(interacao)
        
        return interacao_id
        
    def obter_historico(self, usuario_id, canal, limite=None):
        cache_key = f"{usuario_id}_{canal}"
        
        # Verificar cache
        if cache_key in self.cache:
            historico = self.cache[cache_key]
        else:
            # Carregar do armazenamento persistente se disponível
            if self.db_connector:
                historico = self.db_connector.carregar_historico(usuario_id, canal, self.tamanho_janela)
            else:
                historico = []
            
            # Atualizar cache
            self.cache[cache_key] = historico
        
        # Aplicar limite se especificado
        if limite and limite < len(historico):
            return historico[-limite:]
        
        return historico
        
    def obter_contexto_formatado(self, usuario_id, canal, formato="texto", limite=None):
        historico = self.obter_historico(usuario_id, canal, limite)
        
        if formato == "texto":
            return self._formatar_contexto_texto(historico)
        elif formato == "json":
            return self._formatar_contexto_json(historico)
        else:
            raise ValueError(f"Formato de contexto não suportado: {formato}")
```

### 3.3 Janela Deslizante e Priorização

```python
def _formatar_contexto_texto(self, historico):
    linhas = []
    
    for i, interacao in enumerate(historico):
        # Formatar timestamp
        timestamp = datetime.fromtimestamp(interacao["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        
        # Adicionar cabeçalho da interação
        linhas.append(f"[Interação {i+1} - {timestamp}]")
        
        # Adicionar mensagem do usuário
        linhas.append(f"Usuário: {interacao['mensagem']}")
        
        # Adicionar intenção classificada
        linhas.append(f"Intenção: {interacao['intencao']}")
        
        # Adicionar entidades extraídas (resumidas)
        if interacao["entidades"]:
            entidades_str = ", ".join([f"{k}: {self._resumir_entidade(v)}" for k, v in interacao["entidades"].items()])
            linhas.append(f"Entidades: {entidades_str}")
        
        # Adicionar resposta do sistema
        linhas.append(f"Sistema: {interacao['resposta']}")
        
        # Separador entre interações
        linhas.append("")
    
    return "\n".join(linhas)
```

### 3.4 Mecanismos de Persistência

```python
class AirtableConnector:
    def __init__(self, api_key, base_id, table_name):
        self.api_key = api_key
        self.base_id = base_id
        self.table_name = table_name
        self.client = Airtable(base_id, table_name, api_key)
        
    def salvar_interacao(self, interacao):
        # Preparar dados para Airtable
        record = {
            "ID": interacao["id"],
            "Timestamp": datetime.fromtimestamp(interacao["timestamp"]).isoformat(),
            "Usuario": interacao["usuario_id"],
            "Canal": interacao["canal"],
            "Mensagem": interacao["mensagem"],
            "Resposta": interacao["resposta"],
            "Intencao": interacao["intencao"],
            "Entidades": json.dumps(interacao["entidades"])
        }
        
        # Inserir no Airtable
        self.client.insert(record)
        
    def carregar_historico(self, usuario_id, canal, limite):
        # Consultar Airtable
        formula = f"AND({{Usuario}} = '{usuario_id}', {{Canal}} = '{canal}')"
        records = self.client.get_all(formula=formula, sort=[("Timestamp", "desc")], max_records=limite)
        
        # Converter para formato interno
        historico = []
        for record in records:
            fields = record["fields"]
            interacao = {
                "id": fields["ID"],
                "timestamp": datetime.fromisoformat(fields["Timestamp"]).timestamp(),
                "usuario_id": fields["Usuario"],
                "canal": fields["Canal"],
                "mensagem": fields["Mensagem"],
                "resposta": fields["Resposta"],
                "intencao": fields["Intencao"],
                "entidades": json.loads(fields["Entidades"])
            }
            historico.append(interacao)
        
        # Ordenar por timestamp (mais antigo primeiro)
        historico.sort(key=lambda x: x["timestamp"])
        
        return historico
```

## 4. Integração dos Componentes

### 4.1 Fluxo Completo de Processamento

```python
class ProcessadorMensagens:
    def __init__(self, classificador, extrator, analisador, sistema_contexto):
        self.classificador = classificador
        self.extrator = extrator
        self.analisador = analisador
        self.sistema_contexto = sistema_contexto
        
    def processar_mensagem(self, mensagem, usuario_id, canal):
        # Obter contexto
        contexto = self.sistema_contexto.obter_contexto_formatado(usuario_id, canal)
        
        # Classificar intenção
        resultado_classificacao = self.classificador.classificar(mensagem, contexto)
        intencao = resultado_classificacao["intencao"]
        
        # Extrair entidades
        entidades_brutas = self.extrator.extrair_entidades(mensagem, intencao)
        
        # Analisar e normalizar entidades
        entidades_refinadas = self.analisador.analisar_e_normalizar(
            entidades_brutas, intencao, mensagem, contexto
        )
        
        # Gerar resposta (implementação depende do caso de uso)
        resposta = self._gerar_resposta(intencao, entidades_refinadas, contexto)
        
        # Registrar interação
        self.sistema_contexto.adicionar_interacao(
            usuario_id, canal, mensagem, resposta, intencao, entidades_refinadas
        )
        
        return {
            "intencao": intencao,
            "entidades": entidades_refinadas,
            "resposta": resposta
        }
```

### 4.2 Integração com Make/n8n

```javascript
// Exemplo de fluxo no Make/n8n

// 1. Webhook para receber mensagem do WhatsApp
const webhookData = input.webhook.body;

// 2. Extrair informações da mensagem
const mensagem = webhookData.text;
const usuario_id = webhookData.from;
const canal = "whatsapp";

// 3. Chamar API de processamento
const resultado = await httpRequest({
  method: "POST",
  url: "https://api.beststag.com/processar-mensagem",
  body: {
    mensagem: mensagem,
    usuario_id: usuario_id,
    canal: canal
  }
});

// 4. Processar resultado
const intencao = resultado.intencao;
const entidades = resultado.entidades;
const resposta = resultado.resposta;

// 5. Executar ações baseadas na intenção
if (intencao.startsWith("agenda.")) {
  // Lógica para agenda
  if (intencao === "agenda.criar") {
    // Criar evento no calendário
    await criarEventoCalendario(entidades);
  } else if (intencao === "agenda.consultar") {
    // Consultar eventos
    await consultarEventosCalendario(entidades);
  }
} else if (intencao.startsWith("tarefa.")) {
  // Lógica para tarefas
  if (intencao === "tarefa.criar") {
    // Criar tarefa
    await criarTarefa(entidades);
  } else if (intencao === "tarefa.listar") {
    // Listar tarefas
    await listarTarefas(entidades);
  }
}

// 6. Enviar resposta via WhatsApp
await enviarMensagemWhatsApp(usuario_id, resposta);
```

## 5. Resultados de Testes e Métricas

### 5.1 Métricas de Performance

Os testes incrementais de integração foram executados com sucesso:
- **Taxa de Sucesso de Execução:** 100% (15/15 casos)
- **Tempo Médio de Processamento:** 0.2050 segundos

| Componente    | Sucessos | Falhas | Tempo Médio (s) |
|---------------|----------|--------|-----------------|
| Classificação | 15       | 0      | 0.2042          |
| Extração      | 15       | 0      | 0.0005          |
| Análise       | 15       | 0      | 0.0002          |
| Contexto      | 15       | 0      | 0.0001          |

### 5.2 Métricas de Precisão

- **Taxa de Acerto de Intenções:** 33.33% (5/15)
- **Precisão na Extração de Entidades:** Variável por tipo
  - Data: 100%
  - Hora: 100%
  - Pessoa: 50%
  - Tarefa: 66%
  - Valor: 100%
  - Categoria Financeira: 0%

### 5.3 Oportunidades de Melhoria

1. **Classificação de Intenções**
   - Refinar prompts com exemplos mais diversos
   - Implementar análise de contexto conversacional
   - Aprimorar sistema de fallback hierárquico
   - Aumentar quantidade de palavras-chave por intenção

2. **Extração de Entidades**
   - Aprimorar extração de nomes de pessoas
   - Refinar extração de descrições de tarefas
   - Melhorar identificação de categorias financeiras
   - Implementar validação cruzada entre entidades

3. **Análise Contextual**
   - Implementar análise mais sofisticada para resolver ambiguidades
   - Melhorar inferência de contexto para complementar informações
   - Aprimorar validação de consistência entre entidades

4. **Sistema de Contexto**
   - Implementar mecanismos de priorização mais sofisticados
   - Desenvolver estratégias de esquecimento controlado
   - Aprimorar geração de resumos de contexto

## 6. Próximos Passos

1. **Integração com APIs Reais**
   - Substituir simulações por integrações com OpenAI e Claude
   - Implementar mecanismos de fallback entre provedores
   - Otimizar uso de tokens e custos

2. **Refinamento de Prompts**
   - Desenvolver prompts específicos por domínio
   - Implementar técnicas avançadas de few-shot learning
   - Testar diferentes formatos e estruturas

3. **Aprimoramento da Extração**
   - Implementar extratores específicos para entidades críticas
   - Desenvolver validação contextual mais sofisticada
   - Integrar feedback do usuário para melhorar precisão

4. **Otimização de Performance**
   - Implementar estratégias de cache mais sofisticadas
   - Otimizar tamanho de prompts e uso de tokens
   - Paralelizar processamento quando possível

---

*Esta documentação foi preparada pelo Agente APIs de IA como parte do backup completo do projeto BestStag.*
