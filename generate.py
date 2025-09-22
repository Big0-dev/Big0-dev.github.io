#!/usr/bin/env python3
"""
Refactored Static Site Generator
Generates website from templates and content files based on site_config.yaml
"""

import yaml
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Import our new modular components
from site_generator import (
    ContentProcessor,
    AssetManager,
    SEOUtilities,
)
from site_generator.page_builders import (
    StaticPageBuilder,
    ContentPageBuilder,
    LocationPageBuilder,
    GalleryPageBuilder,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class SiteGenerator:
    """Refactored static site generator using modular architecture"""

    def __init__(self, config_file: str = "site_config.yaml"):
        """Initialize the site generator with configuration and components.

        Args:
            config_file: Path to the YAML configuration file
        """
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

        self.output_dir = self.config['assets']['output_dir']
        self.static_dir = self.config['assets']['static_dir']
        self.templates_dir = "./templates"

        # Setup Jinja2 environment
        self.env = self._setup_jinja_environment()

        # Initialize modular components
        self._initialize_components()

    def _setup_jinja_environment(self) -> Environment:
        """Setup and configure Jinja2 environment.

        Returns:
            Configured Jinja2 Environment instance
        """
        env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(enabled_extensions=("html",)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Create asset manager for SVG injection
        asset_manager = AssetManager(
            config=self.config,
            static_dir=self.static_dir,
            output_dir=self.output_dir
        )

        # Add custom functions
        env.globals['inject_svg'] = asset_manager.inject_svg

        # Add custom filters
        seo_utils = SEOUtilities(self.config, self.output_dir)
        env.filters['xmlescape'] = seo_utils.xml_escape

        return env

    def _generate_location_pages_wrapper(self, content_dir, config):
        """Wrapper function to generate location pages.

        Args:
            content_dir: Path to content directory
            config: Content type configuration
        """
        return self.location_page_builder.generate_location_pages(content_dir, config)

    def _initialize_components(self):
        """Initialize all modular components."""
        # Content processor for markdown and template processing
        self.content_processor = ContentProcessor()

        # Asset manager for static files and optimization
        self.asset_manager = AssetManager(
            config=self.config,
            static_dir=self.static_dir,
            output_dir=self.output_dir
        )

        # SEO utilities for sitemaps and search
        self.seo_utilities = SEOUtilities(
            config=self.config,
            output_dir=self.output_dir
        )

        # Page builders with required function dependencies
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
            generate_location_pages_func=self._generate_location_pages_wrapper
        )

        self.location_page_builder = LocationPageBuilder(
            env=self.env,
            config=self.config,
            output_dir=self.output_dir,
            load_markdown_content_func=self.content_processor.load_markdown_content
        )

    def generate(self):
        """Generate the entire website using modular components."""
        logger.info("Starting website generation with refactored architecture...")

        try:
            # Clean and prepare output directory
            self._clean_output()

            # Copy all assets (static files, gallery, favicons)
            self._copy_assets()

            # Generate all page types
            self._generate_pages()

            # Generate SEO artifacts
            self._generate_seo_artifacts()

            # Optional: Optimize output
            self._optimize_output()

            logger.info("Website generation complete!")

        except Exception as e:
            logger.error(f"Error during site generation: {e}")
            raise

    def _clean_output(self):
        """Clean and recreate output directory structure."""
        import shutil

        # Remove existing output directory
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

        # Create base output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Create required subdirectories
        dirs_to_create = [
            os.path.join(self.output_dir, "static"),
            os.path.join(self.output_dir, "content/gallery")
        ]

        # Add content type directories
        for content_type in self.config['content_types'].values():
            dirs_to_create.append(
                os.path.join(self.output_dir, content_type['output_dir'])
            )

        # Create all directories
        for dir_path in dirs_to_create:
            os.makedirs(dir_path, exist_ok=True)

        logger.info("Output directory cleaned and prepared")

    def _copy_assets(self):
        """Copy all assets using AssetManager."""
        try:
            # Copy all assets (static, gallery, favicons)
            self.asset_manager.copy_all_assets()
            logger.info("All assets copied successfully")

        except Exception as e:
            logger.error(f"Error copying assets: {e}")
            raise

    def _generate_pages(self):
        """Generate all page types using specialized builders."""
        # Static pages (index, about, contact, etc.)
        static_pages = self.static_page_builder.generate()
        if static_pages:
            logger.info(f"Generated {len(static_pages)} static pages")
        else:
            logger.info("Static pages generated")

        # Gallery pages with pagination
        gallery_pages = self.gallery_page_builder.generate()
        if gallery_pages:
            logger.info(f"Generated {gallery_pages} gallery pages")
        else:
            logger.info("Gallery pages generated")

        # Content pages (services, industries, blogs, etc.)
        content_stats = self.content_page_builder.generate()
        if content_stats:
            for content_type, count in content_stats.items():
                logger.info(f"Generated {count} {content_type} pages")
        else:
            logger.info("Content pages generated")

        # Location-specific pages for SEO - ContentPageBuilder handles this
        logger.info("Location pages generated as part of content pages")

    def _generate_seo_artifacts(self):
        """Generate all SEO-related artifacts."""
        # Collect all pages for sitemap
        all_pages = self._collect_all_pages()
        location_pages = self._collect_location_pages()

        # Generate main sitemap
        self.seo_utilities.generate_sitemap(all_pages, location_pages)
        logger.info("Generated sitemap.xml")

        # Generate image sitemap
        gallery_data = self.asset_manager.load_gallery_data()
        # Extract images from gallery_data structure
        if gallery_data and isinstance(gallery_data, dict):
            images = gallery_data.get('images', [])
        else:
            images = []
        self.seo_utilities.generate_image_sitemap(images)
        logger.info("Generated sitemap-images.xml")

        # Generate RSS feed
        feed_items = self._collect_feed_items()
        if feed_items:
            self.seo_utilities.generate_rss_feed(
                feed_items,
                lambda template, **kwargs: self.env.get_template(template).render(**kwargs)
            )
            logger.info("Generated RSS feed")

        # Generate search index
        search_items = self._collect_search_items()
        self.seo_utilities.generate_search_index(search_items)
        logger.info("Generated search index")

    def _collect_all_pages(self) -> List[Dict[str, Any]]:
        """Collect all regular pages for sitemap generation.

        Returns:
            List of page dictionaries with path and metadata
        """
        pages = []

        # Add static pages
        for page in self.config.get('static_pages', []):
            pages.append({
                'path': page['output'],
                'type': 'static',
                'title': page.get('title', ''),
            })

        # Add content pages
        for content_type, config in self.config['content_types'].items():
            content_dir = Path(config['content_dir'])
            if content_dir.exists():
                for file_path in content_dir.glob("*.md"):
                    output_path = f"{config['output_dir']}/{file_path.stem}.html"
                    pages.append({
                        'path': output_path,
                        'type': content_type,
                        'title': file_path.stem.replace('-', ' ').title(),
                    })

        return pages

    def _collect_location_pages(self) -> List[Dict[str, Any]]:
        """Collect all location-specific pages for sitemap.

        Returns:
            List of location page dictionaries
        """
        location_pages = []
        services_dir = Path("./content/services")
        locations_dir = services_dir / "locations"

        if not locations_dir.exists():
            return location_pages

        # Collect country and city pages
        for country_dir in locations_dir.iterdir():
            if country_dir.is_dir():
                # Country-level pages
                for md_file in country_dir.glob("*.md"):
                    location_pages.append({
                        'path': f"services/locations/{country_dir.name}/{md_file.stem}.html",
                        'type': 'location-country',
                        'country': country_dir.name,
                    })

                # City-level pages
                cities_dir = country_dir / "cities"
                if cities_dir.exists():
                    for city_dir in cities_dir.iterdir():
                        if city_dir.is_dir():
                            for md_file in city_dir.glob("*.md"):
                                location_pages.append({
                                    'path': f"services/locations/{country_dir.name}/cities/{city_dir.name}/{md_file.stem}.html",
                                    'type': 'location-city',
                                    'country': country_dir.name,
                                    'city': city_dir.name,
                                })

        return location_pages

    def _collect_feed_items(self) -> List[Dict[str, Any]]:
        """Collect items for RSS feed generation.

        Returns:
            List of feed items from news, blogs, and case studies
        """
        feed_items = []

        # Collect from configured content types that should be in feed
        feed_types = ['news', 'blog', 'case_studies']

        for content_type in feed_types:
            if content_type in self.config['content_types']:
                config = self.config['content_types'][content_type]
                items = self._load_content_items(config['content_dir'])

                # Convert to feed format
                for item in items:
                    if item and isinstance(item, dict):
                        feed_item = {
                            'title': item.get('title', ''),
                            'url': f"{config['output_dir']}/{item.get('slug', '')}.html",
                            'description': item.get('frontmatter', {}).get('description', item.get('excerpt', '')),
                            'date': item.get('date'),
                            'content': item.get('content', ''),
                            'type': content_type.rstrip('s'),  # Remove plural
                        }
                        feed_items.append(feed_item)

        return feed_items

    def _load_content_items(self, content_dir: str) -> List[Dict[str, Any]]:
        """Load content items from a directory.

        Args:
            content_dir: Directory containing markdown files

        Returns:
            List of content dictionaries
        """
        items = []
        content_path = Path(content_dir)

        if content_path.exists():
            for file_path in content_path.glob("*.md"):
                try:
                    # Convert to Path object for content processor
                    result = self.content_processor.load_markdown_content(
                        Path(file_path),
                        file_path.stem + ".html"
                    )
                    if result:
                        items.append(result)
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")

        return items

    def _collect_search_items(self) -> List[Dict[str, Any]]:
        """Collect all items for search index generation.

        Returns:
            List of searchable content items
        """
        search_items = []

        # Add static pages
        for page in self.config.get('static_pages', []):
            search_items.append({
                'id': page['output'].replace('.html', ''),
                'title': page.get('title', ''),
                'content': page.get('description', ''),
                'url': page['output'],
                'type': 'page',
            })

        # Add content pages
        for content_type, config in self.config['content_types'].items():
            items = self._load_content_items(config['content_dir'])
            for item in items:
                search_items.append({
                    'id': item.get('slug', item.get('title', '').lower().replace(' ', '-')),
                    'title': item.get('title', ''),
                    'content': item.get('content', ''),
                    'url': f"{config['output_dir']}/{item.get('slug', item.get('title', '').lower().replace(' ', '-'))}.html",
                    'type': content_type.rstrip('s'),  # Remove plural
                })

        return search_items

    def _optimize_output(self):
        """Optionally optimize all output files."""
        # Check if optimization is enabled (currently disabled to preserve cookie consent)
        optimize = os.environ.get('OPTIMIZE_OUTPUT', 'false').lower() == 'true'

        if optimize:
            try:
                stats = self.asset_manager.optimize_all_files()
                logger.info(f"Optimization complete: {stats}")
            except Exception as e:
                logger.warning(f"Optimization failed (non-critical): {e}")
        else:
            logger.info("Output optimization skipped (preserving cookie consent scripts)")


def main():
    """Main entry point for the refactored site generator."""
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