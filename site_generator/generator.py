import shutil
from pathlib import Path
from typing import List, Dict, Type
from jinja2 import Environment, FileSystemLoader, select_autoescape
import logging
import os

from .config import Config
from .core import TemplateRenderer, Page
from .pages import *  # This imports all page classes including ContentPage
from .content import ContentLoader  # Remove ContentPage from here
from .utils import (
    SitemapGenerator,
    SearchIndexGenerator,
    write_file,
    generate_robots_txt,
    create_redirect_page,
)

logger = logging.getLogger(__name__)


class SiteGenerator:
    """Optimized site generator with better organization"""

    def __init__(self, config: Config):
        self.config = config
        self.pages: List[Page] = []
        self.content = {
            "blog_posts": [],
            "services": [],
            "gallery_images": [],
            "industries": [],
            "case_studies": [],  # Make sure this is initialized
        }

        # Setup Jinja2
        self.env = Environment(
            loader=FileSystemLoader(config.templates_dir),
            autoescape=select_autoescape(
                enabled_extensions=("html",), default_for_string=True
            ),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Create renderer and loader
        self.renderer = TemplateRenderer(self.env, config)
        self.content_loader = ContentLoader(config, self.renderer)

        # Create utility classes
        self.sitemap_gen = SitemapGenerator(config)
        self.search_gen = SearchIndexGenerator(config)

    def generate(self):
        """Generate the website"""
        logger.info("Starting website generation...")

        # Clean and prepare
        self._clean_output()

        # Load all content
        self._load_content()

        # Create all pages
        self._create_all_pages()

        # Render all pages
        self._render_all_pages()

        # Generate additional files
        self._generate_additional_files()

        logger.info(f"Website generation complete! Generated {len(self.pages)} pages.")

    def _clean_output(self):
        """Clean output directories"""
        directories = ["./blogs", "./services", "./industries", "./case-studies"]

        for directory in directories:
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.makedirs(directory, exist_ok=True)

    def _load_content(self):
        """Load all content with error handling"""
        loaders = [
            ("blog_posts", self.content_loader.load_blog_posts),
            ("services", self.content_loader.load_services),
            ("gallery_images", self.content_loader.load_gallery_images),
            ("industries", self.content_loader.load_industries),
            ("case_studies", self.content_loader.load_case_studies),
            ("news_articles", self.content_loader.load_news_articles),
        ]

        for content_type, loader_func in loaders:
            try:
                self.content[content_type] = loader_func()
                logger.info(f"Loaded {len(self.content[content_type])} {content_type}")
            except Exception as e:
                logger.error(f"Error loading {content_type}: {e}")
                self.content[content_type] = []

    def _create_all_pages(self):
        """Create all pages"""
        # Static pages
        self._create_static_pages()

        # Dynamic content pages
        page_creators = [
            (self.content["blog_posts"], self._create_blog_pages),
            (self.content["services"], self._create_service_pages),
            (self.content["industries"], self._create_industry_pages),
            (self.content["gallery_images"], self._create_gallery_pages),
            (self.content["case_studies"], self._create_case_study_pages),
            (self.content["news_articles"], self._create_news_pages),
        ]

        for content_list, creator_func in page_creators:
            if content_list:
                creator_func()

    def _create_static_pages(self):
        """Create static pages"""
        # Home page with content - FIXED: Pass case_studies
        home_page = HomePage(
            self.renderer,
            self.content["services"],
            self.content["blog_posts"],
            self.content["industries"],
            self.content["case_studies"],  # Add case_studies parameter
        )
        self.pages.append(home_page)

        # Simple static pages
        static_pages = [
            (
                "about",
                "About Us",
                "about.html",
                "Learn about Big0's mission to transform businesses through responsible AI innovation.",
                "about",
            ),
            (
                "contact",
                "Get in Touch",
                "contact.html",
                "Get in touch with Big0. Contact us for AI consulting, cloud solutions, and digital transformation services.",
                "contact",
            ),
            (
                "careers",
                "Careers",
                "careers.html",
                "Join the Big0 team. Explore career opportunities in AI, machine learning, cloud computing, and data analytics.",
                "careers",
            ),
            (
                "privacy",
                "Privacy Policy",
                "privacy.html",
                "Big0's privacy policy. Learn how we collect, use, and protect your personal information.",
                "info",
            ),
            (
                "terms",
                "Terms of Service",
                "terms.html",
                "Terms of Service for Big0. Understand the legal agreements that govern the use of our services.",
                "info",
            ),
            ("404", "OOPs Not Found", "404.html", "Page not found", "info"),
            (
                "partners",
                "Our Partners",
                "partners.html",
                "Big0 partners with leading technology companies to deliver comprehensive solutions.",
                "partners",
            ),
            (
                "products",
                "Our Products",
                "products.html",
                "Discover what Big0 is building",
                "products",
            ),
        ]

        for slug, title, template, meta_desc, css in static_pages:
            self.pages.append(
                SimplePage(self.renderer, slug, title, template, meta_desc, css)
            )

        # Services listing page
        services_page = ServicesPage(self.renderer)
        services_page.set_services(self.content["services"])
        self.pages.append(services_page)

        # Industries listing page
        if self.content["industries"]:
            self.pages.append(
                IndustryListingPage(self.renderer, self.content["industries"])
            )

    def _create_blog_pages(self):
        """Create blog pages"""
        # Individual posts
        for post in self.content["blog_posts"]:
            self.pages.append(BlogPostPage(self.renderer, post))

        # Paginated listings
        self._create_paginated_pages(
            self.content["blog_posts"], BlogListingPage, self.config.posts_per_page
        )

    def _create_case_study_pages(self):
        """Create case study pages"""
        # Individual case studies
        for case_study in self.content["case_studies"]:
            self.pages.append(CaseStudyPage(self.renderer, case_study))

        # Paginated listings
        self._create_paginated_pages(
            self.content["case_studies"],
            CaseStudyListingPage,
            self.config.posts_per_page,
        )

    def _create_news_pages(self):
        """Create news pages (listing only, no detail pages)"""
        self._create_paginated_pages(
            self.content["news_articles"], NewsListingPage, self.config.posts_per_page
        )

    def _create_service_pages(self):
        """Create service pages"""
        for service in self.content["services"]:
            self.pages.append(ServicePage(self.renderer, service))

    def _create_industry_pages(self):
        """Create industry pages"""
        for industry in self.content["industries"]:
            self.pages.append(IndustryPage(self.renderer, industry))

    def _create_gallery_pages(self):
        """Create gallery pages"""
        self._create_paginated_pages(
            self.content["gallery_images"],
            GalleryListingPage,
            self.config.gallery_imgs_per_page,
        )

    def _create_paginated_pages(
        self, items: List, page_class: Type[Page], items_per_page: int
    ):
        """Create paginated pages for any content type"""
        if not items:
            # Create empty first page
            self.pages.append(page_class(self.renderer, [], 1, 1))
            return

        total_pages = (len(items) + items_per_page - 1) // items_per_page

        for page_num in range(1, total_pages + 1):
            start = (page_num - 1) * items_per_page
            end = min(start + items_per_page, len(items))
            page_items = items[start:end]

            self.pages.append(
                page_class(self.renderer, page_items, page_num, total_pages)
            )

    def _render_all_pages(self):
        """Render all pages"""
        for page in self.pages:
            try:
                output_path = Path(self.config.output_dir) / page.output_path
                write_file(output_path, page.render())
            except Exception as e:
                logger.error(f"Error rendering {page.slug}: {e}")

    def _generate_additional_files(self):
        """Generate sitemaps, robots.txt, search index, and redirects"""
        # Sitemaps
        sitemap_xml = self.sitemap_gen.generate_sitemap(self.pages)
        write_file(Path("sitemap.xml"), sitemap_xml)

        image_sitemap = self.sitemap_gen.generate_image_sitemap(self.pages)
        if image_sitemap:
            write_file(Path("sitemap-images.xml"), image_sitemap)

        # Robots.txt
        write_file(Path("robots.txt"), generate_robots_txt(self.config))

        # Search index
        self.search_gen.generate(
            self.pages,
            self.content["blog_posts"],
            self.content["services"],
            self.content["industries"],
        )

        # Redirects
        self._create_redirects()

    def _create_redirects(self):
        """Create redirect pages"""
        for old_url, new_url in self.config.redirects.items():
            output_path = Path(self.config.output_dir) / old_url
            redirect_html = create_redirect_page(old_url, new_url, self.config.domain)
            write_file(output_path, redirect_html)
            logger.info(f"Created redirect: {old_url} → {new_url}")
