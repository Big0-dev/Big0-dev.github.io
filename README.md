# Big0 Website - Static Site Generator

A modern, high-performance static website built with Python, Jinja2, and a custom design system.

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Basic knowledge of Markdown and HTML

### Installation & Build

```bash
# Clone the repository
git clone https://github.com/Big0-dev/Big0-dev.github.io.git
cd Big0-dev.github.io

# Install dependencies
pip install -r requirements.txt

# Build the site
python3 generate.py

# The site will be generated in the 'build' directory
```

## 📁 Project Structure

```
Big0-dev.github.io/
├── build/                  # Generated site output
├── content/               # Markdown content files
│   ├── blogs/            # Blog posts
│   ├── case_studies/     # Case study content
│   ├── industries/       # Industry pages
│   ├── news/            # News articles
│   └── services/        # Service pages
├── static/               # CSS, JS, and assets
│   ├── base.css         # Base styles
│   ├── components.css   # Reusable components
│   ├── design-system.css # Design tokens
│   └── ...              # Page-specific CSS
├── templates/            # Jinja2 templates
├── generate.py          # Static site generator
├── site_config.yaml     # Site configuration
└── requirements.txt     # Python dependencies
```

## 📝 Content Management

### Adding New Content

#### 1. **Services**
Create a new markdown file in `content/services/`:

```markdown
---
title: Your Service Name
meta_description: SEO description (150-160 chars)
description: Brief description for cards
icon: service-icon
features: Feature 1, Feature 2, Feature 3
---

# Your Service Content Here

Write your service description using markdown...
```

#### 2. **Industries**
Create a new markdown file in `content/industries/`:

```markdown
---
title: Industry Name
meta_description: SEO description
description: Brief description
icon: industry-icon
challenge: Main challenge this industry faces
solutions: Solution 1, Solution 2, Solution 3
---

# Industry Content Here
```

#### 3. **Blog Posts**
Create a new markdown file in `content/blogs/`:

```markdown
---
title: Blog Post Title
category: Technology
date: 2024-01-15
meta_description: SEO description
tags: ai, technology, innovation
---

# Blog Content Here
```

#### 4. **Case Studies**
Create a new markdown file in `content/case_studies/`:

```markdown
---
title: Case Study Title
client: Client Name
industry: Industry
challenge: The challenge faced
solution: How we solved it
results: Key outcomes
technologies: Tech 1, Tech 2, Tech 3
---

# Case Study Content
```

## 🎨 Template Directives

The site supports special template directives that can be used in markdown content to add rich components:

### Call-to-Action Templates

```markdown
{{template:cta}}                 # General CTA
{{template:cta-service}}         # Service-specific CTA  
{{template:cta-case-study}}      # Case study CTA
```

### Related Content Links

```markdown
# Link to related services
{{related-services:service-slug1,service-slug2,service-slug3}}

# Link to related industries
{{related-industries:industry-slug1,industry-slug2}}
```

### Industry-Specific Components

```markdown
# Display challenges in a grid
{{industry-challenges:Challenge 1|Challenge 2|Challenge 3}}

# Display solutions with descriptions
{{industry-solutions:Solution Title|Description,Another Solution|Its description}}
```

### Example Usage

```markdown
---
title: AI Integration Services
---

# Our AI Solutions

We provide cutting-edge AI integration services...

{{related-industries:finance,healthcare,retail}}

## Why Choose Us

Our expert team delivers...

{{template:cta-service}}
```

## 🛠️ Configuration

### Site Configuration (site_config.yaml)

The main configuration file controls:
- Site metadata and domain
- Navigation structure
- Content types and their templates
- Static pages
- Asset directories

Key sections:
```yaml
domain: https://big0.dev
title: Big0 - AI-Powered Digital Transformation

content_types:
  services:
    content_dir: ./content/services
    template: service_detail.html
    listing_template: services.html
    output_dir: services
```

### Adding Navigation Items

Edit `site_config.yaml`:
```yaml
navigation:
  home: index.html
  about: about.html
  services: services.html
  # Add new items here
```

## 🎯 SEO Optimization

### Best Practices

1. **Meta Descriptions**: Keep between 150-160 characters
2. **Title Tags**: Use descriptive, keyword-rich titles
3. **URL Structure**: Use kebab-case for file names
4. **Internal Linking**: Use template directives for cross-linking

### Sitemap Generation

The generator automatically creates:
- `sitemap.xml` - Main sitemap
- `sitemap-images.xml` - Image sitemap
- `rss.xml` - RSS feed for blogs and news

## 🚀 Deployment

The site is configured for GitHub Pages deployment:

1. Push changes to the main branch
2. GitHub Actions will automatically build and deploy
3. Site will be live at https://big0.dev

### Manual Deployment

```bash
# Build the site
python3 generate.py

# Commit and push
git add .
git commit -m "Update content"
git push origin main
```

## 🔧 Development

### Local Development Server

```bash
# Navigate to build directory
cd build

# Start a simple HTTP server
python3 -m http.server 8000

# View at http://localhost:8000
```

### CSS Architecture

The CSS follows a modular architecture:
- `design-system.css` - Design tokens and variables
- `base.css` - Global styles and resets
- `components.css` - Reusable UI components
- `[page].css` - Page-specific styles

### Adding New Templates

1. Create template in `templates/`
2. Add to `site_config.yaml`
3. Use Jinja2 syntax for dynamic content
4. Extend `base.html` for consistent layout

## 📊 Analytics & Tracking

The site includes:
- Google Analytics 4 (GA4)
- Microsoft Clarity for session recording
- Google Search Console verification

Configuration in `templates/base.html`.

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test locally with `python3 generate.py`
4. Submit a pull request

## 📝 Content Guidelines

### Writing Style
- Use clear, concise language
- Focus on benefits, not just features
- Include specific metrics and results
- Optimize for SEO without keyword stuffing

### Image Guidelines
- Use AVIF format for best performance
- Optimize images before uploading
- Include alt text for accessibility
- Store in appropriate directories

## 🐛 Troubleshooting

### Common Issues

**Build Errors**
```bash
# Check Python version
python3 --version

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

**Missing Content**
- Ensure markdown files have proper frontmatter
- Check file names match URL expectations
- Verify content directory paths in config

**CSS Not Loading**
- Check template includes correct CSS files
- Verify static file paths are correct
- Clear browser cache

## 📞 Support

For issues or questions:
- Create an issue on GitHub
- Contact: contact@big0.dev

---

Built with ❤️ by Big0 Dev Private Limited