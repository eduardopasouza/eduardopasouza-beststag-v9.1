
# BestStag v9.1 - Suite de Testes End-to-End

Esta é a suite completa de testes para o BestStag v9.1, incluindo testes end-to-end, de integração, performance e automação.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Estrutura dos Testes](#estrutura-dos-testes)
- [Configuração](#configuração)
- [Execução](#execução)
- [Tipos de Teste](#tipos-de-teste)
- [Relatórios](#relatórios)
- [CI/CD](#cicd)
- [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

A suite de testes do BestStag v9.1 foi projetada para validar todos os aspectos críticos do sistema:

- **Fluxo Completo**: Simulação real de mensagens WhatsApp → IA → Resposta
- **Integrações**: Validação de todas as APIs (Abacus.AI, WhatsApp, N8N)
- **Performance**: Testes de carga, latência e throughput
- **Confiabilidade**: Validação de cache, circuit breaker e recovery
- **Segurança**: Validação de assinaturas e rate limiting

## 📁 Estrutura dos Testes

```
tests/
├── __init__.py                 # Inicialização da suite
├── conftest.py                 # Fixtures e configurações globais
├── pytest.ini                 # Configuração do pytest
├── requirements.txt            # Dependências de teste
├── README.md                   # Esta documentação
│
├── e2e/                        # Testes End-to-End
│   ├── __init__.py
│   └── test_full_flow.py       # Fluxos completos do sistema
│
├── integration/                # Testes de Integração
│   ├── __init__.py
│   ├── test_api_integrations.py        # APIs e integrações
│   └── test_cache_circuit_breaker.py   # Cache e circuit breaker
│
├── performance/                # Testes de Performance
│   ├── __init__.py
│   ├── locustfile.py          # Testes de carga com Locust
│   └── test_latency.py        # Testes de latência
│
└── automation/                # Automação de Testes
    ├── __init__.py
    └── test_runner.py         # Runner automatizado
```

## ⚙️ Configuração

### Pré-requisitos

1. **Python 3.11+**
2. **Redis** (para cache e queue)
3. **PostgreSQL** (opcional, para testes completos)
4. **Docker** (opcional, para containers de teste)

### Instalação

```bash
# 1. Instalar dependências de teste
pip install -r tests/requirements.txt

# 2. Configurar variáveis de ambiente
export ENVIRONMENT=test
export LOG_LEVEL=DEBUG
export REDIS_URL=redis://localhost:6379/1
export WHATSAPP_WEBHOOK_SECRET=test_webhook_secret_123
export WHATSAPP_VERIFY_TOKEN=test_verify_token_456
export ABACUS_API_KEY=test_abacus_key
export ABACUS_DEPLOYMENT_ID=test_deployment_123

# 3. Iniciar serviços necessários
redis-server --daemonize yes
```

### Configuração Avançada

Para testes completos com banco de dados:

```bash
# PostgreSQL para testes
export DATABASE_URL=postgresql://test_user:test_password@localhost:5432/test_beststag

# Docker Compose para ambiente completo
docker-compose -f docker-compose.dev.yml up -d redis postgres
```

## 🚀 Execução

### Execução Rápida

```bash
# Todos os testes
python tests/automation/test_runner.py

# Tipo específico
python tests/automation/test_runner.py --type e2e

# Sem testes de performance
python tests/automation/test_runner.py --no-performance
```

### Execução Manual com Pytest

```bash
# Testes unitários
pytest tests/ -m "not integration and not e2e and not performance" -v

# Testes de integração
pytest tests/integration/ -v

# Testes end-to-end
pytest tests/e2e/ -v

# Testes de performance
pytest tests/performance/ -v

# Com cobertura
pytest tests/ --cov=src --cov-report=html
```

### Testes de Carga com Locust

```bash
# Teste de carga básico
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Teste automatizado
locust -f tests/performance/locustfile.py \
  --headless \
  --host=http://localhost:8000 \
  -u 50 -r 5 -t 60s \
  --csv=results/load_test
```

## 🧪 Tipos de Teste

### 1. Testes End-to-End (E2E)

**Objetivo**: Validar fluxos completos do sistema

**Cenários Cobertos**:
- ✅ Fluxo completo de mensagem de texto
- ✅ Processamento de mensagens com imagem
- ✅ Memória contextual entre conversas
- ✅ Análise de sentimento
- ✅ Tratamento de erros e fallbacks

**Execução**:
```bash
pytest tests/e2e/ -v
```

### 2. Testes de Integração

**Objetivo**: Validar integrações entre componentes

**Cenários Cobertos**:
- ✅ Integração com Abacus.AI
- ✅ Webhook WhatsApp com validação de assinatura
- ✅ Cache inteligente e circuit breaker
- ✅ Queue assíncrona com Redis
- ✅ Fallbacks e recovery

**Execução**:
```bash
pytest tests/integration/ -v
```

### 3. Testes de Performance

**Objetivo**: Validar performance e escalabilidade

**Métricas Avaliadas**:
- ✅ Latência de webhook (< 100ms)
- ✅ Throughput de API (> 100 req/s)
- ✅ Tempo de resposta E2E (< 2s)
- ✅ Uso de memória
- ✅ Comportamento sob carga

**Execução**:
```bash
pytest tests/performance/ -v
```

### 4. Testes de Carga

**Objetivo**: Validar comportamento sob alta carga

**Cenários**:
- ✅ Load Test: 50 usuários simultâneos
- ✅ Stress Test: 100+ usuários
- ✅ Spike Test: Picos de tráfego
- ✅ Endurance Test: Execução prolongada

**Execução**:
```bash
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

## 📊 Relatórios

### Relatórios Automáticos

Os testes geram automaticamente:

- **HTML Reports**: `test_reports/report_*.html`
- **Coverage Reports**: `test_reports/coverage_*.xml`
- **JUnit XML**: `test_reports/junit_*.xml`
- **Performance CSV**: `test_reports/locust_*.csv`
- **Summary Report**: `test_reports/summary_report_*.html`

### Visualização de Relatórios

```bash
# Abrir relatório HTML no navegador
python -m webbrowser test_reports/summary_report_latest.html

# Servir relatórios via HTTP
python -m http.server 8080 --directory test_reports
```

### Métricas de Qualidade

**Metas de Qualidade**:
- ✅ Cobertura de código: > 80%
- ✅ Taxa de sucesso: > 95%
- ✅ Latência média: < 500ms
- ✅ Zero vazamentos de memória
- ✅ Zero falhas de segurança

## 🔄 CI/CD

### GitHub Actions

O pipeline de CI/CD executa automaticamente:

1. **Unit Tests** - A cada push/PR
2. **Integration Tests** - Após unit tests
3. **E2E Tests** - Após integration tests
4. **Performance Tests** - Agendado diariamente
5. **Security Scan** - A cada push

### Configuração Local

```bash
# Simular pipeline CI/CD localmente
act -j unit-tests
act -j integration-tests
act -j e2e-tests
```

### Triggers Especiais

- `[perf]` no commit message: Executa testes de performance
- `[skip ci]` no commit message: Pula CI/CD
- Schedule diário: Executa suite completa

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Redis não está rodando
```bash
# Verificar status
redis-cli ping

# Iniciar Redis
redis-server --daemonize yes

# Verificar porta
netstat -tlnp | grep 6379
```

#### 2. Testes de timeout
```bash
# Aumentar timeout
pytest tests/ --timeout=600

# Executar teste específico
pytest tests/e2e/test_full_flow.py::TestFullWhatsAppFlow::test_complete_text_message_flow -v
```

#### 3. Falhas de assinatura
```bash
# Verificar variáveis de ambiente
echo $WHATSAPP_WEBHOOK_SECRET

# Regenerar assinatura
python -c "
import hmac, hashlib
secret = 'test_webhook_secret_123'
payload = b'{\"test\": \"data\"}'
sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
print(f'sha256={sig}')
"
```

#### 4. Problemas de dependências
```bash
# Reinstalar dependências
pip install -r tests/requirements.txt --force-reinstall

# Verificar conflitos
pip check

# Ambiente limpo
python -m venv test_env
source test_env/bin/activate
pip install -r tests/requirements.txt
```

### Logs de Debug

```bash
# Executar com logs detalhados
pytest tests/ -v -s --log-cli-level=DEBUG

# Salvar logs em arquivo
pytest tests/ --log-file=debug.log --log-file-level=DEBUG

# Filtrar logs específicos
pytest tests/ --log-cli-level=DEBUG -k "test_webhook"
```

### Performance Debug

```bash
# Profiling de testes
pytest tests/ --profile

# Análise de memória
pytest tests/ --memray

# Benchmark específico
pytest tests/performance/test_latency.py --benchmark-only
```

## 📈 Métricas e Monitoramento

### Métricas Coletadas

- **Latência**: Tempo de resposta por endpoint
- **Throughput**: Requisições por segundo
- **Taxa de Erro**: Percentual de falhas
- **Uso de Memória**: Consumo durante execução
- **Cache Hit Rate**: Eficiência do cache
- **Circuit Breaker**: Estados e transições

### Alertas

O sistema de testes monitora:
- ⚠️ Latência > 1s
- ⚠️ Taxa de erro > 5%
- ⚠️ Uso de memória > 500MB
- ⚠️ Cache hit rate < 70%
- ⚠️ Falhas de circuit breaker

## 🤝 Contribuição

### Adicionando Novos Testes

1. **Criar arquivo de teste**:
```python
# tests/integration/test_new_feature.py
import pytest

@pytest.mark.integration
async def test_new_feature():
    # Implementar teste
    pass
```

2. **Adicionar fixtures se necessário**:
```python
# tests/conftest.py
@pytest.fixture
async def new_feature_setup():
    # Setup específico
    yield
    # Cleanup
```

3. **Executar e validar**:
```bash
pytest tests/integration/test_new_feature.py -v
```

### Padrões de Código

- ✅ Usar async/await para operações assíncronas
- ✅ Nomear testes descritivamente
- ✅ Usar fixtures para setup/cleanup
- ✅ Adicionar docstrings explicativas
- ✅ Validar tanto sucesso quanto falha
- ✅ Incluir assertions de performance

## 📞 Suporte

Para dúvidas ou problemas:

1. **Verificar logs**: `test_reports/` e `tests.log`
2. **Consultar documentação**: Este README
3. **Executar diagnóstico**: `python tests/automation/test_runner.py --type unit`
4. **Reportar issues**: Incluir logs e configuração

---

**BestStag v9.1** - Suite de Testes End-to-End Completa
*Validação robusta para assistente virtual inteligente*
