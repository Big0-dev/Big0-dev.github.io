---
description: Add a new case study to the Big0.dev website. Use when documenting a completed project with challenge, solution, results, and technologies.
---

# Adding a Case Study

## Steps

1. **Create a markdown file** in `content/case_studies/` with a kebab-case filename
   - Example: `content/case_studies/my-project.md` → `/case-studies/my-project.html`

2. **Add YAML frontmatter:**

```yaml
---
title: Project Name
industry: Healthcare
type: AI Platform
icon: ai
meta_description: SEO description under 160 chars.
challenge: One-paragraph problem statement the client faced.
solution: One-paragraph solution summary.
results: Metric 1,Metric 2,Metric 3,Metric 4
result_descriptions: Detailed result 1,Detailed result 2,Detailed result 3,Detailed result 4
technologies: Tech 1,Tech 2,Tech 3,Tech 4
description: Short description for cards and listings.
order: 10
---
```

### Frontmatter Fields

| Field | Required | Description |
|---|---|---|
| `title` | Yes | Project name |
| `industry` | Yes | Industry vertical (e.g., Healthcare, Agriculture, Finance, Legal) |
| `type` | Yes | Project type (e.g., AI Platform, Custom Drone, Web Application) |
| `icon` | Yes | SVG icon name from `static/` (e.g., `ai`, `drone`, `dashboard`, `layers`) |
| `meta_description` | Yes | SEO description, max 160 chars |
| `challenge` | Yes | Problem statement (single paragraph, used in template header) |
| `solution` | Yes | Solution summary (single paragraph, used in template header) |
| `results` | Yes | Comma-separated headline metrics (e.g., "53% Faster,84% Less Water") |
| `result_descriptions` | Yes | Comma-separated detailed explanations of each result metric |
| `technologies` | Yes | Comma-separated tech stack used |
| `description` | Yes | Short description for listing cards |
| `order` | No | Sort order for listings (lower = first, default 999) |
| `attribution` | No | Optional: "research" if IEEE/academic published |

3. **Write the markdown body** with sections like:
   - `## The Market Problem` or `## The Challenge`
   - `## The Solution`
   - `## The Results`
   - `## Technical Details` (optional)
   - Include `{{template:cta}}` or `{{template:cta-case-study}}` between sections

4. **Images**: Reference with `![Alt](../static/image-name.avif)` — place images in `static/`

## Auto-Linking Integration

After adding a case study, consider adding keyword mappings in `content_processor.py` → `case_study_links` dict so that mentions in blogs/conversations auto-link to this case study.

## Build & Preview

```bash
python generate.py
```

Output: `/case-studies/{slug}.html` and listed on `/case-studies.html` (9 per page, sorted by date).

## Templates Used

- Detail: `templates/case_study_detail.html`
- Listing: `templates/case_studies.html`
