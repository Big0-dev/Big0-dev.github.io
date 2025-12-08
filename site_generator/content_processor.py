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
from bs4 import BeautifulSoup, NavigableString

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
        # Check both file_path and output_path for path matching (output_path uses hyphens, content_dir uses underscores)
        paths_to_check = [str(file_path), str(output_path) if output_path else '']
        if any(path in p for p in paths_to_check for path in ['services/', 'industries/', 'blogs/', 'case_studies/', 'case-studies/', 'news/']):
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
            # Check if this is a blog file with the special format
            lines = content.strip().split('\n')
            if len(lines) >= 5 and 'blogs' in str(file_path):
                # Parse blog format: title, category, date, image, description
                frontmatter = {
                    'title': lines[0],
                    'category': lines[1],
                    'date': lines[2],
                    'image_url': lines[3] if lines[3] else '',
                    'meta_description': lines[4]
                }
                markdown_content = '\n'.join(lines[5:]).strip()
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
        # file_path is like "services/locations/usa/ai-integration-usa.html"
        depth = len(file_path.parts) - 1 if file_path.parts else 0
        path_prefix = "../" * depth

        # Define industry mappings (expanded)
        industry_links = {
            # Finance Industry
            'financial services': 'finance',
            'fintech': 'finance',
            'banking': 'finance',
            'investment': 'finance',
            'trading': 'finance',
            'insurance': 'finance',
            'wealth management': 'finance',
            'payment processing': 'finance',
            'digital banking': 'finance',
            'financial institution': 'finance',

            # Healthcare Industry
            'healthcare': 'healthcare',
            'health tech': 'healthcare',
            'medical': 'healthcare',
            'life sciences': 'healthcare',
            'pharmaceutical': 'healthcare',
            'biotech': 'healthcare',
            'hospital': 'healthcare',
            'clinical': 'healthcare',
            'patient care': 'healthcare',
            'medical device': 'healthcare',
            'health information': 'healthcare',

            # Retail Industry
            'retail': 'retail',
            'e-commerce': 'retail',
            'ecommerce': 'retail',
            'online shopping': 'retail',
            'marketplace': 'retail',
            'consumer goods': 'retail',
            'fashion': 'retail',
            'grocery': 'retail',
            'wholesale': 'retail',

            # Manufacturing Industry
            'manufacturing': 'manufacturing',
            'logistics': 'manufacturing',
            'supply chain': 'manufacturing',
            'warehouse': 'manufacturing',
            'inventory': 'manufacturing',
            # Removed 'production' as it's too ambiguous (software production vs manufacturing)
            'factory': 'manufacturing',
            'industrial': 'manufacturing',
            'automotive': 'manufacturing',
            'aerospace': 'manufacturing',
            'agriculture': 'manufacturing',
            'agricultural': 'manufacturing',
            'farming': 'manufacturing',

            # Telecom & Media Industry
            'telecommunications': 'telecom',
            'telecom': 'telecom',
            'media': 'telecom',
            'entertainment': 'telecom',
            'broadcasting': 'telecom',
            'streaming': 'telecom',
            'gaming': 'telecom',
            'education technology': 'telecom',
            'edtech': 'telecom',
            'e-learning': 'telecom',
            'online education': 'telecom',

            # Energy Industry
            'energy': 'energy',
            'oil and gas': 'energy',
            'renewable energy': 'energy',
            'solar': 'energy',
            'wind energy': 'energy',
            'utilities': 'energy',
            'power generation': 'energy',
            'electric': 'energy',
            'sustainability': 'energy',

            # Non-Profit & NGO Industry
            'non-profit': 'non-profit',
            'nonprofit': 'non-profit',
            'ngo': 'non-profit',
            'charity': 'non-profit',
            'foundation': 'non-profit',
            'advocacy': 'non-profit',
            'civic organization': 'non-profit',
            'community organization': 'non-profit',
            'grassroots': 'non-profit',
            'social impact': 'non-profit',
            'volunteer organization': 'non-profit'
        }

        # Define service mappings (comprehensive keyword dictionary)
        service_links = {
            # AI & Machine Learning
            'ai integration': 'ai-ml-services',
            'artificial intelligence': 'ai-ml-services',
            'machine learning': 'ai-ml-services',
            'deep learning': 'ai-ml-services',
            'neural network': 'ai-ml-services',
            'ai model': 'ai-ml-services',
            'ml model': 'ai-ml-services',
            'predictive analytics': 'ai-ml-services',
            'ai solution': 'ai-ml-services',

            # Computer Vision (part of AI/ML services)
            'computer vision': 'ai-ml-services',
            'computer vision applications': 'ai-ml-services',
            'computer vision services': 'ai-ml-services',
            'image recognition': 'ai-ml-services',
            'image recognition systems': 'ai-ml-services',
            'object detection': 'ai-ml-services',
            'facial recognition': 'ai-ml-services',
            'image processing': 'ai-ml-services',
            'visual data': 'ai-ml-services',
            'opencv': 'ai-ml-services',

            # Natural Language Processing (part of AI/ML services)
            'natural language processing': 'ai-ml-services',
            'nlp': 'ai-ml-services',
            'text analysis': 'ai-ml-services',
            'sentiment analysis': 'ai-ml-services',
            'chatbot': 'ai-ml-services',
            'language model': 'ai-ml-services',

            # Software Development
            'custom software': 'software-development',
            'software development': 'software-development',
            'software solution': 'software-development',
            'application development': 'software-development',
            'software engineering': 'software-development',
            'ros': 'software-development',
            'ROS': 'software-development',
            'gazebo': 'software-development',
            'Gazebo': 'software-development',
            'simulation': 'software-development',
            'simulator': 'software-development',

            # Web Development
            'web development': 'web-development',
            'web application': 'web-development',
            'web app': 'web-development',
            'website development': 'web-development',
            'react': 'web-development',
            'angular': 'web-development',
            'vue': 'web-development',
            'javascript': 'web-development',
            'typescript': 'web-development',
            'frontend': 'web-development',
            'backend': 'web-development',
            'full stack': 'web-development',
            'node.js': 'web-development',
            'nodejs': 'web-development',

            # Mobile Development
            'mobile app': 'mobile_app.development',
            'mobile application': 'mobile_app.development',
            'ios app': 'mobile_app.development',
            'android app': 'mobile_app.development',
            'flutter': 'mobile_app.development',
            'react native': 'mobile_app.development',
            'swift': 'mobile_app.development',
            'kotlin': 'mobile_app.development',

            # Hardware & IoT Engineering (consolidated service)
            'cad': 'hardware-iot-engineering',
            'cad model': 'hardware-iot-engineering',
            'hardware design': 'hardware-iot-engineering',
            'mechanical design': 'hardware-iot-engineering',
            '3d modeling': 'hardware-iot-engineering',
            '3d design': 'hardware-iot-engineering',
            '3d scanning': 'hardware-iot-engineering',
            '3d ear scanning': 'hardware-iot-engineering',
            'ergonomic design': 'hardware-iot-engineering',
            'ergonomic 3d design': 'hardware-iot-engineering',
            'product design': 'hardware-iot-engineering',
            'industrial design': 'hardware-iot-engineering',
            'mechanical construction': 'hardware-iot-engineering',
            'modular construction': 'hardware-iot-engineering',
            'modular mechanical design': 'hardware-iot-engineering',
            'precision mechanical design': 'hardware-iot-engineering',
            '3-axis gimbal': 'hardware-iot-engineering',
            'gimbal': 'hardware-iot-engineering',
            'biomechanical': 'hardware-iot-engineering',
            'solidworks': 'hardware-iot-engineering',
            'autocad': 'hardware-iot-engineering',
            'fusion 360': 'hardware-iot-engineering',
            'carbon fiber': 'hardware-iot-engineering',
            'carbon fiber construction': 'hardware-iot-engineering',
            'prototype': 'hardware-iot-engineering',
            'prototyping': 'hardware-iot-engineering',
            'wheelbase': 'hardware-iot-engineering',
            'modular design': 'hardware-iot-engineering',

            # Embedded Systems (part of Hardware & IoT Engineering)
            'embedded system': 'hardware-iot-engineering',
            'embedded software': 'hardware-iot-engineering',
            'embedded': 'hardware-iot-engineering',
            'arduino': 'hardware-iot-engineering',
            'Arduino': 'hardware-iot-engineering',
            'raspberry pi': 'hardware-iot-engineering',
            'microcontroller': 'hardware-iot-engineering',
            'firmware': 'hardware-iot-engineering',
            'px4': 'hardware-iot-engineering',
            'PX4': 'hardware-iot-engineering',
            'px4 autopilot': 'hardware-iot-engineering',
            'PX4 Autopilot': 'hardware-iot-engineering',
            'flight controller': 'hardware-iot-engineering',
            'dji n3': 'hardware-iot-engineering',
            'DJI N3': 'hardware-iot-engineering',
            'stm32': 'hardware-iot-engineering',
            'STM32': 'hardware-iot-engineering',
            'esp32': 'hardware-iot-engineering',
            'ESP32': 'hardware-iot-engineering',
            'bldc': 'hardware-iot-engineering',
            'BLDC': 'hardware-iot-engineering',
            'bldc motor': 'hardware-iot-engineering',
            'BLDC motor': 'hardware-iot-engineering',
            'motor control': 'hardware-iot-engineering',
            'autopilot': 'hardware-iot-engineering',

            # IoT Development (part of Hardware & IoT Engineering)
            'iot': 'hardware-iot-engineering',
            'internet of things': 'hardware-iot-engineering',
            'iot device': 'hardware-iot-engineering',
            'smart device': 'hardware-iot-engineering',
            'sensor': 'hardware-iot-engineering',
            'sensing layer': 'hardware-iot-engineering',
            'environmental sensor': 'hardware-iot-engineering',
            'smart meter': 'hardware-iot-engineering',
            'drone': 'hardware-iot-engineering',
            'octocopter': 'hardware-iot-engineering',
            'uav': 'hardware-iot-engineering',
            'spray system': 'hardware-iot-engineering',
            'precision spraying': 'hardware-iot-engineering',
            'agricultural drone': 'hardware-iot-engineering',
            'sprayer drone': 'hardware-iot-engineering',
            'telemetry': 'hardware-iot-engineering',
            'mqtt': 'hardware-iot-engineering',
            'lorawan': 'hardware-iot-engineering',
            'edge computing': 'hardware-iot-engineering',
            'smart city': 'hardware-iot-engineering',
            'smart cities': 'hardware-iot-engineering',

            # PCB Design (part of Hardware & IoT Engineering)
            'pcb': 'hardware-iot-engineering',
            'circuit board': 'hardware-iot-engineering',
            'circuit design': 'hardware-iot-engineering',
            'electronics design': 'hardware-iot-engineering',
            'altium': 'hardware-iot-engineering',
            'eagle': 'hardware-iot-engineering',
            'kicad': 'hardware-iot-engineering',

            # Cloud Services
            'cloud service': 'cloud-services',
            'cloud management': 'cloud-services',
            'cloud solution': 'cloud-services',
            'aws': 'cloud-services',
            'azure': 'cloud-services',
            'google cloud': 'cloud-services',
            'gcp': 'cloud-services',
            'cloud infrastructure': 'cloud-services',
            '5g network': 'cloud-services',
            '5g': 'cloud-services',
            'cloud platform': 'cloud-services',

            # DevOps & Quality Services
            'devops': 'devops-quality-services',
            'ci/cd': 'devops-quality-services',
            'docker': 'devops-quality-services',
            'kubernetes': 'devops-quality-services',
            'jenkins': 'devops-quality-services',
            'terraform': 'devops-quality-services',
            'ansible': 'devops-quality-services',
            'infrastructure as code': 'devops-quality-services',

            # Database & Analytics
            'data analytics': 'data-analytics-services',
            'data analysis': 'data-analytics-services',
            'business intelligence': 'data-analytics-services',
            'bi solution': 'data-analytics-services',
            'data visualization': 'data-analytics-services',
            'big data': 'data-analytics-services',
            'data science': 'data-analytics-services',
            'sql': 'data-analytics-services',
            'database': 'data-analytics-services',
            'data warehouse': 'data-analytics-services',
            'real-time analytics': 'data-analytics-services',
            'predictive modeling': 'data-analytics-services',
            'data processing': 'data-analytics-services',

            # Dashboard Development (part of Data Analytics)
            'dashboard': 'data-analytics-services',
            'analytics dashboard': 'data-analytics-services',
            'reporting dashboard': 'data-analytics-services',
            'real-time dashboard': 'data-analytics-services',
            'kpi dashboard': 'data-analytics-services',
            'management dashboard': 'data-analytics-services',
            'city management dashboard': 'data-analytics-services',
            'tableau': 'data-analytics-services',
            'power bi': 'data-analytics-services',
            'digital twin': 'data-analytics-services',

            # Python Automation
            'python': 'python-automation',
            'python script': 'python-automation',
            'automation': 'python-automation',
            'web scraping': 'python-automation',
            'pandas': 'python-automation',
            'numpy': 'python-automation',

            # UI/UX & Design Services
            'ui design': 'design-services',
            'ux design': 'design-services',
            'ui/ux': 'design-services',
            'user interface': 'design-services',
            'user experience': 'design-services',
            'figma': 'design-services',
            'sketch': 'design-services',
            'adobe xd': 'design-services',
            'wireframe': 'design-services',
            'mockup': 'design-services',

            # Brand & Digital Design (part of Design Services)
            'brand design': 'design-services',
            'branding': 'design-services',
            'logo design': 'design-services',
            'graphic design': 'design-services',
            'visual identity': 'design-services',
            'brand identity': 'design-services',

            # Blockchain
            'blockchain': 'blockchain_development',
            'smart contract': 'blockchain_development',
            'ethereum': 'blockchain_development',
            'solidity': 'blockchain_development',
            'web3': 'blockchain_development',
            'cryptocurrency': 'blockchain_development',
            'defi': 'blockchain_development',
            'nft': 'blockchain_development',

            # AR/VR Development
            'ar development': 'ar_vr_development',
            'vr development': 'ar_vr_development',
            'ar vr development': 'ar_vr_development',
            'ar vr app development': 'ar_vr_development',
            'ar vr application development': 'ar_vr_development',
            'augmented reality': 'ar_vr_development',
            'virtual reality': 'ar_vr_development',
            'ar/vr': 'ar_vr_development',
            'ar vr': 'ar_vr_development',
            'mixed reality': 'ar_vr_development',
            'xr development': 'ar_vr_development',
            'xr content': 'ar_vr_development',
            'immersive experiences': 'ar_vr_development',
            'virtual simulations': 'ar_vr_development',
            'unity': 'ar_vr_development',
            'unreal engine': 'ar_vr_development',
            'oculus': 'ar_vr_development',
            'metaverse': 'ar_vr_development',

            # E-commerce
            'e-commerce development services': 'e_commerce_solutions',
            'ecommerce development services': 'e_commerce_solutions',
            'e-commerce development': 'e_commerce_solutions',
            'ecommerce development': 'e_commerce_solutions',
            'e-commerce solutions': 'e_commerce_solutions',
            'ecommerce solutions': 'e_commerce_solutions',
            'e-commerce': 'e_commerce_solutions',
            'ecommerce': 'e_commerce_solutions',
            'online store': 'e_commerce_solutions',
            'shopping cart': 'e_commerce_solutions',
            'payment integration': 'e_commerce_solutions',
            'shopify': 'e_commerce_solutions',
            'woocommerce': 'e_commerce_solutions',
            'magento': 'e_commerce_solutions',

            # ERP Implementation
            'erp': 'erp_implementation',
            'enterprise resource planning': 'erp_implementation',
            'sap': 'erp_implementation',
            'oracle erp': 'erp_implementation',
            'microsoft dynamics': 'erp_implementation',
            'odoo': 'erp_implementation',

            # Software Testing (part of DevOps & Quality Services)
            'software testing': 'devops-quality-services',
            'qa testing': 'devops-quality-services',
            'quality assurance': 'devops-quality-services',
            'test automation': 'devops-quality-services',
            'selenium': 'devops-quality-services',
            'unit testing': 'devops-quality-services',
            'integration testing': 'devops-quality-services',
            'performance testing': 'devops-quality-services',

            # Cybersecurity & Security Services
            'cybersecurity': 'security-services',
            'security solution': 'security-services',
            'penetration testing': 'security-services',
            'security audit': 'security-services',
            'vulnerability assessment': 'security-services',
            'data security': 'security-services',

            # FinTech
            'fintech': 'fintech_development',
            'financial technology': 'fintech_development',
            'payment system': 'fintech_development',
            'banking solution': 'fintech_development',
            'trading platform': 'fintech_development',
            'digital wallet': 'fintech_development',

            # Healthcare IT
            'healthcare it': 'healthcare_it_solutions',
            'health tech': 'healthcare_it_solutions',
            'medical software': 'healthcare_it_solutions',
            'ehr system': 'healthcare_it_solutions',
            'telemedicine': 'healthcare_it_solutions',
            'hipaa compliant': 'healthcare_it_solutions',

            # Game Development
            'game development': 'game_development',
            'game design': 'game_development',
            'unity game': 'game_development',
            'unreal game': 'game_development',
            'mobile game': 'game_development',
            'gamedev': 'game_development',

            # Digital Marketing
            'digital marketing': 'digital_marketing_services',
            'seo': 'digital_marketing_services',
            'search engine optimization': 'digital_marketing_services',
            'ppc': 'digital_marketing_services',
            'social media marketing': 'digital_marketing_services',
            'content marketing': 'digital_marketing_services',

            # Staff Augmentation
            'staff augmentation': 'staff-augmentation',
            'it staff augmentation': 'staff-augmentation',
            'offshore staff augmentation': 'staff-augmentation',
            'nearshore staff augmentation': 'staff-augmentation',
            'remote developer staffing': 'staff-augmentation',
            'team scaling': 'staff-augmentation',
            'team augmentation': 'staff-augmentation',
            'dedicated developer': 'staff-augmentation',
            'resource augmentation': 'staff-augmentation',
            'remote developer': 'staff-augmentation',
            'offshore development': 'staff-augmentation',
            'nearshore development': 'staff-augmentation',

            # BPO Services
            'bpo': 'bpo',
            'business process outsourcing': 'bpo',
            'outsourcing service': 'bpo',
            'back office': 'bpo',
            'customer support': 'bpo',

            # Professional Training
            'professional technology training services': 'professional-technology-training',
            'professional technology training': 'professional-technology-training',
            'professional training services': 'professional-technology-training',
            'professional training': 'professional-technology-training',
            'technology training services': 'professional-technology-training',
            'technology training': 'professional-technology-training',
            'training services': 'professional-technology-training',
            'professional development': 'professional-technology-training',
            'tech training': 'professional-technology-training',
            'certification program': 'professional-technology-training',
            'training program': 'professional-technology-training',
            'workshop': 'professional-technology-training',
            'educational partnership': 'professional-technology-training'
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
            # Allow text inside formatting tags like strong, em, b, i
            if is_inside_link(text_node) or text_node.parent.name in ['a', 'script', 'style', 'code', 'pre']:
                continue

            text = str(text_node)
            modified = False

            # Determine what to link based on page type
            file_path_str = str(file_path)
            is_service_page = 'services/' in file_path_str
            is_industry_page = 'industries/' in file_path_str
            is_blog_page = 'blogs/' in file_path_str or 'blog/' in file_path_str
            is_case_study_page = 'case_studies/' in file_path_str or 'case-studies/' in file_path_str
            is_news_page = 'news/' in file_path_str

            # Collect all candidate keywords (combine industries and services)
            all_keywords = []

            # Add industry keywords if applicable
            if is_service_page or is_blog_page or is_case_study_page or is_news_page:
                for term, industry_slug in industry_links.items():
                    all_keywords.append((term, 'industry', industry_slug))

            # Add service keywords if applicable
            if is_industry_page or is_blog_page or is_case_study_page or is_news_page:
                for term, service_slug in service_links.items():
                    if service_slug != current_slug:  # Don't link to self
                        all_keywords.append((term, 'service', service_slug))

            # Sort ALL keywords by length (longest first) to match specific phrases before generic ones
            # This ensures "E-Commerce Development Services" matches before just "E-Commerce"
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
                        if link_type == 'industry':
                            replacement = f'<a href="{path_prefix}industries/{slug}.html" class="auto-link">{matched_text}</a>'
                        else:  # service
                            replacement = f'<a href="{path_prefix}services/{slug}.html" class="auto-link">{matched_text}</a>'
                        matches_to_replace.append((match.start(), match.end(), matched_text, replacement, link_type))

            # Apply all replacements from right to left (so positions don't shift)
            if matches_to_replace:
                modified = True
                # Sort by start position (descending) to replace from right to left
                matches_to_replace.sort(key=lambda x: x[0], reverse=True)
                for start, end, matched_text, replacement, link_type in matches_to_replace:
                    text = text[:start] + replacement + text[end:]

            # Replace the text node with new HTML if modified
            if modified:
                # Parse the modified text and extract all children
                new_soup = BeautifulSoup(text, 'html.parser')
                # Get all the parsed elements (could be text and links mixed)
                new_elements = list(new_soup.children)
                if new_elements:
                    # Replace the original text node with the first element
                    first_element = new_elements[0]
                    text_node.replace_with(first_element)
                    # Insert any remaining elements after the first one
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
  <h3>Ready to Transform Your Business?</h3>
  <p>Let's discuss how we can help you achieve your goals with our innovative solutions.</p>
  <a href="{path_prefix}contact.html" class="btn btn-primary">Get Started Today</a>
</div>
''',
            'cta-service': f'''
<div class="inline-cta">
  <h3>Ready to Get Started?</h3>
  <p>Our experts are ready to help you implement these solutions for your business.</p>
  <a href="{path_prefix}contact.html" class="btn btn-primary">Schedule a Consultation</a>
</div>
''',
            'cta-case-study': f'''
<div class="inline-cta">
  <h3>Want Similar Results?</h3>
  <p>Let's discuss how we can deliver transformative solutions for your organization.</p>
  <a href="{path_prefix}contact.html" class="btn btn-primary">Contact Our Team</a>
</div>
''',
            # Location-specific CTAs
            'cta-location-usa': f'''
<div class="inline-cta">
  <h3>Ready to Transform Your Business in the USA?</h3>
  <p>Connect with our US-based team to discuss your requirements and get started.</p>
  <a href="{path_prefix}contact.html" class="btn btn-primary">Get Started in the USA</a>
</div>
''',
            'cta-location-uk': f'''
<div class="inline-cta">
  <h3>Ready to Transform Your Business in the UK?</h3>
  <p>Connect with our UK team to discuss your requirements and get started.</p>
  <a href="{path_prefix}contact.html" class="btn btn-primary">Get Started in the UK</a>
</div>
''',
            'cta-location-canada': f'''
<div class="inline-cta">
  <h3>Ready to Transform Your Business in Canada?</h3>
  <p>Connect with our Canadian team to discuss your requirements and get started.</p>
  <a href="{path_prefix}contact.html" class="btn btn-primary">Get Started in Canada</a>
</div>
''',
            'cta-location-australia': f'''
<div class="inline-cta">
  <h3>Ready to Transform Your Business in Australia?</h3>
  <p>Connect with our Australian team to discuss your requirements and get started.</p>
  <a href="{path_prefix}contact.html" class="btn btn-primary">Get Started in Australia</a>
</div>
'''
        }

        # Find and replace all template directives
        def replace_template(match):
            template_name = match.group(1)

            # Handle city-specific CTAs dynamically
            if template_name.startswith('cta-location-'):
                location = template_name.replace('cta-location-', '')
                # Check if it's a city name
                city_names = {
                    'new-york': 'New York', 'san-francisco': 'San Francisco',
                    'los-angeles': 'Los Angeles', 'chicago': 'Chicago',
                    'austin': 'Austin', 'seattle': 'Seattle',
                    'london': 'London', 'manchester': 'Manchester', 'birmingham': 'Birmingham',
                    'toronto': 'Toronto', 'vancouver': 'Vancouver', 'montreal': 'Montreal',
                    'sydney': 'Sydney', 'melbourne': 'Melbourne', 'brisbane': 'Brisbane'
                }

                if location in city_names:
                    city_display = city_names[location]
                    return f'''
<div class="inline-cta">
  <h3>Ready to Transform Your Business in {city_display}?</h3>
  <p>Connect with our {city_display} team to discuss your requirements and get started.</p>
  <a href="{path_prefix}contact.html" class="btn btn-primary">Get Started in {city_display}</a>
</div>
'''

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

        # Process {{related-industries:industry1,industry2}} directives
        def replace_related_industries(match):
            industries = [i.strip() for i in match.group(1).split(',')]
            html = '<div class="related-industries-inline">\n<h3>Industries We Serve</h3>\n<div class="related-industries-grid">\n'
            for industry in industries:
                html += f'  <a href="{path_prefix}industries/{industry}.html" class="related-industry-link">\n'
                html += f'    <span class="link-icon">→</span>\n'
                html += f'    <span>{industry.replace("-", " ").title()}</span>\n'
                html += f'  </a>\n'
            html += '</div>\n</div>'
            return html

        content = re.sub(r'\{\{related-industries:([^}]+)\}\}', replace_related_industries, content)

        # Process {{industry-challenges:challenge1,challenge2}} directives
        def replace_industry_challenges(match):
            challenges = [c.strip() for c in match.group(1).split('|')]
            html = '<div class="industry-challenges">\n<h3>Key Challenges We Address</h3>\n<div class="challenges-grid">\n'
            for challenge in challenges:
                html += f'  <div class="challenge-item">\n'
                html += f'    <svg class="challenge-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">\n'
                html += f'      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>\n'
                html += f'    </svg>\n'
                html += f'    <p>{challenge}</p>\n'
                html += f'  </div>\n'
            html += '</div>\n</div>'
            return html

        content = re.sub(r'\{\{industry-challenges:([^}]+)\}\}', replace_industry_challenges, content)

        # Process {{industry-solutions:solution1|description1,solution2|description2}} directives
        def replace_industry_solutions(match):
            solutions = [s.strip() for s in match.group(1).split(',')]
            html = '<div class="industry-solutions">\n<h3>Our Solutions</h3>\n<div class="solutions-grid">\n'
            for solution in solutions:
                if '|' in solution:
                    title, desc = solution.split('|', 1)
                else:
                    title, desc = solution, ''
                html += f'  <div class="solution-card">\n'
                html += f'    <h4>{title.strip()}</h4>\n'
                if desc:
                    html += f'    <p>{desc.strip()}</p>\n'
                html += f'  </div>\n'
            html += '</div>\n</div>'
            return html

        content = re.sub(r'\{\{industry-solutions:([^}]+)\}\}', replace_industry_solutions, content)

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
  <h3>Ready to Transform Your Business?</h3>
  <p>Let's discuss how we can help you achieve your goals with our innovative solutions.</p>
  <a href="../contact.html" class="btn btn-primary">Get Started Today</a>
</div>''',
                'cta-service': '''<div class="inline-cta">
  <h3>Ready to Get Started?</h3>
  <p>Our experts are ready to help you implement these solutions for your business.</p>
  <a href="../contact.html" class="btn btn-primary">Schedule a Consultation</a>
</div>''',
                'cta-case-study': '''<div class="inline-cta">
  <h3>Want Similar Results?</h3>
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