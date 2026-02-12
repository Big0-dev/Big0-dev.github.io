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
from functools import lru_cache
from typing import Dict, Any, Optional, Union
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ContentProcessor:
    """Handles all content processing tasks for the static site generator"""

    def __init__(self):
        """Initialize the content processor with markdown converter"""
        # Initialize markdown converter with extensions
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
        if any(path in p for p in paths_to_check for path in ['services/', 'blogs/', 'case_studies/', 'case-studies/', 'news/', 'conversations/']):
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
        """
        Add automatic links to industry and service mentions in the content

        Args:
            html_content: HTML content to process
            file_path: Path to the file (for depth calculation and self-link avoidance)

        Returns:
            HTML content with automatic links added
        """
        # Calculate the relative path prefix based on file depth
        depth = len(file_path.parts) - 1 if file_path.parts else 0
        path_prefix = "../" * depth

        # Define service mappings (comprehensive keyword dictionary)
        service_links = {
            # AI & Machine Learning
            'ai integration': 'ai-powered-applications',
            'artificial intelligence': 'ai-powered-applications',
            'machine learning': 'ai-powered-applications',
            'deep learning': 'ai-powered-applications',
            'neural network': 'ai-powered-applications',
            'ai model': 'ai-powered-applications',
            'ml model': 'ai-powered-applications',
            'predictive analytics': 'ai-powered-applications',
            'ai solution': 'ai-powered-applications',

            # Computer Vision (part of AI/ML services)
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

            # Natural Language Processing (part of AI/ML services)
            'natural language processing': 'ai-powered-applications',
            'nlp': 'ai-powered-applications',
            'text analysis': 'ai-powered-applications',
            'sentiment analysis': 'ai-powered-applications',
            'chatbot': 'ai-powered-applications',
            'language model': 'ai-powered-applications',

            # Software Development
            'custom software': 'custom-software-development',
            'software development': 'custom-software-development',
            'software solution': 'custom-software-development',
            'application development': 'custom-software-development',
            'software engineering': 'custom-software-development',
            'ros': 'custom-software-development',
            'ROS': 'custom-software-development',
            'gazebo': 'custom-software-development',
            'Gazebo': 'custom-software-development',
            'simulation': 'custom-software-development',
            'simulator': 'custom-software-development',

            # Web & Mobile Development (part of Custom Software Development)
            'web development': 'custom-software-development',
            'web application': 'custom-software-development',
            'web app': 'custom-software-development',
            'website development': 'custom-software-development',
            'mobile app': 'custom-software-development',
            'mobile application': 'custom-software-development',
            'frontend': 'custom-software-development',
            'backend': 'custom-software-development',
            'full stack': 'custom-software-development',

            # Hardware & IoT Engineering (consolidated service)
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

            # Embedded Systems (part of Hardware & IoT Engineering)
            'embedded system': 'startup-engineering',
            'embedded software': 'startup-engineering',
            'embedded': 'startup-engineering',
            'arduino': 'startup-engineering',
            'Arduino': 'startup-engineering',
            'raspberry pi': 'startup-engineering',
            'microcontroller': 'startup-engineering',
            'firmware': 'startup-engineering',
            'px4': 'startup-engineering',
            'PX4': 'startup-engineering',
            'px4 autopilot': 'startup-engineering',
            'PX4 Autopilot': 'startup-engineering',
            'flight controller': 'startup-engineering',
            'dji n3': 'startup-engineering',
            'DJI N3': 'startup-engineering',
            'stm32': 'startup-engineering',
            'STM32': 'startup-engineering',
            'esp32': 'startup-engineering',
            'ESP32': 'startup-engineering',
            'bldc': 'startup-engineering',
            'BLDC': 'startup-engineering',
            'bldc motor': 'startup-engineering',
            'BLDC motor': 'startup-engineering',
            'motor control': 'startup-engineering',
            'autopilot': 'startup-engineering',

            # IoT Development (part of Hardware & IoT Engineering)
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

            # PCB Design (part of Hardware & IoT Engineering)
            'pcb': 'startup-engineering',
            'circuit board': 'startup-engineering',
            'circuit design': 'startup-engineering',
            'electronics design': 'startup-engineering',
            'altium': 'startup-engineering',
            'eagle': 'startup-engineering',
            'kicad': 'startup-engineering',

            # Database & Analytics
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

            # Dashboard Development (part of Data Analytics)
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

            # UI/UX & Design (part of Custom Software Development)
            'ui design': 'custom-software-development',
            'ux design': 'custom-software-development',
            'ui/ux': 'custom-software-development',
            'user interface': 'custom-software-development',
            'user experience': 'custom-software-development',

        }

        # Define case study mappings
        case_study_links = {
            # Agricultural Drone
            'agricultural drone': 'agridrone',
            'sprayer drone': 'agridrone',
            'agridrone': 'agridrone',
            'precision agriculture': 'agridrone',
            'crop spraying': 'agridrone',

            # AI Legal Document Analysis
            'legal document analysis': 'ai-legal-document-analysis-tool',
            'conveyancing': 'ai-legal-document-analysis-tool',
            'legal ai': 'ai-legal-document-analysis-tool',
            'document analysis tool': 'ai-legal-document-analysis-tool',

            # Civic Engagement Platform
            'civic engagement': 'civic-engagement-digital-platform',
            'member management': 'civic-engagement-digital-platform',
            'civic platform': 'civic-engagement-digital-platform',
            'grassroots organization': 'civic-engagement-digital-platform',


            # FedGAN
            'fedgan': 'fedgan',
            'federated learning': 'fedgan',
            'medical image generation': 'fedgan',
            'privacy-preserving ai': 'fedgan',
            'hipaa compliant ai': 'fedgan',

            # Healthcare Document Management
            'healthcare document': 'firstclass-healthcare-document-management',
            'firstclass': 'firstclass-healthcare-document-management',
            'medical records management': 'firstclass-healthcare-document-management',

            # Global Logistics Dashboard
            'logistics dashboard': 'global-logistics-dashboard',
            'global logistics': 'global-logistics-dashboard',
            'shipping visibility': 'global-logistics-dashboard',
            'container tracking': 'global-logistics-dashboard',

            # Premium Finance Platform
            'premium finance': 'premium-finance-management-platform',
            'insurance premium': 'premium-finance-management-platform',
            'finance management platform': 'premium-finance-management-platform',

            # Real Estate Analytics
            'real estate analytics': 'real_estate_analytics_case_study',
            'property analytics': 'real_estate_analytics_case_study',
            'real estate platform': 'real_estate_analytics_case_study',

            # Sports Card Trading
            'sports card': 'sports-card-trading-marketplace',
            'card trading': 'sports-card-trading-marketplace',
            'collectibles marketplace': 'sports-card-trading-marketplace',
            'trading marketplace': 'sports-card-trading-marketplace',
        }

        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Get current page slug to avoid self-linking
        current_slug = file_path.stem

        # Function to check if text is already inside a link
        def is_inside_link(element):
            for parent in element.parents:
                if parent.name == 'a':
                    return True
            return False

        # Process text nodes for auto-linking
        for text_node in soup.find_all(string=True):
            # Skip if already inside a link, script, style, code or pre tag
            if is_inside_link(text_node) or text_node.parent.name in ['a', 'script', 'style', 'code', 'pre']:
                continue

            text = str(text_node)
            modified = False

            # Determine what to link based on page type
            file_path_str = str(file_path)
            is_service_page = 'services/' in file_path_str
            is_blog_page = 'blogs/' in file_path_str or 'blog/' in file_path_str
            is_case_study_page = 'case_studies/' in file_path_str or 'case-studies/' in file_path_str
            is_news_page = 'news/' in file_path_str
            is_conversation_page = 'conversations/' in file_path_str

            # Collect all candidate keywords (services and case studies)
            all_keywords = []

            # Add service keywords if applicable
            if is_blog_page or is_case_study_page or is_news_page or is_conversation_page:
                for term, service_slug in service_links.items():
                    if service_slug != current_slug:
                        all_keywords.append((term, 'service', service_slug))

            # Add case study keywords for conversations, blogs, and news
            if is_conversation_page or is_blog_page or is_news_page:
                for term, case_study_slug in case_study_links.items():
                    if case_study_slug != current_slug:
                        all_keywords.append((term, 'case_study', case_study_slug))

            # Sort ALL keywords by length (longest first) to match specific phrases before generic ones
            all_keywords.sort(key=lambda x: len(x[0]), reverse=True)

            # Collect all matches first (to avoid overlapping links)
            matches_to_replace = []

            for term, link_type, slug in all_keywords:
                pattern = r'\b(' + re.escape(term) + r')\b'
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    # Check if this match overlaps with any existing match
                    overlaps = any(
                        match.start() < existing_end and match.end() > existing_start
                        for existing_start, existing_end, _, _, _ in matches_to_replace
                    )
                    if not overlaps:
                        matched_text = match.group(1)
                        if link_type == 'case_study':
                            replacement = f'<a href="{path_prefix}case-studies/{slug}.html" class="auto-link">{matched_text}</a>'
                        else:  # service
                            replacement = f'<a href="{path_prefix}services/{slug}.html" class="auto-link">{matched_text}</a>'
                        matches_to_replace.append((match.start(), match.end(), matched_text, replacement, link_type))

            # Apply all replacements from right to left (so positions don't shift)
            if matches_to_replace:
                modified = True
                matches_to_replace.sort(key=lambda x: x[0], reverse=True)
                for start, end, matched_text, replacement, link_type in matches_to_replace:
                    text = text[:start] + replacement + text[end:]

            # Replace the text node with new HTML if modified
            if modified:
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

        # Process {{related-industries:...}} directives (no-op, industries removed)
        content = re.sub(r'\{\{related-industries:([^}]+)\}\}', '', content)

        # Process {{industry-challenges:...}} directives (no-op, industries removed)
        content = re.sub(r'\{\{industry-challenges:([^}]+)\}\}', '', content)

        # Process {{industry-solutions:...}} directives (no-op, industries removed)
        content = re.sub(r'\{\{industry-solutions:([^}]+)\}\}', '', content)

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

        # Also handle directives that got wrapped in <p> tags
        # Replace <p>{{template:xxx}}</p> patterns
        def replace_p_wrapped_template(match):
            directive = match.group(1)
            templates = {
                'cta': '''<div class="inline-cta">
  <p class="cta-title">Ready to Transform Your Business?</p>
  <p>Let's discuss how we can help you achieve your goals with our innovative solutions.</p>
  <a href="../contact.html" class="btn btn-primary">Get Started Today</a>
</div>''',
                'cta-service': '''<div class="inline-cta">
  <p class="cta-title">Ready to Get Started?</p>
  <p>Our experts are ready to help you implement these solutions for your business.</p>
  <a href="../contact.html" class="btn btn-primary">Schedule a Consultation</a>
</div>''',
                'cta-case-study': '''<div class="inline-cta">
  <p class="cta-title">Want Similar Results?</p>
  <p>Let's discuss how we can deliver transformative solutions for your organization.</p>
  <a href="../contact.html" class="btn btn-primary">Contact Our Team</a>
</div>'''
            }
            return templates.get(directive, match.group(0))

        html_content = re.sub(r'<p>\{\{template:([\w-]+)\}\}</p>', replace_p_wrapped_template, html_content)

        return html_content

    @lru_cache(maxsize=128)
    def _parse_date(self, date_value: Union[str, datetime, None]) -> Optional[datetime]:
        """
        Parse date from various formats with caching

        Args:
            date_value: Date value to parse

        Returns:
            Parsed datetime object or None if parsing fails
        """
        if not date_value:
            return None

        # If already a datetime object
        if isinstance(date_value, datetime):
            return date_value

        date_str = str(date_value)

        # Try different date formats
        date_formats = [
            '%Y-%m-%d',          # 2024-01-15
            '%B %d, %Y',         # January 15, 2024
            '%b %d, %Y',         # Jan 15, 2024
            '%d %B %Y',          # 15 January 2024
            '%d %b %Y',          # 15 Jan 2024
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # If no format matches, return None
        logger.warning(f"Could not parse date: {date_str}")
        return None