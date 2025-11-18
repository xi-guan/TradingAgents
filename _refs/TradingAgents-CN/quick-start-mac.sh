#!/bin/bash
# TradingAgents-CN Quick Start Script for macOS
# Author: TradingAgents-CN Team
# Description: One-click deployment script for Docker environment

set -e  # exit on error

# ==================== Color Definitions ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ==================== Symbols ====================
CHECK_MARK="✓"
CROSS_MARK="✗"
ARROW="→"
INFO="•"

# ==================== Configuration ====================
COMPOSE_FILE="docker-compose.hub.nginx.arm.yml"
BACKEND_CONTAINER="tradingagents-backend"
MONGODB_CONTAINER="tradingagents-mongodb"
REDIS_CONTAINER="tradingagents-redis"
NGINX_CONTAINER="tradingagents-nginx"

# Default admin credentials
DEFAULT_USERNAME="admin"
DEFAULT_PASSWORD="admin123"
DEFAULT_EMAIL="admin@tradingagents.cn"

# Parse command line arguments
USERNAME="${DEFAULT_USERNAME}"
PASSWORD="${DEFAULT_PASSWORD}"
EMAIL="${DEFAULT_EMAIL}"

while [[ $# -gt 0 ]]; do
    case $1 in
        --username)
            USERNAME="$2"
            shift 2
            ;;
        --password)
            PASSWORD="$2"
            shift 2
            ;;
        --email)
            EMAIL="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --username USERNAME    Admin username (default: admin)"
            echo "  --password PASSWORD    Admin password (default: admin123)"
            echo "  --email EMAIL          Admin email (default: admin@tradingagents.cn)"
            echo "  --help                 Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}${CROSS_MARK} Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# ==================== Helper Functions ====================
print_header() {
    echo ""
    echo -e "${CYAN}================================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}================================================================================${NC}"
    echo ""
}

print_info() {
    echo -e "${BLUE}${INFO} $1${NC}"
}

print_success() {
    echo -e "${GREEN}${CHECK_MARK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS_MARK} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}${ARROW} $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 not found. Please install Docker first."
        exit 1
    fi
}

wait_for_service() {
    local service_name=$1
    local check_command=$2
    local max_attempts=60
    local attempt=1

    print_info "Waiting for ${service_name}..."

    while [ $attempt -le $max_attempts ]; do
        if eval $check_command &> /dev/null; then
            print_success "${service_name} is ready"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo ""
    print_error "${service_name} failed to start within timeout"
    return 1
}

# ==================== Main Script ====================
print_header "TradingAgents-CN Quick Start - macOS"

# Check prerequisites
print_info "Checking prerequisites..."
check_command docker
check_command docker-compose
print_success "All prerequisites met"

# Check if compose file exists
if [ ! -f "${COMPOSE_FILE}" ]; then
    print_error "Docker Compose file not found: ${COMPOSE_FILE}"
    exit 1
fi

# Stop existing containers
print_info "Stopping existing containers (if any)..."
docker-compose -f ${COMPOSE_FILE} down 2>/dev/null || true
print_success "Cleanup completed"

# Start services
print_header "Starting Docker Services"
print_info "Starting containers..."
docker-compose -f ${COMPOSE_FILE} up -d

if [ $? -eq 0 ]; then
    print_success "Docker containers started"
else
    print_error "Failed to start Docker containers"
    exit 1
fi

# Wait for services
print_header "Health Check"

# Wait for MongoDB
wait_for_service "MongoDB" \
    "docker exec ${MONGODB_CONTAINER} mongosh --quiet --eval 'db.adminCommand({ping: 1})' 2>/dev/null"

# Wait for Redis
wait_for_service "Redis" \
    "docker exec ${REDIS_CONTAINER} redis-cli -a tradingagents123 ping 2>/dev/null | grep -q PONG"

# Wait for Backend API
wait_for_service "Backend API" \
    "curl -f -s http://localhost:8000/api/health > /dev/null 2>&1"

# Wait for Nginx
wait_for_service "Nginx" \
    "curl -f -s http://localhost:8004/ > /dev/null 2>&1"

# Create admin user
print_header "Initializing Admin User"

print_info "Checking if admin user exists..."

# Check if user exists
USER_EXISTS=$(docker exec ${BACKEND_CONTAINER} python -c "
from pymongo import MongoClient
try:
    client = MongoClient('mongodb://admin:tradingagents123@mongodb:27017/tradingagents?authSource=admin', serverSelectionTimeoutMS=5000)
    db = client['tradingagents']
    existing = db.users.find_one({'username': '${USERNAME}'})
    print('true' if existing else 'false')
    client.close()
except Exception as e:
    print('error')
" 2>/dev/null)

if [ "$USER_EXISTS" = "true" ]; then
    print_warning "User '${USERNAME}' already exists, skipping creation"
elif [ "$USER_EXISTS" = "error" ]; then
    print_error "Failed to check user existence"
    exit 1
else
    print_info "Creating admin user: ${USERNAME}"

    # Create admin user
    docker exec ${BACKEND_CONTAINER} python -c "
import hashlib
from datetime import datetime
from pymongo import MongoClient

MONGO_URI = 'mongodb://admin:tradingagents123@mongodb:27017/tradingagents?authSource=admin'
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client['tradingagents']

user_doc = {
    'username': '${USERNAME}',
    'email': '${EMAIL}',
    'hashed_password': hashlib.sha256('${PASSWORD}'.encode()).hexdigest(),
    'is_active': True,
    'is_verified': True,
    'is_admin': True,
    'created_at': datetime.utcnow(),
    'updated_at': datetime.utcnow(),
    'last_login': None,
    'preferences': {
        'default_market': 'A股',
        'default_depth': '深度',
        'ui_theme': 'light',
        'language': 'zh-CN',
        'notifications_enabled': True,
        'email_notifications': False
    },
    'daily_quota': 10000,
    'concurrent_limit': 10,
    'total_analyses': 0,
    'successful_analyses': 0,
    'failed_analyses': 0,
    'favorite_stocks': []
}

db.users.insert_one(user_doc)
client.close()
" 2>/dev/null

    if [ $? -eq 0 ]; then
        print_success "Admin user created successfully"
    else
        print_error "Failed to create admin user"
        exit 1
    fi
fi

# Display access information
print_header "Deployment Complete!"

echo -e "${GREEN}${CHECK_MARK} All services are running${NC}"
echo ""
echo -e "${CYAN}Access Information:${NC}"
echo -e "${INFO} Frontend:     ${GREEN}http://localhost:8004${NC}"
echo -e "${INFO} API Docs:     ${GREEN}http://localhost:8004/api/docs${NC}"
echo -e "${INFO} Health Check: ${GREEN}http://localhost:8004/api/health${NC}"
echo ""
echo -e "${CYAN}Login Credentials:${NC}"
echo -e "${INFO} Username: ${GREEN}${USERNAME}${NC}"
echo -e "${INFO} Password: ${GREEN}${PASSWORD}${NC}"
echo ""
echo -e "${YELLOW}${ARROW} Please change the default password after first login${NC}"
echo ""
echo -e "${CYAN}Container Status:${NC}"
docker-compose -f ${COMPOSE_FILE} ps
echo ""
echo -e "${GREEN}${CHECK_MARK} Deployment successful! Visit http://localhost:8004 to get started.${NC}"
echo ""
