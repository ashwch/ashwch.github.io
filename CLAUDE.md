# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal blog built with Pelican (Python static site generator) and hosted on GitHub Pages at https://ashwch.com. The blog features a custom responsive theme with dark/light mode support and an AI-powered photography gallery.

## Project Structure

```
.
├── blog.sh                 # Main build/management script
├── content/               # Blog content
│   ├── articles/         # Blog posts
│   ├── pages/           # Static pages
│   └── images/          # Images including photography/
├── docs/                  # Documentation
│   └── workflows/        # Workflow guides
├── scripts/              # Utility scripts
│   ├── photo_manager.py  # AI-powered photo processor
│   └── set_photo_order.py # Photo ordering tool
├── theme/                # Custom Pelican theme
│   ├── static/          # CSS, JS, fonts
│   └── templates/       # Jinja2 templates
├── output/              # Generated site (git-ignored)
├── pelicanconf.py       # Development settings
└── publishconf.py       # Production settings
```

## Development Commands

The primary build tool is `blog.sh`. All commands assume you're in the project root:

```bash
# Set up virtual environment and install dependencies
./blog.sh setup

# Build and serve locally at http://localhost:8000
./blog.sh serve

# Build with live reload (auto-refreshes on changes)
./blog.sh livereload

# Build for production
./blog.sh build production

# Deploy to GitHub Pages (gh-pages branch)
./blog.sh deploy

# Clean output directory
./blog.sh clean
```

Alternative build systems (Makefile and tasks.py) are available but `blog.sh` is preferred.

## Architecture

### Content Structure
- **Articles**: `content/articles/*.md` - Blog posts with metadata headers
- **Pages**: `content/pages/*.md` - Static pages (About, etc.)
- **Images**: `content/images/` - Image assets

Required article metadata:
```markdown
Title: Post Title
Date: YYYY-MM-DD
Category: Category Name
Tags: tag1, tag2
Slug: url-slug
Authors: Author Name
Summary: Brief description
```

### Theme System
- **Templates**: `theme/templates/` - Jinja2 templates
  - `_includes/` - Reusable partials (header, footer, etc.)
  - Page templates use Bootstrap 5 with custom styling
- **Static Assets**: `theme/static/`
  - `css/main.css` - Main stylesheet with CSS variables for theming
  - Dark/light mode toggle implementation in base template

### Configuration
- **pelicanconf.py**: Development settings (local URLs, debug settings)
- **publishconf.py**: Production settings (extends pelicanconf, adds analytics, feeds)

Key configuration patterns:
- Theme customization through THEME variable
- Plugin system (though no plugins currently used)
- Social links and navigation defined in pelicanconf

### Deployment
- Uses `ghp-import` to manage gh-pages branch
- Production site at https://ashwch.com
- GitHub Pages serves from gh-pages branch

## Development Workflow

### Content Workflow
1. Create/edit content in `content/articles/`
2. Use `./blog.sh livereload` for development
3. Theme changes in `theme/` directory auto-refresh
4. Deploy with `./blog.sh deploy` when ready

### Photography Workflow
1. Drop photos in `content/images/photography/`
2. Run `./blog.sh photos update` to process
3. Gallery auto-updates with thumbnails and EXIF data
4. Use `./blog.sh photos stats` to view statistics

Photography commands:
- `./blog.sh photos update` - Process new photos
- `./blog.sh photos regenerate` - Force regenerate all
- `./blog.sh photos stats` - Show gallery statistics
- `./blog.sh photos clean` - Remove orphaned files

## Key Technical Details

- Uses `uv` package manager (modern Python tooling)
- Bootstrap 5 for responsive layout
- Inter (UI) + Merriweather (content) fonts
- Disqus comments integration
- Google Analytics tracking
- No testing framework or linting configured