#!/usr/bin/env python3
"""
Content Processor Module

Handles all content processing functionality including:
- Markdown to HTML conversion
- Template directive processing
- FAQ section processing
- Automatic interlinking
- Frontmatter parsing

Extracted from generate.py to improve modularity and maintainability.
"""

import re
import json
import yaml
import logging
import markdown
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Union
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ContentProcessor:
    """Handles all content processing tasks for the static site generator"""

    # Service keyword → slug mappings (class-level constant)
    SERVICE_LINKS = {
        'ai integration': 'ai-powered-applications',
        'artificial intelligence': 'ai-powered-applications',
        'machine learning': 'ai-powered-applications',
        'deep learning': 'ai-powered-applications',
        'neural network': 'ai-powered-applications',
        'ai model': 'ai-powered-applications',
        'ml model': 'ai-powered-applications',
        'predictive analytics': 'ai-powered-applications',
        'ai solution': 'ai-powered-applications',
        'computer vision': 'ai-powered-applications',
        'computer vision applications': 'ai-powered-applications',
        'computer vision services': 'ai-powered-applications',
        'image recognition': 'ai-powered-applications',
        'image recognition systems': 'ai-powered-applications',
        'object detection': 'ai-powered-applications',
        'facial recognition': 'ai-powered-applications',
        'image processing': 'ai-powered-applications',
        'visual data': 'ai-powered-applications',
        'opencv': 'ai-powered-applications',
        'natural language processing': 'ai-powered-applications',
        'nlp': 'ai-powered-applications',
        'text analysis': 'ai-powered-applications',
        'sentiment analysis': 'ai-powered-applications',
        'chatbot': 'ai-powered-applications',
        'language model': 'ai-powered-applications',
        'custom software': 'custom-software-development',
        'software development': 'custom-software-development',
        'software solution': 'custom-software-development',
        'application development': 'custom-software-development',
        'software engineering': 'custom-software-development',
        'ros': 'custom-software-development',
        'gazebo': 'custom-software-development',
        'simulation': 'custom-software-development',
        'simulator': 'custom-software-development',
        'web development': 'custom-software-development',
        'web application': 'custom-software-development',
        'web app': 'custom-software-development',
        'website development': 'custom-software-development',
        'mobile app': 'custom-software-development',
        'mobile application': 'custom-software-development',
        'frontend': 'custom-software-development',
        'backend': 'custom-software-development',
        'full stack': 'custom-software-development',
        'cad': 'startup-engineering',
        'cad model': 'startup-engineering',
        'hardware design': 'startup-engineering',
        'mechanical design': 'startup-engineering',
        '3d modeling': 'startup-engineering',
        '3d design': 'startup-engineering',
        '3d scanning': 'startup-engineering',
        '3d ear scanning': 'startup-engineering',
        'ergonomic design': 'startup-engineering',
        'ergonomic 3d design': 'startup-engineering',
        'product design': 'startup-engineering',
        'industrial design': 'startup-engineering',
        'mechanical construction': 'startup-engineering',
        'modular construction': 'startup-engineering',
        'modular mechanical design': 'startup-engineering',
        'precision mechanical design': 'startup-engineering',
        '3-axis gimbal': 'startup-engineering',
        'gimbal': 'startup-engineering',
        'biomechanical': 'startup-engineering',
        'solidworks': 'startup-engineering',
        'autocad': 'startup-engineering',
        'fusion 360': 'startup-engineering',
        'carbon fiber': 'startup-engineering',
        'carbon fiber construction': 'startup-engineering',
        'prototype': 'startup-engineering',
        'prototyping': 'startup-engineering',
        'wheelbase': 'startup-engineering',
        'modular design': 'startup-engineering',
        'embedded system': 'startup-engineering',
        'embedded software': 'startup-engineering',
        'embedded': 'startup-engineering',
        'arduino': 'startup-engineering',
        'raspberry pi': 'startup-engineering',
        'microcontroller': 'startup-engineering',
        'firmware': 'startup-engineering',
        'px4': 'startup-engineering',
        'px4 autopilot': 'startup-engineering',
        'flight controller': 'startup-engineering',
        'dji n3': 'startup-engineering',
        'stm32': 'startup-engineering',
        'esp32': 'startup-engineering',
        'bldc': 'startup-engineering',
        'bldc motor': 'startup-engineering',
        'motor control': 'startup-engineering',
        'autopilot': 'startup-engineering',
        'iot': 'startup-engineering',
        'internet of things': 'startup-engineering',
        'iot device': 'startup-engineering',
        'smart device': 'startup-engineering',
        'sensor': 'startup-engineering',
        'sensing layer': 'startup-engineering',
        'environmental sensor': 'startup-engineering',
        'smart meter': 'startup-engineering',
        'drone': 'startup-engineering',
        'octocopter': 'startup-engineering',
        'uav': 'startup-engineering',
        'spray system': 'startup-engineering',
        'precision spraying': 'startup-engineering',
        'agricultural drone': 'startup-engineering',
        'sprayer drone': 'startup-engineering',
        'telemetry': 'startup-engineering',
        'mqtt': 'startup-engineering',
        'lorawan': 'startup-engineering',
        'edge computing': 'startup-engineering',
        'smart city': 'startup-engineering',
        'smart cities': 'startup-engineering',
        'pcb': 'startup-engineering',
        'circuit board': 'startup-engineering',
        'circuit design': 'startup-engineering',
        'electronics design': 'startup-engineering',
        'altium': 'startup-engineering',
        'eagle': 'startup-engineering',
        'kicad': 'startup-engineering',
        'data analytics': 'ai-powered-applications',
        'data analysis': 'ai-powered-applications',
        'business intelligence': 'ai-powered-applications',
        'bi solution': 'ai-powered-applications',
        'data visualization': 'ai-powered-applications',
        'big data': 'ai-powered-applications',
        'data science': 'ai-powered-applications',
        'sql': 'ai-powered-applications',
        'database': 'ai-powered-applications',
        'data warehouse': 'ai-powered-applications',
        'real-time analytics': 'ai-powered-applications',
        'predictive modeling': 'ai-powered-applications',
        'data processing': 'ai-powered-applications',
        'dashboard': 'ai-powered-applications',
        'analytics dashboard': 'ai-powered-applications',
        'reporting dashboard': 'ai-powered-applications',
        'real-time dashboard': 'ai-powered-applications',
        'kpi dashboard': 'ai-powered-applications',
        'management dashboard': 'ai-powered-applications',
        'city management dashboard': 'ai-powered-applications',
        'tableau': 'ai-powered-applications',
        'power bi': 'ai-powered-applications',
        'digital twin': 'ai-powered-applications',
        'ui design': 'custom-software-development',
        'ux design': 'custom-software-development',
        'ui/ux': 'custom-software-development',
        'user interface': 'custom-software-development',
        'user experience': 'custom-software-development',
    }

    # Case study keyword → slug mappings (class-level constant)
    CASE_STUDY_LINKS = {
        'agricultural drone': 'agridrone',
        'sprayer drone': 'agridrone',
        'agridrone': 'agridrone',
        'precision agriculture': 'agridrone',
        'crop spraying': 'agridrone',
        'legal document analysis': 'ai-legal-document-analysis-tool',
        'conveyancing': 'ai-legal-document-analysis-tool',
        'legal ai': 'ai-legal-document-analysis-tool',
        'document analysis tool': 'ai-legal-document-analysis-tool',
        'civic engagement': 'civic-engagement-digital-platform',
        'member management': 'civic-engagement-digital-platform',
        'civic platform': 'civic-engagement-digital-platform',
        'grassroots organization': 'civic-engagement-digital-platform',
        'fedgan': 'fedgan',
        'federated learning': 'fedgan',
        'medical image generation': 'fedgan',
        'privacy-preserving ai': 'fedgan',
        'hipaa compliant ai': 'fedgan',
        'healthcare document': 'firstclass-healthcare-document-management',
        'firstclass': 'firstclass-healthcare-document-management',
        'medical records management': 'firstclass-healthcare-document-management',
        'logistics dashboard': 'global-logistics-dashboard',
        'global logistics': 'global-logistics-dashboard',
        'shipping visibility': 'global-logistics-dashboard',
        'container tracking': 'global-logistics-dashboard',
        'premium finance': 'premium-finance-management-platform',
        'insurance premium': 'premium-finance-management-platform',
        'finance management platform': 'premium-finance-management-platform',
        'real estate analytics': 'real_estate_analytics_case_study',
        'property analytics': 'real_estate_analytics_case_study',
        'real estate platform': 'real_estate_analytics_case_study',
        'sports card': 'sports-card-trading-marketplace',
        'card trading': 'sports-card-trading-marketplace',
        'collectibles marketplace': 'sports-card-trading-marketplace',
        'trading marketplace': 'sports-card-trading-marketplace',
    }

    # Pre-sorted keyword lists (sorted by length descending, computed once)
    _SERVICE_KEYWORDS_SORTED = sorted(
        SERVICE_LINKS.items(), key=lambda x: len(x[0]), reverse=True
    )
    _CASE_STUDY_KEYWORDS_SORTED = sorted(
        CASE_STUDY_LINKS.items(), key=lambda x: len(x[0]), reverse=True
    )

    # Pre-compiled regex for removing deprecated directives
    _DEPRECATED_DIRECTIVES_RE = re.compile(
        r'\{\{(?:related-industries|industry-challenges|industry-solutions):([^}]+)\}\}'
    )

    # Date formats to try when parsing
    _DATE_FORMATS = [
        '%Y-%m-%d',
        '%B %d, %Y',
        '%b %d, %Y',
        '%d %B %Y',
        '%d %b %Y',
    ]

    # Date parse cache (module-level dict instead of broken lru_cache on instance method)
    _date_cache: Dict[str, Optional[datetime]] = {}

    def __init__(self):
        """Initialize the content processor with markdown converter"""
        self._md_converter = markdown.Markdown(
            extensions=['extra', 'codehilite', 'toc']
        )

    def process_markdown(self, content: str, metadata: Dict[str, Any],
                        file_path: Path, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Main method to process markdown content with all transformations

        Args:
            content: Raw markdown content
            metadata: Frontmatter metadata
            file_path: Source file path
            output_path: Output file path (for depth calculation)

        Returns:
            Dict with processed content and metadata
        """
        # Use output_path if provided for correct depth calculation, otherwise use file_path
        template_path = output_path if output_path else file_path

        # Process template directives before converting to HTML
        processed_content = self.process_template_directives(content, template_path)

        # Convert markdown to HTML
        self._md_converter.reset()
        html_content = self._md_converter.convert(processed_content)

        # Process any remaining directives that might have been wrapped in HTML tags
        html_content = self._process_template_directives_in_html(html_content, template_path)

        # Auto-link industry and service mentions for specific page types
        link_path = output_path if output_path else file_path
        paths_to_check = [str(file_path), str(output_path) if output_path else '']
        if any(path in p for p in paths_to_check for path in ['services/', 'blogs/', 'case_studies/', 'case-studies/', 'news/']):
            html_content = self.add_automatic_interlinking(html_content, link_path)

        # Extract first paragraph as excerpt
        soup = BeautifulSoup(html_content, 'html.parser')
        first_p = soup.find('p')
        excerpt = first_p.text if first_p else ""

        # Parse features if they exist
        features = metadata.get('features', '')
        if isinstance(features, str):
            features = [f.strip() for f in features.split(',') if f.strip()]

        # Create short description from description or excerpt
        short_description = metadata.get('description', '')
        if not short_description and excerpt:
            short_description = excerpt[:160] + '...' if len(excerpt) > 160 else excerpt

        return {
            'slug': file_path.stem,
            'title': metadata.get('title', 'Untitled'),
            'meta_description': metadata.get('meta_description', excerpt[:160]),
            'short_description': short_description,
            'content_html': html_content,
            'frontmatter': metadata,
            'icon': metadata.get('icon', ''),
            'price': metadata.get('price', ''),
            'features': features,
            'excerpt': metadata.get('description', excerpt[:200] + '...' if len(excerpt) > 200 else excerpt),
            'category': metadata.get('category', 'General'),
            'date': self._parse_date(metadata.get('date')),
            'tags': metadata.get('tags', '').split(',') if metadata.get('tags') else [],
            'external_link': metadata.get('external_link', ''),
        }

    def load_markdown_content(self, file_path: Path, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load and parse markdown content from file

        Args:
            file_path: Path to markdown file
            output_path: Output path for depth calculation

        Returns:
            Dict with processed content and metadata
        """
        content = file_path.read_text(encoding='utf-8')

        # Extract frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                markdown_content = parts[2].strip()
            else:
                frontmatter = {}
                markdown_content = content
        else:
            frontmatter = {}
            markdown_content = content

        return self.process_markdown(markdown_content, frontmatter, file_path, output_path)

    def add_automatic_interlinking(self, html_content: str, file_path: Path) -> str:
        """Add automatic links to service/case-study mentions in the content."""
        depth = len(file_path.parts) - 1 if file_path.parts else 0
        path_prefix = "../" * depth

        soup = BeautifulSoup(html_content, 'html.parser')
        current_slug = file_path.stem

        # Determine page type once (not per text node)
        file_path_str = str(file_path)
        is_blog_page = 'blogs/' in file_path_str or 'blog/' in file_path_str
        is_case_study_page = 'case_studies/' in file_path_str or 'case-studies/' in file_path_str
        is_news_page = 'news/' in file_path_str

        # Build keyword list once using pre-sorted class-level constants
        all_keywords = []
        if is_blog_page or is_case_study_page or is_news_page:
            for term, slug in self._SERVICE_KEYWORDS_SORTED:
                if slug != current_slug:
                    all_keywords.append((term, 'service', slug))

        if is_blog_page or is_news_page:
            for term, slug in self._CASE_STUDY_KEYWORDS_SORTED:
                if slug != current_slug:
                    all_keywords.append((term, 'case_study', slug))

        # Re-sort combined list by length (longest first)
        all_keywords.sort(key=lambda x: len(x[0]), reverse=True)

        if not all_keywords:
            return html_content

        # Skip tags that should not be auto-linked
        skip_tags = frozenset(['a', 'script', 'style', 'code', 'pre'])

        def is_inside_link(element):
            for parent in element.parents:
                if parent.name == 'a':
                    return True
            return False

        for text_node in soup.find_all(string=True):
            if is_inside_link(text_node) or text_node.parent.name in skip_tags:
                continue

            text = str(text_node)
            matches_to_replace = []

            for term, link_type, slug in all_keywords:
                pattern = r'\b(' + re.escape(term) + r')\b'
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    overlaps = any(
                        match.start() < ee and match.end() > es
                        for es, ee, _, _ in matches_to_replace
                    )
                    if not overlaps:
                        matched_text = match.group(1)
                        if link_type == 'case_study':
                            replacement = f'<a href="{path_prefix}case-studies/{slug}.html" class="auto-link">{matched_text}</a>'
                        else:
                            replacement = f'<a href="{path_prefix}services/{slug}.html" class="auto-link">{matched_text}</a>'
                        matches_to_replace.append((match.start(), match.end(), matched_text, replacement))

            if matches_to_replace:
                matches_to_replace.sort(key=lambda x: x[0], reverse=True)
                for start, end, _, replacement in matches_to_replace:
                    text = text[:start] + replacement + text[end:]

                new_soup = BeautifulSoup(text, 'html.parser')
                new_elements = list(new_soup.children)
                if new_elements:
                    first_element = new_elements[0]
                    text_node.replace_with(first_element)
                    for element in new_elements[1:]:
                        first_element.insert_after(element)
                        first_element = element

        return str(soup)

    def process_template_directives(self, content: str, file_path: Optional[Path] = None) -> str:
        """
        Process template directives like {{template:cta}} in markdown content

        Args:
            content: Content to process
            file_path: Path for depth calculation (optional)

        Returns:
            Content with template directives replaced
        """
        # Calculate the relative path prefix based on file depth
        if file_path:
            depth = len(file_path.parts) - 1 if file_path.parts else 0
            path_prefix = "../" * depth
        else:
            path_prefix = "../"  # Default for single-level pages

        # Define template replacements
        templates = {
            'cta': f'''
<div class="inline-cta">
  <p class="cta-title">Talk to Our Engineers</p>
  <p>The people who built this are the people you'll talk to. No sales team in between.</p>
  <a href="{path_prefix}contact.html" class="btn btn-primary">Start a Conversation &rarr;</a>
</div>
''',
            'cta-service': f'''
<div class="inline-cta">
  <p class="cta-title">Need This Built?</p>
  <p>Tell us what you're working on. Our engineers will scope it, not a sales team.</p>
  <a href="{path_prefix}contact.html" class="btn btn-primary">Talk to Engineers &rarr;</a>
</div>
''',
            'cta-case-study': f'''
<div class="inline-cta">
  <p class="cta-title">Want Similar Results?</p>
  <p>Same engineers, same approach. Tell us what you're building.</p>
  <a href="{path_prefix}contact.html" class="btn btn-primary">Start a Conversation &rarr;</a>
</div>
''',
        }

        # Find and replace all template directives
        def replace_template(match):
            template_name = match.group(1)
            return templates.get(template_name, match.group(0))

        # Process {{template:name}} directives (updated to handle hyphens in template names)
        content = re.sub(r'\{\{template:([\w-]+)\}\}', replace_template, content)

        # Process {{related-services:service1,service2,service3}} directives
        def replace_related_services(match):
            services = [s.strip() for s in match.group(1).split(',')]
            html = '<div class="related-services-inline">\n<h3>Related Services</h3>\n<div class="related-services-grid">\n'
            for service in services:
                html += f'  <a href="{path_prefix}services/{service}.html" class="related-service-link">\n'
                html += f'    <span class="link-icon">→</span>\n'
                html += f'    <span>{service.replace("-", " ").replace("_", " ").title()}</span>\n'
                html += f'  </a>\n'
            html += '</div>\n</div>'
            return html

        content = re.sub(r'\{\{related-services:([^}]+)\}\}', replace_related_services, content)

        # Remove deprecated industry directives (single pass)
        content = self._DEPRECATED_DIRECTIVES_RE.sub('', content)

        return content

    def process_faq_sections(self, html_content: str) -> str:
        """
        Convert FAQ sections to interactive accordion format

        Args:
            html_content: HTML content to process

        Returns:
            HTML content with FAQ sections converted to interactive components
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find FAQ sections (h2 with "Frequently Asked Questions" or "FAQ")
        for h2 in soup.find_all('h2'):
            if h2.text and ('frequently asked questions' in h2.text.lower() or 'faq' in h2.text.lower()):
                # Create FAQ container
                faq_container = soup.new_tag('div', attrs={'class': 'faq-section'})
                faq_header = soup.new_tag('div', attrs={'class': 'faq-header'})
                faq_title = soup.new_tag('h2')
                faq_title.string = h2.text
                faq_header.append(faq_title)

                # Add intro paragraph if exists
                next_elem = h2.find_next_sibling()
                if next_elem and next_elem.name == 'p' and not next_elem.find_next_sibling('h3'):
                    intro = soup.new_tag('p', attrs={'class': 'faq-intro'})
                    if next_elem.string:
                        intro.string = next_elem.string
                    else:
                        # Preserve inner HTML
                        for child in list(next_elem.children):
                            intro.append(child.extract())
                    faq_header.append(intro)
                    next_elem.decompose()

                faq_container.append(faq_header)

                # Create FAQ items container
                faq_items = soup.new_tag('div', attrs={'class': 'faq-items'})

                # Process FAQ items (h3 questions followed by answers)
                current_elem = h2.find_next_sibling()
                item_index = 0
                while current_elem:
                    if current_elem.name == 'h2':
                        # Stop if we hit another h2
                        break
                    elif current_elem.name == 'h3':
                        item_index += 1
                        # This is a question
                        faq_item = soup.new_tag('div', attrs={'class': 'faq-item', 'data-faq-index': str(item_index)})

                        # Create question button
                        question = soup.new_tag('button', attrs={
                            'class': 'faq-question',
                            'aria-expanded': 'false',
                            'aria-controls': f'faq-answer-{item_index}'
                        })
                        question_text = soup.new_tag('span', attrs={'class': 'faq-question-text'})
                        question_text.string = current_elem.text
                        question.append(question_text)

                        # Add chevron icon
                        icon = soup.new_tag('span', attrs={'class': 'faq-icon'})
                        icon.string = '▼'  # Will be styled with CSS
                        question.append(icon)

                        faq_item.append(question)

                        # Create answer container
                        answer_container = soup.new_tag('div', attrs={
                            'class': 'faq-answer',
                            'id': f'faq-answer-{item_index}'
                        })
                        answer_content = soup.new_tag('div', attrs={'class': 'faq-answer-content'})

                        # Get the answer (next paragraph(s) until next h3 or h2)
                        to_remove = current_elem
                        answer_elem = current_elem.find_next_sibling()
                        while answer_elem and answer_elem.name not in ['h2', 'h3']:
                            if answer_elem.name in ['p', 'ul', 'ol', 'blockquote']:
                                # Clone the element to preserve its content
                                cloned = soup.new_tag(answer_elem.name)
                                if answer_elem.attrs:
                                    cloned.attrs = answer_elem.attrs.copy()
                                if answer_elem.string:
                                    cloned.string = answer_elem.string
                                else:
                                    for child in list(answer_elem.children):
                                        cloned.append(child.extract())
                                answer_content.append(cloned)
                            next_answer = answer_elem.find_next_sibling()
                            answer_elem.decompose()
                            answer_elem = next_answer

                        answer_container.append(answer_content)
                        faq_item.append(answer_container)
                        faq_items.append(faq_item)

                        # Move to next element
                        current_elem = answer_elem
                        to_remove.decompose()
                    else:
                        # Skip any other elements between FAQs
                        next_elem = current_elem.find_next_sibling()
                        current_elem.decompose()
                        current_elem = next_elem

                faq_container.append(faq_items)

                # Add FAQ schema script for SEO
                schema_script = soup.new_tag('script', attrs={'type': 'application/ld+json'})
                faq_data = []
                for item in faq_items.find_all('div', class_='faq-item'):
                    q = item.find('span', class_='faq-question-text')
                    a = item.find('div', class_='faq-answer-content')
                    if q and a:
                        faq_data.append({
                            "@type": "Question",
                            "name": q.text,
                            "acceptedAnswer": {
                                "@type": "Answer",
                                "text": a.get_text(strip=True)
                            }
                        })

                if faq_data:
                    schema = {
                        "@context": "https://schema.org",
                        "@type": "FAQPage",
                        "mainEntity": faq_data
                    }
                    schema_script.string = json.dumps(schema, indent=2)
                    faq_container.append(schema_script)

                # Replace the original h2 with the new FAQ structure
                h2.replace_with(faq_container)

        return str(soup)

    def _process_template_directives_in_html(self, html_content: str, file_path: Optional[Path] = None) -> str:
        """
        Process template directives that may be wrapped in HTML tags

        Args:
            html_content: HTML content to process
            file_path: Path for depth calculation (optional)

        Returns:
            HTML content with directives processed
        """
        # First process FAQ sections
        html_content = self.process_faq_sections(html_content)

        # Then process any directives that are already in the markdown
        html_content = self.process_template_directives(html_content, file_path)

        # Handle directives that got wrapped in <p> tags — re-run directive processing
        html_content = re.sub(
            r'<p>\{\{template:([\w-]+)\}\}</p>',
            lambda m: self.process_template_directives(
                '{{template:' + m.group(1) + '}}', file_path
            ),
            html_content
        )

        return html_content

    def _parse_date(self, date_value: Union[str, datetime, None]) -> Optional[datetime]:
        """Parse date from various formats with dict-based caching."""
        if not date_value:
            return None

        if isinstance(date_value, datetime):
            return date_value

        date_str = str(date_value)

        # Check cache first
        if date_str in self._date_cache:
            return self._date_cache[date_str]

        for fmt in self._DATE_FORMATS:
            try:
                result = datetime.strptime(date_str, fmt)
                self._date_cache[date_str] = result
                return result
            except ValueError:
                continue

        logger.warning(f"Could not parse date: {date_str}")
        self._date_cache[date_str] = None
        return None