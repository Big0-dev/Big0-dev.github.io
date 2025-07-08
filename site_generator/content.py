# content.py - Complete corrected version
from pathlib import Path
from typing import List, Dict, Any, Optional, Type, TypeVar
from datetime import datetime
from dataclasses import dataclass, field
import markdown
import json
import logging
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

from .core import Page, TemplateRenderer

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="ContentItem")


@dataclass
class ContentItem(ABC):
    """Base class for all content items"""

    slug: str
    title: str
    content_html: str
    meta_description: str = ""
    order: int = 999
    image: str = None
    icon: str = None

    @classmethod
    @abstractmethod
    def from_metadata(
        cls, slug: str, metadata: Dict[str, Any], html_content: str
    ) -> "ContentItem":
        """Create instance from metadata dict"""
        pass


@dataclass
class BlogPost(ContentItem):
    category: str = "Uncategorized"
    date: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_metadata(
        cls, slug: str, metadata: Dict[str, Any], html_content: str
    ) -> "BlogPost":
        return cls(
            slug=slug,
            title=metadata.get("title", "Untitled Post"),
            content_html=html_content,
            meta_description=metadata.get("meta_description", "")[:160],
            category=metadata.get("category", "Uncategorized"),
            date=metadata.get("date", datetime.now()),
            image=metadata.get("image"),
        )


@dataclass
class Service(ContentItem):
    price: str = None
    features: List[str] = field(default_factory=list)
    short_description: str = ""

    @classmethod
    def from_metadata(
        cls, slug: str, metadata: Dict[str, Any], html_content: str
    ) -> "Service":
        features = []
        if metadata.get("features"):
            features = [f.strip() for f in metadata["features"].split(",")]

        return cls(
            slug=slug,
            title=metadata.get("title", "Untitled Service"),
            content_html=html_content,
            meta_description=metadata.get("description", "")[:160],
            short_description=metadata.get(
                "short_description", metadata.get("description", "")
            )[:200],
            icon=metadata.get("icon"),
            image=metadata.get("image"),
            price=metadata.get("price"),
            features=features,
            order=int(metadata.get("order", 999)),
        )


@dataclass
class Industry(ContentItem):
    short_description: str = ""
    challenge: str = ""
    solutions: List[str] = field(default_factory=list)
    case_studies: List[str] = field(default_factory=list)

    @classmethod
    def from_metadata(
        cls, slug: str, metadata: Dict[str, Any], html_content: str
    ) -> "Industry":
        solutions = []
        if metadata.get("solutions"):
            solutions = [s.strip() for s in metadata["solutions"].split(",")]

        case_studies = []
        if metadata.get("case_studies"):
            case_studies = [c.strip() for c in metadata["case_studies"].split(",")]

        return cls(
            slug=slug,
            title=metadata.get("title", "Untitled Industry"),
            content_html=html_content,
            meta_description=metadata.get("description", "")[:160],
            short_description=metadata.get(
                "short_description", metadata.get("description", "")
            )[:200],
            icon=metadata.get("icon"),
            image=metadata.get("image"),
            challenge=metadata.get("challenge", ""),
            solutions=solutions,
            case_studies=case_studies,
            order=int(metadata.get("order", 999)),
        )


@dataclass
class CaseStudy(ContentItem):
    industry: str = ""
    case_study_type: str = ""
    challenge: str = ""
    solution: str = ""
    results: List[Dict[str, str]] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    metrics: List[Dict[str, str]] = field(default_factory=list)

    @classmethod
    def from_metadata(
        cls, slug: str, metadata: Dict[str, Any], html_content: str
    ) -> "CaseStudy":
        # Parse results
        results = []
        if metadata.get("results"):
            result_values = [r.strip() for r in metadata["results"].split(",")]
            result_descriptions = []
            if metadata.get("result_descriptions"):
                result_descriptions = [
                    r.strip() for r in metadata["result_descriptions"].split(",")
                ]

            for i, value in enumerate(result_values):
                # Parse "98% Order Accuracy" format
                parts = value.split(" ", 1)
                if len(parts) == 2:
                    results.append(
                        {
                            "value": parts[0],
                            "label": parts[1],
                            "description": result_descriptions[i]
                            if i < len(result_descriptions)
                            else "",
                        }
                    )

        # Parse technologies
        technologies = []
        if metadata.get("technologies"):
            technologies = [t.strip() for t in metadata["technologies"].split(",")]

        # Create metrics from results for card display
        metrics = []
        for result in results[:4]:  # Limit to 4 for card display
            metrics.append({"value": result["value"], "label": result["label"]})

        return cls(
            slug=slug,
            title=metadata.get("title", "Untitled Case Study"),
            content_html=html_content,
            meta_description=metadata.get("description", "")[:160],
            industry=metadata.get("industry", ""),
            case_study_type=metadata.get("type", ""),
            challenge=metadata.get("challenge", ""),
            solution=metadata.get("solution", ""),
            results=results,
            technologies=technologies,
            metrics=metrics,
            icon=metadata.get("icon"),
            order=int(metadata.get("order", 999)),
        )


@dataclass
class NewsArticle(ContentItem):
    category: str = "News"
    date: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    external_link: str = None
    excerpt: str = ""

    @classmethod
    def from_metadata(
        cls, slug: str, metadata: Dict[str, Any], html_content: str
    ) -> "NewsArticle":
        # Parse tags
        tags = []
        if metadata.get("tags"):
            tags = [t.strip() for t in metadata["tags"].split(",")]

        # Parse date
        date_obj = datetime.now()
        if metadata.get("date"):
            date_str = str(metadata.get("date", ""))
            if date_str:
                formats = ["%Y-%m-%d", "%B %d, %Y", "%d %B %Y", "%d/%m/%Y", "%m/%d/%Y"]
                for fmt in formats:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue

        # Create excerpt from description or first paragraph of content
        excerpt = metadata.get("description", "")
        if not excerpt and html_content:
            # Extract first paragraph as excerpt
            soup = BeautifulSoup(html_content, "html.parser")
            first_p = soup.find("p")
            if first_p:
                excerpt = first_p.get_text()[:200] + "..."

        return cls(
            slug=slug,
            title=metadata.get("title", "Untitled Article"),
            content_html=html_content,
            meta_description=metadata.get("description", "")[:160],
            category=metadata.get("category", "News"),
            date=date_obj,
            tags=tags,
            external_link=metadata.get("external_link"),
            excerpt=excerpt,
            order=int(metadata.get("order", 999)),
        )


@dataclass
class GalleryImage:
    """Gallery image with metadata"""

    filename: str
    title: str
    description: str = ""
    category: str = "General"
    date: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)


class ContentLoader:
    """Unified content loader with better error handling"""

    def __init__(self, config, renderer=None):
        self.config = config
        self.renderer = renderer
        self.md = markdown.Markdown(extensions=["extra", "codehilite"])

    def load_content(
        self, content_dir: Path, content_class: Type[T], use_frontmatter: bool = True
    ) -> List[T]:
        """Generic content loading method"""
        items = []

        if not content_dir.exists():
            logger.warning(f"Content directory not found: {content_dir}")
            return items

        for file_path in sorted(content_dir.iterdir()):
            if file_path.suffix.lower() not in [".md", ".txt"]:
                continue

            try:
                content = self._read_file(file_path)
                if not content:
                    continue

                if use_frontmatter:
                    metadata, markdown_content = self._parse_frontmatter(content)
                else:
                    # For blog posts with line-based format
                    metadata, markdown_content = self._parse_blog_format(
                        content, file_path
                    )

                if metadata is None:
                    continue

                # Process content
                self.md.reset()
                if self.renderer:
                    markdown_content = self._process_template_includes(
                        markdown_content,
                        content_class=content_class,
                    )

                html_content = self.md.convert(markdown_content)

                # Create content item
                item = content_class.from_metadata(
                    slug=file_path.stem, metadata=metadata, html_content=html_content
                )
                items.append(item)

            except Exception as e:
                logger.error(f"Error loading {file_path.name}: {e}")

        # Sort by order then title
        items.sort(key=lambda x: (x.order, x.title))
        return items

    def _read_file(self, file_path: Path) -> Optional[str]:
        """Read file with multiple encoding attempts"""
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                return file_path.read_text(encoding=encoding).strip()
            except UnicodeDecodeError:
                continue
        return None

    def _parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Parse YAML frontmatter from content"""
        if not content.startswith("---"):
            return {}, content

        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content

        metadata = {}
        for line in parts[1].strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

        return metadata, parts[2]

    def _parse_blog_format(
        self, content: str, file_path: Path
    ) -> tuple[Dict[str, Any], str]:
        """Parse blog posts in line-based format"""
        lines = content.split("\n")
        if len(lines) < 5:
            return None, ""

        metadata = {
            "title": lines[0].strip() or "Untitled Post",
            "category": lines[1].strip() if len(lines) > 1 else "Uncategorized",
            "date": self._parse_date(lines[2].strip() if len(lines) > 2 else ""),
            "image": lines[3].strip() if len(lines) > 3 else "",
            "meta_description": lines[4].strip() if len(lines) > 4 else "",
        }

        markdown_content = "\n".join(lines[5:]) if len(lines) > 5 else ""
        return metadata, markdown_content

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date from various formats"""
        if not date_str:
            return datetime.now()

        formats = ["%Y-%m-%d", "%B %d, %Y", "%d %B %Y", "%d/%m/%Y", "%m/%d/%Y"]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return datetime.now()

    def _process_template_includes(
        self, markdown_content: str, content_class=None
    ) -> str:
        """Process template includes with proper error handling"""
        import re

        pattern = r"{{(template|video):([a-zA-Z0-9_-]+)}}"

        def replace_template(match):
            tag_type = match.group(1)
            value = match.group(2)

            try:
                if tag_type == "template":
                    template_name = value + ".html"

                    # Determine if content goes in subdirectory
                    is_subdirectory = content_class and content_class in [
                        BlogPost,
                        Service,
                        Industry,
                        CaseStudy,
                        NewsArticle,
                    ]

                    context = {
                        "inject_svg": self.renderer.inject_svg,
                        "static": "../static" if is_subdirectory else "./static",
                        "config": self.config,
                        # Add navigation URLs with proper relative paths
                        "contact": "../contact.html"
                        if is_subdirectory
                        else "./contact.html",
                        "services_page": "../services.html"
                        if is_subdirectory
                        else "./services.html",
                        "about": "../about.html" if is_subdirectory else "./about.html",
                        "blog": "../blog.html" if is_subdirectory else "./blog.html",
                        "home": "../index.html" if is_subdirectory else "./index.html",
                    }

                    template = self.renderer.env.get_template(template_name)
                    return template.render(**context)

                elif tag_type == "video":
                    template = self.renderer.env.get_template("video.html")
                    return template.render(youtube_id=value, config=self.config)

            except Exception as e:
                logger.error(f"Template include failed: {str(e)}")
                return f"<!-- Template include failed: {str(e)} -->"

            return ""

        return re.sub(pattern, replace_template, markdown_content)

    # Specific loading methods that use the generic loader
    def load_blog_posts(self) -> List[BlogPost]:
        """Load blog posts"""
        return self.load_content(
            Path(self.config.blog_dir), BlogPost, use_frontmatter=False
        )

    def load_services(self) -> List[Service]:
        """Load services"""
        return self.load_content(
            Path(self.config.services_dir), Service, use_frontmatter=True
        )

    def load_industries(self) -> List[Industry]:
        """Load industries"""
        return self.load_content(
            Path(self.config.industries_dir), Industry, use_frontmatter=True
        )

    def load_case_studies(self) -> List[CaseStudy]:
        """Load case studies"""
        return self.load_content(
            Path(self.config.case_studies_dir), CaseStudy, use_frontmatter=True
        )

    def load_news_articles(self) -> List[NewsArticle]:
        """Load news articles"""
        return self.load_content(
            Path(self.config.news_dir), NewsArticle, use_frontmatter=True
        )

    def load_gallery_images(self) -> List["GalleryImage"]:
        """Load gallery images with metadata"""
        images = []
        gallery_dir = Path(self.config.gallery_dir)

        if not gallery_dir.exists():
            logger.warning(f"Gallery directory not found: {gallery_dir}")
            return images

        # Load metadata
        metadata = {}
        metadata_file = gallery_dir / "metadata.json"
        if metadata_file.exists():
            try:
                metadata = json.loads(metadata_file.read_text())
            except Exception as e:
                logger.error(f"Error loading gallery metadata: {e}")

        # Scan for images
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}

        for file_path in sorted(gallery_dir.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                filename = file_path.name
                image_meta = metadata.get(filename, {})

                images.append(
                    GalleryImage(
                        filename=filename,
                        title=image_meta.get(
                            "title", file_path.stem.replace("-", " ").title()
                        ),
                        description=image_meta.get("description", ""),
                        category=image_meta.get("category", "General"),
                        date=self._parse_date(image_meta.get("date", "")),
                        tags=image_meta.get("tags", []),
                    )
                )

        images.sort(key=lambda img: img.date, reverse=True)
        return images
