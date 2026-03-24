---
description: Add a new blog post to the Big0.dev website. Use when creating a blog article with proper frontmatter, SEO metadata, and content formatting.
---

# Adding a Blog Post

## Steps

1. **Create a markdown file** in `content/blogs/` with a kebab-case filename (this becomes the URL slug)
   - Example: `content/blogs/my-new-post.md` → `/blogs/my-new-post.html`

2. **Add YAML frontmatter** at the top of the file:

```yaml
---
title: Your Blog Post Title
category: AI Applications
date: March 24, 2026
image_url: hero-image-name.avif
meta_description: SEO description under 160 characters summarizing the post.
tags: tag1, tag2, tag3
---
```

### Frontmatter Fields

| Field | Required | Description |
|---|---|---|
| `title` | Yes | Article headline |
| `category` | Yes | Category label (e.g., "AI Applications", "Engineering", "Industry Insights") |
| `date` | Yes | Publication date in format `Month Day, Year` (e.g., `January 15, 2026`) |
| `image_url` | Yes | Filename of hero image in `static/` directory (AVIF format preferred) |
| `meta_description` | Yes | SEO description, max 160 chars |
| `tags` | Yes | Comma-separated tags for categorization and search |

3. **Write the markdown body** after the frontmatter:
   - Use `## Heading` for sections (H2)
   - Use `### Subheading` for subsections (H3)
   - Use bold, italic, lists as normal markdown
   - Images: `![Alt text](../static/image-name.avif)`
   - Internal links: `[Link text](/path/to/page.html)`

4. **Available template directives** (optional, placed on their own line):
   - `{{template:cta}}` — generic call-to-action block
   - `{{template:cta-service}}` — service-oriented CTA
   - `{{related-services:ai-powered-applications,custom-software-development}}` — related services grid

5. **FAQ sections** (optional): Use an `## FAQ` or `## Frequently Asked Questions` heading followed by `### Question?` / answer paragraphs. These auto-convert to interactive accordions with JSON-LD schema.

6. **Auto-linking**: Keywords matching services and case studies are automatically linked in blog content. No manual linking needed for terms like "machine learning", "custom software", "agricultural drone", etc.

## Build & Preview

```bash
python generate.py
```

The blog post will appear at `/blogs/{slug}.html` and in the paginated listing at `/blogs.html` (sorted by date, newest first, 9 per page).

## Hero Image

- Place the hero image in `static/` as AVIF format
- Reference just the filename in `image_url` (not the full path)
- Recommended: optimize images before adding (AVIF format, reasonable dimensions)

## Template Used

- Detail page: `templates/blog_post.html`
- Listing page: `templates/blogs.html`
