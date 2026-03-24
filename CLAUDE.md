# CLAUDE.md — Big0.dev Website

## About This Project

This is the marketing website for **Big0 Dev** (https://big0.dev), a software engineering company based in Islamabad, Pakistan. The site is a custom Python-based static site generator that outputs to Cloudflare Pages.

## About the Company

**Big0 Dev** is an engineer-led software firm that builds AI-powered applications, custom software, and startup engineering solutions for clients in the UK, US, Australia, and Middle East.

**Key differentiators:**
- The CEO (Hassan Kamran) writes code and talks to every client directly — no salespeople
- The CTO (Musab Akram) reviews every PR across all projects
- Published AI research in PLOS ONE and IEEE journals
- Engineering hub in Islamabad with senior talent at fair rates
- Sprint-based delivery with working demos every 2 weeks

**Leadership:**
- **Kamran Bashir** — Chairman (aerospace engineer, 25+ years defense, NED + NUST)
- **Hassan Kamran** — CEO & Founder (Army Captain → NUST → published researcher → Big0)
- **Musab Akram** — Co-Founder & CTO (NUST → CarbonTeq → Radity → Big0)

**3 Services:**
1. AI-Powered Applications — document processing, intelligent search, workflow automation, analytics
2. Custom Software Development — web/mobile apps, full-stack platforms, UI/UX
3. Startup Engineering — hardware, IoT, embedded systems, PCB, drones, prototyping

**Clients:** Khan (internal AI project manager), Slap Stack (Germany), Auxilio UK (legal tech)

**Contact:** contact@big0.dev | +92 303 944 1945 | Islamabad, PKT (GMT+5)

**Brand voice:** Direct, evidence-based, no-BS. "Not claims. Evidence." — ship working software, not slide decks. Anti-corporate, engineer-first tone.

## Tech Stack

- **Generator:** Custom Python 3.13+ static site generator (`generate.py`)
- **Templating:** Jinja2
- **Content:** Markdown with YAML frontmatter
- **Styling:** Hand-written CSS with design system (dark theme default, light mode supported)
- **JS:** Vanilla JavaScript (no frameworks)
- **Fonts:** "Exo 2" (display), "DM Sans" (body)
- **Images:** AVIF format, optimized
- **Hosting:** Cloudflare Pages
- **Dependencies:** jinja2, markdown, pyyaml, beautifulsoup4, minify-html, rcssmin, jsmin

## Project Structure

```
generate.py              # Main entry point — `python generate.py` builds the site
site_config.yaml         # Central config: pages, content types, nav URLs, assets
site_generator/          # Core modules (content_processor, asset_manager, page_builders, seo_utilities)
content/                 # All markdown content
  blogs/                 # Blog posts (19 files)
  case_studies/          # Case studies (13 files)
  conversations/         # Interview-format dialogues (12 files)
  newsletters/           # Newsletter issues (7 files)
  news/                  # Company news (4 files)
  services/              # Service pages (3 files)
  team/                  # Team profiles (4 files)
  gallery/               # Images + metadata.json
  products/              # Products (currently empty)
templates/               # Jinja2 HTML templates
static/                  # CSS, JS, fonts, images, SVG icons
build/                   # Generated output (gitignored)
```

## Key Commands

```bash
# Build the site
python generate.py

# Preview locally
cd build && python -m http.server 8000

# Build with optimization disabled (faster for dev)
OPTIMIZE_OUTPUT=false uv run python generate.py
```

## Content Workflow

All content is markdown with YAML frontmatter in the `content/` directory. The filename (without extension) becomes the URL slug.

**Adding content:** Create a `.md` file in the appropriate `content/` subdirectory with the correct frontmatter. Run `python generate.py` to build. See `.claude/skills/` for detailed guides per content type.

**URL pattern:** `/{output_dir}/{slug}.html` (e.g., `/blogs/my-post.html`)

**Template directives in markdown:**
- `{{template:cta}}` — call-to-action block
- `{{template:cta-service}}` — service CTA
- `{{template:cta-case-study}}` — case study CTA
- `{{related-services:slug1,slug2}}` — related services grid

**Auto-linking:** Keywords matching services and case studies are automatically linked in blog, case study, news, and conversation pages. Mappings are in `site_generator/content_processor.py`.

## Additional Working Directory

`/Users/hassan/Code/hassan-kamran.github.io` — Hassan Kamran's personal portfolio site (engrhassankamran.com). Uses the same Python static generator pattern but is a separate, simpler site.

## Relevant MCP Tools Available

Use these tools when working on this project:

- **Claude Preview** (`mcp__Claude_Preview__*`) — Start the dev server, take screenshots, inspect elements, click/fill, check console logs. Use `preview_start` with a launch.json config to serve `build/` and visually verify changes.
- **Claude in Chrome** (`mcp__Claude_in_Chrome__*`) — Browser automation for testing the live site at big0.dev or localhost. Read pages, find elements, take screenshots, execute JS.
- **Google Drive** (`mcp__c1fc4002-*__google_drive_*`) — Search and fetch company documents from Google Drive. Useful for finding brand materials, client briefs, content drafts, or reference docs.
- **Scheduled Tasks** (`mcp__scheduled-tasks__*`) — Schedule recurring tasks like periodic builds, content audits, or SEO checks.

## Code Conventions

- **Python:** Standard Python style, type hints used, logging via `logging` module
- **CSS:** Custom properties (CSS variables) for theming, mobile-first responsive at 768px breakpoint
- **Templates:** Jinja2 with `{% extends "base.html" %}`, autoescape enabled
- **Content:** YAML frontmatter + markdown body, dates as `Month Day, Year` or `YYYY-MM-DD`
- **Images:** AVIF format, placed in `static/`, referenced by filename only in frontmatter
- **SVG icons:** Placed in `static/`, injected inline via `{{ inject_svg('name') }}` in templates

## Design System

- **Colors:** Void (#0A0F1C), Midnight, Slate, Steel, Signal (teal #0D9488), Cloud, Mist, White
- **Badge colors:** cyan, green, amber, primary
- **Border radius:** 10px (cards), 12px (larger elements)
- **Transitions:** 0.2s ease
- **Container:** max-width 1200px
- **Dark theme default**, light mode via toggle (localStorage persisted)

## Skills Reference

Detailed process guides are in `.claude/skills/`:
- `project-overview.md` — Full architecture reference
- `add-blog-post.md` — Creating blog posts
- `add-case-study.md` — Creating case studies
- `add-service.md` — Creating service pages
- `add-newsletter.md` — Creating newsletter issues
- `add-news-item.md` — Creating news items
- `add-team-member.md` — Creating team profiles
- `add-conversation.md` — Creating interview-format content
- `add-static-page.md` — Creating standalone HTML pages
- `build-and-deploy.md` — Build process and deployment
