---
description: Add a news item to the Big0.dev website. Use for company announcements, speaking engagements, press mentions, and events.
---

# Adding a News Item

## Steps

1. **Create a markdown file** in `content/news/` with a descriptive kebab-case filename
   - Example: `content/news/conference-talk-2026.md` → `/news/conference-talk-2026.html`

2. **Add YAML frontmatter:**

```yaml
---
title: News Headline
category: Speaking Engagement
date: 2026-03-24
tags: speaking,conference,ai,topic
description: Short description for listings and SEO.
external_link:
order: 1
---
```

### Frontmatter Fields

| Field | Required | Description |
|---|---|---|
| `title` | Yes | News headline |
| `category` | Yes | Category (e.g., "Speaking Engagement", "Company News", "Press") |
| `date` | Yes | Date in `YYYY-MM-DD` format |
| `tags` | Yes | Comma-separated tags |
| `description` | Yes | Short description for cards |
| `external_link` | No | URL if linking to an external article |
| `order` | No | Sort priority (lower = first on homepage) |

3. **Write the markdown body:**
   - Lead with the key announcement
   - Use `## Section Heading` for structure
   - Include relevant details, quotes, acknowledgements
   - Keep it concise — news items are typically shorter than blog posts

## Build & Preview

```bash
python generate.py
```

Output: `/news/{slug}.html` and listed on `/news.html` (10 per page, sorted by date).

News items also appear on the homepage and in the RSS feed.

## Template Used

- Detail: `templates/news_detail.html`
- Listing: `templates/news.html` (also a static page)
