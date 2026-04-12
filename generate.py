#!/usr/bin/env python3
"""
Static Site Generator
Generates website from templates and content files based on site_config.yaml
"""

import re
import yaml
import logging
import shutil
from email.utils import formatdate
from time import mktime
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, select_autoescape

from site_generator import (
    ContentProcessor,
    AssetManager,
    SEOUtilities,
)
from site_generator.page_builders import (
    StaticPageBuilder,
    ContentPageBuilder,
    GalleryPageBuilder,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Map content types to singular display names (used by feed and search)
TYPE_NAMES = {
    'blogs': 'blog',
    'services': 'service',
    'case_studies': 'case study',
    'news': 'news',
    'newsletters': 'newsletter',
    'team': 'team',
}

# Root files to copy into build output
ROOT_FILES = ['_redirects', 'robots.txt', '_routes.json']


class SiteGenerator:
    """Static site generator using modular architecture"""

    def __init__(self, config_file: str = "site_config.yaml"):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

        self.output_dir = self.config['assets']['output_dir']
        self.static_dir = self.config['assets']['static_dir']
        self.templates_dir = "./templates"

        # Initialize components (single instances, shared across pipeline)
        self.content_processor = ContentProcessor()
        self.asset_manager = AssetManager(
            config=self.config,
            static_dir=self.static_dir,
            output_dir=self.output_dir
        )
        self.seo_utilities = SEOUtilities(
            config=self.config,
            output_dir=self.output_dir
        )

        # Setup Jinja2 environment using the single asset_manager instance
        self.env = self._setup_jinja_environment()

        # Page builders
        self.static_page_builder = StaticPageBuilder(
            env=self.env,
            config=self.config,
            output_dir=self.output_dir,
            load_markdown_content_func=self.content_processor.load_markdown_content,
            load_gallery_data_func=self.asset_manager.load_gallery_data
        )
        self.gallery_page_builder = GalleryPageBuilder(
            env=self.env,
            config=self.config,
            output_dir=self.output_dir,
            load_gallery_data_func=self.asset_manager.load_gallery_data
        )
        self.content_page_builder = ContentPageBuilder(
            env=self.env,
            config=self.config,
            output_dir=self.output_dir,
            load_markdown_content_func=self.content_processor.load_markdown_content,
        )

    def _setup_jinja_environment(self) -> Environment:
        """Setup and configure Jinja2 environment."""
        env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(enabled_extensions=("html",)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Reuse the single asset_manager instance for SVG injection
        env.globals['inject_svg'] = self.asset_manager.inject_svg
        env.filters['xmlescape'] = self.seo_utilities.xml_escape

        return env

    def generate(self):
        """Generate the entire website."""
        logger.info("Starting website generation...")

        try:
            self._clean_output()
            self._copy_assets()
            self._generate_pages()
            self._generate_seo_artifacts()
            self.asset_manager.optimize_output()
            logger.info("Website generation complete!")

        except Exception as e:
            logger.error(f"Error during site generation: {e}")
            raise

    def _clean_output(self):
        """Clean and recreate output directory structure."""
        output = Path(self.output_dir)
        if output.exists():
            shutil.rmtree(output)

        # Create all required directories in one pass
        dirs_to_create = [
            output / "static",
            output / "content" / "gallery",
        ]
        for content_type in self.config['content_types'].values():
            dirs_to_create.append(output / content_type['output_dir'])
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)

        logger.info("Output directory cleaned and prepared")

    def _copy_assets(self):
        """Copy all assets using AssetManager."""
        try:
            self.asset_manager.copy_all_assets()

            # Copy root files (consolidate repeated copy logic)
            for filename in ROOT_FILES:
                src = Path(filename)
                if src.exists():
                    shutil.copy2(src, Path(self.output_dir) / filename)
                    logger.info(f"Copied {filename}")

        except Exception as e:
            logger.error(f"Error copying assets: {e}")
            raise

    def _generate_pages(self):
        """Generate all page types using specialized builders."""
        static_pages = self.static_page_builder.generate()
        if static_pages:
            logger.info(f"Generated {len(static_pages)} static pages")

        gallery_pages = self.gallery_page_builder.generate()
        if gallery_pages:
            logger.info(f"Generated {gallery_pages} gallery pages")

        content_stats = self.content_page_builder.generate()
        if content_stats:
            for content_type, count in content_stats.items():
                logger.info(f"Generated {count} {content_type} pages")

    def _generate_seo_artifacts(self):
        """Generate all SEO-related artifacts."""
        # Collect all pages for sitemap
        all_pages = self._collect_all_pages()
        self.seo_utilities.generate_sitemap(all_pages)
        logger.info("Generated sitemap.xml")

        # Generate image sitemap
        gallery_data = self.asset_manager.load_gallery_data()
        images = gallery_data.get('images', []) if isinstance(gallery_data, dict) else []
        self.seo_utilities.generate_image_sitemap(images)
        logger.info("Generated sitemap-images.xml")

        # Load content items once and reuse for both feed and search
        all_content = self._load_all_content()

        # Generate RSS feed
        feed_items = self._build_feed_items(all_content)
        if feed_items:
            self.seo_utilities.generate_rss_feed(feed_items, self.env)
            logger.info("Generated RSS feed")

        # Generate search index
        search_items = self._build_search_items(all_content)
        self.seo_utilities.generate_search_index(search_items)
        logger.info("Generated search index")

    def _collect_all_pages(self) -> List[Dict[str, Any]]:
        """Collect all pages for sitemap generation."""
        pages = []

        for page in self.config.get('static_pages', []):
            pages.append({
                'path': page['output'],
                'type': 'static',
                'title': page.get('title', ''),
            })

        for content_type, config in self.config['content_types'].items():
            content_dir = Path(config['content_dir'])
            if content_dir.exists():
                for file_path in content_dir.glob("*.md"):
                    pages.append({
                        'path': f"{config['output_dir']}/{file_path.stem}.html",
                        'type': content_type,
                        'title': file_path.stem.replace('-', ' ').title(),
                    })

        return pages

    def _load_all_content(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all content items once, keyed by content type."""
        all_content = {}
        for content_type, config in self.config['content_types'].items():
            content_path = Path(config['content_dir'])
            items = []
            if content_path.exists():
                for file_path in content_path.glob("*.md"):
                    try:
                        result = self.content_processor.load_markdown_content(
                            file_path,
                            Path(config['output_dir']) / f"{file_path.stem}.html"
                        )
                        if result:
                            items.append(result)
                    except Exception as e:
                        logger.error(f"Error loading {file_path}: {e}")
            all_content[content_type] = items
        return all_content

    def _build_feed_items(self, all_content: Dict[str, List]) -> List[Dict[str, Any]]:
        """Build RSS feed items from pre-loaded content."""
        feed_items = []
        feed_types = ['news', 'blogs', 'case_studies']

        for content_type in feed_types:
            if content_type not in self.config['content_types']:
                continue
            config = self.config['content_types'][content_type]

            for item in all_content.get(content_type, []):
                if not item or not isinstance(item, dict):
                    continue

                pub_date = ''
                date_obj = item.get('date')
                if date_obj:
                    try:
                        pub_date = formatdate(mktime(date_obj.timetuple()))
                    except (AttributeError, TypeError):
                        pass

                feed_items.append({
                    'title': item.get('title', ''),
                    'url': f"{config['output_dir']}/{item.get('slug', '')}.html",
                    'description': item.get('frontmatter', {}).get('description', item.get('excerpt', '')),
                    'pub_date': pub_date,
                    'date_obj': date_obj,
                    'content_html': item.get('content_html', ''),
                    'category': item.get('category', ''),
                    'tags': item.get('tags', []),
                    'type': TYPE_NAMES.get(content_type, content_type.rstrip('s')),
                })

        return feed_items

    def _build_search_items(self, all_content: Dict[str, List]) -> List[Dict[str, Any]]:
        """Build search index items from pre-loaded content."""
        search_items = []

        # Static pages
        for page in self.config.get('static_pages', []):
            search_items.append({
                'id': page['output'].replace('.html', ''),
                'title': page.get('title', ''),
                'content': page.get('description', ''),
                'url': page['output'],
                'type': 'page',
            })

        # Content pages
        for content_type, config in self.config['content_types'].items():
            type_name = TYPE_NAMES.get(content_type, content_type.rstrip('s'))
            for item in all_content.get(content_type, []):
                content_html = item.get('content_html', '')
                plain_text = re.sub(r'<[^>]+>', ' ', content_html)
                plain_text = re.sub(r'\s+', ' ', plain_text).strip()[:1000]

                slug = item.get('slug', item.get('title', '').lower().replace(' ', '-'))
                search_items.append({
                    'id': f"{type_name}-{slug}",
                    'title': item.get('title', ''),
                    'content': plain_text,
                    'description': item.get('meta_description', ''),
                    'url': f"{config['output_dir']}/{slug}.html",
                    'type': type_name,
                    'category': item.get('category', ''),
                    'date': str(item.get('date', '')) if item.get('date') else '',
                })

        return search_items


def main():
    try:
        generator = SiteGenerator()
        generator.generate()
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
