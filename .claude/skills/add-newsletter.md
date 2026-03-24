---
description: Add a new newsletter issue to the Big0.dev website. Use when publishing a new newsletter with topics and commentary.
---

# Adding a Newsletter Issue

## Steps

1. **Create a markdown file** in `content/newsletters/` with the naming pattern `issue-NNN-slug.md`
   - Example: `content/newsletters/issue-008-new-topic.md` → `/newsletters/issue-008-new-topic.html`
   - Check existing files to determine the next issue number

2. **Add YAML frontmatter:**

```yaml
---
title: "Newsletter Title - The Hook"
issue_number: 8
date: March 24, 2026
meta_description: SEO description under 160 chars summarizing the issue.
subtitle: Perspectives on AI technology and what's next
topics: [topic1, topic2, topic3, topic4, topic5]
---
```

### Frontmatter Fields

| Field | Required | Description |
|---|---|---|
| `title` | Yes | Newsletter headline |
| `issue_number` | Yes | Sequential issue number (integer) |
| `date` | Yes | Publication date in `Month Day, Year` format |
| `meta_description` | Yes | SEO description, max 160 chars |
| `subtitle` | Yes | Subtitle shown below the title |
| `topics` | Yes | YAML array of topic tags |

3. **Write the markdown body:**
   - Open with a compelling hook paragraph
   - Use `---` horizontal rules to separate major sections
   - Structure with `## Section Title` and `### Subsection`
   - Mix analysis with practical insights
   - End with a forward-looking conclusion

4. **Content pattern** (based on existing newsletters):
   - Opening hook / editorial perspective
   - `## What's Moving` — trends and developments
   - Multiple `### Subtopic` sections
   - `## What This Means` — analysis
   - `## What's Next` — predictions
   - Closing thought

## Build & Preview

```bash
python generate.py
```

Output: `/newsletters/{slug}.html` and listed on `/newsletters.html` (12 per page, sorted by issue number descending).

Newsletters also appear in the blog listing page sidebar via `all_newsletters` context variable.

## Template Used

- Detail: `templates/newsletter_detail.html`
- Listing: `templates/newsletters.html`
