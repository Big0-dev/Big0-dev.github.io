---
description: Add a conversation/interview to the Big0.dev website. Use for dialogue-format content where two or more people discuss a topic related to a case study or service.
---

# Adding a Conversation

## Steps

1. **Create a markdown file** in `content/conversations/` with a kebab-case filename
   - Example: `content/conversations/my-topic.md` → `/conversations/my-topic.html`

2. **Add YAML frontmatter:**

```yaml
---
title: "Conversation Title"
subtitle: A conversation between [person A] and [person B] about [topic]
meta_description: SEO description under 160 chars.
category: Topic Category
intro: "Setting the scene — who is talking, where, and why."
date: 2026-03-24
tags: topic1, topic2, topic3
---
```

### Frontmatter Fields

| Field | Required | Description |
|---|---|---|
| `title` | Yes | Conversation title |
| `subtitle` | Yes | Descriptive subtitle explaining the participants |
| `meta_description` | Yes | SEO description |
| `category` | Yes | Topic category |
| `intro` | Yes | Scene-setting paragraph (rendered as intro block) |
| `date` | Yes | Date in `YYYY-MM-DD` format |
| `tags` | Yes | Comma-separated tags |

3. **Write the dialogue body:**
   - Use `## Section Title` to break conversation into thematic sections
   - Format dialogue as: `**Speaker Name:** Dialogue text.`
   - Use `---` horizontal rules between major topic shifts
   - Include natural back-and-forth exchanges
   - Weave in technical details and real project data

4. **Auto-linking** is active in conversations — service and case study keywords are automatically linked.

## Content Pattern (from existing conversations)

```markdown
## The Opening

**Person A:** Opening question or statement.

**Person B:** Response with context.

---

## The Core Topic

**Person A:** Deeper question.

**Person B:** Detailed answer with specifics.

**Person A:** Follow-up.
```

## Notes

- Conversations are excluded from navigation (`exclude_from_nav: true`)
- They are typically linked from case study pages or blog posts
- Auto-linking works for both service and case study keywords

## Build & Preview

```bash
python generate.py
```

Output: `/conversations/{slug}.html`

## Template Used

- Detail: `templates/conversation_detail.html`
