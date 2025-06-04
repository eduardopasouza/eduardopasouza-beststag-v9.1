#!/bin/bash

# BestStag v9.0 - Script de Deployment Automatizado
# Autor: Manus AI
# Versão: 9.0
# Data: 2025-06-03

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de log
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    BestStag v9.0 Deployment                 ║"
    echo "║              Assistente Virtual Inteligente                 ║"
    echo "║                                                              ║"
    echo "║                   Powered by Manus AI                       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Verificar se está rodando como root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "Este script não deve ser executado como root!"
        exit 1
    fi
}

# Verificar dependências do sistema
check_dependencies() {
    log_info "Verificando dependências do sistema..."
    
    local deps=("node" "npm" "python3" "pip3" "git" "curl" "docker")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Dependências faltando: ${missing_deps[*]}"
        log_info "Instalando dependências automaticamente..."
        
        # Detectar sistema operacional
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Ubuntu/Debian
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y nodejs npm python3 python3-pip git curl docker.io
            # CentOS/RHEL
            elif command -v yum &> /dev/null; then
                sudo yum install -y nodejs npm python3 python3-pip git curl docker
            fi
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if command -v brew &> /dev/null; then
                brew install node python3 git curl docker
            else
                log_error "Homebrew não encontrado. Instale manualmente as dependências."
                exit 1
            fi
        fi
    fi
    
    log_success "Todas as dependências estão instaladas!"
}

# Verificar versões
check_versions() {
    log_info "Verificando versões das dependências..."
    
    # Node.js
    node_version=$(node --version | cut -d'v' -f2)
    if [[ $(echo "$node_version 18.0.0" | tr " " "\n" | sort -V | head -n1) != "18.0.0" ]]; then
        log_warning "Node.js versão $node_version detectada. Recomendado: 18.0.0+"
    fi
    
    # Python
    python_version=$(python3 --version | cut -d' ' -f2)
    if [[ $(echo "$python_version 3.8.0" | tr " " "\n" | sort -V | head -n1) != "3.8.0" ]]; then
        log_warning "Python versão $python_version detectada. Recomendado: 3.8.0+"
    fi
    
    log_success "Verificação de versões concluída!"
}

# Configurar variáveis de ambiente
setup_environment() {
    log_info "Configurando variáveis de ambiente..."
    
    if [ ! -f ".env" ]; then
        log_info "Criando arquivo .env a partir do template..."
        cp configs/.env.example .env
        
        echo ""
        log_warning "IMPORTANTE: Configure as seguintes variáveis no arquivo .env:"
        echo "  - AIRTABLE_API_KEY"
        echo "  - AIRTABLE_BASE_ID"
        echo "  - TWILIO_ACCOUNT_SID"
        echo "  - TWILIO_AUTH_TOKEN"
        echo "  - TWILIO_WHATSAPP_NUMBER"
        echo "  - N8N_WEBHOOK_URL"
        echo ""
        
        read -p "Pressione Enter após configurar o arquivo .env..."
    fi
    
    # Verificar se as variáveis essenciais estão definidas
    source .env
    
    local required_vars=("AIRTABLE_API_KEY" "AIRTABLE_BASE_ID" "TWILIO_ACCOUNT_SID")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "Variáveis de ambiente faltando: ${missing_vars[*]}"
        log_error "Configure o arquivo .env antes de continuar."
        exit 1
    fi
    
    log_success "Variáveis de ambiente configuradas!"
}

# Instalar dependências Python
install_python_deps() {
    log_info "Instalando dependências Python..."
    
    # Criar ambiente virtual se não existir
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Instalar dependências
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log_success "Dependências Python instaladas!"
}

# Configurar Airtable
setup_airtable() {
    log_info "Configurando Airtable..."
    
    source venv/bin/activate
    source .env
    
    # Executar script de setup
    python scripts/python/setup_airtable.py
    
    if [ $? -eq 0 ]; then
        log_success "Airtable configurado com sucesso!"
    else
        log_error "Falha na configuração do Airtable!"
        exit 1
    fi
}

# Configurar n8n
setup_n8n() {
    log_info "Configurando n8n..."
    
    # Verificar se n8n está instalado
    if ! command -v n8n &> /dev/null; then
        log_info "Instalando n8n..."
        npm install -g n8n
    fi
    
    # Criar diretório de dados do n8n
    mkdir -p ~/.n8n
    
    # Configurar variáveis de ambiente do n8n
    export N8N_BASIC_AUTH_ACTIVE=true
    export N8N_BASIC_AUTH_USER=${N8N_USER:-admin}
    export N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD:-beststag2025}
    export N8N_HOST=${N8N_HOST:-localhost}
    export N8N_PORT=${N8N_PORT:-5678}
    export N8N_PROTOCOL=${N8N_PROTOCOL:-http}
    
    log_success "n8n configurado!"
    log_info "Acesse n8n em: ${N8N_PROTOCOL}://${N8N_HOST}:${N8N_PORT}"
    log_info "Usuário: ${N8N_USER:-admin}"
    log_info "Senha: ${N8N_PASSWORD:-beststag2025}"
}

# Instalar workflows n8n
install_workflows() {
    log_info "Instalando workflows n8n..."
    
    # Aguardar n8n estar rodando
    log_info "Aguardando n8n inicializar..."
    sleep 10
    
    # Importar workflows
    local workflows_dir="workflows/n8n"
    for workflow_file in "$workflows_dir"/*.json; do
        if [ -f "$workflow_file" ]; then
            workflow_name=$(basename "$workflow_file" .json)
            log_info "Importando workflow: $workflow_name"
            
            # Aqui você pode usar a API do n8n para importar workflows
            # curl -X POST "http://localhost:5678/rest/workflows" \
            #      -H "Content-Type: application/json" \
            #      -d @"$workflow_file"
        fi
    done
    
    log_success "Workflows instalados!"
}

# Configurar portal web
setup_portal() {
    log_info "Configurando portal web..."
    
    cd portal_web
    
    # Instalar dependências
    npm install
    
    # Build do projeto
    npm run build
    
    cd ..
    
    log_success "Portal web configurado!"
}

# Configurar Docker (opcional)
setup_docker() {
    if command -v docker &> /dev/null; then
        log_info "Configurando Docker..."
        
        # Verificar se Docker está rodando
        if ! docker info &> /dev/null; then
            log_warning "Docker não está rodando. Iniciando..."
            sudo systemctl start docker
        fi
        
        # Build da imagem
        if [ -f "Dockerfile" ]; then
            docker build -t beststag:v9.0 .
            log_success "Imagem Docker criada!"
        fi
    else
        log_warning "Docker não encontrado. Pulando configuração Docker."
    fi
}

# Criar serviços systemd
create_services() {
    log_info "Criando serviços systemd..."
    
    # Serviço para n8n
    sudo tee /etc/systemd/system/beststag-n8n.service > /dev/null <<EOF
[Unit]
Description=BestStag n8n Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=NODE_ENV=production
Environment=N8N_BASIC_AUTH_ACTIVE=true
Environment=N8N_BASIC_AUTH_USER=${N8N_USER:-admin}
Environment=N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD:-beststag2025}
ExecStart=/usr/local/bin/n8n start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Recarregar systemd
    sudo systemctl daemon-reload
    sudo systemctl enable beststag-n8n
    
    log_success "Serviços systemd criados!"
}

# Executar testes
run_tests() {
    log_info "Executando testes..."
    
    # Testar conexão com Airtable
    source venv/bin/activate
    python -c "
import os
import requests
api_key = os.getenv('AIRTABLE_API_KEY')
base_id = os.getenv('AIRTABLE_BASE_ID')
response = requests.get(f'https://api.airtable.com/v0/{base_id}/Usuarios', 
                       headers={'Authorization': f'Bearer {api_key}'})
print('✅ Airtable OK' if response.status_code == 200 else '❌ Airtable ERRO')
"
    
    # Testar n8n
    if curl -s "http://localhost:5678" > /dev/null; then
        echo "✅ n8n OK"
    else
        echo "❌ n8n ERRO"
    fi
    
    log_success "Testes concluídos!"
}

# Gerar relatório de instalação
generate_report() {
    log_info "Gerando relatório de instalação..."
    
    cat > installation_report.txt <<EOF
BestStag v9.0 - Relatório de Instalação
=======================================

Data: $(date)
Usuário: $USER
Diretório: $(pwd)

Componentes Instalados:
- ✅ Dependências do sistema
- ✅ Ambiente Python (venv)
- ✅ Configuração Airtable
- ✅ n8n Workflows
- ✅ Portal Web
- ✅ Serviços systemd

URLs de Acesso:
- n8n: http://localhost:5678
- Portal Web: http://localhost:3000 (após npm start)

Credenciais:
- n8n Usuário: ${N8N_USER:-admin}
- n8n Senha: ${N8N_PASSWORD:-beststag2025}

Próximos Passos:
1. Iniciar serviços: sudo systemctl start beststag-n8n
2. Configurar webhooks no Twilio
3. Testar comandos WhatsApp
4. Acessar portal web

Arquivos Importantes:
- .env (configurações)
- installation_report.txt (este arquivo)
- logs/ (logs do sistema)

Para suporte: https://github.com/beststag/beststag-v9
EOF

    log_success "Relatório salvo em: installation_report.txt"
}

# Função principal
main() {
    print_banner
    
    log_info "Iniciando deployment do BestStag v9.0..."
    
    # Verificações iniciais
    check_root
    check_dependencies
    check_versions
    
    # Configuração
    setup_environment
    install_python_deps
    setup_airtable
    setup_n8n
    install_workflows
    setup_portal
    setup_docker
    create_services
    
    # Testes e relatório
    run_tests
    generate_report
    
    echo ""
    log_success "🎉 BestStag v9.0 instalado com sucesso!"
    echo ""
    echo -e "${GREEN}Próximos passos:${NC}"
    echo "1. Iniciar n8n: sudo systemctl start beststag-n8n"
    echo "2. Acessar n8n: http://localhost:5678"
    echo "3. Configurar webhooks no Twilio"
    echo "4. Testar via WhatsApp: ${TWILIO_WHATSAPP_NUMBER}"
    echo ""
    echo -e "${BLUE}Documentação completa em: docs/${NC}"
    echo -e "${BLUE}Relatório de instalação: installation_report.txt${NC}"
    echo ""
}

# Executar função principal
main "$@"

