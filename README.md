# Modern Pelican Blog

A clean, responsive, and modern blog built with Pelican, featuring dark mode support, improved typography, and an elegant design.

## Features

- **Responsive Design**: Looks great on all devices from mobile to desktop
- **Dark/Light Mode**: Toggle between themes with a click, with preference saved for returning visitors
- **Modern Typography**: Uses Inter for UI and Merriweather for article content
- **Card-Based Layout**: Attractive presentation of blog posts
- **Improved Code Blocks**: Better styling for code and syntax highlighting
- **Social Integration**: Easy links to social profiles
- **Disqus Comments**: Integrated comment system
- **Analytics Support**: Google Analytics integration
- **Improved Performance**: Optimized for speed and accessibility
- **Easy Management**: Simple scripts to build, serve, and deploy your blog

## Getting Started

### Prerequisites

- Python 3.8 or higher
- uv (modern Python package manager)
- Pelican 4.5 or higher

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/ashwch/ashwch.github.io-source.git
   cd ashwch.github.io-source
   ```

2. Install uv if you don't have it already:
   ```bash
   curl -sSf https://install.python-poetry.org | python3 -
   pipx install uv
   ```

   Or with Homebrew on macOS:
   ```bash
   brew install uv
   ```

3. Set up a virtual environment and install required packages:
   ```bash
   # Create and activate a virtual environment
   uv venv
   
   # Activate the environment (Linux/macOS)
   source .venv/bin/activate
   
   # Activate the environment (Windows)
   # .venv\Scripts\activate
   ```

4. Install required Python packages:
   ```bash
   # If you have a requirements.txt
   uv pip install -r requirements.txt
   
   # Or install the packages directly
   uv pip install pelican markdown ghp-import "pelican-livereload>=0.1"
   ```

### Local Development

The blog comes with a convenient management script (`blog.sh`) that simplifies common tasks:

1. Make the script executable:
   ```bash
   chmod +x blog.sh
   ```

2. Start the local development server:
   ```bash
   ./blog.sh serve
   ```
   This will build your blog and serve it at http://localhost:8000

3. For auto-reloading during development:
   ```bash
   ./blog.sh livereload
   ```
   Your browser will automatically refresh when you make changes

### Creating Content

Posts are written in Markdown and stored in the `content/articles/` directory. Create a new file with the following format:

```markdown
Title: Your Post Title
Date: 2025-03-10
Modified: 2025-03-10
Category: Your Category
Tags: tag1, tag2, tag3
Slug: your-post-slug
Authors: Your Name
Summary: A brief summary of your post

Your post content starts here. You can use **Markdown** formatting.
```

### Configuration

The main configuration files are:

- `pelicanconf.py` - Development configuration
- `publishconf.py` - Production configuration

Edit these files to customize your blog settings.

## Customization

### Theme Customization

The theme files are located in the `theme/` directory:

- `templates/` - HTML templates
- `static/css/` - CSS stylesheets
- `static/font/` - Font files

The main CSS variables for theme colors can be found at the top of `theme/static/css/main.css`.

### Adding Pages

To add static pages (like About, Contact, etc.), create Markdown files in the `content/pages/` directory.

## Deployment

### GitHub Pages

To deploy your blog to GitHub Pages:

```bash
./blog.sh deploy
```

This script will:
1. Build your site with production settings
2. Use ghp-import to push to your gh-pages branch
3. Deploy to GitHub Pages

### Other Hosting

If you want to deploy elsewhere, run:

```bash
./blog.sh build production
```

This will generate the static site in the `output/` directory, which you can then upload to any web host.

## Folder Structure

```
.
├── blog.sh                # Management script
├── content/               # Blog content
│   ├── articles/          # Blog posts
│   └── pages/             # Static pages
├── output/                # Generated static site
├── pelicanconf.py         # Development settings
├── publishconf.py         # Production settings
└── theme/                 # Theme files
    ├── static/            # Static assets (CSS, JS, fonts)
    └── templates/         # HTML templates
```

## Using PEP 723 with uv

For simple scripts, you can use PEP 723 to specify dependencies inline within the script itself:

```python
# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "pelican",
#   "markdown",
#   "ghp-import",
# ]
# ///

# Your script code here
```

Then run it using:

```bash
uv run your_script.py
```

This is particularly useful for auxiliary scripts or one-off tools used with your blog.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Pelican - The static site generator
- Bootstrap 5 - For the responsive design
- Inter & Merriweather - Beautiful web fonts
- uv - Modern Python package manager
