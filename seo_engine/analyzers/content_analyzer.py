"""
Content Analyzer - Scans existing content and extracts metadata
"""

import re
import yaml
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from ..config import Config, FUNNEL_STAGES
from ..models import PageData, ContentType, FunnelStage


@dataclass
class ContentFile:
    """Parsed content file"""
    file_path: Path
    url: str
    title: str
    meta_description: str = ""
    content_type: ContentType = ContentType.STATIC
    funnel_stage: FunnelStage = FunnelStage.TOFU
    frontmatter: dict = field(default_factory=dict)
    body_content: str = ""
    word_count: int = 0
    has_cta: bool = False
    has_faq: bool = False
    internal_links: list[str] = field(default_factory=list)
    target_keywords: list[str] = field(default_factory=list)


class ContentAnalyzer:
    """
    Analyzes existing content files to extract metadata and identify opportunities.
    """

    def __init__(self, config: Config):
        self.config = config
        self.content_dir = config.content_dir

    def scan_all_content(self) -> list[ContentFile]:
        """Scan all content files in the content directory"""
        content_files = []

        # Scan each content type
        content_mappings = [
            ("services", ContentType.SERVICE),
            ("industries", ContentType.INDUSTRY),
            ("blogs", ContentType.BLOG),
            ("case_studies", ContentType.CASE_STUDY),
            ("news", ContentType.NEWS),
        ]

        for subdir, content_type in content_mappings:
            dir_path = self.content_dir / subdir
            if dir_path.exists():
                for md_file in dir_path.rglob("*.md"):
                    parsed = self._parse_markdown_file(md_file, content_type)
                    if parsed:
                        content_files.append(parsed)

        print(f"  [Content] Scanned {len(content_files)} content files")
        return content_files

    def _parse_markdown_file(self, file_path: Path, content_type: ContentType) -> Optional[ContentFile]:
        """Parse a markdown file and extract metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse frontmatter
            frontmatter = {}
            body = content

            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        body = parts[2]
                    except:
                        pass

            # Determine URL from file path
            url = self._file_path_to_url(file_path, content_type)

            # Extract title
            title = frontmatter.get('title', '')
            if not title:
                # Try to find H1 in body
                h1_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
                if h1_match:
                    title = h1_match.group(1)

            # Determine funnel stage
            funnel_stage = self._determine_funnel_stage(file_path, content_type, frontmatter, body)

            # Extract keywords from frontmatter
            target_keywords = []
            if 'keywords' in frontmatter:
                keywords = frontmatter['keywords']
                if isinstance(keywords, str):
                    target_keywords = [k.strip() for k in keywords.split(',')]
                elif isinstance(keywords, list):
                    target_keywords = keywords

            # Check for CTAs and FAQs
            has_cta = '{{template:cta' in body or 'contact' in body.lower()
            has_faq = 'frequently asked' in body.lower() or '## faq' in body.lower()

            # Extract internal links
            internal_links = re.findall(r'\[([^\]]+)\]\((/[^)]+)\)', body)

            # Word count
            word_count = len(body.split())

            return ContentFile(
                file_path=file_path,
                url=url,
                title=title,
                meta_description=frontmatter.get('meta_description', frontmatter.get('description', '')),
                content_type=content_type,
                funnel_stage=funnel_stage,
                frontmatter=frontmatter,
                body_content=body,
                word_count=word_count,
                has_cta=has_cta,
                has_faq=has_faq,
                internal_links=[link[1] for link in internal_links],
                target_keywords=target_keywords,
            )

        except Exception as e:
            print(f"  [Content] Error parsing {file_path}: {e}")
            return None

    def _file_path_to_url(self, file_path: Path, content_type: ContentType) -> str:
        """Convert file path to expected URL"""
        relative = file_path.relative_to(self.content_dir)
        parts = list(relative.parts)

        # Handle different content type URL patterns
        if content_type == ContentType.SERVICE:
            if 'locations' in parts:
                # Location-specific service page
                return f"{self.config.site_domain}/{'/'.join(parts[:-1])}/{file_path.stem}.html"
            return f"{self.config.site_domain}/services/{file_path.stem}.html"

        elif content_type == ContentType.INDUSTRY:
            return f"{self.config.site_domain}/industries/{file_path.stem}.html"

        elif content_type == ContentType.BLOG:
            return f"{self.config.site_domain}/blogs/{file_path.stem}.html"

        elif content_type == ContentType.CASE_STUDY:
            return f"{self.config.site_domain}/case-studies/{file_path.stem}.html"

        elif content_type == ContentType.NEWS:
            return f"{self.config.site_domain}/news/{file_path.stem}.html"

        return f"{self.config.site_domain}/{file_path.stem}.html"

    def _determine_funnel_stage(
        self,
        file_path: Path,
        content_type: ContentType,
        frontmatter: dict,
        body: str
    ) -> FunnelStage:
        """Determine the funnel stage for a piece of content"""

        # Explicit funnel stage in frontmatter
        if 'funnel_stage' in frontmatter:
            stage = frontmatter['funnel_stage'].lower()
            if stage in ['tofu', 'top', 'awareness']:
                return FunnelStage.TOFU
            elif stage in ['mofu', 'middle', 'consideration']:
                return FunnelStage.MOFU
            elif stage in ['bofu', 'bottom', 'decision']:
                return FunnelStage.BOFU

        # Content type based defaults
        if content_type == ContentType.BLOG:
            return FunnelStage.TOFU

        if content_type == ContentType.CASE_STUDY:
            return FunnelStage.MOFU

        # Check for location pages (BOFU)
        if 'locations' in str(file_path):
            return FunnelStage.BOFU

        # Keyword analysis
        body_lower = body.lower()

        bofu_signals = ['pricing', 'cost', 'hire', 'contact', 'quote', 'consultation', 'get started']
        mofu_signals = ['solution', 'how we', 'our approach', 'benefits', 'features', 'case study']
        tofu_signals = ['what is', 'introduction', 'guide', 'learn', 'understand', 'basics']

        bofu_count = sum(1 for signal in bofu_signals if signal in body_lower)
        mofu_count = sum(1 for signal in mofu_signals if signal in body_lower)
        tofu_count = sum(1 for signal in tofu_signals if signal in body_lower)

        if bofu_count >= mofu_count and bofu_count >= tofu_count:
            return FunnelStage.BOFU
        elif mofu_count >= tofu_count:
            return FunnelStage.MOFU
        else:
            return FunnelStage.TOFU

    def get_content_gaps(self, content_files: list[ContentFile]) -> list[dict]:
        """Identify content gaps based on funnel analysis"""
        gaps = []

        # Count content by funnel stage
        stage_counts = {
            FunnelStage.TOFU: 0,
            FunnelStage.MOFU: 0,
            FunnelStage.BOFU: 0,
        }

        for cf in content_files:
            stage_counts[cf.funnel_stage] += 1

        total = sum(stage_counts.values())
        if total == 0:
            return []

        # Check for imbalanced funnel
        tofu_pct = stage_counts[FunnelStage.TOFU] / total
        mofu_pct = stage_counts[FunnelStage.MOFU] / total
        bofu_pct = stage_counts[FunnelStage.BOFU] / total

        if tofu_pct < 0.3:
            gaps.append({
                'type': 'funnel_gap',
                'stage': 'TOFU',
                'message': f"Only {tofu_pct*100:.0f}% of content is awareness-stage. Consider adding more educational blog posts.",
                'priority': 'high',
            })

        if mofu_pct < 0.3:
            gaps.append({
                'type': 'funnel_gap',
                'stage': 'MOFU',
                'message': f"Only {mofu_pct*100:.0f}% of content is consideration-stage. Add more case studies and solution pages.",
                'priority': 'high',
            })

        if bofu_pct < 0.2:
            gaps.append({
                'type': 'funnel_gap',
                'stage': 'BOFU',
                'message': f"Only {bofu_pct*100:.0f}% of content is decision-stage. Add more location pages and pricing content.",
                'priority': 'medium',
            })

        # Check for missing CTAs
        no_cta = [cf for cf in content_files if not cf.has_cta and cf.content_type != ContentType.BLOG]
        if no_cta:
            gaps.append({
                'type': 'missing_cta',
                'pages': [cf.url for cf in no_cta[:5]],
                'message': f"{len(no_cta)} pages lack clear CTAs",
                'priority': 'high',
            })

        # Check for thin content
        thin_content = [cf for cf in content_files if cf.word_count < 300]
        if thin_content:
            gaps.append({
                'type': 'thin_content',
                'pages': [cf.url for cf in thin_content[:5]],
                'message': f"{len(thin_content)} pages have thin content (<300 words)",
                'priority': 'medium',
            })

        return gaps

    def get_optimization_opportunities(self, content_files: list[ContentFile]) -> list[dict]:
        """Identify optimization opportunities for existing content"""
        opportunities = []

        for cf in content_files:
            # Missing meta description
            if not cf.meta_description or len(cf.meta_description) < 50:
                opportunities.append({
                    'type': 'missing_meta',
                    'url': cf.url,
                    'file': str(cf.file_path),
                    'message': 'Missing or too short meta description',
                    'priority': 'high',
                })

            # Meta description too long
            elif len(cf.meta_description) > 160:
                opportunities.append({
                    'type': 'long_meta',
                    'url': cf.url,
                    'file': str(cf.file_path),
                    'message': f'Meta description too long ({len(cf.meta_description)} chars)',
                    'priority': 'medium',
                })

            # No target keywords defined
            if not cf.target_keywords and cf.content_type in [ContentType.SERVICE, ContentType.INDUSTRY]:
                opportunities.append({
                    'type': 'no_keywords',
                    'url': cf.url,
                    'file': str(cf.file_path),
                    'message': 'No target keywords defined in frontmatter',
                    'priority': 'medium',
                })

            # Service/Industry pages without FAQ
            if cf.content_type in [ContentType.SERVICE, ContentType.INDUSTRY] and not cf.has_faq:
                opportunities.append({
                    'type': 'no_faq',
                    'url': cf.url,
                    'file': str(cf.file_path),
                    'message': 'Consider adding FAQ section for featured snippets',
                    'priority': 'low',
                })

        return opportunities
