"""
Page Builders Module

This module contains specialized page builders for generating different types of pages
in the static site generator.
"""

import logging
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from abc import ABC, abstractmethod
from jinja2 import Environment
import json

logger = logging.getLogger(__name__)


class BasePageBuilder(ABC):
    """Base class for all page builders"""

    def __init__(self, env: Environment, config: Dict[str, Any], output_dir: str):
        self.env = env
        self.config = config
        self.output_dir = output_dir

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

    @abstractmethod
    def generate(self):
        """Generate pages - must be implemented by subclasses"""
        pass


class StaticPageBuilder(BasePageBuilder):
    """Builder for static pages from templates"""

    def __init__(self, env: Environment, config: Dict[str, Any], output_dir: str,
                 load_markdown_content_func, load_gallery_data_func):
        super().__init__(env, config, output_dir)
        self._load_markdown_content = load_markdown_content_func
        self._load_gallery_data = load_gallery_data_func

    def generate(self):
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


class GalleryPageBuilder(BasePageBuilder):
    """Builder for gallery pages with pagination"""

    def __init__(self, env: Environment, config: Dict[str, Any], output_dir: str,
                 load_gallery_data_func):
        super().__init__(env, config, output_dir)
        self._load_gallery_data = load_gallery_data_func

    def generate(self):
        """Generate gallery pages with pagination"""
        try:
            gallery_data = self._load_gallery_data()
            images = gallery_data.get('images', [])
            gallery_url = gallery_data.get('gallery_url')

            # Sort images by date descending (newest first)
            images.sort(key=lambda x: x.get('date') or datetime.min, reverse=True)

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


class ContentPageBuilder(BasePageBuilder):
    """Builder for content pages from markdown files"""

    def __init__(self, env: Environment, config: Dict[str, Any], output_dir: str,
                 load_markdown_content_func, generate_location_pages_func):
        super().__init__(env, config, output_dir)
        self._load_markdown_content = load_markdown_content_func
        self._generate_location_pages = generate_location_pages_func

    def generate(self):
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
                self._generate_listing_pages(content_type, config, items)

    def _generate_listing_pages(self, content_type: str, config: Dict[str, Any], items: List[Dict[str, Any]]):
        """Generate paginated listing pages for content"""
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


class LocationPageBuilder(BasePageBuilder):
    """Builder for location-specific service pages"""

    def __init__(self, env: Environment, config: Dict[str, Any], output_dir: str,
                 load_markdown_content_func):
        super().__init__(env, config, output_dir)
        self._load_markdown_content = load_markdown_content_func

    def generate_location_pages(self, content_dir: Path, config: dict):
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
                        def fix_service_link(match):
                            service_name = match.group(1)
                            return f'href="../../../services/{service_name}.html"'

                        location_item['content_html'] = re.sub(
                            r'href="([a-zA-Z_\-]+)\.html"',
                            fix_service_link,
                            location_item['content_html']
                        )

                        # Generate the HTML page
                        template = self.env.get_template(config.get('template', 'service_detail.html'))

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

        # Process city-specific standalone files
        for country_key, country_cities in cities.items():
            for city_key, city in country_cities.items():
                city_dir = locations_dir / country_key / 'cities' / city_key

                if city_dir.exists():
                    # Process all .md files in this city directory
                    for md_file in city_dir.glob('*.md'):
                        # Skip if already processed (matches service-city pattern)
                        if any(md_file.stem == f"{service.stem}-{city_key}"
                               for service in services_dir.glob('*.md')):
                            continue

                        # Generate this standalone city page
                        try:
                            output_path = Path(f"services/locations/{country_key}/cities/{city_key}/{md_file.stem}.html")
                            city_item = self._load_markdown_content(md_file, output_path)

                            # Fix service links for city pages
                            def fix_city_service_link(match):
                                service_name = match.group(1)
                                return f'href="../../../../../services/{service_name}.html"'

                            city_item['content_html'] = re.sub(
                                r'href="([a-zA-Z_\-]+)\.html"',
                                fix_city_service_link,
                                city_item['content_html']
                            )

                            # Generate the HTML page
                            template = self.env.get_template(config.get('template', 'service_detail.html'))

                            # Create output directory
                            output_dir = Path(self.output_dir) / 'services' / 'locations' / country_key / 'cities' / city_key
                            output_dir.mkdir(parents=True, exist_ok=True)

                            output_path = output_dir / f"{md_file.stem}.html"

                            # Get context with appropriate depth for deeply nested directory
                            base_context = self._get_base_context(depth=5)

                            city_context = {
                                **base_context,
                                'current_service': city_item,
                                'item': city_item
                            }

                            html_content = template.render(**city_context)
                            output_path.write_text(html_content)

                            logger.info(f"Generated standalone city page: {output_path.relative_to(self.output_dir)}")

                        except Exception as e:
                            logger.error(f"Error generating standalone city page {md_file}: {e}")

    def generate(self):
        """Main entry point - not used directly, use generate_location_pages instead"""
        pass