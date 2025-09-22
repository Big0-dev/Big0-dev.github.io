#!/usr/bin/env python3
"""
Static Site Generator
Generates website from templates and content files based on site_config.yaml
"""

import yaml
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import logging
import os
from datetime import datetime
from typing import Dict, Any, List
import markdown
from bs4 import BeautifulSoup
import minify_html
import rcssmin
import jsmin
from functools import lru_cache

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class SiteGenerator:
    """Static site generator using config and templates"""
    
    def __init__(self, config_file="site_config.yaml"):
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.output_dir = self.config['assets']['output_dir']
        self.static_dir = self.config['assets']['static_dir']
        self.templates_dir = "./templates"
        
        # Setup Jinja2
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(enabled_extensions=("html",)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Add custom functions
        self.env.globals['inject_svg'] = self._inject_svg
        
        # Add custom filters
        self.env.filters['xmlescape'] = self._xml_escape_filter
        
    def generate(self):
        """Generate the entire website"""
        logger.info("Starting website generation...")
        
        # Clean and prepare
        self._clean_output()
        
        # Copy assets
        self._copy_assets()
        
        # Generate pages
        self._generate_static_pages()
        self._generate_gallery_pages()
        self._generate_content_pages()
        
        # Generate sitemaps (includes location pages)
        self._generate_sitemaps()
        
        # Generate search index
        self._generate_search_index()
        
        # Post-generation optimization
        # Temporarily disabled to preserve cookie consent scripts
        # self._optimize_output()
        
        logger.info("Website generation complete!")
        
    def _clean_output(self):
        """Clean and recreate output directory"""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
            
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create all subdirectories at once
        dirs_to_create = [
            os.path.join(self.output_dir, "static"),
            os.path.join(self.output_dir, "content/gallery")
        ]
        
        for content_type in self.config['content_types'].values():
            dirs_to_create.append(os.path.join(self.output_dir, content_type['output_dir']))
        
        for dir_path in dirs_to_create:
            os.makedirs(dir_path, exist_ok=True)
        
    def _copy_assets(self):
        """Copy all assets according to config"""
        # Copy static assets (excluding SVGs and favicon files)
        if os.path.exists(self.static_dir):
            dest_static = os.path.join(self.output_dir, "static")
            
            for item in os.listdir(self.static_dir):
                if item.endswith('.svg') or item.startswith('favicon'):
                    continue
                    
                src = os.path.join(self.static_dir, item)
                dest = os.path.join(dest_static, item)
                
                if os.path.isfile(src):
                    shutil.copy2(src, dest)
                elif os.path.isdir(src):
                    shutil.copytree(src, dest)
                    
        # Copy gallery images
        gallery_dir = self.config['assets']['gallery_dir']
        if os.path.exists(gallery_dir):
            dest_gallery = os.path.join(self.output_dir, "content", "gallery")
            
            for item in os.listdir(gallery_dir):
                if item.endswith(('.avif', '.jpg', '.jpeg', '.png', '.webp', '.json')):
                    src = os.path.join(gallery_dir, item)
                    dest = os.path.join(dest_gallery, item)
                    shutil.copy2(src, dest)
                    
        # Copy root assets
        for asset in self.config['assets']['root_assets']:
            src = Path(asset)
            if src.exists():
                dest = Path(self.output_dir) / asset
                shutil.copy2(src, dest)
                
        # Copy favicon files to build root
        favicon_files = ['favicon.ico', 'favicon.png']
        for favicon in favicon_files:
            src = Path(self.static_dir) / favicon
            if src.exists():
                dest = Path(self.output_dir) / favicon
                shutil.copy2(src, dest)
                
    def _inject_svg(self, filename: str, wrap: bool = False, css_class: str = "") -> str:
        """Inject SVG content directly into HTML with caching"""
        # Use instance cache for SVG content
        if not hasattr(self, '_svg_cache'):
            self._svg_cache = {}
            
        cache_key = f"{filename}_{wrap}_{css_class}"
        
        # Return cached content if available
        if cache_key in self._svg_cache:
            return self._svg_cache[cache_key]
            
        svg_path = Path(self.static_dir) / f"{filename}.svg"
        
        if not svg_path.exists():
            return f"<!-- SVG {filename} not found -->"
            
        try:
            svg_content = svg_path.read_text(encoding='utf-8')
            
            if css_class:
                svg_content = svg_content.replace('<svg', f'<svg class="{css_class}"', 1)
                
            if wrap:
                result = f'<span class="svg-wrapper">{svg_content}</span>'
            else:
                result = svg_content
                
            # Cache the result
            self._svg_cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"Error injecting SVG {filename}: {e}")
            return f"<!-- Error loading SVG {filename} -->"
            
    def _get_base_context(self, depth: int = 0) -> Dict[str, Any]:
        """Get base context for all templates"""
        # Calculate relative path prefix based on depth
        path_prefix = '../' * depth if depth > 0 else ''
        
        context = {
            'static': f'{path_prefix}static',
            'domain': self.config['domain'],
            'copyright': datetime.now().year,
            'path_prefix': path_prefix,
            'image_sitemap': f'{path_prefix}sitemap-images.xml',
        }
        
        # Add navigation URLs with proper paths
        for key, value in self.config['navigation'].items():
            context[key] = f'{path_prefix}{value}'
        
        return context
        
    def _load_gallery_data(self) -> Dict[str, Any]:
        """Load gallery images and metadata"""
        gallery_dir = Path(self.config['assets']['gallery_dir'])
        metadata_file = gallery_dir / 'metadata.json'
        
        images = []
        gallery_url = 'content/gallery'
        
        if metadata_file.exists():
            import json
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Get all image files
            for image_file in sorted(gallery_dir.glob('*.avif')):
                # Try to find metadata - check both with and without year variations
                meta_key = image_file.name
                if meta_key not in metadata:
                    # Try with 2025 instead of 25
                    alt_key = meta_key.replace('-25-', '-2025-')
                    if alt_key in metadata:
                        meta_key = alt_key
                
                if meta_key in metadata:
                    image_data = metadata[meta_key].copy()
                    image_data['filename'] = image_file.name
                    # Parse date if present
                    if 'date' in image_data:
                        from datetime import datetime
                        image_data['date'] = datetime.strptime(image_data['date'], '%Y-%m-%d')
                    images.append(image_data)
                else:
                    # Add image even without metadata
                    images.append({
                        'filename': image_file.name,
                        'title': image_file.stem.replace('-', ' ').title(),
                        'category': 'Gallery'
                    })
        
        return {
            'images': images,
            'gallery_url': gallery_url
        }
        
    def _generate_static_pages(self):
        """Generate static pages from templates"""
        context = self._get_base_context()
        
        # Pre-load templates for better performance
        templates_cache = {}
        
        for page in self.config['static_pages']:
            try:
                # Use cached template if available
                if page['template'] not in templates_cache:
                    templates_cache[page['template']] = self.env.get_template(page['template'])
                template = templates_cache[page['template']]
                output_path = Path(self.output_dir) / page['output']
                
                # Special handling for different pages
                page_context = context.copy()
                
                # Special handling for 404 page - use absolute paths
                if page['template'] == '404.html':
                    # Override static paths to use absolute URLs for 404 page
                    page_context['static'] = '/static'
                    # Override navigation URLs to use absolute paths
                    for key, value in self.config['navigation'].items():
                        page_context[key] = f'/{value}'
                    page_context['path_prefix'] = '/'
                    page_context['image_sitemap'] = '/sitemap-images.xml'
                elif page['template'] == 'gallery.html':
                    # Skip generating the base gallery.html here, it will be handled with pagination
                    continue
                elif page['template'] == 'index.html':
                    # Load all content for homepage
                    for content_type, config in self.config['content_types'].items():
                        content_dir = Path(config['content_dir'])
                        if content_dir.exists():
                            items = []
                            for file_path in content_dir.glob('*.md'):
                                item = self._load_markdown_content(file_path)
                                items.append(item)
                            # Sort by date if available
                            items.sort(key=lambda x: x.get('date') or datetime.min, reverse=True)
                            page_context[f'all_{content_type}'] = items
                    
                    # Also load news articles
                    news_dir = Path('content/news')
                    if news_dir.exists():
                        news_articles = []
                        for file_path in news_dir.glob('*.md'):
                            article = self._load_markdown_content(file_path)
                            news_articles.append(article)
                        news_articles.sort(key=lambda x: x.get('date') or datetime.min, reverse=True)
                        page_context['news_articles'] = news_articles
                
                html_content = template.render(**page_context)
                output_path.write_text(html_content)
                
                logger.info(f"Generated: {page['output']}")
            except Exception as e:
                logger.error(f"Error generating {page['template']}: {e}")
    
    def _generate_gallery_pages(self):
        """Generate gallery pages with pagination"""
        try:
            gallery_data = self._load_gallery_data()
            images = gallery_data.get('images', [])
            gallery_url = gallery_data.get('gallery_url')
            
            # Pagination settings
            per_page = 6
            total_images = len(images)
            total_pages = (total_images + per_page - 1) // per_page if total_images > 0 else 1
            
            template = self.env.get_template('gallery.html')
            
            for page_num in range(1, total_pages + 1):
                # Get images for this page
                start_idx = (page_num - 1) * per_page
                end_idx = start_idx + per_page
                page_images = images[start_idx:end_idx]
                
                # Determine output path
                if page_num == 1:
                    output_path = Path(self.output_dir) / 'gallery.html'
                else:
                    output_path = Path(self.output_dir) / f'gallery-{page_num}.html'
                
                # Create context
                context = self._get_base_context()
                context.update({
                    'images': page_images,
                    'gallery_url': gallery_url,
                    'page_num': page_num,
                    'total_pages': total_pages,
                    'per_page': per_page,
                })
                
                html_content = template.render(**context)
                output_path.write_text(html_content)
                
                logger.info(f"Generated: gallery{'' if page_num == 1 else f'-{page_num}'}.html")
                
        except Exception as e:
            logger.error(f"Error generating gallery pages: {e}")
                
    @lru_cache(maxsize=128)
    def _parse_date(self, date_value):
        """Parse date from various formats with caching"""
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
    
    def _add_automatic_interlinking(self, html_content: str, file_path: Path) -> str:
        """Add automatic links to industry and service mentions in the content"""
        import re
        from bs4 import BeautifulSoup, NavigableString
        
        # Calculate the relative path prefix based on file depth
        # file_path is like "services/locations/usa/ai-integration-usa.html"
        depth = len(file_path.parts) - 1 if file_path.parts else 0
        path_prefix = "../" * depth
        
        # Define industry mappings
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
            'sustainability': 'energy'
        }
        
        # Define service mappings (comprehensive keyword dictionary)
        service_links = {
            # AI & Machine Learning
            'ai integration': 'ai-integration',
            'artificial intelligence': 'ai-integration',
            'machine learning': 'ai-integration',
            'deep learning': 'ai-integration',
            'neural network': 'ai-integration',
            'ai model': 'ai-integration',
            'ml model': 'ai-integration',
            'predictive analytics': 'ai-integration',
            'ai solution': 'ai-integration',
            
            # Computer Vision
            'computer vision': 'computer_vision_service',
            'computer vision applications': 'computer_vision_service',
            'computer vision services': 'computer_vision_service',
            'image recognition': 'computer_vision_service',
            'image recognition systems': 'computer_vision_service',
            'object detection': 'computer_vision_service',
            'facial recognition': 'computer_vision_service',
            'image processing': 'computer_vision_service',
            'visual data': 'computer_vision_service',
            'opencv': 'computer_vision_service',
            
            # Natural Language Processing
            'natural language processing': 'natural_language_processing',
            'nlp': 'natural_language_processing',
            'text analysis': 'natural_language_processing',
            'sentiment analysis': 'natural_language_processing',
            'chatbot': 'natural_language_processing',
            'language model': 'natural_language_processing',
            
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
            
            # Hardware & CAD
            'cad': 'hardware_cad',
            'cad model': 'hardware_cad',
            'hardware design': 'hardware_cad',
            'mechanical design': 'hardware_cad',
            '3d modeling': 'hardware_cad',
            '3d design': 'hardware_cad',
            '3d scanning': 'hardware_cad',
            '3d ear scanning': 'hardware_cad',
            'ergonomic design': 'hardware_cad',
            'ergonomic 3d design': 'hardware_cad',
            'product design': 'hardware_cad',
            'industrial design': 'hardware_cad',
            'mechanical construction': 'hardware_cad',
            'modular construction': 'hardware_cad',
            'modular mechanical design': 'hardware_cad',
            'precision mechanical design': 'hardware_cad',
            '3-axis gimbal': 'hardware_cad',
            'gimbal': 'hardware_cad',
            'biomechanical': 'hardware_cad',
            'solidworks': 'hardware_cad',
            'autocad': 'hardware_cad',
            'fusion 360': 'hardware_cad',
            'carbon fiber': 'hardware_cad',
            'carbon fiber construction': 'hardware_cad',
            'prototype': 'hardware_cad',
            'prototyping': 'hardware_cad',
            'wheelbase': 'hardware_cad',
            'modular design': 'hardware_cad',
            
            # Embedded Systems
            'embedded system': 'embedded_systems_development',
            'embedded software': 'embedded_systems_development',
            'embedded': 'embedded_systems_development',
            'arduino': 'embedded_systems_development',
            'Arduino': 'embedded_systems_development',
            'raspberry pi': 'embedded_systems_development',
            'microcontroller': 'embedded_systems_development',
            'firmware': 'embedded_systems_development',
            'px4': 'embedded_systems_development',
            'PX4': 'embedded_systems_development',
            'px4 autopilot': 'embedded_systems_development',
            'PX4 Autopilot': 'embedded_systems_development',
            'flight controller': 'embedded_systems_development',
            'dji n3': 'embedded_systems_development',
            'DJI N3': 'embedded_systems_development',
            'stm32': 'embedded_systems_development',
            'STM32': 'embedded_systems_development',
            'esp32': 'embedded_systems_development',
            'ESP32': 'embedded_systems_development',
            'bldc': 'embedded_systems_development',
            'BLDC': 'embedded_systems_development',
            'bldc motor': 'embedded_systems_development',
            'BLDC motor': 'embedded_systems_development',
            'motor control': 'embedded_systems_development',
            'autopilot': 'embedded_systems_development',
            
            # IoT Development
            'iot': 'iot_device_development',
            'internet of things': 'iot_device_development',
            'iot device': 'iot_device_development',
            'smart device': 'iot_device_development',
            'sensor': 'iot_device_development',
            'sensing layer': 'iot_device_development',
            'environmental sensor': 'iot_device_development',
            'smart meter': 'iot_device_development',
            'drone': 'iot_device_development',
            'octocopter': 'iot_device_development',
            'uav': 'iot_device_development',
            'spray system': 'iot_device_development',
            'precision spraying': 'iot_device_development',
            'agricultural drone': 'iot_device_development',
            'sprayer drone': 'iot_device_development',
            'telemetry': 'iot_device_development',
            'mqtt': 'iot_device_development',
            'lorawan': 'iot_device_development',
            'edge computing': 'iot_device_development',
            'smart city': 'iot_device_development',
            'smart cities': 'iot_device_development',
            
            # PCB Design
            'pcb': 'pcb_design_and_layout',
            'circuit board': 'pcb_design_and_layout',
            'circuit design': 'pcb_design_and_layout',
            'electronics design': 'pcb_design_and_layout',
            'altium': 'pcb_design_and_layout',
            'eagle': 'pcb_design_and_layout',
            'kicad': 'pcb_design_and_layout',
            
            # Cloud & DevOps
            'cloud service': 'cloud-managment',
            'cloud management': 'cloud-managment',
            'cloud solution': 'cloud-managment',
            'aws': 'cloud-managment',
            'azure': 'cloud-managment',
            'google cloud': 'cloud-managment',
            'gcp': 'cloud-managment',
            'cloud infrastructure': 'cloud-managment',
            '5g network': 'cloud-managment',
            '5g': 'cloud-managment',
            'cloud platform': 'cloud-managment',
            
            # DevOps
            'devops': 'devops_consulting',
            'ci/cd': 'devops_consulting',
            'docker': 'devops_consulting',
            'kubernetes': 'devops_consulting',
            'jenkins': 'devops_consulting',
            'terraform': 'devops_consulting',
            'ansible': 'devops_consulting',
            'infrastructure as code': 'devops_consulting',
            
            # Database & Analytics
            'data analytics': 'data-analytics',
            'data analysis': 'data-analytics',
            'business intelligence': 'data-analytics',
            'bi solution': 'data-analytics',
            'data visualization': 'data-analytics',
            'big data': 'data-analytics',
            'data science': 'data-analytics',
            'sql': 'data-analytics',
            'database': 'data-analytics',
            'data warehouse': 'data-analytics',
            'real-time analytics': 'data-analytics',
            'predictive modeling': 'data-analytics',
            'data processing': 'data-analytics',
            
            # Dashboard Development
            'dashboard': 'dashboards',
            'analytics dashboard': 'dashboards',
            'reporting dashboard': 'dashboards',
            'real-time dashboard': 'dashboards',
            'kpi dashboard': 'dashboards',
            'management dashboard': 'dashboards',
            'city management dashboard': 'dashboards',
            'tableau': 'dashboards',
            'power bi': 'dashboards',
            'digital twin': 'dashboards',
            
            # Python Automation
            'python': 'python-automation',
            'python script': 'python-automation',
            'automation': 'python-automation',
            'web scraping': 'python-automation',
            'pandas': 'python-automation',
            'numpy': 'python-automation',
            
            # UI/UX Design
            'ui design': 'ui_ux_design_services',
            'ux design': 'ui_ux_design_services',
            'ui/ux': 'ui_ux_design_services',
            'user interface': 'ui_ux_design_services',
            'user experience': 'ui_ux_design_services',
            'figma': 'ui_ux_design_services',
            'sketch': 'ui_ux_design_services',
            'adobe xd': 'ui_ux_design_services',
            'wireframe': 'ui_ux_design_services',
            'mockup': 'ui_ux_design_services',
            
            # Brand & Digital Design
            'brand design': 'brand_and_digital_design',
            'branding': 'brand_and_digital_design',
            'logo design': 'brand_and_digital_design',
            'graphic design': 'brand_and_digital_design',
            'visual identity': 'brand_and_digital_design',
            'brand identity': 'brand_and_digital_design',
            
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
            
            # Software Testing
            'software testing': 'software_testing',
            'qa testing': 'software_testing',
            'quality assurance': 'software_testing',
            'test automation': 'software_testing',
            'selenium': 'software_testing',
            'unit testing': 'software_testing',
            'integration testing': 'software_testing',
            'performance testing': 'software_testing',
            
            # Cybersecurity
            'cybersecurity': 'cybersecurity-solutions',
            'security solution': 'cybersecurity-solutions',
            'penetration testing': 'cybersecurity-solutions',
            'security audit': 'cybersecurity-solutions',
            'vulnerability assessment': 'cybersecurity-solutions',
            'data security': 'cybersecurity-solutions',
            
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
            'training': 'professional-technology-training',
            'professional development': 'professional-technology-training',
            'tech training': 'professional-technology-training',
            'certification': 'professional-technology-training',
            'workshop': 'professional-technology-training'
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
            is_service_page = 'services/' in str(file_path)
            is_industry_page = 'industries/' in str(file_path)
            is_blog_page = 'blogs/' in str(file_path)
            is_case_study_page = 'case_studies/' in str(file_path)
            is_news_page = 'news/' in str(file_path)
            
            # Check for industry mentions
            # Link on service pages, blog pages, case study pages, and news pages
            if is_service_page or is_blog_page or is_case_study_page or is_news_page:
                for term, industry_slug in industry_links.items():
                    # Case-insensitive search with word boundaries
                    pattern = r'\b(' + re.escape(term) + r')\b'
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        # Replace with link (preserving original case)
                        matched_text = match.group(1)
                        replacement = f'<a href="{path_prefix}industries/{industry_slug}.html" class="auto-link">{matched_text}</a>'
                        text = text[:match.start()] + replacement + text[match.end():]
                        modified = True
                        break  # Only link one term per text node
            
            # Check for service mentions
            # Link on industry pages, blog pages, case study pages, and news pages
            if is_industry_page or is_blog_page or is_case_study_page or is_news_page:
                if not modified:  # Only check if we haven't already modified the text
                    for term, service_slug in service_links.items():
                        if service_slug != current_slug:  # Don't link to self
                            pattern = r'\b(' + re.escape(term) + r')\b'
                            match = re.search(pattern, text, re.IGNORECASE)
                            if match:
                                # Replace with link (preserving original case)
                                matched_text = match.group(1)
                                replacement = f'<a href="{path_prefix}services/{service_slug}.html" class="auto-link">{matched_text}</a>'
                                text = text[:match.start()] + replacement + text[match.end():]
                                modified = True
                                break
            
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
    
    def _process_template_directives(self, content: str, file_path: Path = None) -> str:
        """Process template directives like {{template:cta}} in markdown content"""
        import re
        
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
    
    def _process_faq_sections(self, html_content: str) -> str:
        """Convert FAQ sections to interactive accordion format"""
        from bs4 import BeautifulSoup
        
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
                    import json
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
    
    def _process_template_directives_in_html(self, html_content: str) -> str:
        """Process template directives that may be wrapped in HTML tags"""
        import re
        
        # First process FAQ sections
        html_content = self._process_faq_sections(html_content)
        
        # Then process any directives that are already in the markdown
        html_content = self._process_template_directives(html_content)
        
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
    
    def _load_markdown_content(self, file_path: Path, output_path: Path = None) -> Dict[str, Any]:
        """Load and parse markdown content"""
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
            
        # Process template directives before converting to HTML
        # Use output_path if provided for correct depth calculation, otherwise use file_path
        template_path = output_path if output_path else file_path
        markdown_content = self._process_template_directives(markdown_content, template_path)
        
        # Convert markdown to HTML - reuse single markdown instance for performance
        if not hasattr(self, '_md_converter'):
            self._md_converter = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
        else:
            self._md_converter.reset()
        html_content = self._md_converter.convert(markdown_content)
        
        # Also process any remaining directives that might have been wrapped in HTML tags
        html_content = self._process_template_directives_in_html(html_content)
        
        # Auto-link industry and service mentions (for service, industry, blog, case study, and news pages)
        # Use output_path if provided (for correct depth calculation), otherwise use file_path
        link_path = output_path if output_path else file_path
        if any(path in str(file_path) for path in ['services/', 'industries/', 'blogs/', 'case_studies/', 'news/']):
            html_content = self._add_automatic_interlinking(html_content, link_path)
        
        # Extract first paragraph as excerpt
        soup = BeautifulSoup(html_content, 'html.parser')
        first_p = soup.find('p')
        excerpt = first_p.text if first_p else ""
        
        # Parse features if they exist
        features = frontmatter.get('features', '')
        if isinstance(features, str):
            features = [f.strip() for f in features.split(',') if f.strip()]
        
        # Create short description from description or excerpt
        short_description = frontmatter.get('description', '')
        if not short_description and excerpt:
            short_description = excerpt[:160] + '...' if len(excerpt) > 160 else excerpt
        
        return {
            'slug': file_path.stem,
            'title': frontmatter.get('title', 'Untitled'),
            'meta_description': frontmatter.get('meta_description', excerpt[:160]),
            'short_description': short_description,
            'content_html': html_content,
            'frontmatter': frontmatter,
            'icon': frontmatter.get('icon', ''),
            'price': frontmatter.get('price', ''),
            'features': features,
            'excerpt': frontmatter.get('description', excerpt[:200] + '...' if len(excerpt) > 200 else excerpt),
            'category': frontmatter.get('category', 'General'),
            'date': self._parse_date(frontmatter.get('date')),
            'tags': frontmatter.get('tags', '').split(',') if frontmatter.get('tags') else [],
            'external_link': frontmatter.get('external_link', ''),
        }
        
    def _generate_content_pages(self):
        """Generate pages from content files"""
        context = self._get_base_context()
        
        for content_type, config in self.config['content_types'].items():
            content_dir = Path(config['content_dir'])
            if not content_dir.exists():
                continue
                
            # Load all content - use sorted for consistent ordering
            items = []
            for file_path in sorted(content_dir.glob('*.md')):
                # Calculate the output path for correct link depth
                output_path = Path(config['output_dir']) / f"{file_path.stem}.html"
                item = self._load_markdown_content(file_path, output_path)
                # Skip location pages from main listing
                if not item.get('frontmatter', {}).get('is_location_page', False):
                    items.append(item)
            
            # Generate location pages for services
            if content_type == 'services':
                self._generate_location_pages(content_dir, config)
            
            # Generate detail pages for all items
            if 'template' in config:
                for item in items:
                    try:
                        template = self.env.get_template(config['template'])
                        output_path = Path(self.output_dir) / config['output_dir'] / f"{item['slug']}.html"
                        
                        # Get context with depth 1 for subdirectory pages
                        # Map content_type to singular form
                        singular_map = {
                            'services': 'service',
                            'industries': 'industry', 
                            'blog': 'blog',
                            'case_studies': 'case_studie'
                        }
                        singular = singular_map.get(content_type, content_type[:-1])
                        # Get base context
                        base_context = self._get_base_context(depth=1)
                        
                        # Create item context, ensuring navigation URLs are preserved
                        item_context = {
                            **base_context,
                            'item': item, 
                            f'current_{singular}': item
                        }
                        
                        # Add related items for news
                        if content_type == 'news':
                            # Get other news items excluding current
                            related_news = [n for n in items if n['slug'] != item['slug']]
                            # Sort by date and take first 3
                            related_news.sort(key=lambda x: x.get('date') or datetime.min, reverse=True)
                            item_context['related_news'] = related_news[:3]
                        
                        html_content = template.render(**item_context)
                        output_path.write_text(html_content)
                        
                        logger.info(f"Generated: {content_type}/{item['slug']}.html")
                    except Exception as e:
                        logger.error(f"Error generating {content_type} detail: {e}")
                        
            # Generate listing pages
            if 'listing_template' in config and items:
                try:
                    template = self.env.get_template(config['listing_template'])
                    per_page = config.get('per_page', len(items))
                    
                    # Paginate if needed
                    for page_num, i in enumerate(range(0, len(items), per_page), 1):
                        page_items = items[i:i + per_page]
                        total_pages = (len(items) + per_page - 1) // per_page
                        
                        output_name = f"{content_type.replace('_', '-')}.html" if page_num == 1 else f"{content_type.replace('_', '-')}-{page_num}.html"
                        output_path = Path(self.output_dir) / output_name
                        
                        # Get base context first
                        base_context = self._get_base_context()
                        
                        list_context = {
                            **base_context,
                            'items': page_items,
                            f'all_{content_type}': page_items,  # Use all_ prefix to avoid conflicts
                            'page_num': page_num,
                            'total_pages': total_pages,
                            'per_page': per_page,
                        }
                        
                        # Special handling for news template
                        if content_type == 'news':
                            list_context['news_articles'] = page_items
                        
                        html_content = template.render(**list_context)
                        output_path.write_text(html_content)
                        
                        logger.info(f"Generated: {output_name}")
                except Exception as e:
                    logger.error(f"Error generating {content_type} listing: {e}")
    
    def _generate_location_pages(self, content_dir: Path, config: dict):
        """Generate location-specific versions of service pages"""
        # Dynamically discover locations from directory structure
        locations_dir = content_dir / 'locations'
        locations = {}
        
        if locations_dir.exists():
            for location_dir in locations_dir.iterdir():
                if location_dir.is_dir():
                    location_name = location_dir.name
                    # Convert directory name to proper display name
                    display_name = location_name.replace('-', ' ').title()
                    
                    # Special cases for country names
                    name_mappings = {
                        'usa': 'USA',
                        'uk': 'UK',
                        'uae': 'UAE'
                    }
                    
                    display_name = name_mappings.get(location_name, display_name)
                    
                    locations[location_name] = {
                        'name': display_name,
                        'full_name': display_name if display_name != 'USA' else 'United States',
                        'slug': location_name,
                        'meta_suffix': f'in {display_name}' if display_name != 'USA' else 'in the USA',
                        'content_suffix': f'across {display_name}' if display_name != 'USA' else 'across the United States',
                        'type': 'country'
                    }
        
        # Dynamically discover cities from directory structure
        cities = {}
        for country_name, country_data in locations.items():
            cities[country_name] = {}
            country_cities_dir = locations_dir / country_name / 'cities'
            
            if country_cities_dir.exists():
                for city_dir in country_cities_dir.iterdir():
                    if city_dir.is_dir():
                        city_name = city_dir.name
                        # Convert directory name to proper display name
                        display_name = city_name.replace('-', ' ').title()
                        
                        cities[country_name][city_name] = {
                            'name': display_name,
                            'full_name': display_name,
                            'slug': city_name,
                            'meta_suffix': f'in {display_name}',
                            'content_suffix': f'in {display_name}',
                            'parent_country': country_name,
                            'type': 'city'
                        }
        
        # No services are skipped from location pages anymore
        
        locations_dir = content_dir / 'locations'
        
        # Process each service file
        for service_file in sorted(content_dir.glob('*.md')):
            
            # Load the service content
            service_item = self._load_markdown_content(service_file)
            
            # Skip if already a location page
            if service_item.get('frontmatter', {}).get('is_location_page'):
                continue
                
            # Generate country pages
            for location_key, location in locations.items():
                location_dir = locations_dir / location_key
                
                # Check if location-specific markdown exists (exact match)
                location_md_path = location_dir / f"{service_file.stem}-{location_key}.md"
                
                if location_md_path.exists():
                    # Load and generate the location page with correct output path for auto-linking
                    output_path = Path(f"services/locations/{location_key}/{service_file.stem}-{location_key}.html")
                    location_item = self._load_markdown_content(location_md_path, output_path)
                    
                    # Fix hardcoded service links in content (e.g., href="computer_vision_service.html")
                    # These should point to ../../../services/computer_vision_service.html
                    import re
                    def fix_service_link(match):
                        service_name = match.group(1)
                        return f'href="../../../services/{service_name}.html"'
                    
                    # Fix links that are relative to current directory (no path prefix)
                    location_item['content_html'] = re.sub(
                        r'href="([a-zA-Z_\-]+)\.html"',
                        fix_service_link,
                        location_item['content_html']
                    )
                    
                    # Generate the HTML page
                    try:
                        template = self.env.get_template(config.get('template', 'service_detail.html'))
                        
                        # Create output directory
                        output_dir = Path(self.output_dir) / 'services' / 'locations' / location_key
                        output_dir.mkdir(parents=True, exist_ok=True)
                        
                        output_path = output_dir / f"{service_file.stem}-{location_key}.html"
                        
                        # Get context with appropriate depth for nested directory
                        base_context = self._get_base_context(depth=3)
                        
                        location_context = {
                            **base_context,
                            'current_service': location_item,
                            'item': location_item
                        }
                        
                        html_content = template.render(**location_context)
                        output_path.write_text(html_content)
                        
                        logger.info(f"Generated location page: {output_path.relative_to(self.output_dir)}")
                        
                    except Exception as e:
                        logger.error(f"Error generating location page {location_md_path}: {e}")
            
            # Generate city pages
            for country_key, country_cities in cities.items():
                for city_key, city in country_cities.items():
                    city_dir = locations_dir / country_key / 'cities' / city_key
                    
                    # Check if city-specific markdown exists
                    city_md_path = city_dir / f"{service_file.stem}-{city_key}.md"
                    
                    if city_md_path.exists():
                        # Load and generate the city page with correct output path for auto-linking
                        output_path = Path(f"services/locations/{country_key}/cities/{city_key}/{service_file.stem}-{city_key}.html")
                        city_item = self._load_markdown_content(city_md_path, output_path)
                        
                        # Fix hardcoded service links in content
                        def fix_city_service_link(match):
                            service_name = match.group(1)
                            return f'href="../../../../../services/{service_name}.html"'
                        
                        city_item['content_html'] = re.sub(
                            r'href="([a-zA-Z_\-]+)\.html"',
                            fix_city_service_link,
                            city_item['content_html']
                        )
                        
                        # Generate the HTML page
                        try:
                            template = self.env.get_template(config.get('template', 'service_detail.html'))
                            
                            # Create output directory for city
                            output_dir = Path(self.output_dir) / 'services' / 'locations' / country_key / 'cities' / city_key
                            output_dir.mkdir(parents=True, exist_ok=True)
                            
                            output_path = output_dir / f"{service_file.stem}-{city_key}.html"
                            
                            # Get context with appropriate depth for deeply nested directory
                            base_context = self._get_base_context(depth=5)
                            
                            city_context = {
                                **base_context,
                                'current_service': city_item,
                                'item': city_item
                            }
                            
                            html_content = template.render(**city_context)
                            output_path.write_text(html_content)
                            
                            logger.info(f"Generated city page: {output_path.relative_to(self.output_dir)}")
                            
                        except Exception as e:
                            logger.error(f"Error generating city page {city_md_path}: {e}")
        
        # Process ALL remaining markdown files in location directories that don't match service patterns
        # This handles files like engineering-consultancy-pakistan.md that don't follow the service-location pattern
        services_dir = content_dir  # Define services_dir for checking existing services
        for location_key in locations:
            location_dir = locations_dir / location_key
            if location_dir.exists():
                # Process all .md files in this location directory
                for md_file in location_dir.glob('*.md'):
                    # Skip if already processed (matches service-location pattern)
                    if any(md_file.stem == f"{service.stem}-{location_key}" 
                           for service in services_dir.glob('*.md')):
                        continue
                    
                    # Generate this standalone location page
                    try:
                        output_path = Path(f"services/locations/{location_key}/{md_file.stem}.html")
                        location_item = self._load_markdown_content(md_file, output_path)
                        
                        # Fix service links to point to correct relative path
                        import re
                        def fix_service_link(match):
                            service_name = match.group(1)
                            return f'href="../../../services/{service_name}.html"'
                        
                        location_item['content_html'] = re.sub(
                            r'href="([a-zA-Z_\-]+)\.html"',
                            fix_service_link,
                            location_item['content_html']
                        )
                        
                        # Generate the HTML page
                        template = self.env.get_template('service_detail.html')
                        
                        # Create output directory
                        output_dir = Path(self.output_dir) / 'services' / 'locations' / location_key
                        output_dir.mkdir(parents=True, exist_ok=True)
                        
                        output_path = output_dir / f"{md_file.stem}.html"
                        
                        # Get context with appropriate depth for nested directory
                        base_context = self._get_base_context(depth=3)
                        
                        location_context = {
                            **base_context,
                            'current_service': location_item,
                            'item': location_item
                        }
                        
                        html_content = template.render(**location_context)
                        output_path.write_text(html_content)
                        
                        logger.info(f"Generated standalone location page: {output_path.relative_to(self.output_dir)}")
                        
                    except Exception as e:
                        logger.error(f"Error generating standalone location page {md_file}: {e}")
                    
    def _generate_sitemaps(self):
        """Generate XML sitemaps"""
        # Simple sitemap generation
        sitemap_path = Path(self.output_dir) / "sitemap.xml"
        
        urls = []
        
        # Add static pages
        for page in self.config['static_pages']:
            urls.append(f"{self.config['domain']}/{page['output']}")
            
        # Add content pages
        for content_type, config in self.config['content_types'].items():
            content_dir = Path(config['content_dir'])
            if content_dir.exists():
                for file_path in content_dir.glob('*.md'):
                    slug = file_path.stem
                    urls.append(f"{self.config['domain']}/{config['output_dir']}/{slug}.html")
                
                # Add location pages for services
                if content_type == 'services':
                    locations_dir = content_dir / 'locations'
                    if locations_dir.exists():
                        # Add country-level location pages
                        for location_dir in locations_dir.iterdir():
                            if location_dir.is_dir():
                                # Country pages
                                for location_file in location_dir.glob('*.md'):
                                    location_slug = location_file.stem
                                    location_key = location_dir.name
                                    urls.append(f"{self.config['domain']}/services/locations/{location_key}/{location_slug}.html")
                                
                                # City pages
                                cities_dir = location_dir / 'cities'
                                if cities_dir.exists():
                                    for city_dir in cities_dir.iterdir():
                                        if city_dir.is_dir():
                                            for city_file in city_dir.glob('*.md'):
                                                city_slug = city_file.stem
                                                city_key = city_dir.name
                                                urls.append(f"{self.config['domain']}/services/locations/{location_key}/cities/{city_key}/{city_slug}.html")
        
        # Add listing/index pages that are auto-generated
        listing_pages = [
            'services.html',  # Main services listing page
            'blog.html',
            'industries.html',
            'case-studies.html',
            'case-studies-2.html',  # Pagination page
            'gallery-2.html'  # Pagination page
        ]
        for page in listing_pages:
            # Check if the page actually exists in build directory
            if (Path(self.output_dir) / page).exists():
                urls.append(f"{self.config['domain']}/{page}")
                    
        # Generate sitemap XML with lastmod, changefreq, and priority
        from datetime import datetime
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url in urls:
            # Determine priority and changefreq based on URL type
            if url.endswith('/index.html'):
                priority = '1.0'
                changefreq = 'daily'
            elif '/services/' in url and '/locations/' not in url:
                priority = '0.9'
                changefreq = 'weekly'
            elif '/blog/' in url or '/news/' in url:
                priority = '0.7'
                changefreq = 'weekly'
            elif '/case-studies/' in url:
                priority = '0.6'
                changefreq = 'monthly'
            elif '/locations/' in url:
                priority = '0.5'
                changefreq = 'monthly'
            else:
                priority = '0.5'
                changefreq = 'monthly'
                
            sitemap_xml += f'  <url>\n'
            sitemap_xml += f'    <loc>{url}</loc>\n'
            sitemap_xml += f'    <lastmod>{current_date}</lastmod>\n'
            sitemap_xml += f'    <changefreq>{changefreq}</changefreq>\n'
            sitemap_xml += f'    <priority>{priority}</priority>\n'
            sitemap_xml += f'  </url>\n'
            
        sitemap_xml += '</urlset>'
        
        sitemap_path.write_text(sitemap_xml)
        logger.info("Generated sitemap.xml")
        
        # Generate image sitemap
        self._generate_image_sitemap()
        
        # Generate RSS feed
        self._generate_rss_feed()
    
    def _generate_image_sitemap(self):
        """Generate comprehensive image sitemap for all pages"""
        image_sitemap_path = Path(self.output_dir) / "sitemap-images.xml"
        
        # Dictionary to store images by page URL
        pages_with_images = {}
        
        # Get gallery images
        gallery_data = self._load_gallery_data()
        images = gallery_data.get('images', [])
        
        # Add gallery images - split between gallery.html and gallery-2.html if needed
        if images:
            # First 12 images for gallery.html
            gallery1_images = images[:12]
            pages_with_images[f'{self.config["domain"]}/gallery.html'] = []
            for image in gallery1_images:
                pages_with_images[f'{self.config["domain"]}/gallery.html'].append({
                    'loc': f'{self.config["domain"]}/content/gallery/{image["filename"]}',
                    'title': image.get('title'),
                    'caption': image.get('description')
                })
            
            # Remaining images for gallery-2.html if exists
            if len(images) > 12:
                gallery2_images = images[12:]
                pages_with_images[f'{self.config["domain"]}/gallery-2.html'] = []
                for image in gallery2_images:
                    pages_with_images[f'{self.config["domain"]}/gallery-2.html'].append({
                        'loc': f'{self.config["domain"]}/content/gallery/{image["filename"]}',
                        'title': image.get('title'),
                        'caption': image.get('description')
                    })
        
        # Add favicon for homepage
        pages_with_images[f'{self.config["domain"]}/index.html'] = [{
            'loc': f'{self.config["domain"]}/favicon.png',
            'title': 'Big0 Logo',
            'caption': 'Big0 - AI-Powered Digital Transformation'
        }]
        
        # Check for images in blog posts
        blog_dir = Path('content/blogs')
        if blog_dir.exists():
            for blog_file in blog_dir.glob('*.md'):
                # For now, just check if blog posts reference images
                # This can be expanded to parse actual image references
                pass
        
        # Check for images in case studies  
        case_dir = Path('content/case_studies')
        if case_dir.exists():
            for case_file in case_dir.glob('*.md'):
                # For now, just check if case studies reference images
                # This can be expanded to parse actual image references
                pass
        
        # Generate image sitemap XML
        sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        sitemap_xml += '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        
        # Add all pages with images
        for page_url, page_images in pages_with_images.items():
            if page_images:
                sitemap_xml += '  <url>\n'
                sitemap_xml += f'    <loc>{page_url}</loc>\n'
                
                for image in page_images:
                    sitemap_xml += '    <image:image>\n'
                    sitemap_xml += f'      <image:loc>{image["loc"]}</image:loc>\n'
                    if image.get('title'):
                        # Escape XML special characters
                        title = str(image["title"]).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
                        sitemap_xml += f'      <image:title>{title}</image:title>\n'
                    if image.get('caption'):
                        # Escape XML special characters
                        caption = str(image["caption"]).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
                        sitemap_xml += f'      <image:caption>{caption}</image:caption>\n'
                    sitemap_xml += '    </image:image>\n'
                
                sitemap_xml += '  </url>\n'
        
        sitemap_xml += '</urlset>'
        
        image_sitemap_path.write_text(sitemap_xml)
        logger.info(f"Generated sitemap-images.xml with {len(pages_with_images)} pages and {sum(len(imgs) for imgs in pages_with_images.values())} images")
    
    def _escape_xml(self, text):
        """Escape special characters for XML"""
        if not text:
            return text
        # Even in CDATA, we need to handle the CDATA end sequence
        return text.replace(']]>', ']]]]><![CDATA[>')
    
    def _xml_escape_filter(self, text):
        """Escape special characters for XML (for use as Jinja2 filter)"""
        if not text:
            return text
        # Replace XML special characters
        text = str(text)
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&apos;')
        return text
    
    def _generate_rss_feed(self):
        """Generate RSS feed for news and blog posts"""
        try:
            from email.utils import formatdate
            import time
            
            # Collect all feed items
            feed_items = []
            
            # Add news articles
            news_dir = Path('content/news')
            if news_dir.exists():
                for file_path in news_dir.glob('*.md'):
                    item = self._load_markdown_content(file_path)
                    feed_items.append({
                        'title': item['title'],
                        'url': f"news/{item['slug']}.html",
                        'description': item['frontmatter'].get('description', item.get('excerpt', '')),
                        'content_html': self._escape_xml(item.get('content_html', '')),
                        'pub_date': formatdate(time.mktime(item['date'].timetuple()) if item.get('date') else time.time()),
                        'category': item['frontmatter'].get('category', 'News'),
                        'tags': item['frontmatter'].get('tags', '').split(',') if item['frontmatter'].get('tags') else [],
                        'date_obj': item.get('date', datetime.now())
                    })
            
            # Add blog posts
            blog_dir = Path('content/blogs')
            if blog_dir.exists():
                for file_path in blog_dir.glob('*.md'):
                    item = self._load_markdown_content(file_path)
                    feed_items.append({
                        'title': item['title'],
                        'url': f"blog/{item['slug']}.html",
                        'description': item['frontmatter'].get('description', item.get('excerpt', '')),
                        'content_html': self._escape_xml(item.get('content_html', '')),
                        'pub_date': formatdate(time.mktime(item['date'].timetuple()) if item.get('date') else time.time()),
                        'category': item['frontmatter'].get('category', 'Blog'),
                        'tags': item['frontmatter'].get('tags', '').split(',') if item['frontmatter'].get('tags') else [],
                        'date_obj': item.get('date', datetime.now())
                    })
            
            # Add case studies
            case_studies_dir = Path('content/case_studies')
            if case_studies_dir.exists():
                for file_path in case_studies_dir.glob('*.md'):
                    item = self._load_markdown_content(file_path)
                    feed_items.append({
                        'title': item['title'],
                        'url': f"case-studies/{item['slug']}.html",
                        'description': item['frontmatter'].get('description', item.get('excerpt', '')),
                        'content_html': self._escape_xml(item.get('content_html', '')),
                        'pub_date': formatdate(time.mktime(item['date'].timetuple()) if item.get('date') else time.time()),
                        'category': 'Case Study',
                        'tags': item['frontmatter'].get('tags', '').split(',') if item['frontmatter'].get('tags') else [],
                        'date_obj': item.get('date', datetime.now())
                    })
            
            # Sort by date (newest first)
            feed_items.sort(key=lambda x: x['date_obj'] or datetime.min, reverse=True)
            
            # Remove date_obj from items
            for item in feed_items:
                del item['date_obj']
            
            # Generate RSS
            template = self.env.get_template('rss.xml')
            rss_content = template.render(
                domain=self.config['domain'],
                build_date=formatdate(time.time()),
                current_year=datetime.now().year,
                feed_items=feed_items[:20]  # Limit to 20 most recent items
            )
            
            rss_path = Path(self.output_dir) / "rss.xml"
            rss_path.write_text(rss_content)
            logger.info("Generated rss.xml")
            
        except Exception as e:
            logger.error(f"Error generating RSS feed: {e}")
    
    def _generate_search_index(self):
        """Generate search index for all pages"""
        try:
            import json
            
            search_documents = []
            doc_id = 1
            
            # Index static pages
            for page in self.config['static_pages']:
                # Skip sitemap pages
                if page['output'].endswith('.xml'):
                    continue
                    
                doc = {
                    'id': doc_id,
                    'url': page['output'],
                    'title': page.get('title', page['output'].replace('.html', '').title()),
                    'content': '',  # Could extract content from template if needed
                    'description': page.get('description', ''),
                    'type': 'page'
                }
                search_documents.append(doc)
                doc_id += 1
            
            # Index all content pages
            for content_type, config in self.config['content_types'].items():
                content_dir = Path(config['content_dir'])
                if not content_dir.exists():
                    continue
                    
                # Add listing page
                if 'listing_template' in config:
                    doc = {
                        'id': doc_id,
                        'url': f"{content_type.replace('_', '-')}.html",
                        'title': content_type.replace('_', ' ').title(),
                        'content': '',
                        'description': f"Browse all {content_type.replace('_', ' ')}",
                        'type': 'listing'
                    }
                    search_documents.append(doc)
                    doc_id += 1
                
                # Add individual content pages (excluding location pages)
                for file_path in content_dir.glob('*.md'):
                    item = self._load_markdown_content(file_path)
                    
                    # Skip location pages from search index
                    if item.get('frontmatter', {}).get('is_location_page', False):
                        continue
                    
                    # Clean content for search - remove HTML tags
                    clean_content = ''
                    if item.get('content_html'):
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(item['content_html'], 'html.parser')
                        clean_content = soup.get_text(' ', strip=True)
                    
                    # Fix type for news articles and industries
                    doc_type = content_type.rstrip('s')  # Remove plural
                    if content_type == 'news':
                        doc_type = 'news'  # Keep 'news' as is, don't change to 'new'
                    elif content_type == 'industries':
                        doc_type = 'industry'  # Change 'industries' to 'industry', not 'industrie'
                    
                    doc = {
                        'id': doc_id,
                        'url': f"{config['output_dir']}/{item['slug']}.html",
                        'title': item['title'],
                        'content': clean_content[:1000],  # Limit content length
                        'description': item.get('short_description', item.get('excerpt', '')),
                        'type': doc_type,
                        'category': item.get('category', ''),
                        'date': item['date'].strftime('%Y-%m-%d') if item.get('date') else ''
                    }
                    search_documents.append(doc)
                    doc_id += 1
            
            # Add gallery page if it exists
            gallery_doc = {
                'id': doc_id,
                'url': 'gallery.html',
                'title': 'Gallery',
                'content': 'Photo gallery showcasing our events, team, and projects',
                'description': 'Browse through our collection of photos from events, team activities, and project showcases',
                'type': 'page'
            }
            search_documents.append(gallery_doc)
            
            # Write search index
            search_index_path = Path(self.output_dir) / 'static' / 'search-index.json'
            search_index_path.write_text(json.dumps(search_documents, indent=2))
            
            logger.info(f"Generated search index with {len(search_documents)} documents")
            
        except Exception as e:
            logger.error(f"Error generating search index: {e}")
    
    def _optimize_output(self):
        """Optimize all generated files for performance"""
        logger.info("Starting post-generation optimization...")
        
        # Track optimization stats
        stats = {
            'html_files': 0,
            'html_saved': 0,
            'css_files': 0,
            'css_saved': 0,
            'total_saved': 0
        }
        
        # Optimize HTML files
        self._optimize_html_files(stats)
        
        # Optimize CSS files
        self._optimize_css_files(stats)
        
        # Log optimization results
        total_saved_kb = stats['total_saved'] / 1024
        logger.info(f"Optimization complete! Saved {total_saved_kb:.2f} KB total")
        logger.info(f"  - HTML: {stats['html_files']} files, saved {stats['html_saved']/1024:.2f} KB")
        logger.info(f"  - CSS: {stats['css_files']} files, saved {stats['css_saved']/1024:.2f} KB")
    
    def _optimize_html_files(self, stats):
        """Minify all HTML files in the output directory"""
        output_path = Path(self.output_dir)
        
        for html_file in output_path.rglob('*.html'):
            try:
                # Read original content
                original_content = html_file.read_text(encoding='utf-8')
                original_size = len(original_content.encode('utf-8'))
                
                # Extract and minify inline scripts
                soup = BeautifulSoup(original_content, 'html.parser')
                
                # Minify inline JavaScript
                for script in soup.find_all('script'):
                    if script.string and not script.get('src'):
                        try:
                            minified_js = jsmin.jsmin(script.string)
                            script.string = minified_js
                        except Exception as e:
                            logger.warning(f"Failed to minify inline JS in {html_file}: {e}")
                
                # Minify inline CSS
                for style in soup.find_all('style'):
                    if style.string:
                        try:
                            minified_css = rcssmin.cssmin(style.string)
                            style.string = minified_css
                        except Exception as e:
                            logger.warning(f"Failed to minify inline CSS in {html_file}: {e}")
                
                # Convert back to string
                modified_html = str(soup)
                
                # Minify the entire HTML
                # Start with the safest options and gradually enable more
                minified_html = None
                try:
                    # Try without JS/CSS minification first (safer)
                    minified_html = minify_html.minify(
                        modified_html,
                        minify_js=False,
                        minify_css=False,
                        remove_processing_instructions=False,
                        keep_html_and_head_opening_tags=True,
                        keep_closing_tags=True,
                        minify_doctype=False
                    )
                except:
                    # If that fails, use a simple regex-based approach
                    logger.debug(f"minify_html failed for {html_file.name}, using fallback")
                    minified_html = self._simple_html_minify(modified_html)
                
                # Write minified content
                html_file.write_text(minified_html, encoding='utf-8')
                
                # Calculate savings
                minified_size = len(minified_html.encode('utf-8'))
                saved = original_size - minified_size
                
                stats['html_files'] += 1
                stats['html_saved'] += saved
                stats['total_saved'] += saved
                
                if saved > 0:
                    percent_saved = (saved / original_size) * 100
                    logger.debug(f"Minified {html_file.relative_to(output_path)}: {percent_saved:.1f}% smaller")
                    
            except Exception as e:
                logger.error(f"Error optimizing {html_file}: {e}")
    
    def _optimize_css_files(self, stats):
        """Minify all CSS files in the static directory"""
        static_dir = Path(self.output_dir) / 'static'
        
        if not static_dir.exists():
            return
        
        for css_file in static_dir.rglob('*.css'):
            try:
                # Read original content
                original_content = css_file.read_text(encoding='utf-8')
                original_size = len(original_content.encode('utf-8'))
                
                # Minify CSS
                minified_css = rcssmin.cssmin(original_content, keep_bang_comments=True)
                
                # Write minified content
                css_file.write_text(minified_css, encoding='utf-8')
                
                # Calculate savings
                minified_size = len(minified_css.encode('utf-8'))
                saved = original_size - minified_size
                
                stats['css_files'] += 1
                stats['css_saved'] += saved
                stats['total_saved'] += saved
                
                if saved > 0:
                    percent_saved = (saved / original_size) * 100
                    logger.debug(f"Minified {css_file.relative_to(static_dir)}: {percent_saved:.1f}% smaller")
                    
            except Exception as e:
                logger.error(f"Error optimizing {css_file}: {e}")
    
    def _simple_html_minify(self, html):
        """Simple regex-based HTML minification fallback"""
        import re
        
        # Remove HTML comments (but keep IE conditional comments)
        html = re.sub(r'<!--(?!\[if).*?-->', '', html, flags=re.DOTALL)
        
        # Remove whitespace between tags
        html = re.sub(r'>\s+<', '><', html)
        
        # Remove leading/trailing whitespace
        html = html.strip()
        
        # Collapse multiple spaces to single space
        html = re.sub(r'\s+', ' ', html)
        
        return html


def main():
    """Main entry point"""
    generator = SiteGenerator()
    generator.generate()


if __name__ == "__main__":
    main()