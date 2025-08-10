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

# Photography management functions
photos_update() {
    print_header "Updating Photo Gallery..."
    check_venv
    
    # Ensure photo directory exists
    mkdir -p content/images/photography
    
    # Run the photo manager
    if [ -f "scripts/photo_manager.py" ]; then
        echo "🤖 Processing photos (works with any filename)..."
        chmod +x scripts/photo_manager.py
        python3 scripts/photo_manager.py
    else
        echo -e "${RED}✗ Photo manager script not found!${NC}"
        echo "Please ensure scripts/photo_manager.py exists"
        exit 1
    fi
    
    # Rebuild the site
    echo ""
    echo "🔨 Rebuilding site with updated gallery..."
    build
    echo -e "${GREEN}✓ Photo gallery updated successfully!${NC}"
}

photos_regenerate() {
    print_header "Regenerating All Thumbnails..."
    check_venv
    
    # Remove cache to force regeneration
    if [ -f "content/images/photography/thumbnails/.cache.json" ]; then
        rm -f content/images/photography/thumbnails/.cache.json
        echo "🗑️  Cleared thumbnail cache"
    fi
    
    if [ -f "content/images/photography/gallery_metadata.json" ]; then
        rm -f content/images/photography/gallery_metadata.json
        echo "🗑️  Cleared metadata cache"
    fi
    
    # Run update which will now regenerate everything
    photos_update
}

photos_stats() {
    print_header "Photography Gallery Statistics"
    
    PHOTO_DIR="content/images/photography"
    THUMB_DIR="$PHOTO_DIR/thumbnails"
    
    if [ ! -d "$PHOTO_DIR" ]; then
        echo -e "${RED}No photography directory found!${NC}"
        exit 1
    fi
    
    # Count files
    ORIG_COUNT=$(find "$PHOTO_DIR" -maxdepth 1 -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) 2>/dev/null | wc -l | tr -d ' ')
    THUMB_COUNT=$(find "$THUMB_DIR" -type f -name "*.jpg" 2>/dev/null | wc -l | tr -d ' ')
    
    # Calculate sizes
    ORIG_SIZE=$(du -sh "$PHOTO_DIR" 2>/dev/null | cut -f1)
    THUMB_SIZE=$(du -sh "$THUMB_DIR" 2>/dev/null | cut -f1)
    
    echo -e "${BLUE}📊 Gallery Statistics:${NC}"
    echo "  Original photos: $ORIG_COUNT"
    echo "  Thumbnails: $THUMB_COUNT"
    echo "  Original size: $ORIG_SIZE"
    echo "  Thumbnail size: $THUMB_SIZE"
    
    # Show categories if metadata exists
    if [ -f "$PHOTO_DIR/gallery_metadata.json" ]; then
        echo ""
        echo -e "${BLUE}📷 Categories:${NC}"
        python3 -c "
import json
with open('$PHOTO_DIR/gallery_metadata.json') as f:
    data = json.load(f)
    cats = {}
    for photo in data.values():
        cat = photo.get('category', 'uncategorized')
        cats[cat] = cats.get(cat, 0) + 1
    for cat, count in sorted(cats.items()):
        print(f'  {cat}: {count} photos')
        "
    fi
    
    echo -e "${GREEN}✓ Statistics generated${NC}"
}

photos_order() {
    print_header "Set Photo Gallery Order"
    
    if [ ! -f "scripts/set_photo_order.py" ]; then
        echo -e "${RED}scripts/set_photo_order.py not found!${NC}"
        exit 1
    fi
    
    python3 scripts/set_photo_order.py
}

photos_clean() {
    print_header "Cleaning Orphaned Thumbnails..."
    
    PHOTO_DIR="content/images/photography"
    THUMB_DIR="$PHOTO_DIR/thumbnails"
    
    if [ ! -d "$THUMB_DIR" ]; then
        echo -e "${YELLOW}No thumbnails directory found${NC}"
        exit 0
    fi
    
    echo "🔍 Checking for orphaned thumbnails..."
    
    # Find and remove orphaned thumbnails
    CLEANED=0
    for thumb in "$THUMB_DIR"/*_*.jpg; do
        if [ -f "$thumb" ]; then
            # Extract base name without size suffix
            base=$(basename "$thumb" | sed -E 's/_(small|medium|large)\.jpg$//')
            
            # Check if original exists
            if [ ! -f "$PHOTO_DIR/${base}.jpg" ] && [ ! -f "$PHOTO_DIR/${base}.jpeg" ] && [ ! -f "$PHOTO_DIR/${base}.png" ]; then
                echo "  Removing orphaned: $(basename $thumb)"
                rm "$thumb"
                ((CLEANED++))
            fi
        fi
    done
    
    if [ $CLEANED -gt 0 ]; then
        echo -e "${GREEN}✓ Cleaned $CLEANED orphaned thumbnails${NC}"
    else
        echo -e "${GREEN}✓ No orphaned thumbnails found${NC}"
    fi
}

photos() {
    case "$1" in
        update)
            photos_update
            ;;
        regenerate)
            photos_regenerate
            ;;
        stats)
            photos_stats
            ;;
        clean)
            photos_clean
            ;;
        order)
            photos_order
            ;;
        *)
            echo -e "${RED}Unknown photos command: $1${NC}"
            echo "Available commands: update, regenerate, stats, clean, order"
            exit 1
            ;;
    esac
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
    echo ""
    echo -e "${BLUE}Photography Commands:${NC}"
    echo "  photos update      - Process new photos and update gallery"
    echo "  photos regenerate  - Force regenerate all thumbnails"
    echo "  photos stats       - Show gallery statistics"
    echo "  photos clean       - Remove orphaned thumbnails"
    echo "  photos order       - Set manual ordering for photos"
    echo ""
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
    photos)
        photos "$2"
        ;;
    help|*)
        show_help
        ;;
esac
