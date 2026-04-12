"""
SEO Utilities Module

Handles all SEO-related functionality including sitemap generation,
RSS feed creation, search index building, and XML escaping.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from email.utils import formatdate
import time

logger = logging.getLogger(__name__)


class SEOUtilities:
    """
    Handles all SEO-related functionality for the static site generator.

    This class provides methods for generating sitemaps, RSS feeds, search indexes,
    and other SEO-related artifacts.
    """

    def __init__(self, config: Dict[str, Any], output_dir: str):
        """
        Initialize SEOUtilities with site configuration and output directory.

        Args:
            config: Site configuration dictionary
            output_dir: Directory where generated files will be written
        """
        self.config = config
        self.output_dir = output_dir

    def xml_escape(self, text: str) -> str:
        """
        Escape special characters for XML content.

        Args:
            text: Text to escape

        Returns:
            XML-escaped text
        """
        if not text:
            return text

        text = str(text)
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&apos;')
        return text

    def _escape_xml_cdata(self, text: str) -> str:
        """
        Escape XML for CDATA sections.

        Args:
            text: Text to escape for CDATA

        Returns:
            CDATA-safe text
        """
        if not text:
            return text
        # Even in CDATA, we need to handle the CDATA end sequence
        return text.replace(']]>', ']]]]><![CDATA[>')

    def generate_sitemap(self, pages: List[Dict[str, Any]]) -> None:
        """
        Generate XML sitemap for all site pages.

        Args:
            pages: List of page dictionaries with URL and metadata
        """
        sitemap_path = Path(self.output_dir) / "sitemap.xml"

        urls = []

        # Add static pages (exclude 404 page from sitemap)
        for page in self.config['static_pages']:
            if page['output'] == '404.html':
                continue
            urls.append(f"{self.config['domain']}/{page['output']}")

        # Add content pages
        for content_type, config in self.config['content_types'].items():
            content_dir = Path(config['content_dir'])
            if content_dir.exists():
                for file_path in content_dir.glob('*.md'):
                    slug = file_path.stem
                    urls.append(f"{self.config['domain']}/{config['output_dir']}/{slug}.html")

        # Add listing/index pages that are auto-generated
        # Start with known listing pages
        listing_pages = [
            'services.html',
            'blog.html',
            'case-studies.html',
            'gallery.html',
            'newsletters.html',
            'news.html',
        ]

        # Dynamically discover all pagination pages (blog-2.html, blog-3.html, etc.)
        output_path = Path(self.output_dir)
        pagination_patterns = ['blog-*.html', 'case-studies-*.html', 'gallery-*.html', 'newsletters-*.html']
        for pattern in pagination_patterns:
            for page_file in output_path.glob(pattern):
                listing_pages.append(page_file.name)

        # Add newsletter detail pages
        newsletters_dir = output_path / 'newsletters'
        if newsletters_dir.exists():
            for newsletter_file in newsletters_dir.glob('*.html'):
                listing_pages.append(f'newsletters/{newsletter_file.name}')



        # Deduplicate and add to urls
        for page in set(listing_pages):
            # Check if the page actually exists in build directory
            if (Path(self.output_dir) / page).exists():
                urls.append(f"{self.config['domain']}/{page}")

        # Deduplicate URLs while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        urls = unique_urls

        # Generate sitemap XML with lastmod, changefreq, and priority
        current_date = datetime.now().strftime('%Y-%m-%d')

        parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]

        for url in urls:
            # Determine priority and changefreq based on URL type
            if url.endswith('/index.html'):
                priority, changefreq = '1.0', 'daily'
            elif '/services/' in url:
                priority, changefreq = '0.9', 'weekly'
            elif '/blog/' in url or '/news/' in url:
                priority, changefreq = '0.7', 'weekly'
            elif '/case-studies/' in url:
                priority, changefreq = '0.6', 'monthly'
            else:
                priority, changefreq = '0.5', 'monthly'

            parts.append(f'  <url>\n    <loc>{self.xml_escape(url)}</loc>\n    <lastmod>{current_date}</lastmod>\n    <changefreq>{changefreq}</changefreq>\n    <priority>{priority}</priority>\n  </url>')

        parts.append('</urlset>')
        sitemap_path.write_text('\n'.join(parts))
        logger.info("Generated sitemap.xml")

    def generate_image_sitemap(self, images: List[Dict[str, Any]]) -> None:
        """
        Generate comprehensive image sitemap for all pages.

        Args:
            images: List of image dictionaries with filename, title, description
        """
        image_sitemap_path = Path(self.output_dir) / "sitemap-images.xml"

        # Dictionary to store images by page URL
        pages_with_images = {}

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
                        title = self.xml_escape(image["title"])
                        sitemap_xml += f'      <image:title>{title}</image:title>\n'
                    if image.get('caption'):
                        # Escape XML special characters
                        caption = self.xml_escape(image["caption"])
                        sitemap_xml += f'      <image:caption>{caption}</image:caption>\n'
                    sitemap_xml += '    </image:image>\n'

                sitemap_xml += '  </url>\n'

        sitemap_xml += '</urlset>'

        image_sitemap_path.write_text(sitemap_xml)
        logger.info(f"Generated sitemap-images.xml with {len(pages_with_images)} pages and {sum(len(imgs) for imgs in pages_with_images.values())} images")

    def generate_rss_feed(self, feed_items: List[Dict[str, Any]], env: Any) -> None:
        """
        Generate RSS feed for news and blog posts.

        Args:
            feed_items: List of feed item dictionaries
            env: Jinja2 Environment instance
        """
        try:
            # Sort by date (newest first)
            sorted_items = sorted(
                feed_items,
                key=lambda x: x.get('date_obj') or datetime.min,
                reverse=True
            )

            # Remove date_obj from items for template rendering
            clean_items = [
                {k: v for k, v in item.items() if k != 'date_obj'}
                for item in sorted_items
            ]

            # Generate RSS using Jinja2 template directly
            rss_content = env.get_template('rss.xml').render(
                domain=self.config['domain'],
                build_date=formatdate(time.time()),
                current_year=datetime.now().year,
                feed_items=clean_items[:20]
            )

            rss_path = Path(self.output_dir) / "rss.xml"
            rss_path.write_text(rss_content)
            logger.info("Generated rss.xml")

        except Exception as e:
            logger.error(f"Error generating RSS feed: {e}")

    def generate_search_index(self, content_items: List[Dict[str, Any]]) -> None:
        """
        Generate search index for all pages compatible with MiniSearch.

        Args:
            content_items: Pre-formatted list of search documents (with 'id' and 'url' keys)
        """
        try:
            search_documents = list(content_items)

            # Add gallery page
            search_documents.append({
                'id': f"page-gallery",
                'url': 'gallery.html',
                'title': 'Gallery',
                'content': 'Photo gallery showcasing our events, team, and projects',
                'description': 'Browse through our collection of photos from events, team activities, and project showcases',
                'type': 'page',
            })

            # Write search index
            search_index_path = Path(self.output_dir) / 'static' / 'search-index.json'
            search_index_path.parent.mkdir(parents=True, exist_ok=True)
            search_index_path.write_text(json.dumps(search_documents, indent=2))

            logger.info(f"Generated search index with {len(search_documents)} documents")

        except Exception as e:
            logger.error(f"Error generating search index: {e}")

