#!/bin/bash

# blog.sh - A script to manage your Pelican blog with uv package manager
# Usage: ./blog.sh [command]
# Commands:
#   serve    - Build and serve the blog locally
#   build    - Just build the blog
#   deploy   - Deploy to GitHub Pages
#   clean    - Clean output directory
#   setup    - Set up virtual environment and install dependencies
#   help     - Show this help message

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
OUTPUT_DIR="output"
GITHUB_PAGES_BRANCH="gh-pages"
PELICAN_CONFIG="pelicanconf.py"
PUBLISH_CONFIG="publishconf.py"
VENV_DIR=".venv"
REQUIREMENTS="pelican markdown ghp-import pelican-livereload"

# Function to print colorful headers
print_header() {
    echo -e "${BLUE}==========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}==========================================${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

# Function to print warnings
print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Check if uv is installed
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_error "uv is not installed. Please install it with 'pipx install uv' or 'brew install uv'."
        echo "Visit https://github.com/astral-sh/uv for installation instructions."
        exit 1
    fi
}

# Check if Pelican is installed
check_pelican() {
    if ! command -v pelican &> /dev/null; then
        print_error "Pelican is not installed in your environment."
        echo "Run './blog.sh setup' to create a virtual environment and install dependencies."
        exit 1
    fi
}

# Check if virtual environment exists and activate it
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_warning "Virtual environment not found."
        read -p "Would you like to create one now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            setup_environment
        else
            print_error "Cannot continue without a virtual environment."
            exit 1
        fi
    else
        # Activate the virtual environment
        if [ -f "$VENV_DIR/bin/activate" ]; then
            source "$VENV_DIR/bin/activate"
        elif [ -f "$VENV_DIR/Scripts/activate" ]; then
            source "$VENV_DIR/Scripts/activate"
        else
            print_error "Virtual environment exists but activate script not found."
            exit 1
        fi
    fi
}

# Setup environment with uv
setup_environment() {
    print_header "Setting up virtual environment with uv..."
    check_uv
    
    # Create virtual environment
    uv venv "$VENV_DIR"
    
    # Activate the virtual environment
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    elif [ -f "$VENV_DIR/Scripts/activate" ]; then
        source "$VENV_DIR/Scripts/activate"
    else
        print_error "Failed to create virtual environment."
        exit 1
    fi
    
    # Install dependencies
    print_header "Installing dependencies with uv..."
    if [ -f "requirements.txt" ]; then
        uv pip install -r requirements.txt
    else
        uv pip install $REQUIREMENTS
    fi
    
    echo -e "${GREEN}✓ Environment setup complete!${NC}"
    echo "You can now run './blog.sh serve' to start the development server."
}

# Build the blog
build() {
    print_header "Building blog with Pelican..."
    check_venv
    check_pelican
    
    if [ "$1" == "production" ]; then
        pelican content -s "$PUBLISH_CONFIG" -t theme
        echo -e "${GREEN}✓ Blog built successfully for production!${NC}"
    else
        pelican content -s "$PELICAN_CONFIG" -t theme
        echo -e "${GREEN}✓ Blog built successfully for development!${NC}"
    fi
}

# Clean the output directory
clean() {
    print_header "Cleaning output directory..."
    if [ -d "$OUTPUT_DIR" ]; then
        rm -rf "$OUTPUT_DIR"
        mkdir -p "$OUTPUT_DIR"
        echo -e "${GREEN}✓ Output directory cleaned!${NC}"
    else
        mkdir -p "$OUTPUT_DIR"
        echo -e "${YELLOW}Output directory did not exist. Created a new one.${NC}"
    fi
}

# Serve the blog locally
serve() {
    print_header "Serving blog locally..."
    check_venv
    check_pelican
    
    # Check if port is provided
    PORT=${1:-8000}
    
    # Build first
    build
    
    # Start server
    echo -e "Starting server on http://localhost:${PORT}"
    echo -e "Press Ctrl+C to stop the server."
    pelican --listen --port "$PORT"
}

# Live reload server (with automatic rebuild)
livereload() {
    print_header "Starting live reload server..."
    check_venv
    check_pelican
    
    # Check if port is provided
    PORT=${1:-8000}
    
    if ! command -v pelican-livereload &> /dev/null; then
        print_warning "pelican-livereload not found. Installing it..."
        uv pip install pelican-livereload
    fi
    
    echo -e "Starting live reload server on http://localhost:${PORT}"
    echo -e "The blog will automatically rebuild when files change."
    echo -e "Press Ctrl+C to stop the server."
    
    pelican-livereload --port "$PORT"
}

# Deploy to GitHub Pages
deploy() {
    print_header "Deploying blog to GitHub Pages..."
    check_venv
    
    # Check if ghp-import is installed
    if ! command -v ghp-import &> /dev/null; then
        print_warning "ghp-import not found. Installing it..."
        uv pip install ghp-import
    fi
    
    # Build for production
    build production
    
    # Confirm deployment
    echo -e "You are about to deploy to the ${GITHUB_PAGES_BRANCH} branch."
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Deployment cancelled.${NC}"
        exit 0
    fi
    
    # Deploy using ghp-import
    echo -e "Deploying to GitHub Pages..."
    ghp-import -m "Update blog $(date +'%Y-%m-%d %H:%M:%S')" -b "$GITHUB_PAGES_BRANCH" "$OUTPUT_DIR"
    git push origin "$GITHUB_PAGES_BRANCH"
    
    echo -e "${GREEN}✓ Blog successfully deployed to GitHub Pages!${NC}"
    echo -e "Your blog should be live at your GitHub Pages URL soon."
}

# Show help
show_help() {
    echo "Blog Management Script (using uv)"
    echo
    echo "Usage: ./blog.sh [command] [options]"
    echo
    echo "Commands:"
    echo "  setup              - Set up virtual environment and install dependencies"
    echo "  serve [port]       - Build and serve the blog locally (default port: 8000)"
    echo "  livereload [port]  - Start a live reload server (default port: 8000)"
    echo "  build              - Build the blog for development"
    echo "  build production   - Build the blog for production"
    echo "  deploy             - Deploy to GitHub Pages"
    echo "  clean              - Clean output directory"
    echo "  help               - Show this help message"
}

# Main execution
case "$1" in
    setup)
        setup_environment
        ;;
    serve)
        serve "$2"
        ;;
    livereload)
        livereload "$2"
        ;;
    build)
        build "$2"
        ;;
    deploy)
        deploy
        ;;
    clean)
        clean
        ;;
    help|*)
        show_help
        ;;
esac
