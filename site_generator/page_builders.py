"""
Page Builders Module

This module contains specialized page builders for generating different types of pages
in the static site generator.
"""

import logging
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
                            # Sort by order field if available, then by date
                            items.sort(key=lambda x: (x.get('frontmatter', {}).get('order', 999), -(x.get('date') or datetime.min).timestamp() if x.get('date') else 0))
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
                 load_markdown_content_func):
        super().__init__(env, config, output_dir)
        self._load_markdown_content = load_markdown_content_func

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
                items.append(item)

            # Generate detail pages for all items
            if 'template' in config:
                for item in items:
                    try:
                        custom_tpl = item.get('frontmatter', {}).get('template')
                        template_name = custom_tpl if custom_tpl else config['template']
                        template = self.env.get_template(template_name)
                        output_path = Path(self.output_dir) / config['output_dir'] / f"{item['slug']}.html"

                        # Get context with depth 1 for subdirectory pages
                        # Map content_type to singular form
                        singular_map = {
                            'services': 'service',
                            'industries': 'industry',
                            'blogs': 'blog',
                            'case_studies': 'case_study'
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

            # Sort items by date (newest first) for blog, news, case_studies
            if content_type in ['blogs', 'news', 'case_studies', 'newsletters']:
                items = sorted(items, key=lambda x: x.get('date') or datetime.min, reverse=True)

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

                # Special handling for blogs template - include newsletters
                if content_type == 'blogs':
                    newsletters_config = self.config['content_types'].get('newsletters')
                    if newsletters_config:
                        newsletters_dir = Path(newsletters_config['content_dir'])
                        if newsletters_dir.exists():
                            newsletters = []
                            for file_path in newsletters_dir.glob('*.md'):
                                newsletter = self._load_markdown_content(file_path)
                                newsletters.append(newsletter)
                            # Sort by issue number descending
                            newsletters.sort(key=lambda x: x.get('frontmatter', {}).get('issue_number', 0), reverse=True)
                            list_context['all_newsletters'] = newsletters

                html_content = template.render(**list_context)
                output_path.write_text(html_content)

                logger.info(f"Generated: {output_name}")
        except Exception as e:
            logger.error(f"Error generating {content_type} listing: {e}")


