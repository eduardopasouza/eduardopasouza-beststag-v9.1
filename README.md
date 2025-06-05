
# BestStag v9.1 🚀

**Assistente Virtual Inteligente Multicanal com IA Contextual**

BestStag é um MicroSaaS de assistente virtual que combina Python, React, N8N e Abacus.AI para criar uma solução completa de automação e inteligência artificial contextual.

## 🌟 Características Principais

- **IA Contextual**: Memória inteligente que aprende com cada interação
- **Multicanal**: Suporte para WhatsApp, Telegram, Web e mais
- **Relatórios Inteligentes**: Análises automáticas e insights personalizados
- **Análise de Sentimentos**: Compreensão emocional das conversas
- **Integração Abacus.AI**: Poder da IA empresarial
- **Workflows N8N**: Automações visuais e flexíveis

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Abacus.AI     │
│   React + TS    │◄──►│  FastAPI + Py   │◄──►│   AI Engine     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      N8N        │    │   PostgreSQL    │    │     Redis       │
│   Workflows     │    │   Database      │    │     Cache       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Pré-requisitos

- Docker & Docker Compose
- Python 3.11+
- Node.js 20+
- Git

### Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/beststag-v9.1.git
cd beststag-v9.1

# Execute o setup automático
chmod +x scripts/setup.sh
./scripts/setup.sh

# Inicie o ambiente de desenvolvimento
make dev
```

### Acesso aos Serviços

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **N8N**: http://localhost:5678
- **Adminer**: http://localhost:8080

## 📋 Comandos Disponíveis

```bash
# Desenvolvimento
make dev              # Iniciar ambiente de desenvolvimento
make test             # Executar todos os testes
make lint             # Verificar código
make format           # Formatar código

# Docker
make docker-build     # Build das imagens
make docker-up        # Subir serviços
make docker-down      # Parar serviços
make docker-logs      # Ver logs

# Produção
make prod             # Preparar para produção
make ci               # Pipeline de CI
make security-scan    # Verificações de segurança

# Monitoramento
make health           # Verificar saúde
make status           # Status do projeto
make monitor          # Monitoramento contínuo

# Banco de dados
make backup-db        # Backup do banco
make db-migrate       # Executar migrações
```

## 🔧 Configuração

### Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```bash
# Aplicação
ENVIRONMENT=development
LOG_LEVEL=INFO

# Banco de dados
DATABASE_URL=postgresql://beststag:beststag123@localhost:5432/beststag

# Abacus.AI
ABACUS_API_KEY=your_api_key_here

# N8N
N8N_WEBHOOK_URL=http://localhost:5678/webhook
```

### Estrutura do Projeto

```
beststag-v9.1/
├── src/
│   ├── backend/           # FastAPI application
│   ├── frontend/          # React application
│   ├── python/           # Core Python modules
│   └── workflows/        # N8N workflows
├── config/               # Configurações
├── scripts/              # Scripts de automação
├── tests/                # Testes
├── docs/                 # Documentação
├── docker-compose.yml    # Orquestração Docker
└── Makefile             # Comandos de automação
```

## 🧪 Testes

```bash
# Todos os testes
make test

# Apenas backend
make test-backend

# Apenas frontend
make test-frontend

# Com coverage
pytest tests/ --cov=src/backend --cov-report=html
```

## 📊 Monitoramento

### Health Checks

```bash
# Verificação simples
curl http://localhost:8000/health

# Verificação detalhada
curl http://localhost:8000/health/detailed
```

### Logs Estruturados

Os logs são salvos em formato JSON em `logs/`:

```bash
# Ver logs em tempo real
make docker-logs

# Logs específicos
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Métricas

- **CPU/Memória**: Monitoramento via psutil
- **Banco de dados**: Conexões e performance
- **Redis**: Uso de memória e latência
- **APIs**: Tempo de resposta e erros

## 🔒 Segurança

### Verificações Automáticas

- **Dependências**: Safety check para Python, npm audit para Node.js
- **Código**: Bandit para Python, ESLint para TypeScript
- **Containers**: Trivy scan para vulnerabilidades
- **Secrets**: Verificação de credenciais expostas

### Executar Scan de Segurança

```bash
make security-scan
```

## 🚀 Deploy

### Staging

```bash
./scripts/deploy.sh staging
```

### Produção

```bash
./scripts/deploy.sh production v9.1.0
```

### CI/CD

O projeto inclui workflows GitHub Actions para:

- ✅ Testes automatizados
- 🔍 Análise de código
- 🐳 Build de imagens Docker
- 🔒 Scans de segurança
- 📦 Deploy automático

## 📚 Documentação

- [Guia de Desenvolvimento](docs/development.md)
- [API Reference](docs/api.md)
- [Arquitetura](docs/architecture.md)
- [Deploy](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código

- **Python**: Black, Flake8, MyPy
- **TypeScript**: ESLint, Prettier
- **Commits**: Conventional Commits
- **Testes**: Cobertura mínima de 80%

## 📈 Roadmap

### v9.2 (Próxima)
- [ ] Interface de administração
- [ ] Métricas avançadas
- [ ] Integração com mais canais
- [ ] API de webhooks

### v10.0 (Futuro)
- [ ] Multi-tenancy
- [ ] Marketplace de plugins
- [ ] IA generativa avançada
- [ ] Mobile app

## 🐛 Problemas Conhecidos

- Frontend pode demorar para carregar na primeira execução
- N8N requer configuração manual inicial
- Logs podem crescer rapidamente em desenvolvimento

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Equipe

- **Backend**: Python + FastAPI + Abacus.AI
- **Frontend**: React + TypeScript + Material-UI
- **DevOps**: Docker + GitHub Actions
- **Automação**: N8N + Workflows

## 📞 Suporte

- 📧 Email: suporte@beststag.com
- 💬 Discord: [BestStag Community](https://discord.gg/beststag)
- 📖 Docs: [docs.beststag.com](https://docs.beststag.com)
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/beststag-v9.1/issues)

---

**BestStag v9.1** - Transformando conversas em inteligência 🧠✨
