#!/bin/bash

# blog.sh - A script to manage your Pelican blog
# Usage: ./blog.sh [command]
# Commands:
#   serve    - Build and serve the blog locally
#   build    - Just build the blog
#   deploy   - Deploy to GitHub Pages
#   clean    - Clean output directory
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

# Check if Pelican is installed
check_pelican() {
    if ! command -v pelican &> /dev/null; then
        print_error "Pelican is not installed. Please install it with 'pip install pelican'."
        exit 1
    fi
}

# Build the blog
build() {
    print_header "Building blog with Pelican..."
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
    check_pelican
    
    # Check if port is provided
    PORT=${1:-8000}
    
    if ! command -v pelican-livereload &> /dev/null; then
        print_warning "pelican-livereload not found. Installing it..."
        pip install pelican-livereload
    fi
    
    echo -e "Starting live reload server on http://localhost:${PORT}"
    echo -e "The blog will automatically rebuild when files change."
    echo -e "Press Ctrl+C to stop the server."
    
    pelican-livereload --port "$PORT"
}

# Deploy to GitHub Pages
deploy() {
    print_header "Deploying blog to GitHub Pages..."
    
    # Check if ghp-import is installed
    if ! command -v ghp-import &> /dev/null; then
        print_error "ghp-import is not installed. Please install it with 'pip install ghp-import'."
        exit 1
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
    echo "Blog Management Script"
    echo
    echo "Usage: ./blog.sh [command] [options]"
    echo
    echo "Commands:"
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