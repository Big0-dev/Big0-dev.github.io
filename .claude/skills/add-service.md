---
description: Add a new service page to the Big0.dev website. Use when creating a new service offering with capabilities, evidence items, and bespoke layout.
---

# Adding a Service Page

## Steps

1. **Create a markdown file** in `content/services/` with a kebab-case filename
   - Example: `content/services/my-service.md` → `/services/my-service.html`

2. **Add YAML frontmatter** (services use the richest frontmatter of any content type):

```yaml
---
template: service_bespoke.html
title: "Service Title | Big0"
hero_title: "Service Title"
description: "Short description of the service offering."
meta_description: SEO description under 160 chars.
icon: ai
hero_image: hero-image-name
features: "Feature 1, Feature 2, Feature 3, Feature 4, Feature 5, Feature 6"
keywords:
  - keyword1
hero_badges:
  - text: "Badge Text"
    color: cyan
  - text: "Another Badge"
    color: green
hero_scramble:
  - "Scramble Line 1"
  - "Scramble Line 2"
  - "Scramble Line 3"
challenge: "Problem statement paragraph."
challenge_title: "Challenge Section Heading"
capabilities:
  - title: "Capability 1"
    desc: "Description of capability."
    icon: layers
    badge: "Shipped"
    badge_color: cyan
  - title: "Capability 2"
    desc: "Description of capability."
    icon: dashboard
    badge: "Real-Time"
    badge_color: green
evidence_items:
  - title: "Case Study Title"
    desc: "Brief description of the evidence."
    badge: "Published"
    badge_color: cyan
    slug: case-study-slug
---
```

### Key Frontmatter Fields

| Field | Required | Description |
|---|---|---|
| `template` | Yes | Use `service_bespoke.html` for the custom layout |
| `title` | Yes | Page title (include "| Big0" suffix) |
| `hero_title` | Yes | Display title in hero section |
| `description` | Yes | Service description |
| `meta_description` | Yes | SEO description |
| `icon` | Yes | SVG icon name from `static/` |
| `hero_image` | Yes | Hero background image name from `static/` |
| `features` | Yes | Comma-separated feature list (shown as badges) |
| `hero_badges` | No | Array of `{text, color}` badges in hero |
| `hero_scramble` | No | Array of text lines for scramble animation |
| `challenge` | Yes | Problem statement paragraph |
| `challenge_title` | Yes | Challenge section heading |
| `capabilities` | Yes | Array of `{title, desc, icon, badge, badge_color}` |
| `evidence_items` | No | Array of case study references with `slug` linking to case studies |

### Badge Colors

Available colors: `cyan`, `green`, `amber`, `primary`

3. **Write the markdown body** — this renders below the structured frontmatter sections.

4. **Evidence items** automatically pull icons from linked case studies via `slug` field. Ensure the case study exists in `content/case_studies/`.

## Auto-Linking Integration

After adding a service, add keyword mappings in `content_processor.py` → `service_links` dict so mentions auto-link from blogs/case studies/conversations.

## Build & Preview

```bash
python generate.py
```

Output: `/services/{slug}.html` and listed on `/services.html`.

## Templates Used

- Detail: `templates/service_bespoke.html` (custom) or `templates/service_detail.html` (generic)
- Listing: `templates/services.html`
