# Content Writing Guide

This guide documents how to write each type of markdown content file for the Big0 website. Use these templates and guidelines when creating or generating content.

## Quick Reference

| Content Type | Location | Template |
|--------------|----------|----------|
| Services | `content/services/*.md` | [Service Pages](#service-pages) |
| Industries | `content/industries/*.md` | [Industry Pages](#industry-pages) |
| Blogs | `content/blogs/*.md` | [Blog Posts](#blog-posts) |
| Case Studies | `content/case_studies/*.md` | [Case Studies](#case-studies) |
| News | `content/news/*.md` | [News Articles](#news-articles) |
| Location Pages | `content/services/locations/[country]/*.md` | [Location Pages](#location-specific-pages) |

---

## Service Pages

**Location:** `content/services/*.md`

### Frontmatter

```yaml
---
title: AI & Machine Learning Services
meta_description: "Enterprise AI & ML solutions: custom models, computer vision, NLP. 150-160 chars for SEO"
description: Brief description for cards and listings (1-2 sentences)
icon: ai  # Icon name: ai, cloud, code, chart-line, dollar-sign, etc.
features: Custom AI models, Machine learning, Computer vision, NLP  # Comma-separated
---
```

### Content Structure

```markdown
# Opening Statement (H1)

Powerful opening paragraph that captures the value proposition and key benefits. Include primary keyword naturally in first 100 words.

## Main Section Title

Detailed explanation of the service category with comprehensive overview.

### Subsection with Specific Services

**Service Component Name**
Detailed description of this specific component, its benefits, and use cases.

**Another Service Component**
Description focusing on business value and technical capabilities.

## Implementation Approach

Structured content about methodology, process, or approach.

## Key Benefits Section

- **Benefit 1**: Explanation with metrics if possible
- **Benefit 2**: Description of value delivered
- **Benefit 3**: Details on outcomes

{{template:cta-service}}

## Frequently Asked Questions

### What is the typical timeline?
Answer in paragraph format. Be specific and helpful.

### How much does it cost?
Detailed pricing explanation or factors that affect pricing.
```

### SEO Guidelines
- **Title**: 50-60 characters, include primary keyword
- **Meta description**: 150-160 characters, include CTA
- **Word count**: 800-1500 words minimum
- **Headers**: Use H2 for main sections, H3 for subsections
- **Keywords**: Include primary keyword 3-5 times naturally

---

## Industry Pages

**Location:** `content/industries/*.md`

### Frontmatter

```yaml
---
title: Finance
icon: dollar-sign
meta_description: Transform financial institutions with AI. Include key metrics and benefits.
description: Short description for industry cards
short_description: Extended description for listings (2-3 sentences)
challenge: Main challenge this industry faces (1-2 sentences)
solutions: Risk Management, Fraud Detection, Compliance  # Comma-separated
case_studies: Case Study 1, Case Study 2  # Related case studies
---
```

### Content Structure

```markdown
# Industry-Specific Headline | Targeted Solutions

Opening paragraph with industry statistics, challenges, and value proposition. Use real numbers when possible.

{{template:cta}}

## Why [Industry] Companies Choose Big0

{{industry-challenges:Challenge 1|Challenge 2|Challenge 3|Challenge 4}}

## Core Solutions Section

### Solution Category 1

- **Specific Implementation**: Details with metrics
- **Another Implementation**: Benefits and features
- **Key Feature**: Technical details

### Solution Category 2

Detailed explanation of solutions specific to this industry.

{{industry-solutions:Solution Name|Description,Another Solution|Its description}}

## Industry-Specific Benefits

Focus on ROI, compliance, efficiency gains specific to this industry.

## Success Metrics

- 45% reduction in costs
- 90% accuracy improvement
- 3x faster processing

{{template:cta}}
```

### SEO Guidelines
- Include industry-specific terminology
- Reference regulations and compliance requirements
- Use case study links when available
- Target industry + service combination keywords

---

## Blog Posts

**Location:** `content/blogs/*.md`

### Frontmatter

```yaml
---
title: The AI Revolution in 2024
category: AI & Machine Learning  # AI & Machine Learning, Software Development, Cloud, Fintech, Data Analytics
date: 2024-11-20
meta_description: SEO description for search engines (150-160 chars)
tags: ai, machine-learning, innovation, technology
image: ai-revolution.avif  # Optional featured image
---
```

### Content Structure

```markdown
Opening paragraph that hooks the reader and introduces the topic. Address a pain point or question immediately.

## Main Section

Content with insights, analysis, and valuable information. Be educational, not salesy.

### Subsection with Details

**Key Point 1**
Explanation and real-world examples.

**Key Point 2**
Supporting information with data when possible.

## Practical Applications

Real-world examples and use cases that readers can relate to.

## Key Takeaways

- Bullet point summary of main insights
- Actionable items readers can implement
- Clear next steps

## Conclusion

Summary and soft call to action mentioning Big0's relevant services.

{{template:cta}}
```

### Blog Categories
- `AI & Machine Learning`
- `Software Development`
- `Cloud`
- `Fintech`
- `Data Analytics`
- `Technology`
- `Company News`

### SEO Guidelines
- **Title**: 50-60 characters, compelling and keyword-rich
- **Word count**: 800-1500 words
- **Funnel stage**: TOFU (educational, informational)
- **Keywords**: Target "what is", "how to", "guide" queries
- **Internal links**: Link to relevant services and industries

---

## Case Studies

**Location:** `content/case_studies/*.md`

### Frontmatter

```yaml
---
title: Project Name Case Study
industry: Finance Technology
type: Digital Transformation  # Digital Transformation, AI Implementation, Cloud Migration, etc.
icon: chart-line
challenge: Brief problem statement (1-2 sentences)
solution: How the problem was solved (1-2 sentences)
results: 50% Cost Reduction, 3x Performance, 99.9% Uptime  # Comma-separated metrics
result_descriptions: Detailed explanation, For each result, With specific numbers
technologies: React, Python, AWS, Docker, Kubernetes  # Tech stack
description: Brief case study description for cards
order: 1  # Display order (lower = higher priority)
---
```

### Content Structure

```markdown
## The Business Challenge

Detailed explanation of the client's problem, industry context, and why existing solutions weren't working. Be specific about pain points.

## Our Innovative Solution

Comprehensive description of the approach, methodology, and implementation details.

Technical details about architecture, design decisions, and development process.

![System Architecture](../static/architecture-diagram.avif)
_Caption describing the image_

{{template:cta-case-study}}

## Measurable Results & Impact

Detailed results with specific metrics, ROI calculations, and business impact.

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Processing Time | 2 hours | 5 minutes | 96% faster |
| Error Rate | 5% | 0.1% | 98% reduction |

## Technical Implementation Details

- **Architecture**: Description of system design
- **Technology Stack**: Details on tools used
- **Integration**: How it connects with existing systems
- **Deployment**: Cloud/on-premise strategy

## Client Testimonial

> "Quote from client about the success and impact"
> — Client Name, Title, Company

## Long-term Benefits

Future-looking statement about scalability, maintenance, and ongoing value.
```

### SEO Guidelines
- Include specific metrics and numbers
- Use industry + solution keywords
- Link to related services
- Funnel stage: MOFU/BOFU (consideration/decision)

---

## News Articles

**Location:** `content/news/*.md`

### Frontmatter

```yaml
---
title: Company Announces Major Partnership
category: Company News  # Company News, Industry News, Product Updates
date: 2025-06-15
tags: partnership, growth, announcement
description: Brief summary for news listings
external_link: https://example.com  # Optional link to external coverage
order: 1  # Display priority
---
```

### Content Structure

```markdown
Lead paragraph with the main news - who, what, when, where, why. Most important information first.

## Key Announcement Details

Detailed information about the news item. Expand on the lead with specifics.

## What This Means

Impact and implications of the news for customers, industry, or company.

## Quote from Leadership

> "Statement from CEO or relevant executive about the announcement"
> — Name, Title

## About the Partnership/Event/News

Background information and context. History if relevant.

## Looking Forward

Future implications and next steps. What comes next.
```

### SEO Guidelines
- Use newsworthy, timely headlines
- Include dates and specific details
- Keep content factual and professional
- Update order field to prioritize recent news

---

## Location-Specific Pages

**Location:** `content/services/locations/[country]/*.md`

### Directory Structure
```
content/services/locations/
├── usa/
│   ├── ai-ml-services-usa.md
│   └── cities/
│       ├── new-york/
│       │   └── ai-ml-services-new-york.md
│       └── chicago/
│           └── ai-ml-services-chicago.md
└── pakistan/
    ├── ai-ml-services-pakistan.md
    └── cities/
        └── karachi/
            └── ai-ml-services-karachi.md
```

### Frontmatter

```yaml
---
title: AI & ML Services in USA | Enterprise Solutions
meta_description: Location-focused SEO description mentioning USA, cities, local benefits (150-160 chars)
canonical: /services/locations/usa/ai-ml-services-usa.html
location: USA
parent_service: ai-ml-services  # Links to parent service
is_location_page: true
noindex: false  # Allow indexing for local SEO
---
```

### Content Structure

```markdown
# AI & Machine Learning Services in USA

Location-specific opening focusing on the USA market needs, regulations, and benefits. Mention key cities.

## Local Market Expertise

USA-specific content including:
- Local regulations and compliance (SOC 2, HIPAA, etc.)
- Time zone advantages
- Local team or partnerships
- Industry presence in the region

## Why Choose Big0 for USA Projects

- Understanding of American business culture
- Compliance with US data regulations
- Support during US business hours
- Case studies from US clients

{{template:cta-location-usa}}

## Industries We Serve in USA

Focus on industries strong in this location (Finance in NYC, Tech in SF, etc.)

## Get Started

Local contact information and next steps.
```

### SEO Guidelines
- Include city and country names in title and content
- Mention local regulations and compliance
- Use location-specific keywords naturally
- Keep canonical pointing to the main service page (prevents duplicate content)

---

## Template Directives

Use these directives in markdown to insert dynamic content:

| Directive | Purpose | Example |
|-----------|---------|---------|
| `{{template:cta}}` | Generic call-to-action | End of blog posts |
| `{{template:cta-service}}` | Service-specific CTA | Service pages |
| `{{template:cta-location-usa}}` | Location CTA for USA | USA location pages |
| `{{template:cta-case-study}}` | Case study CTA | Case study pages |
| `{{related-services:slug1,slug2}}` | Link related services | Industry pages |
| `{{related-industries:slug1,slug2}}` | Link related industries | Service pages |

---

## Auto-Generated Content Notes

When using the blog generator (`--generate-blogs`), the AI will:

1. Generate content following this guide's structure
2. Add proper frontmatter automatically
3. Include `auto_generated: true` flag
4. Save to `content/blogs/` directory

**Always review auto-generated content** for:
- Factual accuracy
- Brand voice consistency
- Technical correctness
- Proper keyword usage
- Quality of examples

---

## SEO Best Practices Summary

1. **Meta titles**: 50-60 characters, keyword near beginning
2. **Meta descriptions**: 150-160 characters, include CTA
3. **Headers**: Logical H2/H3 hierarchy, include keywords
4. **Content length**: 800+ words for services/industries, 600+ for blogs
5. **Keywords**: Natural placement, avoid stuffing
6. **Internal links**: Link to related content
7. **Images**: Use AVIF format, include alt text
8. **FAQs**: Add for featured snippet opportunities
