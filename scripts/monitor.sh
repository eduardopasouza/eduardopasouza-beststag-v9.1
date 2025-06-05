
#!/bin/bash

# BestStag v9.1 - Script de Monitoramento
# Monitora a saúde e performance do sistema

set -e

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/monitor.log"
ALERT_THRESHOLD_CPU=80
ALERT_THRESHOLD_MEMORY=80
ALERT_THRESHOLD_DISK=85

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    local message="[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    echo -e "${BLUE}$message${NC}"
    echo "$message" >> "$LOG_FILE"
}

error() {
    local message="[ERROR] $1"
    echo -e "${RED}$message${NC}" >&2
    echo "$message" >> "$LOG_FILE"
}

success() {
    local message="[SUCCESS] $1"
    echo -e "${GREEN}$message${NC}"
    echo "$message" >> "$LOG_FILE"
}

warning() {
    local message="[WARNING] $1"
    echo -e "${YELLOW}$message${NC}"
    echo "$message" >> "$LOG_FILE"
}

# Função para enviar alertas (placeholder)
send_alert() {
    local severity=$1
    local message=$2
    
    # Aqui você pode integrar com Slack, Discord, email, etc.
    echo "ALERT [$severity]: $message" >> "$LOG_FILE"
    
    # Exemplo de integração com webhook
    if [ -n "$WEBHOOK_URL" ]; then
        curl -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"text\": \"BestStag Alert [$severity]: $message\"}" \
            2>/dev/null || true
    fi
}

# Verificar saúde dos containers
check_containers() {
    log "Verificando containers..."
    
    local containers=("beststag-backend" "beststag-frontend" "beststag-postgres" "beststag-redis")
    local unhealthy_containers=()
    
    for container in "${containers[@]}"; do
        if docker ps --filter "name=$container" --filter "status=running" | grep -q "$container"; then
            # Verificar health status se disponível
            health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-health-check")
            
            if [ "$health_status" = "unhealthy" ]; then
                unhealthy_containers+=("$container")
                warning "Container $container está unhealthy"
            elif [ "$health_status" = "healthy" ] || [ "$health_status" = "no-health-check" ]; then
                success "Container $container está rodando"
            fi
        else
            unhealthy_containers+=("$container")
            error "Container $container não está rodando"
        fi
    done
    
    if [ ${#unhealthy_containers[@]} -gt 0 ]; then
        send_alert "HIGH" "Containers com problemas: ${unhealthy_containers[*]}"
        return 1
    fi
    
    return 0
}

# Verificar uso de recursos
check_resources() {
    log "Verificando uso de recursos..."
    
    # CPU
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    cpu_usage=${cpu_usage%.*}  # Remover decimais
    
    if [ "$cpu_usage" -gt "$ALERT_THRESHOLD_CPU" ]; then
        warning "Alto uso de CPU: ${cpu_usage}%"
        send_alert "MEDIUM" "Alto uso de CPU: ${cpu_usage}%"
    else
        success "Uso de CPU: ${cpu_usage}%"
    fi
    
    # Memória
    memory_info=$(free | grep Mem)
    memory_total=$(echo $memory_info | awk '{print $2}')
    memory_used=$(echo $memory_info | awk '{print $3}')
    memory_usage=$((memory_used * 100 / memory_total))
    
    if [ "$memory_usage" -gt "$ALERT_THRESHOLD_MEMORY" ]; then
        warning "Alto uso de memória: ${memory_usage}%"
        send_alert "MEDIUM" "Alto uso de memória: ${memory_usage}%"
    else
        success "Uso de memória: ${memory_usage}%"
    fi
    
    # Disco
    disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    if [ "$disk_usage" -gt "$ALERT_THRESHOLD_DISK" ]; then
        warning "Alto uso de disco: ${disk_usage}%"
        send_alert "HIGH" "Alto uso de disco: ${disk_usage}%"
    else
        success "Uso de disco: ${disk_usage}%"
    fi
}

# Verificar endpoints da aplicação
check_endpoints() {
    log "Verificando endpoints..."
    
    # Backend health
    if curl -f -s http://localhost:8000/health > /dev/null; then
        success "Backend health check OK"
    else
        error "Backend health check FALHOU"
        send_alert "HIGH" "Backend não está respondendo"
        return 1
    fi
    
    # Frontend
    if curl -f -s http://localhost:3000 > /dev/null; then
        success "Frontend está acessível"
    else
        warning "Frontend não está acessível"
        send_alert "MEDIUM" "Frontend não está acessível"
    fi
    
    # API detalhada
    health_response=$(curl -s http://localhost:8000/health/detailed 2>/dev/null || echo '{"status":"error"}')
    overall_status=$(echo "$health_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('overall_status', 'unknown'))" 2>/dev/null || echo "unknown")
    
    if [ "$overall_status" = "healthy" ]; then
        success "Health check detalhado: $overall_status"
    elif [ "$overall_status" = "degraded" ]; then
        warning "Health check detalhado: $overall_status"
        send_alert "MEDIUM" "Sistema em estado degradado"
    else
        error "Health check detalhado: $overall_status"
        send_alert "HIGH" "Sistema em estado crítico"
    fi
}

# Verificar logs por erros
check_logs() {
    log "Verificando logs por erros..."
    
    # Verificar logs dos últimos 5 minutos por erros
    error_count=$(docker-compose logs --since=5m 2>/dev/null | grep -i error | wc -l)
    
    if [ "$error_count" -gt 10 ]; then
        warning "Muitos erros nos logs: $error_count erros nos últimos 5 minutos"
        send_alert "MEDIUM" "Alto número de erros nos logs: $error_count"
    elif [ "$error_count" -gt 0 ]; then
        log "Erros encontrados nos logs: $error_count"
    else
        success "Nenhum erro recente nos logs"
    fi
}

# Verificar conectividade de banco
check_database() {
    log "Verificando conectividade do banco..."
    
    if docker-compose exec -T postgres pg_isready -U beststag > /dev/null 2>&1; then
        success "PostgreSQL está acessível"
        
        # Verificar número de conexões
        connections=$(docker-compose exec -T postgres psql -U beststag -d beststag -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | xargs || echo "0")
        log "Conexões ativas no banco: $connections"
        
        if [ "$connections" -gt 50 ]; then
            warning "Muitas conexões no banco: $connections"
            send_alert "MEDIUM" "Alto número de conexões no banco: $connections"
        fi
    else
        error "PostgreSQL não está acessível"
        send_alert "HIGH" "Banco de dados não está acessível"
        return 1
    fi
}

# Verificar Redis
check_redis() {
    log "Verificando Redis..."
    
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        success "Redis está acessível"
        
        # Verificar uso de memória do Redis
        memory_usage=$(docker-compose exec -T redis redis-cli info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
        log "Uso de memória do Redis: $memory_usage"
    else
        error "Redis não está acessível"
        send_alert "HIGH" "Redis não está acessível"
        return 1
    fi
}

# Gerar relatório de status
generate_report() {
    local report_file="$PROJECT_DIR/logs/status_report_$(date +%Y%m%d_%H%M%S).json"
    
    log "Gerando relatório de status..."
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "system": {
        "cpu_usage": "$cpu_usage%",
        "memory_usage": "$memory_usage%",
        "disk_usage": "$disk_usage%"
    },
    "containers": {
        "backend": "$(docker ps --filter 'name=beststag-backend' --format '{{.Status}}')",
        "frontend": "$(docker ps --filter 'name=beststag-frontend' --format '{{.Status}}')",
        "postgres": "$(docker ps --filter 'name=beststag-postgres' --format '{{.Status}}')",
        "redis": "$(docker ps --filter 'name=beststag-redis' --format '{{.Status}}')"
    },
    "endpoints": {
        "backend_health": "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health 2>/dev/null || echo 'error')",
        "frontend": "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 2>/dev/null || echo 'error')"
    },
    "database_connections": "$connections",
    "recent_errors": "$error_count"
}
EOF
    
    success "Relatório salvo em: $report_file"
}

# Função principal
main() {
    local mode=${1:-"check"}
    
    case $mode in
        "check")
            log "Iniciando verificação de saúde do sistema..."
            
            check_containers
            check_resources
            check_endpoints
            check_database
            check_redis
            check_logs
            
            success "Verificação de saúde concluída"
            ;;
        
        "watch")
            log "Iniciando monitoramento contínuo..."
            while true; do
                main "check"
                echo ""
                log "Aguardando próxima verificação em 60 segundos..."
                sleep 60
            done
            ;;
        
        "report")
            main "check"
            generate_report
            ;;
        
        *)
            echo "Uso: $0 [check|watch|report]"
            echo ""
            echo "  check   - Executar verificação única"
            echo "  watch   - Monitoramento contínuo"
            echo "  report  - Gerar relatório JSON"
            exit 1
            ;;
    esac
}

# Criar diretório de logs se não existir
mkdir -p "$(dirname "$LOG_FILE")"

# Executar função principal
main "$@"
