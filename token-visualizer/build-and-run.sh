#!/bin/bash

# vLLM Token Visualizer - Build and Run Script

IMAGE_NAME="vllm-token-visualizer"
CONTAINER_NAME="token-visualizer"
PORT="3000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if podman or docker is available
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
else
    print_error "Neither podman nor docker is available. Please install one of them."
    exit 1
fi

print_status "Using $CONTAINER_CMD to build and run the container"

# Stop and remove existing container if it exists
if $CONTAINER_CMD ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    print_warning "Stopping and removing existing container: $CONTAINER_NAME"
    $CONTAINER_CMD stop $CONTAINER_NAME >/dev/null 2>&1
    $CONTAINER_CMD rm $CONTAINER_NAME >/dev/null 2>&1
fi

# Build the image
print_status "Building container image: $IMAGE_NAME"
if $CONTAINER_CMD build -t $IMAGE_NAME -f Containerfile .; then
    print_success "Container image built successfully"
else
    print_error "Failed to build container image"
    exit 1
fi

# Run the container
print_status "Starting container on port $PORT"
if $CONTAINER_CMD run -d \
    --name $CONTAINER_NAME \
    -p $PORT:8080 \
    --env VLLM_SERVER_URL="${VLLM_SERVER_URL:-http://localhost:8000}" \
    --env VLLM_REFRESH_INTERVAL="${VLLM_REFRESH_INTERVAL:-2000}" \
    $IMAGE_NAME; then
    
    print_success "Container started successfully"
    print_status "Application is available at: http://localhost:$PORT"
    print_status "Container name: $CONTAINER_NAME"
    
    if [ -n "$VLLM_SERVER_URL" ]; then
        print_status "vLLM Server URL: $VLLM_SERVER_URL"
    else
        print_status "vLLM Server URL: http://localhost:8000 (default)"
    fi
    
    echo ""
    echo "To stop the container, run:"
    echo "  $CONTAINER_CMD stop $CONTAINER_NAME"
    echo ""
    echo "To view logs, run:"
    echo "  $CONTAINER_CMD logs -f $CONTAINER_NAME"
    echo ""
    echo "To remove the container, run:"
    echo "  $CONTAINER_CMD rm $CONTAINER_NAME"
    
else
    print_error "Failed to start container"
    exit 1
fi