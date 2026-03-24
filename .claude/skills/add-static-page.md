---
description: Add a new static page to the Big0.dev website. Use when creating pages like About, Contact, Careers, or other standalone pages that don't come from markdown content files.
---

# Adding a Static Page

Static pages are HTML templates that contain their own content (unlike content pages which are generated from markdown files).

## Steps

1. **Create a Jinja2 template** in `templates/` directory
   - Example: `templates/my-page.html`

2. **Extend the base template:**

```html
{% extends "base.html" %}

{% block title %}Page Title — Big0{% endblock %}
{% block meta_description %}SEO description under 160 chars.{% endblock %}

{% block content %}
<main>
  <section class="hero hero--standard">
    <div class="container">
      <h1>Page Title</h1>
      <p>Subtitle or description.</p>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <!-- Page content here -->
    </div>
  </section>
</main>
{% endblock %}
```

3. **Register in `site_config.yaml`** under `static_pages`:

```yaml
static_pages:
  # ... existing pages ...
  - template: my-page.html
    output: my-page.html
    title: Page Title
    description: SEO description for this page.
```

4. **Add navigation** (optional) — add to `navigation` section in `site_config.yaml`:

```yaml
navigation:
  # ... existing nav ...
  my_page: my-page.html
```

Then reference `{{ my_page }}` in templates for the URL.

## Template Context Variables

All static pages receive these context variables:

- `{{ static }}` — path to static assets directory
- `{{ domain }}` — site domain (https://big0.dev)
- `{{ path_prefix }}` — relative path prefix for URLs
- `{{ copyright }}` — current year
- `{{ home }}`, `{{ about }}`, `{{ services }}`, `{{ blog }}`, `{{ contact }}`, etc. — navigation URLs
- For the homepage (`index.html`): `{{ all_blogs }}`, `{{ all_services }}`, `{{ all_case_studies }}`, `{{ news_articles }}`, etc.

## CSS Classes Available

- `.hero`, `.hero--standard` — hero sections
- `.container` — max-width 1200px centered container
- `.section` — standard section padding
- `.btn`, `.btn-primary` — button styles
- `.badge` — badge/tag elements
- `.card` — card components

## SVG Icons

Use the `inject_svg` function in templates:

```html
{{ inject_svg('icon-name') }}
```

This injects the SVG from `static/icon-name.svg` inline.

## Build & Preview

```bash
python generate.py
```

Output: `/{output-filename}` (root level of the site).

## Special Pages

- **404 page** uses absolute paths (`/static/...`) instead of relative paths
- **Gallery page** is handled separately by `GalleryPageBuilder` with pagination
- **Homepage** (`index.html`) receives all content type data for rendering listings
