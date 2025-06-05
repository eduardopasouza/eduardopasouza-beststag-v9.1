
#!/bin/bash

# BestStag v9.1 - Script de Setup Inicial
# Configura o ambiente de desenvolvimento completo

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar se está no diretório correto
if [ ! -f "package.json" ] || [ ! -f "docker-compose.yml" ]; then
    error "Execute este script no diretório raiz do projeto BestStag"
    exit 1
fi

log "Iniciando setup do BestStag v9.1..."

# Verificar dependências do sistema
log "Verificando dependências do sistema..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    error "Docker não está instalado. Instale o Docker primeiro."
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    error "Docker Compose não está instalado."
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    error "Python 3 não está instalado."
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    error "Node.js não está instalado."
    exit 1
fi

success "Todas as dependências do sistema estão instaladas"

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    log "Criando arquivo .env..."
    cp .env.example .env
    success "Arquivo .env criado. Configure as variáveis necessárias."
else
    warning "Arquivo .env já existe"
fi

# Criar diretórios necessários
log "Criando diretórios necessários..."
mkdir -p logs
mkdir -p backups
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/n8n

# Configurar permissões
chmod 755 logs backups
chmod 700 data/postgres data/redis data/n8n

success "Diretórios criados"

# Instalar dependências Python
log "Instalando dependências Python..."
if command -v pip3 &> /dev/null; then
    pip3 install -r config/requirements.txt
    pip3 install -r config/requirements_fase2.txt
    pip3 install -r config/requirements_backend.txt
else
    python3 -m pip install -r config/requirements.txt
    python3 -m pip install -r config/requirements_fase2.txt
    python3 -m pip install -r config/requirements_backend.txt
fi

success "Dependências Python instaladas"

# Instalar dependências Node.js
log "Instalando dependências Node.js..."
cd src/frontend
npm install
cd ../..

success "Dependências Node.js instaladas"

# Build das imagens Docker
log "Fazendo build das imagens Docker..."
docker-compose build

success "Imagens Docker criadas"

# Inicializar banco de dados
log "Inicializando banco de dados..."
docker-compose up -d postgres redis
sleep 10

# Aguardar postgres estar pronto
log "Aguardando PostgreSQL estar pronto..."
until docker-compose exec postgres pg_isready -U beststag; do
    sleep 2
done

success "Banco de dados inicializado"

# Executar testes básicos
log "Executando testes básicos..."
python3 -m pytest tests/ -v --tb=short || warning "Alguns testes falharam"

# Verificar se frontend compila
log "Verificando build do frontend..."
cd src/frontend
npm run build
cd ../..

success "Frontend compilado com sucesso"

# Configurar Git hooks (se for um repositório Git)
if [ -d ".git" ]; then
    log "Configurando Git hooks..."
    
    # Pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# BestStag pre-commit hook

echo "Executando verificações pre-commit..."

# Lint Python
echo "Verificando código Python..."
flake8 src/backend config/ --max-line-length=127
if [ $? -ne 0 ]; then
    echo "Erro no linting Python. Corrija os problemas antes do commit."
    exit 1
fi

# Lint TypeScript
echo "Verificando código TypeScript..."
cd src/frontend
npm run lint
if [ $? -ne 0 ]; then
    echo "Erro no linting TypeScript. Corrija os problemas antes do commit."
    exit 1
fi
cd ../..

echo "Verificações pre-commit concluídas com sucesso!"
EOF

    chmod +x .git/hooks/pre-commit
    success "Git hooks configurados"
fi

# Criar script de desenvolvimento
log "Criando script de desenvolvimento..."
cat > scripts/dev.sh << 'EOF'
#!/bin/bash
# Script para iniciar ambiente de desenvolvimento

echo "Iniciando ambiente de desenvolvimento BestStag v9.1..."

# Subir serviços
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

echo "Aguardando serviços ficarem prontos..."
sleep 15

echo "Serviços disponíveis:"
echo "- Frontend: http://localhost:3000"
echo "- Backend: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- Adminer: http://localhost:8080"
echo "- Redis Commander: http://localhost:8081"
echo "- N8N: http://localhost:5678"
echo "- MailHog: http://localhost:8025"

echo "Para ver logs: docker-compose logs -f"
echo "Para parar: docker-compose down"
EOF

chmod +x scripts/dev.sh

# Criar script de produção
cat > scripts/prod.sh << 'EOF'
#!/bin/bash
# Script para deploy em produção

echo "Preparando para produção..."

# Executar testes
echo "Executando testes..."
make ci

# Build de produção
echo "Fazendo build de produção..."
make build

# Build Docker
echo "Fazendo build das imagens Docker..."
docker-compose build

echo "Pronto para produção!"
echo "Para deploy: docker-compose up -d"
EOF

chmod +x scripts/prod.sh

success "Scripts de automação criados"

# Verificar saúde do sistema
log "Verificando saúde do sistema..."
docker-compose up -d
sleep 20

# Testar endpoints
if curl -s http://localhost:8000/health > /dev/null; then
    success "Backend está respondendo"
else
    warning "Backend não está respondendo"
fi

if curl -s http://localhost:3000 > /dev/null; then
    success "Frontend está respondendo"
else
    warning "Frontend não está respondendo"
fi

# Parar serviços
docker-compose down

# Resumo final
echo ""
echo "=================================="
echo -e "${GREEN}Setup do BestStag v9.1 concluído!${NC}"
echo "=================================="
echo ""
echo "Próximos passos:"
echo "1. Configure as variáveis no arquivo .env"
echo "2. Execute 'make dev' para iniciar o ambiente de desenvolvimento"
echo "3. Acesse http://localhost:3000 para o frontend"
echo "4. Acesse http://localhost:8000/docs para a documentação da API"
echo ""
echo "Comandos úteis:"
echo "- make help          # Ver todos os comandos disponíveis"
echo "- make dev           # Iniciar ambiente de desenvolvimento"
echo "- make test          # Executar testes"
echo "- make docker-logs   # Ver logs dos serviços"
echo "- make status        # Ver status do projeto"
echo ""
echo "Documentação: docs/README.md"
echo ""

success "Setup concluído com sucesso!"
