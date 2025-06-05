
# BestStag v9.1 - Makefile para Automação
# Comandos para desenvolvimento, testes e deploy

.PHONY: help install test test-unit test-integration test-e2e test-performance test-all
.PHONY: lint format security coverage clean setup dev prod logs
.PHONY: docker-build docker-up docker-down docker-logs
.PHONY: backup restore migrate

# Configurações
PYTHON := python3
PIP := pip3
PYTEST := pytest
DOCKER_COMPOSE := docker-compose
PROJECT_NAME := beststag
VERSION := 9.1.0

# Cores para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Help
help: ## Mostra esta ajuda
	@echo "$(BLUE)BestStag v$(VERSION) - Comandos Disponíveis$(NC)"
	@echo "================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Instalação e Setup
install: ## Instala todas as dependências
	@echo "$(BLUE)Instalando dependências...$(NC)"
	$(PIP) install -r config/requirements.txt
	$(PIP) install -r config/requirements_fase2.txt
	$(PIP) install -r tests/requirements.txt
	@echo "$(GREEN)✅ Dependências instaladas$(NC)"

setup: install ## Setup completo do ambiente
	@echo "$(BLUE)Configurando ambiente...$(NC)"
	mkdir -p logs test_reports data/redis data/postgres
	cp .env.example .env 2>/dev/null || true
	@echo "$(GREEN)✅ Ambiente configurado$(NC)"

# Desenvolvimento
dev: ## Inicia ambiente de desenvolvimento
	@echo "$(BLUE)Iniciando ambiente de desenvolvimento...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✅ Ambiente de desenvolvimento iniciado$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:8000$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)N8N: http://localhost:5678$(NC)"

prod: ## Inicia ambiente de produção
	@echo "$(BLUE)Iniciando ambiente de produção...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Ambiente de produção iniciado$(NC)"

# Testes
test: test-unit ## Executa testes básicos (unit)

test-unit: ## Executa testes unitários
	@echo "$(BLUE)Executando testes unitários...$(NC)"
	$(PYTEST) tests/ -m "not integration and not e2e and not performance" -v --tb=short
	@echo "$(GREEN)✅ Testes unitários concluídos$(NC)"

test-integration: ## Executa testes de integração
	@echo "$(BLUE)Executando testes de integração...$(NC)"
	$(PYTEST) tests/integration/ -v --tb=short
	@echo "$(GREEN)✅ Testes de integração concluídos$(NC)"

test-e2e: ## Executa testes end-to-end
	@echo "$(BLUE)Executando testes end-to-end...$(NC)"
	$(PYTEST) tests/e2e/ -v --tb=short
	@echo "$(GREEN)✅ Testes end-to-end concluídos$(NC)"

test-performance: ## Executa testes de performance
	@echo "$(BLUE)Executando testes de performance...$(NC)"
	$(PYTEST) tests/performance/ -v --tb=short
	@echo "$(GREEN)✅ Testes de performance concluídos$(NC)"

test-load: ## Executa testes de carga com Locust
	@echo "$(BLUE)Executando testes de carga...$(NC)"
	locust -f tests/performance/locustfile.py --headless --host=http://localhost:8000 -u 50 -r 5 -t 60s --csv=test_reports/load_test
	@echo "$(GREEN)✅ Testes de carga concluídos$(NC)"

test-all: ## Executa todos os testes
	@echo "$(BLUE)Executando suite completa de testes...$(NC)"
	$(PYTHON) tests/automation/test_runner.py
	@echo "$(GREEN)✅ Todos os testes concluídos$(NC)"

# Qualidade de Código
lint: ## Executa linting do código
	@echo "$(BLUE)Executando linting...$(NC)"
	flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503
	@echo "$(GREEN)✅ Linting concluído$(NC)"

format: ## Formata o código
	@echo "$(BLUE)Formatando código...$(NC)"
	black src/ tests/ --line-length=100
	isort src/ tests/ --profile=black
	@echo "$(GREEN)✅ Código formatado$(NC)"

security: ## Executa análise de segurança
	@echo "$(BLUE)Executando análise de segurança...$(NC)"
	bandit -r src/ -f txt
	safety check
	@echo "$(GREEN)✅ Análise de segurança concluída$(NC)"

coverage: ## Gera relatório de cobertura
	@echo "$(BLUE)Gerando relatório de cobertura...$(NC)"
	$(PYTEST) tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✅ Relatório de cobertura gerado em htmlcov/$(NC)"

# Docker
docker-build: ## Constrói imagens Docker
	@echo "$(BLUE)Construindo imagens Docker...$(NC)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✅ Imagens Docker construídas$(NC)"

docker-up: ## Inicia containers Docker
	@echo "$(BLUE)Iniciando containers...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Containers iniciados$(NC)"

docker-down: ## Para containers Docker
	@echo "$(BLUE)Parando containers...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ Containers parados$(NC)"

docker-logs: ## Mostra logs dos containers
	$(DOCKER_COMPOSE) logs -f

docker-restart: docker-down docker-up ## Reinicia containers

# Logs e Monitoramento
logs: ## Mostra logs da aplicação
	tail -f logs/beststag.log

logs-error: ## Mostra apenas logs de erro
	tail -f logs/beststag.log | grep ERROR

status: ## Mostra status dos serviços
	@echo "$(BLUE)Status dos serviços:$(NC)"
	@curl -s http://localhost:8000/health | jq . 2>/dev/null || echo "Backend: $(RED)Offline$(NC)"
	@curl -s http://localhost:3000 >/dev/null 2>&1 && echo "Frontend: $(GREEN)Online$(NC)" || echo "Frontend: $(RED)Offline$(NC)"
	@redis-cli ping >/dev/null 2>&1 && echo "Redis: $(GREEN)Online$(NC)" || echo "Redis: $(RED)Offline$(NC)"

# Banco de Dados
migrate: ## Executa migrações do banco
	@echo "$(BLUE)Executando migrações...$(NC)"
	alembic upgrade head
	@echo "$(GREEN)✅ Migrações executadas$(NC)"

migrate-create: ## Cria nova migração
	@read -p "Nome da migração: " name; \
	alembic revision --autogenerate -m "$$name"

# Backup e Restore
backup: ## Cria backup do banco de dados
	@echo "$(BLUE)Criando backup...$(NC)"
	mkdir -p backups
	pg_dump $(DATABASE_URL) > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Backup criado$(NC)"

restore: ## Restaura backup do banco de dados
	@echo "$(BLUE)Restaurando backup...$(NC)"
	@read -p "Arquivo de backup: " file; \
	psql $(DATABASE_URL) < $$file
	@echo "$(GREEN)✅ Backup restaurado$(NC)"

# Limpeza
clean: ## Limpa arquivos temporários
	@echo "$(BLUE)Limpando arquivos temporários...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov/ .mypy_cache
	@echo "$(GREEN)✅ Limpeza concluída$(NC)"

clean-all: clean ## Limpeza completa incluindo logs e reports
	@echo "$(BLUE)Limpeza completa...$(NC)"
	rm -rf logs/* test_reports/* data/redis/* data/postgres/*
	@echo "$(GREEN)✅ Limpeza completa concluída$(NC)"

# Utilitários
check: ## Verifica saúde do sistema
	@echo "$(BLUE)Verificando sistema...$(NC)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@echo "Docker: $(shell docker --version 2>/dev/null || echo 'Não instalado')"
	@echo "Redis: $(shell redis-cli --version 2>/dev/null || echo 'Não instalado')"
	@echo "PostgreSQL: $(shell psql --version 2>/dev/null || echo 'Não instalado')"
	@make status

install-dev: ## Instala dependências de desenvolvimento
	@echo "$(BLUE)Instalando dependências de desenvolvimento...$(NC)"
	$(PIP) install black isort flake8 mypy bandit safety pre-commit
	pre-commit install
	@echo "$(GREEN)✅ Dependências de desenvolvimento instaladas$(NC)"

# Comandos compostos
ci: lint security test-all ## Executa pipeline de CI completo

deploy-staging: test-all docker-build ## Deploy para staging
	@echo "$(BLUE)Deploy para staging...$(NC)"
	# Adicionar comandos de deploy específicos
	@echo "$(GREEN)✅ Deploy para staging concluído$(NC)"

deploy-prod: test-all docker-build ## Deploy para produção
	@echo "$(BLUE)Deploy para produção...$(NC)"
	# Adicionar comandos de deploy específicos
	@echo "$(YELLOW)⚠️  Confirme o deploy para produção$(NC)"
	@read -p "Continuar? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(GREEN)✅ Deploy para produção concluído$(NC)"; \
	else \
		echo "$(RED)❌ Deploy cancelado$(NC)"; \
	fi

# Informações
version: ## Mostra versão atual
	@echo "$(BLUE)BestStag v$(VERSION)$(NC)"

info: ## Mostra informações do projeto
	@echo "$(BLUE)BestStag v$(VERSION) - Assistente Virtual Inteligente$(NC)"
	@echo "================================================"
	@echo "Tecnologias: Python + FastAPI + React + N8N + Abacus.AI"
	@echo "Arquitetura: Microserviços com Docker"
	@echo "Testes: Pytest + Locust + E2E"
	@echo "Monitoramento: Prometheus + Grafana"
	@echo "================================================"
	@echo "Comandos principais:"
	@echo "  make setup     - Configurar ambiente"
	@echo "  make dev       - Iniciar desenvolvimento"
	@echo "  make test-all  - Executar todos os testes"
	@echo "  make ci        - Pipeline de CI completo"
	@echo "================================================"

# Default target
.DEFAULT_GOAL := help
