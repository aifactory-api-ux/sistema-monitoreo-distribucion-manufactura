#!/bin/bash

# DistroViz v3 - Zero-Config Startup Script
# Validates Docker, builds images, starts services, and waits for healthy status

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker Desktop and try again."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available. Please ensure Docker Desktop includes Compose."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Create necessary directories
setup_directories() {
    print_status "Setting up directories..."
    mkdir -p data
    print_success "Directories created"
}

# Copy environment file if it doesn't exist
setup_environment() {
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        print_success "Environment file created. You can customize .env if needed."
    else
        print_status "Using existing .env file"
    fi
}

# Stop any existing containers
stop_existing() {
    print_status "Stopping any existing containers..."
    if docker compose ps -q 2>/dev/null | grep -q .; then
        docker compose down --remove-orphans
        print_success "Existing containers stopped"
    else
        print_status "No existing containers to stop"
    fi
}

# Build and start services
start_services() {
    print_status "Building and starting services..."
    
    # Use docker compose if available, fallback to docker-compose
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    $COMPOSE_CMD build --no-cache
    print_success "Images built successfully"
    
    $COMPOSE_CMD up -d
    print_success "Services started"
}

# Wait for services to be healthy
wait_for_health() {
    print_status "Waiting for services to be healthy..."
    
    local max_attempts=60
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        local backend_health=$(docker compose ps --format json | jq -r '.[] | select(.Service == "backend") | .Health')
        local frontend_health=$(docker compose ps --format json | jq -r '.[] | select(.Service == "frontend") | .Health')
        
        if [ "$backend_health" = "healthy" ] && [ "$frontend_health" = "healthy" ]; then
            print_success "All services are healthy!"
            return 0
        fi
        
        if [ $((attempt % 10)) -eq 0 ]; then
            print_status "Still waiting... (attempt $attempt/$max_attempts)"
            print_status "Backend: $backend_health, Frontend: $frontend_health"
        fi
        
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_warning "Services may not be fully healthy yet, but continuing..."
    docker compose ps
}

# Test API endpoints
test_endpoints() {
    print_status "Testing API endpoints..."
    
    local backend_port=$(grep BACKEND_PORT .env 2>/dev/null | cut -d'=' -f2 || echo "8000")
    local base_url="http://localhost:${backend_port}"
    
    # Test health endpoint
    if curl -s -f "${base_url}/api/health" > /dev/null; then
        print_success "Health endpoint responding"
    else
        print_warning "Health endpoint not responding yet"
    fi
    
    # Test dashboard endpoint
    if curl -s -f "${base_url}/api/dashboard/summary" > /dev/null; then
        print_success "Dashboard API responding"
    else
        print_warning "Dashboard API not responding yet"
    fi
}

# Print access information
print_access_info() {
    local frontend_port=$(grep FRONTEND_PORT .env 2>/dev/null | cut -d'=' -f2 || echo "3000")
    local backend_port=$(grep BACKEND_PORT .env 2>/dev/null | cut -d'=' -f2 || echo "8000")
    
    echo
    echo "=========================================="
    print_success "DistroViz v3 is ready!"
    echo "=========================================="
    echo
    echo "🌐 Web Application: http://localhost:${frontend_port}"
    echo "🔧 API Documentation: http://localhost:${backend_port}/docs"
    echo "❤️  Health Check: http://localhost:${backend_port}/api/health"
    echo
    echo "📊 Available Features:"
    echo "  • Dashboard with KPIs and charts"
    echo "  • Orders management interface"
    echo "  • Real-time data updates"
    echo
    echo "🛠️  Management Commands:"
    echo "  • View logs: docker compose logs -f"
    echo "  • Stop services: docker compose down"
    echo "  • Restart: ./run.sh"
    echo
    echo "=========================================="
}

# Main execution
main() {
    echo
    print_status "Starting DistroViz v3..."
    echo
    
    check_docker
    setup_directories
    setup_environment
    stop_existing
    start_services
    wait_for_health
    test_endpoints
    print_access_info
    
    print_success "Startup complete! 🚀"
}

# Handle script interruption
trap 'print_error "Script interrupted. Run \"docker compose down\" to clean up."; exit 1' INT TERM

# Run main function
main "$@"