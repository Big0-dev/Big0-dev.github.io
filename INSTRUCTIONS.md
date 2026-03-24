# Big0.dev Website — Developer & AI Agent Instructions

This document tells you everything you need to work on the Big0.dev website, whether you're a human developer or an AI coding agent (Claude Code, Cursor, etc.). Read this before touching any code.

---

## 1. What Is This Project?

This is the marketing website for **Big0 Dev** — a software engineering company based in Islamabad, Pakistan. The site lives at https://big0.dev.

It is **not** built with any framework you've seen before. It's a **custom Python static site generator** that:
- Reads markdown files with YAML frontmatter from `content/`
- Renders them through Jinja2 templates in `templates/`
- Outputs a fully optimized static site into `build/`
- Deploys to Cloudflare Pages on push to `main`

There is no React, no Next.js, no Hugo, no Jekyll. It's custom Python. Don't try to install npm packages or run framework-specific commands.

---

## 2. First-Time Setup

```bash
# Clone the repo
git clone <repo-url>
cd Big0-dev.github.io

# Install Python dependencies (requires Python 3.13+)
pip install -r requirements.txt
# OR with uv (preferred):
uv sync

# Build the site
python generate.py

# Preview locally
cd build && python -m http.server 8000
# Open http://localhost:8000
```

### Quick build (skip minification during development):
```bash
OPTIMIZE_OUTPUT=false uv run python generate.py
```

---

## 3. Project Map

Learn where everything lives before you change anything.

```
Big0-dev.github.io/
│
├── generate.py                  ← Entry point. Run this to build.
├── site_config.yaml             ← Central config. All pages, content types, nav URLs.
├── CLAUDE.md                    ← AI agent context (company info, conventions, tools)
├── INSTRUCTIONS.md              ← You are here
│
├── site_generator/              ← The engine (don't touch unless fixing bugs)
│   ├── content_processor.py     ← Markdown→HTML, frontmatter parsing, auto-linking, FAQ accordions
│   ├── asset_manager.py         ← Copies static files, injects SVGs, minifies output
│   ├── page_builders.py         ← StaticPageBuilder, ContentPageBuilder, GalleryPageBuilder
│   └── seo_utilities.py         ← Generates sitemap.xml, RSS feed, search index
│
├── content/                     ← ALL CONTENT LIVES HERE (markdown files)
│   ├── blogs/                   ← Blog posts (date-sorted, paginated at 9/page)
│   ├── case_studies/            ← Client work evidence (challenge/solution/results format)
│   ├── conversations/           ← Interview-style dialogues about case studies
│   ├── newsletters/             ← Newsletter issues (issue_number sorted)
│   ├── news/                    ← Company announcements, speaking events
│   ├── services/                ← The 3 service pages (AI, Software, Startup Engineering)
│   ├── team/                    ← Team member profiles
│   ├── gallery/                 ← Event photos (images + metadata.json)
│   └── products/                ← Product pages (currently empty)
│
├── templates/                   ← Jinja2 HTML templates
│   ├── base.html                ← Master layout — nav, footer, meta, CSS/JS loading
│   ├── index.html               ← Homepage
│   ├── blog_post.html           ← Blog detail page
│   ├── service_bespoke.html     ← Service detail (used by all 3 services)
│   ├── case_study_detail.html   ← Case study detail
│   ├── conversation_detail.html ← Conversation detail
│   ├── newsletter_detail.html   ← Newsletter detail
│   ├── news_detail.html         ← News detail
│   ├── team_detail.html         ← Team member profile
│   ├── blogs.html               ← Blog listing (paginated)
│   ├── case_studies.html        ← Case studies listing (paginated)
│   ├── services.html            ← Services listing
│   ├── newsletters.html         ← Newsletter listing
│   ├── cta.html                 ← Reusable CTA section (included via {% include %})
│   ├── contact-form-bant.html   ← Contact form component
│   └── [about, contact, careers, privacy, terms, 404, compliance, gallery].html
│
├── static/                      ← All static assets
│   ├── *.css                    ← Stylesheets (see CSS Architecture below)
│   ├── *.js                     ← Client-side scripts
│   ├── *.avif                   ← Optimized images (AVIF format only)
│   ├── *.svg                    ← Icons (injected inline by the generator)
│   ├── *.woff2                  ← Fonts (DM Sans, Exo 2)
│   └── clients/                 ← Client logo SVGs
│
├── build/                       ← Generated output (GITIGNORED — never edit directly)
├── functions/                   ← Cloudflare Pages edge functions
│   └── _middleware.js
├── _routes.json                 ← Cloudflare Pages routing
├── _redirects                   ← URL redirect rules
└── robots.txt
```

---

## 4. How the Build Works

When you run `python generate.py`, this happens in order:

1. **Load config** — reads `site_config.yaml`
2. **Clean** — deletes and recreates `build/`
3. **Copy assets** — static files, gallery images, `_redirects`, `robots.txt`, `_routes.json`
4. **Generate static pages** — index, about, contact, careers, privacy, terms, 404, compliance
5. **Generate gallery** — paginated (6 images per page)
6. **Generate content pages** — for each content type defined in config:
   - Reads all `.md` files from the content directory
   - Parses YAML frontmatter + markdown body
   - Processes template directives, FAQ sections, auto-links
   - Renders through Jinja2 template → writes `.html` to `build/`
   - Generates paginated listing pages
7. **Generate SEO** — sitemap.xml, sitemap-images.xml, rss.xml, search-index.json
8. **Minify** — compresses all HTML, CSS, JS in `build/`

### What the content processor does to your markdown:

- Converts markdown → HTML (with `extra`, `codehilite`, `toc` extensions)
- Replaces `{{template:cta}}` directives with CTA HTML blocks
- Converts FAQ sections (## FAQ + ### Question headings) into interactive accordions with JSON-LD schema
- Auto-links keywords: if your blog post mentions "machine learning", it auto-links to the AI service page. Mappings are in `content_processor.py`

---

## 5. How to Add Content

### The universal pattern:

1. Create a `.md` file in the right `content/` subdirectory
2. Add the correct YAML frontmatter at the top (between `---` markers)
3. Write your markdown body below
4. Run `python generate.py`
5. Preview at `http://localhost:8000`

**The filename becomes the URL slug.** `content/blogs/my-post.md` → `/blogs/my-post.html`

### Blog Post (`content/blogs/`)

```yaml
---
title: Your Blog Post Title
category: AI Applications
date: March 24, 2026
image_url: hero-image.avif
meta_description: SEO description under 160 chars.
tags: tag1, tag2, tag3
---

Your markdown content here. Use ## for sections.
```

### Case Study (`content/case_studies/`)

```yaml
---
title: Project Name
industry: Healthcare
type: AI Platform
icon: ai
meta_description: SEO description under 160 chars.
challenge: One paragraph about the problem.
solution: One paragraph about what we built.
results: 53% Faster,84% Less Water,65% Cost Savings
result_descriptions: Detail 1,Detail 2,Detail 3
technologies: Python,React,AWS,PostgreSQL
description: Short card description.
order: 10
---
```

### Newsletter (`content/newsletters/`)

```yaml
---
title: "Issue Title"
issue_number: 8
date: March 24, 2026
meta_description: SEO description.
subtitle: Tagline
topics: [ai, security, tools]
---
```

### News (`content/news/`)

```yaml
---
title: News Headline
category: Speaking Engagement
date: 2026-03-24
tags: tag1,tag2
description: Short description.
order: 1
---
```

### Team Member (`content/team/`)

```yaml
---
title: "Full Name"
role: "Job Title"
photo: "team-photo.avif"
meta_description: "Short bio."
linkedin: "https://linkedin.com/in/..."
timeline: ["Step 1", "Step 2", "Current"]
badges:
  - text: "Credential"
    color: "green"
experience:
  - company: "Company"
    role: "Title"
    period: "Start — End"
    location: "City"
    highlights:
      - "Achievement"
---
```

### Conversation (`content/conversations/`)

```yaml
---
title: "Conversation Title"
subtitle: A conversation between X and Y about Z
meta_description: SEO description.
category: Agriculture Technology
intro: "Scene-setting paragraph."
date: 2024-12-15
tags: tag1, tag2
---

## Section Title

**Speaker A:** Dialogue text.

**Speaker B:** Response text.
```

### Service Page (`content/services/`)

Service pages are the most complex. They use `service_bespoke.html` template with structured frontmatter for capabilities, evidence items, badges, and hero content. See `.claude/skills/add-service.md` for the full schema.

---

## 6. CSS Architecture

There are no CSS preprocessors. All styles are hand-written CSS with custom properties.

| File | Purpose |
|---|---|
| `design-system.css` | Color palette, spacing tokens, typography, grid, shadows, theme variables |
| `base.css` | Resets, font-face declarations (inlined in `<head>` for critical rendering) |
| `components.css` | Navbar, buttons, badges, cards, forms, search, footer |
| `home.css` | Homepage-specific: hero, trusted strip, process grid, differentiators |
| `detail-pages.css` | Blog/case study/newsletter article styling |
| `services-bespoke.css` | Service page custom layout |
| `contact-form-bant.css` | Contact form styling |
| `cookie-consent.css` | Cookie banner |

### Design tokens (CSS custom properties):

```css
/* Colors */
--color-void: #0A0F1C;      /* Darkest background */
--color-midnight: #0F1629;   /* Dark background */
--color-slate: #151B2E;      /* Card background */
--color-steel: #1E2642;      /* Borders */
--color-signal: #0D9488;     /* Teal accent (primary action color) */
--color-cloud: #94A3B8;      /* Secondary text */
--color-mist: #CBD5E1;       /* Lighter secondary text */
--color-white: #F8FAFC;      /* Primary text */

/* Typography */
--font-display: "Exo 2", sans-serif;    /* Headings */
--font-body: "DM Sans", sans-serif;     /* Body text */

/* Spacing */
--space-xs: 4px;  --space-sm: 8px;  --space-md: 16px;
--space-lg: 24px; --space-xl: 32px; --space-2xl: 48px;
```

### Rules:
- Always use CSS variables, never hardcode colors
- Both dark and light theme must work — test both
- Mobile breakpoint: `768px`
- Container max-width: `1200px`
- Border radius: `10px` (cards), `12px` (larger)
- Transitions: `0.2s ease`

---

## 7. JavaScript

Vanilla JS only. No build tools, no bundlers, no npm.

| File | Purpose |
|---|---|
| `text-scramble.js` | Text scramble animation on hero headings |
| `hero-particles.js` | Background particle effect on homepage hero |
| `search.js` | Client-side search using MiniSearch (reads `search-index.json`) |
| `cookie-consent.js` | Cookie consent banner logic |
| `minisearch@7.1.2.min.js` | MiniSearch library (vendored) |

If you need new JS, add a `.js` file in `static/` and include it in the relevant template with `<script src="{{ static }}/your-file.js" defer></script>`.

---

## 8. Templates

All templates extend `base.html`. The pattern:

```html
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}
{% block meta_description %}SEO description{% endblock %}

{% block content %}
  <!-- Your page HTML here -->
{% endblock %}
```

### Template context variables (available in all templates):

| Variable | Value |
|---|---|
| `{{ static }}` | Path to static assets (`static` or `../static`) |
| `{{ domain }}` | `https://big0.dev` |
| `{{ path_prefix }}` | Relative path prefix (empty for root, `../` for subdirs) |
| `{{ home }}`, `{{ about }}`, `{{ blog }}`, `{{ contact }}`, etc. | Navigation URLs |
| `{{ copyright }}` | Current year |
| `{{ inject_svg('icon-name') }}` | Inline SVG from `static/icon-name.svg` |

### Content detail templates receive:

| Variable | Value |
|---|---|
| `{{ item }}` | Full content dict (slug, title, content_html, frontmatter, etc.) |
| `{{ item.content_html }}` | Rendered HTML from markdown |
| `{{ item.frontmatter }}` | Raw YAML frontmatter dict |
| `{{ item.slug }}` | URL slug |
| `{{ item.title }}` | Page title |
| `{{ item.meta_description }}` | SEO description |

---

## 9. Images

- **Format:** AVIF only (exception: SVG for icons/logos)
- **Location:** `static/` directory
- **Reference in frontmatter:** just the filename (`hero-image.avif`), not the path
- **Reference in markdown:** `![Alt text](../static/image-name.avif)`
- **Reference in templates:** `{{ static }}/image-name.avif`
- **Optimization:** keep images under ~100KB. Use `avifenc` to compress.

### Converting to AVIF:
```bash
avifenc --min 20 --max 40 input.jpg output.avif
```

---

## 10. Adding a New Content Type

If you need a content type beyond blogs/case studies/news/etc.:

1. Create the content directory: `content/my_type/`
2. Create the detail template: `templates/my_type_detail.html`
3. (Optional) Create the listing template: `templates/my_types.html`
4. Register in `site_config.yaml`:

```yaml
content_types:
  my_type:
    content_dir: ./content/my_type
    template: my_type_detail.html
    listing_template: my_types.html   # optional
    output_dir: my-type               # URL path segment
    per_page: 9                       # optional, for pagination
    exclude_from_nav: true            # optional
```

5. Run `python generate.py` — it will automatically pick up the new type.

---

## 11. Auto-Linking System

The content processor automatically links keyword mentions to relevant service and case study pages. This happens in `site_generator/content_processor.py` in the `add_automatic_interlinking` method.

**Active on:** blog posts, case studies, news, conversations

**How it works:**
- A dict maps keywords → slugs (e.g., `'machine learning' → 'ai-powered-applications'`)
- When rendering HTML, text nodes are scanned for keyword matches
- Matches get wrapped in `<a>` tags pointing to the service/case study page
- Longest matches win (prevents "machine" matching before "machine learning")
- Self-links are avoided (a page won't link to itself)

**To add a new auto-link:** Add the keyword mapping to `service_links` or `case_study_links` in `content_processor.py`.

---

## 12. Template Directives

You can embed these in your markdown content (on their own line):

| Directive | What it renders |
|---|---|
| `{{template:cta}}` | Generic CTA: "Talk to Our Engineers" |
| `{{template:cta-service}}` | Service CTA: "Need This Built?" |
| `{{template:cta-case-study}}` | Case study CTA: "Want Similar Results?" |
| `{{related-services:slug1,slug2}}` | Grid of related service links |

---

## 13. SEO Artifacts

The build automatically generates:

| File | Content |
|---|---|
| `sitemap.xml` | All pages (static + content) |
| `sitemap-images.xml` | Gallery images with metadata |
| `rss.xml` | Feed of blogs, news, case studies |
| `search-index.json` | JSON index for client-side MiniSearch |

These are generated by `site_generator/seo_utilities.py`. No manual work needed.

---

## 14. Deployment

**Hosting:** Cloudflare Pages

**Deploy process:** Push to `main`. Cloudflare Pages auto-builds and deploys.

**Key deployment files:**
- `_routes.json` — tells Cloudflare which routes hit edge functions
- `_redirects` — URL redirect rules (old URLs → new URLs)
- `functions/_middleware.js` — Cloudflare Pages edge middleware
- `robots.txt` — search engine crawling rules

**The `build/` directory is gitignored.** Cloudflare runs the build on their end.

---

## 15. Common Tasks — Quick Reference

| Task | What to do |
|---|---|
| Add a blog post | Create `content/blogs/slug.md` with frontmatter, run `python generate.py` |
| Add a case study | Create `content/case_studies/slug.md`, run build |
| Add a team member | Create `content/team/slug.md`, add photo to `static/`, run build |
| Change nav links | Edit `navigation:` in `site_config.yaml` |
| Add an SVG icon | Place `icon.svg` in `static/`, use `{{ inject_svg('icon') }}` in templates |
| Add an image | Convert to AVIF, place in `static/`, reference in content/templates |
| Change colors/spacing | Edit `static/design-system.css` |
| Change layout/components | Edit `static/components.css` |
| Fix a page template | Edit the relevant file in `templates/` |
| Add auto-link keywords | Edit `service_links` or `case_study_links` in `content_processor.py` |
| Add a redirect | Add a line to `_redirects` |
| Debug build errors | Check the terminal output for ERROR/WARNING logs |

---

## 16. Rules & Gotchas

1. **Never edit files in `build/`** — they get deleted on every build
2. **Filenames are URLs** — `my-great-post.md` becomes `/blogs/my-great-post.html`
3. **Dates matter** — blogs and news sort by date (newest first). Use `Month Day, Year` or `YYYY-MM-DD`
4. **AVIF only for images** — no JPG/PNG in production. Convert first.
5. **Test both themes** — dark mode is default but light mode exists. Don't hardcode colors.
6. **Run the build after every change** — there's no hot reload, it's a static generator
7. **Check the listing pages** — after adding content, verify it appears on the listing page too
8. **Frontmatter is YAML** — indentation matters, strings with colons need quotes
9. **Service pages use `service_bespoke.html`** — they specify `template: service_bespoke.html` in frontmatter to override the default
10. **Auto-linking is aggressive** — if you don't want a keyword linked, it can't be avoided without modifying the processor

---

## 17. AI Agent Instructions

If you're an AI coding agent (Claude Code, Cursor, etc.) working on this project:

1. **Read `CLAUDE.md` first** — it has company context, brand voice, and tool references
2. **Read the relevant `.claude/skills/` file** before creating content — each content type has a detailed guide with exact frontmatter schemas
3. **Always build after changes** — run `python generate.py` and check for errors
4. **Don't over-engineer** — this is a content site. Simple changes should stay simple.
5. **Don't add frameworks** — no React, no Tailwind, no npm packages. It's vanilla CSS/JS.
6. **Don't create new CSS files** — add styles to the existing CSS file that matches the scope
7. **Use AVIF for images** — convert with `avifenc` before adding
8. **Preserve the brand voice** — direct, evidence-based, engineer-first, no corporate fluff
9. **Test the build** — if the build breaks, you broke something. Fix it before committing.
10. **Commit granularly** — one logical change per commit, clear messages

### Available AI tools (if using Claude Code with MCP):
- **Claude Preview** — serve `build/`, take screenshots, inspect CSS, verify layouts
- **Claude in Chrome** — test the live site or localhost in a real browser
- **Google Drive** — search for company docs, client briefs, content drafts
- **Scheduled Tasks** — automate recurring builds or audits

---

## 18. File-by-File Reference

### `site_config.yaml` fields:

```yaml
domain: https://big0.dev                    # Base URL
static_pages:                               # Templates rendered as-is at root level
  - template: index.html
    output: index.html
    title: Page Title
    description: SEO description
content_types:                              # Content generated from markdown
  blogs:
    content_dir: ./content/blogs            # Where to find .md files
    template: blog_post.html                # Jinja2 detail template
    listing_template: blogs.html            # Jinja2 listing template
    output_dir: blogs                       # URL path segment
    per_page: 9                             # Items per listing page
    exclude_from_nav: false                 # Hide from navigation
navigation:                                 # URL mappings for template variables
  home: index.html
  about: about.html
  # ...
assets:
  static_dir: ./static
  output_dir: ./build
```

### Content dict (what templates receive as `item`):

```python
{
    'slug': 'filename-without-extension',
    'title': 'From frontmatter title field',
    'meta_description': 'From frontmatter or auto-extracted',
    'short_description': 'From description field or excerpt',
    'content_html': '<p>Rendered HTML from markdown body</p>',
    'frontmatter': { ... },  # Raw YAML dict — access any custom field here
    'icon': 'svg-icon-name',
    'features': ['Feature 1', 'Feature 2'],
    'excerpt': 'First paragraph text',
    'category': 'Category Name',
    'date': datetime(2026, 3, 24),  # Parsed datetime object
    'tags': ['tag1', 'tag2'],
    'external_link': 'https://...',  # Optional
}
```

---

*Last updated: March 2026. If something in this doc doesn't match reality, the code is the source of truth — update this doc.*
