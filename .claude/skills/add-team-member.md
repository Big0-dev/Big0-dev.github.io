---
description: Add a team member profile to the Big0.dev website. Use when adding a new person with their role, experience timeline, and credentials.
---

# Adding a Team Member

## Steps

1. **Create a markdown file** in `content/team/` with a kebab-case name
   - Example: `content/team/jane-doe.md` → `/team/jane-doe.html`

2. **Add YAML frontmatter:**

```yaml
---
title: "Full Name"
role: "Job Title"
photo: "team-photo.avif"
meta_description: "Short bio for SEO — 160 chars max."
linkedin: "https://www.linkedin.com/in/username/"
website: "https://personalsite.com"
timeline:
  - "Previous Role"
  - "Education"
  - "Achievement"
  - "Current Role"
badges:
  - text: "Credential 1"
    color: "green"
  - text: "Credential 2"
    color: "cyan"
  - text: "Credential 3"
    color: "amber"
experience:
  - company: "Company Name"
    role: "Job Title"
    period: "Start — Present"
    location: "City, Country"
    highlights:
      - "Key achievement or responsibility"
      - "Another highlight"
  - company: "Previous Company"
    role: "Previous Role"
    period: "Start — End"
    location: "City, Country"
    highlights:
      - "Achievement"
---
```

### Frontmatter Fields

| Field | Required | Description |
|---|---|---|
| `title` | Yes | Full name |
| `role` | Yes | Current job title |
| `photo` | Yes | Photo filename in `static/` (AVIF format) |
| `meta_description` | Yes | Short bio for SEO |
| `linkedin` | No | LinkedIn profile URL |
| `website` | No | Personal website URL |
| `timeline` | Yes | Array of career milestones (shown as visual timeline) |
| `badges` | No | Array of `{text, color}` credential badges |
| `experience` | Yes | Array of work experience entries with company, role, period, location, highlights |

### Badge Colors

Available: `green`, `cyan`, `amber`, `primary`

3. **Add team photo** to `static/` directory in AVIF format.

4. **Markdown body** (optional) — additional bio content rendered below the structured sections.

## Notes

- Team pages are excluded from navigation (`exclude_from_nav: true` in config)
- Team members are linked from the `about.html` template and other pages
- No listing page is generated — team members are accessed via direct links

## Build & Preview

```bash
python generate.py
```

Output: `/team/{slug}.html`

## Template Used

- Detail: `templates/team_detail.html`
