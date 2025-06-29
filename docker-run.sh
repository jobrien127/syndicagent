#!/bin/bash

# SyndicAgent Docker Helper Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop and try again."
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "SyndicAgent Docker Helper"
    echo ""
    echo "Usage: ./docker-run.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  demo       - Run the demo application"
    echo "  test       - Run comprehensive tests"
    echo "  pytest     - Run pytest unit tests"
    echo "  build      - Build Docker images"
    echo "  up         - Start all services"
    echo "  down       - Stop all services"
    echo "  logs       - Show logs"
    echo "  clean      - Clean up containers and images"
    echo "  shell      - Open shell in syndicagent container"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./docker-run.sh demo"
    echo "  ./docker-run.sh test"
    echo "  AGWORLD_API_TOKEN=your_token ./docker-run.sh demo"
}

# Change to project root directory
cd "$(dirname "$0")"

case "${1:-help}" in
    demo)
        print_status "Running SyndicAgent demo in Docker..."
        check_docker
        docker-compose up --build syndicagent
        ;;
    
    test)
        print_status "Running comprehensive tests in Docker..."
        check_docker
        docker-compose --profile test up --build syndicagent-test
        ;;
    
    pytest)
        print_status "Running pytest unit tests in Docker..."
        check_docker
        docker-compose --profile test up --build syndicagent-pytest
        ;;
    
    build)
        print_status "Building Docker images..."
        check_docker
        docker-compose build
        print_success "Docker images built successfully"
        ;;
    
    up)
        print_status "Starting all services..."
        check_docker
        docker-compose up -d
        print_success "Services started. Use 'docker-run.sh logs' to view logs"
        ;;
    
    down)
        print_status "Stopping all services..."
        docker-compose down
        print_success "Services stopped"
        ;;
    
    logs)
        print_status "Showing logs..."
        docker-compose logs -f
        ;;
    
    clean)
        print_warning "This will remove all containers, images, and volumes related to SyndicAgent"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Cleaning up..."
            docker-compose down -v
            docker-compose rm -f
            docker system prune -f
            print_success "Cleanup completed"
        else
            print_status "Cleanup cancelled"
        fi
        ;;
    
    shell)
        print_status "Opening shell in syndicagent container..."
        check_docker
        docker-compose exec syndicagent /bin/bash || \
        docker-compose run --rm syndicagent /bin/bash
        ;;
    
    help|--help|-h)
        show_help
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
