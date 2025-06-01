# utils.py - Optimized version
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple
from datetime import datetime
import json
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SitemapGenerator:
    """Handles all sitemap generation"""

    def __init__(self, config):
        self.config = config

    def generate_sitemap(self, pages: List) -> str:
        """Generate standard sitemap.xml"""
        urls = []

        for page in pages:
            if hasattr(page, "slug") and page.slug in ["404"]:
                continue

            loc = self._get_page_url(page)
            priority = self._get_page_priority(page)

            urls.append(
                {
                    "loc": loc,
                    "lastmod": datetime.now().strftime("%Y-%m-%d"),
                    "priority": priority,
                }
            )

        #        # Add static resources
        #        urls.append(
        #            {
        #                "loc": f"{self.config.domain}/static/hassan_resume.pdf",
        #                "lastmod": datetime.now().strftime("%Y-%m-%d"),
        #                "priority": "0.6",
        #            }
        #        )
        #
        return self._format_sitemap(urls)

    def generate_image_sitemap(self, pages: List) -> str:
        """Generate image sitemap"""
        image_entries = []
        seen_images = set()

        for page in pages:
            if hasattr(page, "slug") and page.slug in ["404"]:
                continue

            page_url = self._get_page_url(page)
            images = self._extract_page_images(page)

            for img_url, alt_text in images:
                image_key = (page_url, img_url)
                if image_key not in seen_images:
                    seen_images.add(image_key)
                    image_entries.append(
                        {"page_url": page_url, "image_url": img_url, "title": alt_text}
                    )

        if not image_entries:
            return ""

        return self._format_image_sitemap(image_entries)

    def _get_page_url(self, page) -> str:
        """Get canonical page URL"""
        if hasattr(page, "canonical_url"):
            return page.canonical_url

        if page.output_path.name == "index.html":
            return f"{self.config.domain}/"
        return f"{self.config.domain}/{page.output_path}"

    def _get_page_priority(self, page) -> str:
        """Get page priority for sitemap"""
        if page.slug == "index":
            return "1.0"
        elif page.slug.startswith("blog-"):
            return "0.7"
        else:
            return "0.8"

    def _extract_page_images(self, page) -> List[Tuple[str, str]]:
        """Extract images from page context"""
        images = []
        context = page.get_context()

        # Extract from different context types
        extractors = [
            self._extract_from_blog_posts,
            self._extract_from_services,
            self._extract_from_gallery,
            self._extract_from_simple_fields,
        ]

        for extractor in extractors:
            images.extend(extractor(context, page.title))

        return images

    def _extract_from_blog_posts(
        self, context: Dict, page_title: str
    ) -> List[Tuple[str, str]]:
        """Extract images from blog posts"""
        images = []
        if "blog_posts" in context:
            for post in context["blog_posts"]:
                if "image_url" in post:
                    alt_text = post.get("title", post.get("meta_des", ""))
                    images.append((post["image_url"], alt_text))
        return images

    def _extract_from_services(
        self, context: Dict, page_title: str
    ) -> List[Tuple[str, str]]:
        """Extract images from services"""
        images = []
        if "services" in context:
            for service in context["services"]:
                if hasattr(service, "image") and service.image:
                    images.append((f"./static/{service.image}", service.title))
        return images

    def _extract_from_gallery(
        self, context: Dict, page_title: str
    ) -> List[Tuple[str, str]]:
        """Extract images from gallery"""
        images = []
        if "images" in context:
            for img in context["images"]:
                if hasattr(img, "filename"):
                    images.append((f"./content/gallery/{img.filename}", img.title))
        return images

    def _extract_from_simple_fields(
        self, context: Dict, page_title: str
    ) -> List[Tuple[str, str]]:
        """Extract images from simple fields"""
        images = []
        image_keys = ["hero", "image", "profile_image", "background_image"]

        for key in image_keys:
            if key in context and context[key]:
                img_value = context[key]
                if isinstance(img_value, str) and self._is_image_file(img_value):
                    alt_text = f"{page_title} {key.replace('_', ' ')}"
                    images.append((f"./static/{img_value}", alt_text))

        return images

    def _is_image_file(self, filename: str) -> bool:
        """Check if filename is an image"""
        extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg"}
        return any(filename.lower().endswith(ext) for ext in extensions)

    def _format_sitemap(self, urls: List[Dict]) -> str:
        """Format standard sitemap XML"""
        xml_entries = []
        for url in urls:
            xml_entries.append(f"""  <url>
    <loc>{url["loc"]}</loc>
    <lastmod>{url["lastmod"]}</lastmod>
    <priority>{url["priority"]}</priority>
  </url>""")

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(xml_entries)}
</urlset>"""

    def _format_image_sitemap(self, entries: List[Dict]) -> str:
        """Format image sitemap XML"""
        xml_entries = []
        for entry in entries:
            xml_entries.append(f"""  <url>
    <loc>{entry["page_url"]}</loc>
    <image:image>
      <image:loc>{entry["image_url"]}</image:loc>
      <image:title>{self._escape_xml(entry["title"])}</image:title>
    </image:image>
  </url>""")

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
{chr(10).join(xml_entries)}
</urlset>"""

    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters"""
        if not text:
            return ""
        replacements = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&apos;",
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text


class SearchIndexGenerator:
    """Handles search index generation"""

    def __init__(self, config):
        self.config = config
        self.seen_ids = set()

    def generate(
        self, pages: List, blog_posts: List, services: List, industries: List = None
    ) -> str:
        """Generate search index JSON"""
        documents = []

        # Add different content types
        self._add_pages(documents, pages)
        self._add_blog_posts(documents, blog_posts)
        self._add_services(documents, services)
        if industries:
            self._add_industries(documents, industries)

        # Save to file
        output_path = Path("static/search-index.json")
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(json.dumps(documents, indent=2))

        logger.info(f"Generated search index with {len(documents)} entries")
        return json.dumps(documents, indent=2)

    def _add_document(self, documents: List[Dict], doc: Dict):
        """Add document with duplicate checking"""
        if doc["id"] in self.seen_ids:
            logger.warning(f"Skipping duplicate ID: {doc['id']}")
            return
        self.seen_ids.add(doc["id"])
        documents.append(doc)

    def _add_pages(self, documents: List[Dict], pages: List):
        """Add static pages to search index"""
        skip_paths = ["blog/", "services/", "industries/"]

        for page in pages:
            if hasattr(page, "slug") and page.slug not in ["404"]:
                # Skip dynamic content pages
                if any(path in str(page.output_path) for path in skip_paths):
                    continue

                self._add_document(
                    documents,
                    {
                        "id": f"page-{page.slug}",
                        "url": str(page.output_path),
                        "title": page.title,
                        "content": "",
                        "description": page.meta_description,
                        "type": "page",
                    },
                )

    def _add_blog_posts(self, documents: List[Dict], blog_posts: List):
        """Add blog posts to search index"""
        for post in blog_posts:
            self._add_document(
                documents,
                {
                    "id": f"blog-{post.slug}",
                    "url": f"blogs/{post.slug}.html",
                    "title": post.title,
                    "content": post.meta_description,
                    "description": post.meta_description,
                    "type": "blog",
                    "category": post.category,
                    "date": post.date.strftime("%Y-%m-%d"),
                },
            )

    def _add_services(self, documents: List[Dict], services: List):
        """Add services to search index"""
        for service in services:
            self._add_document(
                documents,
                {
                    "id": f"service-{service.slug}",
                    "url": f"services/{service.slug}.html",
                    "title": service.title,
                    "content": service.meta_description,
                    "description": service.meta_description,
                    "type": "service",
                },
            )

    def _add_industries(self, documents: List[Dict], industries: List):
        """Add industries to search index"""
        for industry in industries:
            self._add_document(
                documents,
                {
                    "id": f"industry-{industry.slug}",
                    "url": f"industries/{industry.slug}.html",
                    "title": industry.title,
                    "content": industry.meta_description,
                    "description": industry.meta_description,
                    "type": "industry",
                },
            )


# Simplified utility functions
def ensure_directory(path: Path) -> None:
    """Ensure directory exists"""
    path.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str) -> None:
    """Write content to file"""
    ensure_directory(path.parent)
    path.write_text(content, encoding="utf-8")


def generate_robots_txt(config) -> str:
    """Generate robots.txt"""
    return f"""# robots.txt for {config.domain}
User-agent: *
Allow: /

Sitemap: {config.domain}/sitemap.xml
Sitemap: {config.domain}/sitemap-images.xml"""


def create_redirect_page(old_url: str, new_url: str, domain: str) -> str:
    """Create redirect HTML"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Redirecting...</title>
    <link rel="canonical" href="{domain}{new_url}">
    <meta http-equiv="refresh" content="0;url={new_url}">
    <script>window.location.href = "{new_url}";</script>
</head>
<body>
    <h1>Redirecting...</h1>
    <p>This page has moved. If you are not redirected automatically, <a href="{new_url}">click here</a>.</p>
</body>
</html>"""
