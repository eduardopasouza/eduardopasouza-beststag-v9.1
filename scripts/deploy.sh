
#!/bin/bash

# BestStag v9.1 - Script de Deploy
# Automatiza o processo de deploy em diferentes ambientes

set -e

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Função de ajuda
show_help() {
    echo "BestStag v9.1 Deploy Script"
    echo ""
    echo "Uso: $0 [ENVIRONMENT] [VERSION]"
    echo ""
    echo "Ambientes disponíveis:"
    echo "  staging     Deploy para ambiente de staging"
    echo "  production  Deploy para ambiente de produção"
    echo "  local       Deploy local para testes"
    echo ""
    echo "Exemplos:"
    echo "  $0 staging latest"
    echo "  $0 production v9.1.0"
    echo "  $0 local"
}

# Verificar argumentos
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ] && [ "$ENVIRONMENT" != "local" ]; then
    error "Ambiente inválido: $ENVIRONMENT"
fi

log "Iniciando deploy para ambiente: $ENVIRONMENT (versão: $VERSION)"

# Mudar para diretório do projeto
cd "$PROJECT_DIR"

# Verificar se está no branch correto
if [ "$ENVIRONMENT" = "production" ]; then
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        error "Deploy de produção deve ser feito a partir do branch main. Branch atual: $CURRENT_BRANCH"
    fi
fi

# Verificar se há mudanças não commitadas
if [ -n "$(git status --porcelain)" ]; then
    warning "Há mudanças não commitadas no repositório"
    if [ "$ENVIRONMENT" = "production" ]; then
        error "Deploy de produção não pode ter mudanças não commitadas"
    fi
fi

# Executar testes antes do deploy
if [ "$ENVIRONMENT" != "local" ]; then
    log "Executando testes..."
    make ci || error "Testes falharam. Deploy cancelado."
    success "Todos os testes passaram"
fi

# Fazer backup do banco (apenas produção)
if [ "$ENVIRONMENT" = "production" ]; then
    log "Fazendo backup do banco de dados..."
    make backup-db || warning "Falha no backup do banco"
fi

# Build das imagens
log "Fazendo build das imagens Docker..."
docker-compose build

# Tag das imagens com a versão
if [ "$VERSION" != "latest" ]; then
    log "Taggeando imagens com versão $VERSION..."
    docker tag beststag_backend:latest beststag_backend:$VERSION
    docker tag beststag_frontend:latest beststag_frontend:$VERSION
fi

# Deploy baseado no ambiente
case $ENVIRONMENT in
    "local")
        log "Deploy local..."
        docker-compose down
        docker-compose up -d
        ;;
    
    "staging")
        log "Deploy para staging..."
        
        # Configurar ambiente de staging
        export ENVIRONMENT=staging
        export DATABASE_URL=${STAGING_DATABASE_URL}
        export REDIS_URL=${STAGING_REDIS_URL}
        
        # Deploy
        docker-compose -f docker-compose.yml -f docker-compose.staging.yml down
        docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
        ;;
    
    "production")
        log "Deploy para produção..."
        
        # Confirmação adicional para produção
        echo -e "${RED}ATENÇÃO: Deploy para PRODUÇÃO!${NC}"
        read -p "Tem certeza que deseja continuar? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            error "Deploy cancelado pelo usuário"
        fi
        
        # Configurar ambiente de produção
        export ENVIRONMENT=production
        export DATABASE_URL=${PRODUCTION_DATABASE_URL}
        export REDIS_URL=${PRODUCTION_REDIS_URL}
        
        # Deploy com zero downtime
        log "Iniciando deploy com zero downtime..."
        
        # Subir novos containers
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=2
        
        # Aguardar health check
        log "Aguardando health check..."
        sleep 30
        
        # Verificar se novos containers estão saudáveis
        if ! curl -f http://localhost:8000/health; then
            error "Health check falhou. Rollback necessário."
        fi
        
        # Remover containers antigos
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=1
        ;;
esac

# Aguardar serviços ficarem prontos
log "Aguardando serviços ficarem prontos..."
sleep 20

# Verificar health checks
log "Verificando health checks..."

# Backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    success "Backend está saudável"
else
    error "Backend não está respondendo"
fi

# Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    success "Frontend está saudável"
else
    warning "Frontend não está respondendo"
fi

# Executar migrações de banco (se necessário)
if [ "$ENVIRONMENT" != "local" ]; then
    log "Executando migrações do banco..."
    docker-compose exec backend alembic upgrade head || warning "Falha nas migrações"
fi

# Limpar imagens antigas
log "Limpando imagens Docker antigas..."
docker image prune -f

# Notificação de sucesso
success "Deploy para $ENVIRONMENT concluído com sucesso!"

# Informações pós-deploy
echo ""
echo "=================================="
echo -e "${GREEN}Deploy Concluído!${NC}"
echo "=================================="
echo ""
echo "Ambiente: $ENVIRONMENT"
echo "Versão: $VERSION"
echo "Data: $(date)"
echo ""

case $ENVIRONMENT in
    "local")
        echo "URLs disponíveis:"
        echo "- Frontend: http://localhost:3000"
        echo "- Backend: http://localhost:8000"
        echo "- API Docs: http://localhost:8000/docs"
        ;;
    "staging")
        echo "URLs de staging:"
        echo "- Frontend: https://staging.beststag.com"
        echo "- Backend: https://api-staging.beststag.com"
        echo "- API Docs: https://api-staging.beststag.com/docs"
        ;;
    "production")
        echo "URLs de produção:"
        echo "- Frontend: https://beststag.com"
        echo "- Backend: https://api.beststag.com"
        echo "- API Docs: https://api.beststag.com/docs"
        ;;
esac

echo ""
echo "Para monitorar:"
echo "- Logs: make docker-logs"
echo "- Status: make status"
echo "- Health: make health"
echo ""

# Log do deploy
echo "$(date): Deploy $ENVIRONMENT $VERSION concluído" >> logs/deploy.log

success "Deploy finalizado!"
