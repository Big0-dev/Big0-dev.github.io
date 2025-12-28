"""
Blog Generator - Auto-generates TOFU content based on keyword opportunities

Uses improved prompt engineering techniques:
- Role-based prompting ("Assume the role of...")
- Chain-of-thought ("Take a deep breath and work step-by-step")
- Structured output formatting

Features:
- Auto-downloads relevant images from Unsplash
- Converts images to AVIF format for optimal performance
"""

import json
import urllib.request
import urllib.error
import subprocess
import tempfile
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from ..config import Config, INDUSTRY_VERTICALS
from ..models import KeywordData, FunnelStage


@dataclass
class BlogPost:
    """Generated blog post"""
    title: str
    slug: str
    category: str
    meta_description: str
    content: str
    target_keywords: list[str]
    image_filename: Optional[str] = None
    funnel_stage: FunnelStage = FunnelStage.TOFU
    word_count: int = 0
    generated_at: datetime = field(default_factory=datetime.now)


class BlogGenerator:
    """
    Generates SEO-optimized blog posts for TOFU content.

    Uses AI to create educational content targeting:
    - "What is X" queries
    - "How to X" queries
    - Industry trend topics
    - Question-based keywords
    """

    def __init__(self, config: Config):
        self.config = config
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = config.ai_model
        self.static_dir = config.content_dir.parent / "static"

    def _download_image(self, search_query: str, slug: str) -> Optional[str]:
        """Download a relevant image and convert to AVIF"""
        import time

        # Clean query for URL
        clean_query = search_query.replace("'", "").replace('"', "").replace("&", "")
        query = "+".join(clean_query.split()[:3])

        print(f"      Downloading image for: {query}...")

        # Try multiple image sources
        image_sources = [
            # Picsum (Lorem Picsum) - reliable, random high-quality photos
            f"https://picsum.photos/1200/630",
            # Placeholder with seed for variety
            f"https://picsum.photos/seed/{slug[:20]}/1200/630",
        ]

        for url in image_sources:
            try:
                req = urllib.request.Request(
                    url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                    }
                )

                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                    with urllib.request.urlopen(req, timeout=30) as response:
                        tmp_file.write(response.read())
                    tmp_path = tmp_file.name

                # Convert to AVIF
                output_filename = f"{slug}.avif"
                output_path = self.static_dir / output_filename

                result = subprocess.run(
                    ['avifenc', '--min', '20', '--max', '40', tmp_path, str(output_path)],
                    capture_output=True,
                    timeout=60
                )

                # Clean up temp file
                os.unlink(tmp_path)

                if result.returncode == 0 and output_path.exists():
                    print(f"      Image saved: {output_filename}")
                    return output_filename

                time.sleep(0.5)  # Small delay between attempts

            except Exception as e:
                continue

        print(f"      Image download failed - using fallback")
        return None

    def _get_image_search_terms(self, title: str, category: str, keywords: list[str]) -> str:
        """Generate search terms for finding a relevant image"""
        # Map categories to image-friendly terms
        category_terms = {
            "AI & ML": "artificial intelligence robot",
            "AI & Machine Learning": "artificial intelligence technology",
            "Cloud": "cloud computing server",
            "Software Development": "software coding developer",
            "Fintech": "fintech banking digital",
            "Data Analytics": "data analytics dashboard",
            "Technology": "technology digital innovation",
        }

        base_term = category_terms.get(category, "business technology")

        # Add first keyword if relevant
        if keywords:
            first_kw = keywords[0].split()[0]  # First word of first keyword
            if len(first_kw) > 3:
                base_term = f"{first_kw} {base_term}"

        return base_term

    def _call_ai(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """Make AI API call with improved prompts"""
        if not self.config.openrouter_api_key:
            return None

        headers = {
            "Authorization": f"Bearer {self.config.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.config.site_domain,
        }

        # Add chain-of-thought prefix to system prompt
        enhanced_system = f"""Take a deep breath and work on this problem step-by-step.

{system_prompt}

Before writing, think through:
1. Who is the target audience?
2. What problem does this solve?
3. What unique value can Big0 provide?
4. How can this lead readers toward our services?

Now proceed with the task."""

        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": enhanced_system},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }).encode()

        try:
            req = urllib.request.Request(self.api_url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as response:
                data = json.loads(response.read().decode())
            return data['choices'][0]['message']['content']
        except Exception as e:
            print(f"  [BlogGen] AI error: {e}")
            return None

    def generate_blog_ideas(self, keywords: list[KeywordData], count: int = 5) -> list[dict]:
        """Generate blog post ideas based on keyword opportunities"""

        # Filter for TOFU keywords
        tofu_keywords = [
            kw for kw in keywords
            if any(q in kw.keyword.lower() for q in ['what', 'how', 'why', 'guide', 'tutorial', 'best'])
            or kw.impressions > 50
        ][:20]

        keyword_list = "\n".join([f"- {kw.keyword} (impressions: {kw.impressions})" for kw in tofu_keywords])

        system_prompt = """Assume the role of an expert B2B content strategist specializing in technology and AI services.

You work for Big0, a company offering:
- AI & Machine Learning services
- Custom software development
- Cloud services (AWS, Azure, GCP)
- Fintech development
- Data analytics

Your goal is to create blog topic ideas that:
1. Target informational search queries (TOFU - Top of Funnel)
2. Establish thought leadership
3. Naturally lead readers toward Big0's services
4. Have high search potential"""

        user_prompt = f"""Based on these keyword opportunities, generate {count} blog post ideas.

Keywords with search potential:
{keyword_list}

For each blog idea, provide in this exact JSON format:
[
  {{
    "title": "Blog post title (50-60 chars)",
    "slug": "url-friendly-slug",
    "category": "AI & ML|Software Development|Cloud|Fintech|Data Analytics",
    "target_keyword": "primary keyword to target",
    "secondary_keywords": ["keyword2", "keyword3"],
    "meta_description": "150-160 char description",
    "outline": ["Section 1", "Section 2", "Section 3"],
    "why_valuable": "Why this topic matters for our audience"
  }}
]

Return ONLY the JSON array, no other text."""

        response = self._call_ai(system_prompt, user_prompt, max_tokens=1500)

        if response:
            try:
                # Clean response (remove markdown code blocks if present)
                clean = response.strip()
                if clean.startswith("```"):
                    clean = clean.split("```")[1]
                    if clean.startswith("json"):
                        clean = clean[4:]
                return json.loads(clean)
            except json.JSONDecodeError:
                print(f"  [BlogGen] Failed to parse ideas JSON")
                return []
        return []

    def generate_blog_post(
        self,
        title: str,
        target_keyword: str,
        secondary_keywords: list[str],
        outline: list[str],
        category: str
    ) -> Optional[BlogPost]:
        """Generate a complete blog post"""

        system_prompt = """Assume the role of an expert technical writer and SEO specialist for Big0, a leading AI and software development company.

Take a deep breath and plan your content before writing.

Before writing, consider:
1. Who is the target audience for this topic?
2. What pain point or question does this address?
3. What unique insights can Big0 provide?
4. How can this naturally lead readers toward our services?

CONTENT STRUCTURE (follow this exactly):
1. Opening paragraph - Hook the reader with a pain point or compelling question
2. Main sections (H2) - Educational content with real value
3. Subsections (H3) - Specific details and examples
4. Key Takeaways - Bullet point summary
5. Conclusion - Soft CTA mentioning Big0's services

WRITING GUIDELINES:
- Be genuinely helpful and educational (not salesy)
- Demonstrate deep expertise in the topic
- Include practical examples and actionable advice
- Use proper markdown: H2 (##) for main sections, H3 (###) for subsections
- Short paragraphs (2-3 sentences max)
- Use bullet points for lists
- 800-1200 words total
- Include the primary keyword in the first paragraph
- Weave keywords naturally without stuffing

SEO REQUIREMENTS:
- Do NOT include the title as H1 (it's added separately)
- Do NOT include frontmatter (it's added separately)
- Do NOT include {{template:cta}} - it will be added automatically
- Do NOT include any CTA placeholders in your content"""

        user_prompt = f"""Write a complete blog post with these specifications:

Title: {title}
Primary Keyword: {target_keyword}
Secondary Keywords: {', '.join(secondary_keywords)}
Category: {category}

Suggested Outline:
{chr(10).join(f'- {section}' for section in outline)}

Requirements:
1. Start with a hook that addresses a pain point
2. Include the primary keyword in the first paragraph
3. Use H2 (##) for main sections, H3 (###) for subsections
4. Add a "Key Takeaways" section near the end
5. End with a soft CTA mentioning Big0's relevant services
6. Do NOT include the title as H1 (it's added separately)
7. Do NOT include frontmatter (it's added separately)

Write the blog post content in markdown:"""

        response = self._call_ai(system_prompt, user_prompt, max_tokens=2500)

        if not response:
            return None

        # Generate meta description
        meta_desc = self._generate_meta_description(title, target_keyword)

        # Create slug
        slug = title.lower()
        for char in ['?', '!', '.', ',', ':', ';', "'", '"', '(', ')', '&', '+', '/', '\\', '@', '#', '$', '%', '^', '*']:
            slug = slug.replace(char, '')
        slug = '-'.join(slug.split())[:60]

        # Download and convert image
        search_terms = self._get_image_search_terms(title, category, [target_keyword] + secondary_keywords)
        image_filename = self._download_image(search_terms, slug)

        return BlogPost(
            title=title,
            slug=slug,
            category=category,
            meta_description=meta_desc or f"Learn about {target_keyword}. Expert insights from Big0's team on {category}.",
            content=response.strip(),
            target_keywords=[target_keyword] + secondary_keywords,
            image_filename=image_filename,
            word_count=len(response.split()),
        )

    def _generate_meta_description(self, title: str, keyword: str) -> Optional[str]:
        """Generate SEO meta description"""
        system_prompt = """Assume the role of an SEO expert. Generate a meta description that:
- Is exactly 150-160 characters
- Includes the target keyword naturally
- Has a clear value proposition
- Includes a soft call-to-action
- Creates curiosity to click

Respond with ONLY the meta description, nothing else."""

        user_prompt = f"Title: {title}\nKeyword: {keyword}\n\nGenerate the meta description:"

        return self._call_ai(system_prompt, user_prompt, max_tokens=100)

    def save_blog_post(self, post: BlogPost, output_dir: Path = None) -> Path:
        """Save blog post as markdown file"""
        if output_dir is None:
            output_dir = self.config.content_dir / "blogs"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Use downloaded image or fallback to category default
        if post.image_filename:
            image = post.image_filename
        else:
            category_images = {
                "AI & ML": "ai.avif",
                "AI & Machine Learning": "ai.avif",
                "Cloud": "cloud.avif",
                "Software Development": "business.avif",
                "Fintech": "fintech.avif",
                "Data Analytics": "data.avif",
                "Technology": "tech.avif",
            }
            image = category_images.get(post.category, "business.avif")

        # Create frontmatter
        frontmatter = {
            "title": post.title,
            "category": post.category,
            "date": post.generated_at.strftime("%Y-%m-%d"),
            "image_url": image,
            "meta_description": post.meta_description,
            "tags": ", ".join(post.target_keywords[:5]),
            "keywords": post.target_keywords,
            "funnel_stage": "tofu",
            "auto_generated": True,
        }

        # Clean content - remove any CTA directives the AI might have added
        import re
        clean_content = re.sub(r'\{\{template:cta\}\}\s*', '', post.content).strip()

        # Build file content
        import yaml
        frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)

        file_content = f"""---
{frontmatter_yaml}---

# {post.title}

{clean_content}

{{{{template:cta}}}}
"""

        file_path = output_dir / f"{post.slug}.md"
        file_path.write_text(file_content, encoding='utf-8')

        return file_path

    def generate_batch(
        self,
        keywords: list[KeywordData],
        count: int = 3,
        save: bool = True
    ) -> list[BlogPost]:
        """Generate multiple blog posts based on keyword opportunities"""

        print(f"\n  [BlogGen] Generating {count} blog post ideas...")

        # Generate ideas
        ideas = self.generate_blog_ideas(keywords, count=count)

        if not ideas:
            print("  [BlogGen] No ideas generated")
            return []

        print(f"  [BlogGen] Got {len(ideas)} ideas, generating posts...")

        posts = []
        for i, idea in enumerate(ideas[:count]):
            print(f"    Writing {i+1}/{count}: {idea.get('title', 'Unknown')[:40]}...")

            post = self.generate_blog_post(
                title=idea.get('title', ''),
                target_keyword=idea.get('target_keyword', ''),
                secondary_keywords=idea.get('secondary_keywords', []),
                outline=idea.get('outline', []),
                category=idea.get('category', 'Technology'),
            )

            if post:
                posts.append(post)
                if save:
                    file_path = self.save_blog_post(post)
                    print(f"      Saved: {file_path.name}")

        print(f"  [BlogGen] Generated {len(posts)} blog posts")
        return posts


def generate_blogs_from_keywords(config: Config, count: int = 3) -> list[BlogPost]:
    """Helper function to generate blogs from current keyword opportunities"""
    from ..collectors.gsc import GoogleSearchConsoleCollector

    # Get keyword data from GSC
    gsc = GoogleSearchConsoleCollector(config)
    if not gsc.initialize():
        print("  [BlogGen] Could not connect to GSC")
        return []

    queries = gsc.get_top_queries(limit=100)
    keywords = [
        KeywordData(
            keyword=q.query,
            impressions=q.impressions,
            clicks=q.clicks,
            ctr=q.ctr,
            position=q.position,
        )
        for q in queries
    ]

    generator = BlogGenerator(config)
    return generator.generate_batch(keywords, count=count, save=True)
