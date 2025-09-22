# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Instructions

- **ALWAYS use uv** for Python package management and running Python scripts
- **NEVER use pip** to install libraries unless explicitly specified by the user
- Use `uv add` for adding dependencies
- Use `uv run` for running Python scripts
- This applies to all Python-related tasks

## Project Setup with uv

This project uses **uv** as the Python package manager. Do not use pip or pip3.

### Install dependencies
```bash
uv pip install -r requirements.txt
# or
uv sync
```

### Add new dependencies
```bash
uv add package-name
```

## Build and Development Commands

### Primary Build Command
```bash
# Always use uv to run the generator
uv run python generate.py
```
This generates the entire static website in the `build/` directory.

### Local Development Server
```bash
cd build && python3 -m http.server 8000
# View at http://localhost:8000
```

### Deployment
The site is deployed to **Cloudflare Pages**. Push to main branch triggers automatic deployment to https://big0.dev

#### Cloudflare Pages Configuration
- **Platform**: Cloudflare Pages (not GitHub Pages)
- **Build command**: Not needed (we build locally and push the build folder)
- **Build output directory**: `/build`
- **Production branch**: `main`
- **Custom domain**: big0.dev
- **Auto-deploy**: Enabled for pushes to main branch
- **GitHub repo name**: Big0-dev.github.io (kept for compatibility, but hosted on Cloudflare)

**Important**: The repository is still named `Big0-dev.github.io` on GitHub for historical reasons, but the actual hosting is done through Cloudflare Pages, not GitHub Pages

## How This Project Works - Complete Workflow

### 1. **Site Generation Process**

When you run `uv run python generate.py`, the following happens in sequence:

1. **Initialization** (`SiteGenerator.__init__`):
   - Loads `site_config.yaml` configuration
   - Sets up Jinja2 template environment with custom functions
   - Configures output directories

2. **Clean & Prepare** (`_clean_output`):
   - Removes existing `build/` directory
   - Creates fresh directory structure

3. **Asset Copying** (`_copy_assets`):
   - Copies static files (CSS, JS, fonts) to `build/static/`
   - Copies gallery images to `build/content/gallery/`
   - Copies favicon files to build root
   - Excludes SVG files (they're injected inline for performance)

4. **Page Generation**:
   - **Static Pages** (`_generate_static_pages`): Generates pages like index, about, contact from templates
   - **Gallery Pages** (`_generate_gallery_pages`): Creates paginated gallery with 6 images per page
   - **Content Pages** (`_generate_content_pages`): Processes markdown files into HTML pages

5. **Location SEO Pages** (`_generate_location_pages`):
   - Auto-generates location-specific versions of services
   - Creates country pages (USA, Pakistan)
   - Creates city pages (New York, Chicago, Karachi, etc.)
   - Sets proper canonical tags to avoid duplicate content penalties

6. **Sitemaps & Feeds** (`_generate_sitemaps`):
   - `sitemap.xml` - All pages including location variants
   - `sitemap-images.xml` - Image sitemap for SEO
   - `rss.xml` - RSS feed for blogs and news

7. **Search Index** (`_generate_search_index`):
   - Creates `search-index.json` for client-side search using MiniSearch

8. **Optimization** (`_optimize_output`):
   - Currently disabled (line 79) to preserve cookie consent scripts
   - When enabled: Minifies HTML, CSS, and JavaScript

### 2. **Content Processing Pipeline**

#### Markdown to HTML Transformation (`_load_markdown_content`):

1. **Frontmatter Extraction**:
   - Parses YAML frontmatter from markdown files
   - Extracts metadata (title, description, date, tags, etc.)

2. **Template Directive Processing** (`_process_template_directives`):
   - Replaces `{{template:cta-service}}` with HTML CTAs
   - Handles `{{related-services:...}}` and `{{related-industries:...}}`
   - Processes location-specific CTAs

3. **Markdown Conversion**:
   - Uses Python-Markdown with extensions (extra, codehilite, toc)
   - Converts markdown to HTML

4. **FAQ Section Processing** (`_process_faq_sections`):
   - Detects "Frequently Asked Questions" headers
   - Transforms Q&A format into interactive FAQ components
   - Adds structured data (schema.org) for SEO

5. **Auto-linking** (`_add_automatic_interlinking`):
   - Scans content for service/industry keywords
   - Adds contextual links (200+ service terms, 70+ industry terms)
   - Avoids self-linking and respects existing links

### 3. **Template System Architecture**

#### Base Template (`base.html`):
- Master template with all pages inherit from
- Includes:
  - Google Analytics 4 (consent-aware)
  - Microsoft Clarity (ID: t1zp8ama5q)
  - Cookie consent system
  - Search functionality
  - Navigation structure
  - Critical CSS inlining
  - Favicon and meta tags

#### Template Hierarchy:
```
base.html
├── index.html (homepage)
├── service_detail.html (service pages)
├── industry_detail.html (industry pages)
├── blog_post.html (blog articles)
├── case_study_detail.html (case studies)
├── news_detail.html (news articles)
└── [static pages] (about, contact, etc.)
```

#### Context Variables:
- `static`: Path to static assets
- `domain`: Site domain (https://big0.dev)
- `path_prefix`: Relative path prefix based on page depth
- Navigation URLs dynamically adjusted for page depth

### 4. **Location-Based SEO Strategy**

#### How It Works:
1. **Generic Pages** (Canonical):
   - URL: `/services/ai-integration.html`
   - Canonical: Self-referencing
   - Purpose: Global/generic searches

2. **Location Pages**:
   - URL: `/services/locations/usa/ai-integration-usa.html`
   - Canonical: Points to generic page
   - Purpose: Location-specific searches

3. **City Pages**:
   - URL: `/services/locations/usa/cities/new-york/ai-integration-new-york.html`
   - Canonical: Points to generic page
   - Purpose: City-specific searches

#### Dynamic Location Discovery:
- System automatically discovers locations from `content/services/locations/` structure
- No hardcoding needed - just create directories

### 5. **CSS Architecture**

#### Design System (`static/design-system.css`):
- CSS custom properties (variables)
- Color schemes, spacing, typography
- Responsive breakpoints

#### Component Styles (`static/components.css`):
- Reusable UI components
- Cards, buttons, grids, forms
- Navigation components

#### Page-Specific Styles:
- `home.css` - Homepage specific
- `detail-pages.css` - Content pages
- `contact-form-bant.css` - Contact form
- `cookie-consent.css` - Cookie banner

### 6. **JavaScript Components**

#### Search System (`search.js` + `minisearch@7.1.2.min.js`):
- Client-side full-text search
- Indexes all content on page load
- Instant search results

#### Cookie Consent (`cookie-consent.js`):
- GDPR compliance
- Controls GA4 and Clarity tracking
- Stores consent in localStorage

### 7. **Performance Optimizations**

1. **Critical CSS Inlining**: Essential styles inline in `<head>`
2. **Lazy CSS Loading**: Non-critical CSS loaded asynchronously
3. **Font Preloading**: Exo2 font preloaded
4. **Image Optimization**: AVIF format with responsive variants
5. **SVG Injection**: SVGs injected inline (cached in memory)
6. **Minification**: HTML/CSS/JS minification (when enabled)

### 8. **Content Structure**

#### Service Pages (`content/services/`):
```yaml
---
title: Service Name
meta_description: SEO description (150-160 chars)
description: Brief description
icon: service-icon
features: Feature 1, Feature 2, Feature 3
---
# Markdown content here
```

#### Blog Posts (`content/blogs/`):
```yaml
---
title: Blog Title
category: Technology
date: 2024-01-15
meta_description: SEO description
tags: ai, technology, innovation
---
# Blog content
```

### 9. **Key Implementation Details**

1. **Path Management**:
   - `_get_base_context(depth)` calculates relative paths
   - Ensures assets load correctly at any directory depth

2. **Template Caching**:
   - Templates cached in memory during generation
   - SVG content cached with LRU cache

3. **Date Parsing**:
   - Flexible date format support
   - Cached with `@lru_cache` decorator

4. **Batch Processing**:
   - Files processed in sorted order for consistency
   - Pagination for blogs, galleries, case studies

5. **Error Handling**:
   - Individual page errors don't stop generation
   - Detailed logging for debugging

## Adding New Features

### New Content Type
1. Add configuration to `site_config.yaml`:
```yaml
content_types:
  new_type:
    content_dir: ./content/new_type
    template: new_type_detail.html
    listing_template: new_type_list.html
    output_dir: new-type
```

2. Create template files in `templates/`
3. Create content directory and add markdown files

### New Location
1. Create directory: `content/services/locations/[country]/`
2. For cities: `content/services/locations/[country]/cities/[city]/`
3. Add markdown files - location pages auto-generate

### New Template Directive
Edit `_process_template_directives()` in generate.py to add new directives like `{{template:new-directive}}`

## Debugging Tips

1. **Check Logs**: Generator outputs detailed logs during build
2. **Path Issues**: Verify `path_prefix` calculation for nested pages
3. **Template Errors**: Jinja2 provides detailed error messages
4. **Missing Content**: Check frontmatter format and file extensions
5. **Auto-linking**: Test with `_add_automatic_interlinking()` debug output

## Important Files Reference

- `generate.py`: Main generator (2100+ lines)
- `site_config.yaml`: Site configuration
- `templates/base.html`: Master template
- `static/design-system.css`: Design tokens
- `static/search.js`: Search implementation
- `static/cookie-consent.js`: GDPR compliance

## Markdown Writing Guide for Each Content Type

### 1. Service Pages (`content/services/*.md`)

#### Standard Service Page
```markdown
---
title: AI & Machine Learning Services
meta_description: "Enterprise AI & ML solutions: custom models, computer vision, NLP. 150-160 chars for SEO"
description: Brief description for cards and listings (1-2 sentences)
icon: ai  # Icon name from available set
features: Custom AI models, Machine learning, Computer vision, NLP  # Comma-separated list
---

# Opening Statement (H1)

Powerful opening paragraph that captures the value proposition and key benefits.

## Main Section Title

Detailed explanation of the service category with comprehensive overview.

### Subsection with Specific Services

**Service Component Name**
Detailed description of this specific component, its benefits, and use cases.

**Another Service Component**
Description focusing on business value and technical capabilities.

### Implementation Approach

Structured content about methodology, process, or approach.

## Key Benefits Section

- **Benefit 1**: Explanation
- **Benefit 2**: Description
- **Benefit 3**: Details

{{template:cta-service}}  # Add CTA template at strategic points

## FAQ Section (if included)

### Frequently Asked Questions

#### What is the typical timeline?
Answer in paragraph format.

#### How much does it cost?
Detailed pricing explanation.
```

#### Location-Specific Service Page (`content/services/locations/[country]/*.md`)
```markdown
---
title: Service Name in USA | Location-Specific Keywords
meta_description: Location-focused SEO description mentioning USA, cities, local benefits
canonical: /services/locations/usa/service-usa.html  # Self-canonical for location pages
location: USA
parent_service: ai-ml-services  # Links to parent service
is_location_page: true
noindex: false  # Allow indexing for local SEO
---

# Service Name Services in USA

Location-specific opening focusing on USA market needs and benefits.

## Local Market Expertise

USA-specific content, regulations, market conditions, and benefits.

{{template:cta-location-usa}}  # Use location-specific CTA
```

### 2. Industry Pages (`content/industries/*.md`)

```markdown
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

# Industry-Specific Headline | Targeted Solutions

Opening paragraph with industry statistics, challenges, and value proposition.

{{template:cta}}  # Early CTA for engagement

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

{{template:cta}}  # End with strong CTA
```

### 3. Blog Posts (`content/blogs/*.md`)

#### Modern Format (with frontmatter)
```markdown
---
title: The AI Revolution in 2024
category: AI & Machine Learning
date: 2024-11-20
meta_description: SEO description for search engines
tags: ai, machine-learning, innovation, technology
image: ai-revolution.avif  # Featured image
---

Opening paragraph that hooks the reader and introduces the topic.

## Main Section

Content with insights, analysis, and valuable information.

### Subsection with Details

**Key Point 1**
Explanation and examples.

**Key Point 2**
Supporting information.

## Practical Applications

Real-world examples and use cases.

## Conclusion

Summary and call to action.
```

#### Legacy Format (without frontmatter)
```
Blog Post Title Here
Category Name
November 20, 2024
featured-image.avif
Meta description for SEO (150-160 characters)

Blog content starts here...
```

### 4. Case Studies (`content/case_studies/*.md`)

```markdown
---
title: Project Name Case Study
industry: Finance Technology
type: Digital Transformation
icon: chart-line
challenge: Brief problem statement (1-2 sentences)
solution: How the problem was solved (1-2 sentences)
results: 50% Cost Reduction,3x Performance,99.9% Uptime  # Key metrics
result_descriptions: Detailed explanation,For each result,With specific numbers
technologies: React, Python, AWS, Docker, Kubernetes  # Tech stack
description: Brief case study description for cards
order: 1  # Display order
---

## The Business Challenge

Detailed explanation of the client's problem, industry context, and why existing solutions weren't working.

## Our Innovative Solution

Comprehensive description of the approach, methodology, and implementation details.

Technical details about architecture, design decisions, and development process.

![System Architecture](../static/architecture-diagram.avif)
_Caption describing the image_

{{template:cta-case-study}}

## Measurable Results & Impact

Detailed results with specific metrics, ROI calculations, and business impact.

Performance improvements, cost savings, efficiency gains with real numbers.

## Technical Implementation Details

- **Architecture**: Description
- **Technology Stack**: Details
- **Integration**: Approach
- **Deployment**: Strategy

## Client Testimonial (if available)

> "Quote from client about the success"
> — Client Name, Title, Company

## Long-term Benefits

Future-looking statement about scalability, maintenance, and ongoing value.
```

### 5. News Articles (`content/news/*.md`)

```markdown
---
title: Company Announces Major Partnership
category: Company News
date: 2025-06-15
tags: partnership, growth, announcement
description: Brief summary for news listings
external_link: https://example.com  # Optional external link
order: 1  # Display priority
---

Lead paragraph with the main news - who, what, when, where, why.

## Key Announcement Details

Detailed information about the news item.

## What This Means

Impact and implications of the news.

## Quote from Leadership

Statement from CEO or relevant executive.

## About the Partnership/Event/News

Background information and context.

## Looking Forward

Future implications and next steps.
```

### 6. Gallery Metadata (`content/gallery/metadata.json`)

```json
{
  "image-name.avif": {
    "title": "Event Title",
    "date": "2024-03-15",
    "category": "Team Event",
    "description": "Description of the image",
    "tags": ["team", "event", "celebration"]
  }
}
```

## Content Writing Best Practices

### SEO Optimization
1. **Meta Descriptions**: Keep between 150-160 characters
2. **Title Tags**: Include primary keyword early
3. **Headers**: Use H2 for main sections, H3 for subsections
4. **Keywords**: Natural placement without stuffing

### Template Directives
- `{{template:cta}}` - Generic CTA
- `{{template:cta-service}}` - Service-specific CTA
- `{{template:cta-location-usa}}` - Location CTAs
- `{{related-services:slug1,slug2}}` - Link related services
- `{{related-industries:slug1,slug2}}` - Link related industries

### Auto-linking
- Service mentions on industry pages auto-link
- Industry mentions on service pages auto-link
- Works on blogs, case studies, and news pages
- System recognizes 200+ service terms and 70+ industry terms

### FAQ Formatting
When including FAQs, use this structure:
```markdown
## Frequently Asked Questions

Optional intro paragraph about FAQs.

### Question 1 here?
Answer in paragraph format.

### Question 2 here?
Another answer.
```
The generator automatically converts this to interactive FAQ components with schema.org markup.

### Images
- Use AVIF format for best performance
- Store in `static/` directory
- Reference with relative paths: `../static/image.avif`
- Always include alt text in markdown: `![Alt text](path)`

### Location Pages
- Auto-generated from base service pages
- Can override with custom content in `locations/[country]/`
- Use location-specific keywords and content
- Include local regulations, market conditions, testimonials