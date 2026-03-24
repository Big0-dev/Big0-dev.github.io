---
description: Understand the Big0.dev project architecture, code structure, and how all pieces fit together. Use when exploring the codebase, debugging build issues, or understanding how content flows from markdown to HTML.
---

# Big0.dev — Project Architecture & Code Structure

## Overview

Big0.dev is a **custom Python-based static site generator** that converts Markdown content + Jinja2 templates into a fully optimized static website hosted on **Cloudflare Pages**.

## Tech Stack

- **Language:** Python 3.13+
- **Templating:** Jinja2
- **Content:** Markdown with YAML frontmatter
- **Styling:** Hand-written CSS with design system variables
- **JS:** Vanilla JavaScript (no frameworks)
- **Hosting:** Cloudflare Pages
- **Dependencies:** `jinja2`, `markdown`, `pyyaml`, `beautifulsoup4`, `minify-html`, `rcssmin`, `jsmin`

## Directory Structure

```
/
├── generate.py                 # Main entry point — runs the full build
├── site_config.yaml            # Central config: pages, content types, nav, assets
├── site_generator/             # Core modules
│   ├── __init__.py
│   ├── content_processor.py    # Markdown→HTML, frontmatter, auto-linking, FAQ accordions
│   ├── asset_manager.py        # Static file copying, SVG injection, minification
│   ├── page_builders.py        # StaticPageBuilder, ContentPageBuilder, GalleryPageBuilder
│   └── seo_utilities.py        # Sitemap, RSS feed, search index generation
├── content/                    # All content (markdown files)
│   ├── blogs/                  # Blog posts
│   ├── case_studies/           # Case studies
│   ├── conversations/          # Conversational/interview format content
│   ├── gallery/                # Images + metadata.json
│   ├── news/                   # News items
│   ├── newsletters/            # Newsletter issues
│   ├── products/               # Products (currently empty)
│   ├── services/               # Service pages
│   └── team/                   # Team member profiles
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Master layout (nav, footer, meta tags)
│   ├── blog_post.html          # Blog detail page
│   ├── service_detail.html     # Service detail (generic)
│   ├── service_bespoke.html    # Service detail (custom layout — used by all 3 services)
│   ├── case_study_detail.html  # Case study detail
│   ├── newsletter_detail.html  # Newsletter issue detail
│   ├── news_detail.html        # News detail
│   ├── team_detail.html        # Team member profile
│   ├── conversation_detail.html # Conversation detail
│   ├── blogs.html              # Blog listing (paginated)
│   ├── services.html           # Services listing
│   ├── case_studies.html       # Case studies listing (paginated)
│   ├── newsletters.html        # Newsletter listing
│   ├── index.html              # Homepage
│   └── [other static pages]
├── static/                     # Static assets
│   ├── *.avif                  # Optimized images
│   ├── *.svg                   # Icons
│   ├── *.woff2                 # Fonts (DM Sans, Exo 2)
│   ├── *.css                   # Stylesheets
│   ├── *.js                    # Client-side scripts
│   └── clients/                # Client logo SVGs
├── build/                      # Generated output (gitignored, created during build)
├── functions/                  # Cloudflare Pages Functions
│   └── _middleware.js
├── _routes.json                # Cloudflare Pages routing
├── _redirects                  # Redirect rules
└── robots.txt
```

## Build Pipeline

Run: `python generate.py`

The build follows this sequence:
1. Load `site_config.yaml`
2. Setup Jinja2 environment with custom filters (`xmlescape`) and globals (`inject_svg`)
3. Clean `./build/` directory
4. Copy static assets (fonts, images, CSS, JS, gallery, favicons)
5. Generate static pages (index, about, contact, careers, privacy, terms, 404, compliance)
6. Generate gallery pages (with pagination, 6 per page)
7. Generate content pages (detail + listing pages for each content type)
8. Generate SEO artifacts (sitemap.xml, sitemap-images.xml, rss.xml, search-index.json)
9. Minify all HTML, CSS, JS output

## Content Processing Flow

`ContentProcessor.load_markdown_content(file_path)`:
1. Read `.md` file
2. Split YAML frontmatter from markdown body
3. Process template directives (`{{template:cta}}`, `{{related-services:...}}`)
4. Convert markdown → HTML via `markdown` library (extensions: extra, codehilite, toc)
5. Process FAQ sections into interactive accordions with JSON-LD schema
6. Auto-link industry/service/case-study keywords in blog, case study, news, and conversation pages
7. Extract excerpt, parse date, parse features, return structured dict

## URL Routing

- **Static pages:** `/index.html`, `/about.html`, `/contact.html`, etc.
- **Content pages:** `/{output_dir}/{slug}.html` (e.g., `/blogs/my-post.html`)
- **Listing pages:** `/{content-type}.html` with pagination (`/blogs-2.html`)
- **Gallery:** `/gallery.html`, `/gallery-2.html`, etc.

Slugs are derived from the markdown filename (e.g., `my-post.md` → `my-post`).

## Key Config: site_config.yaml

Defines:
- `domain` — base URL
- `static_pages[]` — list of template→output mappings with title/description
- `content_types{}` — each type has: `content_dir`, `template`, `listing_template`, `output_dir`, `per_page`, `exclude_from_nav`
- `navigation{}` — URL mappings for nav links
- `assets{}` — directories for static files, gallery, and output

## Design System

- **Dark theme** by default
- **Colors:** Void (#0A0F1C), Signal (teal #0D9488), Cloud, Mist
- **Fonts:** "Exo 2" (display), "DM Sans" (body) — preloaded WOFF2
- **CSS files:** base.css (critical, inlined), components.css, design-system.css, detail-pages.css, home.css, services-bespoke.css
- **Responsive:** 768px mobile/tablet breakpoint

## Template Directives (usable in markdown content)

- `{{template:cta}}` — inline call-to-action block
- `{{template:cta-service}}` — service-specific CTA
- `{{template:cta-case-study}}` — case study CTA
- `{{related-services:slug1,slug2}}` — related services grid

## Modular Architecture

- `SiteGenerator` (generate.py) — orchestrator
- `ContentProcessor` — markdown conversion, auto-linking, FAQ processing
- `AssetManager` — static file management, SVG injection, output optimization
- `SEOUtilities` — sitemap, RSS, search index
- `StaticPageBuilder` — homepage, about, contact, etc.
- `ContentPageBuilder` — all content type detail + listing pages
- `GalleryPageBuilder` — gallery with pagination
