#!/bin/bash
# Script de déploiement automatisé ODG Géospatial
# Usage: ./deploy_production.sh

set -e  # Arrêter en cas d'erreur

echo "🚀 Déploiement ODG Géospatial - Production"
echo "=========================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Vérifier Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js n'est pas installé"
        exit 1
    fi
    
    # Vérifier Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 n'est pas installé"
        exit 1
    fi
    
    # Vérifier PostgreSQL
    if ! command -v psql &> /dev/null; then
        log_warning "PostgreSQL client non trouvé - assurez-vous que PostgreSQL est installé"
    fi
    
    log_success "Prérequis vérifiés"
}

# Configuration de l'environnement
setup_environment() {
    log_info "Configuration de l'environnement..."
    
    # Créer le fichier .env s'il n'existe pas
    if [ ! -f "backend/.env" ]; then
        log_warning "Fichier .env manquant"
        if [ -f "backend/.env.example" ]; then
            cp backend/.env.example backend/.env
            log_info "Fichier .env créé depuis .env.example"
            log_warning "⚠️  IMPORTANT: Éditez backend/.env avec vos valeurs de production"
            read -p "Appuyez sur Entrée après avoir configuré .env..."
        else
            log_error "Fichier .env.example manquant"
            exit 1
        fi
    fi
    
    # Charger les variables d'environnement
    if [ -f "backend/.env" ]; then
        export $(cat backend/.env | grep -v '^#' | xargs)
    fi
    
    # Vérifier les variables critiques
    if [ -z "$DATABASE_URL" ]; then
        log_error "DATABASE_URL non définie dans .env"
        exit 1
    fi
    
    if [ -z "$SECRET_KEY" ]; then
        log_error "SECRET_KEY non définie dans .env"
        exit 1
    fi
    
    log_success "Environnement configuré"
}

# Installation des dépendances backend
install_backend_dependencies() {
    log_info "Installation des dépendances backend..."
    
    cd backend
    
    # Créer un environnement virtuel s'il n'existe pas
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "Environnement virtuel créé"
    fi
    
    # Activer l'environnement virtuel
    source venv/bin/activate
    
    # Installer les dépendances
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Ajouter les dépendances de production
    pip install gunicorn python-dotenv
    
    cd ..
    log_success "Dépendances backend installées"
}

# Build du frontend
build_frontend() {
    log_info "Build du frontend..."
    
    cd frontend
    
    # Installer les dépendances
    npm install
    
    # Build pour la production
    npm run build
    
    cd ..
    log_success "Frontend buildé"
}

# Initialisation de la base de données
init_database() {
    log_info "Initialisation de la base de données..."
    
    cd backend
    source venv/bin/activate
    
    # Exécuter le script d'initialisation
    python init_production_db.py
    
    if [ $? -eq 0 ]; then
        log_success "Base de données initialisée"
    else
        log_error "Erreur lors de l'initialisation de la base de données"
        exit 1
    fi
    
    cd ..
}

# Tests de validation (pytest - optionnel, désactiver si pas de tests)
run_tests() {
    log_info "Exécution des tests backend (pytest)..."
    
    cd backend
    source venv/bin/activate
    
    if [ -d "tests" ] && command -v pytest &> /dev/null; then
        pytest tests/ -q --tb=short
        if [ $? -eq 0 ]; then
            log_success "Tests validés"
        else
            log_warning "Certains tests ont échoué - vérifiez avant de déployer"
        fi
    else
        log_warning "Dossier tests/ ou pytest non trouvé - étape tests ignorée"
    fi
    
    cd ..
}

# Configuration du serveur web
setup_web_server() {
    log_info "Configuration du serveur web..."
    
    # Créer le fichier de configuration Gunicorn
    cat > backend/gunicorn.conf.py << EOF
# Configuration Gunicorn pour ODG Géospatial
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
user = "www-data"
group = "www-data"
tmp_upload_dir = None
logfile = "/var/log/odg/gunicorn.log"
loglevel = "info"
access_logfile = "/var/log/odg/access.log"
error_logfile = "/var/log/odg/error.log"
EOF
    
    # Créer le service systemd
    sudo tee /etc/systemd/system/odg-geospatial.service > /dev/null << EOF
[Unit]
Description=ODG Géospatial Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$(pwd)/backend
Environment=PATH=$(pwd)/backend/venv/bin
ExecStart=$(pwd)/backend/venv/bin/gunicorn --config gunicorn.conf.py wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF
    
    # Créer les dossiers de logs
    sudo mkdir -p /var/log/odg
    sudo chown www-data:www-data /var/log/odg
    
    # Recharger systemd
    sudo systemctl daemon-reload
    sudo systemctl enable odg-geospatial
    
    log_success "Service systemd configuré"
}

# Configuration Nginx (optionnel)
setup_nginx() {
    if command -v nginx &> /dev/null; then
        log_info "Configuration Nginx..."
        
        sudo tee /etc/nginx/sites-available/odg-geospatial << EOF
server {
    listen 80;
    server_name your-domain.com;  # À modifier
    
    # Frontend statique
    location / {
        root $(pwd)/frontend/dist;
        try_files \$uri \$uri/ /index.html;
        
        # Cache des assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeout pour les uploads
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
    
    # Logs
    access_log /var/log/nginx/odg-access.log;
    error_log /var/log/nginx/odg-error.log;
}
EOF
        
        # Activer le site
        sudo ln -sf /etc/nginx/sites-available/odg-geospatial /etc/nginx/sites-enabled/
        sudo nginx -t && sudo systemctl reload nginx
        
        log_success "Nginx configuré"
    else
        log_warning "Nginx non installé - configuration ignorée"
    fi
}

# Démarrage des services
start_services() {
    log_info "Démarrage des services..."
    
    # Démarrer l'application
    sudo systemctl start odg-geospatial
    sudo systemctl status odg-geospatial --no-pager
    
    log_success "Services démarrés"
}

# Tests post-déploiement
post_deployment_tests() {
    log_info "Tests post-déploiement..."
    
    # Attendre que le service démarre
    sleep 5
    
    # Test de l'API
    if curl -f http://localhost:5000/api/geospatial/supported-formats > /dev/null 2>&1; then
        log_success "API accessible"
    else
        log_error "API non accessible"
        exit 1
    fi
    
    log_success "Tests post-déploiement validés"
}

# Fonction principale
main() {
    echo "🎯 Début du déploiement..."
    
    check_prerequisites
    setup_environment
    install_backend_dependencies
    build_frontend
    init_database
    run_tests
    setup_web_server
    setup_nginx
    start_services
    post_deployment_tests
    
    echo ""
    echo "🎉 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !"
    echo "=================================="
    log_success "Application ODG Géospatial déployée"
    log_info "URL: http://your-domain.com (à configurer dans Nginx)"
    log_info "API: http://your-domain.com/api/geospatial/"
    log_info "Logs: /var/log/odg/"
    log_info "Service: sudo systemctl status odg-geospatial"
    echo ""
    log_warning "N'oubliez pas de :"
    echo "  1. Configurer votre nom de domaine dans Nginx"
    echo "  2. Installer un certificat SSL (Let's Encrypt)"
    echo "  3. Configurer les sauvegardes de base de données"
    echo "  4. Mettre en place le monitoring"
}

# Gestion des arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo "Options:"
        echo "  --help, -h     Afficher cette aide"
        echo "  --check        Vérifier seulement les prérequis"
        echo "  --db-only      Initialiser seulement la base de données"
        exit 0
        ;;
    --check)
        check_prerequisites
        setup_environment
        exit 0
        ;;
    --db-only)
        setup_environment
        init_database
        exit 0
        ;;
    *)
        main
        ;;
esac
