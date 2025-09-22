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

    def generate_sitemap(self, pages: List[Dict[str, Any]], location_pages: List[Dict[str, Any]] = None) -> None:
        """
        Generate XML sitemap for all site pages.

        Args:
            pages: List of page dictionaries with URL and metadata
            location_pages: Optional list of location-specific pages
        """
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

    def generate_rss_feed(self, feed_items: List[Dict[str, Any]], template_renderer: Any) -> None:
        """
        Generate RSS feed for news and blog posts.

        Args:
            feed_items: List of feed item dictionaries
            template_renderer: Template rendering function or object
        """
        try:
            # Sort by date (newest first)
            sorted_items = sorted(
                feed_items,
                key=lambda x: x.get('date_obj', datetime.min),
                reverse=True
            )

            # Remove date_obj from items for template rendering
            clean_items = []
            for item in sorted_items:
                clean_item = item.copy()
                if 'date_obj' in clean_item:
                    del clean_item['date_obj']
                clean_items.append(clean_item)

            # Generate RSS using template
            rss_content = template_renderer.render(
                domain=self.config['domain'],
                build_date=formatdate(time.time()),
                current_year=datetime.now().year,
                feed_items=clean_items[:20]  # Limit to 20 most recent items
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
            content_items: List of content item dictionaries with search data
        """
        try:
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

                # Add individual content pages from content_items
                for item in content_items:
                    # Skip location pages from search index
                    if item.get('frontmatter', {}).get('is_location_page', False):
                        continue

                    # Check if this item belongs to current content type
                    item_type = item.get('content_type', '')
                    if item_type != content_type:
                        continue

                    # Clean content for search - remove HTML tags
                    clean_content = ''
                    if item.get('content_html'):
                        try:
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(item['content_html'], 'html.parser')
                            clean_content = soup.get_text(' ', strip=True)
                        except ImportError:
                            # Fallback if BeautifulSoup is not available
                            import re
                            clean_content = re.sub(r'<[^>]+>', '', item.get('content_html', ''))

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
            search_index_path.parent.mkdir(parents=True, exist_ok=True)
            search_index_path.write_text(json.dumps(search_documents, indent=2))

            logger.info(f"Generated search index with {len(search_documents)} documents")

        except Exception as e:
            logger.error(f"Error generating search index: {e}")

    def collect_feed_items(self, content_loader_func: callable) -> List[Dict[str, Any]]:
        """
        Collect all feed items from news, blogs, and case studies.

        Args:
            content_loader_func: Function to load markdown content from file paths

        Returns:
            List of feed item dictionaries
        """
        feed_items = []

        # Add news articles
        news_dir = Path('content/news')
        if news_dir.exists():
            for file_path in news_dir.glob('*.md'):
                item = content_loader_func(file_path)
                feed_items.append({
                    'title': item['title'],
                    'url': f"news/{item['slug']}.html",
                    'description': item['frontmatter'].get('description', item.get('excerpt', '')),
                    'content_html': self._escape_xml_cdata(item.get('content_html', '')),
                    'pub_date': formatdate(time.mktime(item['date'].timetuple()) if item.get('date') else time.time()),
                    'category': item['frontmatter'].get('category', 'News'),
                    'tags': item['frontmatter'].get('tags', '').split(',') if item['frontmatter'].get('tags') else [],
                    'date_obj': item.get('date', datetime.now())
                })

        # Add blog posts
        blog_dir = Path('content/blogs')
        if blog_dir.exists():
            for file_path in blog_dir.glob('*.md'):
                item = content_loader_func(file_path)
                feed_items.append({
                    'title': item['title'],
                    'url': f"blog/{item['slug']}.html",
                    'description': item['frontmatter'].get('description', item.get('excerpt', '')),
                    'content_html': self._escape_xml_cdata(item.get('content_html', '')),
                    'pub_date': formatdate(time.mktime(item['date'].timetuple()) if item.get('date') else time.time()),
                    'category': item['frontmatter'].get('category', 'Blog'),
                    'tags': item['frontmatter'].get('tags', '').split(',') if item['frontmatter'].get('tags') else [],
                    'date_obj': item.get('date', datetime.now())
                })

        # Add case studies
        case_studies_dir = Path('content/case_studies')
        if case_studies_dir.exists():
            for file_path in case_studies_dir.glob('*.md'):
                item = content_loader_func(file_path)
                feed_items.append({
                    'title': item['title'],
                    'url': f"case-studies/{item['slug']}.html",
                    'description': item['frontmatter'].get('description', item.get('excerpt', '')),
                    'content_html': self._escape_xml_cdata(item.get('content_html', '')),
                    'pub_date': formatdate(time.mktime(item['date'].timetuple()) if item.get('date') else time.time()),
                    'category': 'Case Study',
                    'tags': item['frontmatter'].get('tags', '').split(',') if item['frontmatter'].get('tags') else [],
                    'date_obj': item.get('date', datetime.now())
                })

        return feed_items

    def load_gallery_data(self) -> Dict[str, Any]:
        """
        Load gallery images and metadata for image sitemap generation.

        Returns:
            Dictionary containing gallery data with images list
        """
        gallery_dir = Path(self.config['assets']['gallery_dir'])
        metadata_file = gallery_dir / 'metadata.json'

        images = []

        if metadata_file.exists():
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
                        image_data['date'] = datetime.strptime(image_data['date'], '%Y-%m-%d')
                    images.append(image_data)
                else:
                    # Add image without metadata
                    images.append({
                        'filename': image_file.name,
                        'title': image_file.stem.replace('-', ' ').title(),
                        'description': f'Gallery image: {image_file.stem}'
                    })

        return {'images': images}