---
description: Build the Big0.dev website and understand the deployment process. Use when building locally, debugging build errors, or deploying to Cloudflare Pages.
---

# Build & Deploy Process

## Local Build

```bash
cd /Users/hassan/Code/Big0-dev.github.io
python generate.py
```

This generates the full site into `./build/`.

### Build Sequence

1. **Clean** — removes and recreates `./build/` directory
2. **Copy assets** — static files, gallery images, `_redirects`, `robots.txt`, `_routes.json`
3. **Generate static pages** — index, about, contact, careers, privacy, terms, 404, compliance
4. **Generate gallery** — paginated gallery pages (6 images per page)
5. **Generate content pages** — for each content type: detail pages + paginated listing pages
6. **Generate SEO artifacts** — sitemap.xml, sitemap-images.xml, rss.xml, search-index.json
7. **Optimize output** — minify HTML, CSS, JS

### Prerequisites

```bash
pip install -r requirements.txt
```

Dependencies: `jinja2`, `markdown`, `pyyaml`, `beautifulsoup4`, `minify-html`, `rcssmin`, `jsmin`, `babel`

## Local Preview

After building, serve the `build/` directory with any static server:

```bash
cd build && python -m http.server 8000
```

Then open `http://localhost:8000`.

## Deployment

The site is hosted on **Cloudflare Pages**.

### Deployment Files

- `_routes.json` — Cloudflare Pages function routing config
- `_redirects` — URL redirect rules
- `functions/_middleware.js` — Cloudflare Pages edge function middleware
- `robots.txt` — SEO crawling rules

### Deploy Process

Push to the `main` branch. Cloudflare Pages automatically builds and deploys.

The build output in `./build/` is the deployment artifact — Cloudflare serves everything from that directory.

## Debugging Build Issues

### Common Issues

1. **Missing template** — check `site_config.yaml` content_types for correct template name
2. **Frontmatter parse error** — ensure YAML is valid (check colons, indentation)
3. **Missing image** — verify the file exists in `static/` with the exact filename
4. **Date parse error** — use supported formats: `Month Day, Year` or `YYYY-MM-DD`
5. **Template directive not rendering** — ensure `{{template:name}}` is on its own line in markdown

### Build Logs

The generator uses Python `logging` at INFO level. Watch for:
- `ERROR:` — something broke
- `WARNING:` — non-fatal issues (e.g., unparseable dates)
- `INFO:` — progress updates ("Generated: blogs/my-post.html")

## SEO Artifacts Generated

| File | Purpose |
|---|---|
| `sitemap.xml` | All pages for search engine crawling |
| `sitemap-images.xml` | Gallery images sitemap |
| `rss.xml` | RSS feed (blogs, news, case studies) |
| `search-index.json` | Client-side search index (used by MiniSearch) |
