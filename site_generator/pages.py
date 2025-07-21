# pages.py - Update the HomePage class
from typing import Dict, Any, List, Optional
from pathlib import Path
from abc import abstractmethod
from .core import Page, TemplateRenderer
from .content import (
    ContentItem,
    BlogPost,
    Service,
    Industry,
    GalleryImage,
    CaseStudy,
    NewsArticle,
)


class SimplePage(Page):
    """Base class for simple static pages"""

    def __init__(
        self,
        renderer: TemplateRenderer,
        slug: str,
        title: str,
        template: str,
        meta_description: str,
        custom_css: str = None,
    ):
        super().__init__(renderer)
        self._slug = slug
        self._title = title
        self._template = template
        self._meta_description = meta_description
        self._custom_css = custom_css

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def title(self) -> str:
        return self._title

    @property
    def template(self) -> str:
        return self._template

    @property
    def output_path(self) -> Path:
        return Path(f"{self._slug}.html")

    @property
    def meta_description(self) -> str:
        return self._meta_description

    @property
    def custom_css(self) -> str:
        return self._custom_css


class HomePage(Page):
    def __init__(
        self,
        renderer: TemplateRenderer,
        services: List = None,
        blog_posts: List = None,
        industries: List = None,
        case_studies: List = None,  # Add case_studies parameter
    ):
        super().__init__(renderer)
        self._services = services or []
        self._blog_posts = blog_posts or []
        self._industries = industries or []
        self._case_studies = case_studies or []  # Store case_studies

    @property
    def slug(self) -> str:
        return "index"

    @property
    def title(self) -> str:
        return "Next Level Innovation"

    @property
    def custom_css(self) -> str:
        return "home"

    @property
    def template(self) -> str:
        return "home.html"

    @property
    def output_path(self) -> Path:
        return Path("index.html")

    @property
    def meta_description(self) -> str:
        return "Big0 - Transforming businesses with cutting-edge AI, machine learning, and data-driven solutions. Next level innovation powered by intelligence."

    @property
    def preload(self) -> str:
        return "hero"

    def get_context(self) -> Dict[str, Any]:
        recent_services = self._services[:3] if self._services else []
        recent_posts = self._blog_posts[:3] if self._blog_posts else []

        return {
            "tagline": "Next Level Innovation",
            "subtitle": "Powered by Intelligence",
            "hero_cta": "Get Started",
            "recent_services": recent_services,
            "total_services": len(self._services),
            "recent_posts": recent_posts,
            "industries": self._industries,
            "case_studies": self._case_studies,  # Add case_studies to context
            "services_page": "./services.html",
            "about": "./about.html",
            "blog": "./blog.html",
            "industries_page": "./industries.html",
            "careers": "./careers.html",
        }


class ServicesPage(Page):
    """Services listing page"""

    def __init__(self, renderer: TemplateRenderer):
        super().__init__(renderer)
        self._services = []

    def set_services(self, services: List[Service]):
        """Set services data"""
        self._services = services

    @property
    def slug(self) -> str:
        return "services"

    @property
    def title(self) -> str:
        return "Services"

    @property
    def template(self) -> str:
        return "services.html"

    @property
    def output_path(self) -> Path:
        return Path("services.html")

    @property
    def meta_description(self) -> str:
        return (
            "Comprehensive AI and technology solutions tailored to your business needs."
        )

    def get_context(self) -> Dict[str, Any]:
        return {"services": self._services}

    @property
    def custom_css(self) -> str:
        return "services"


class ContentPage(Page):
    """Base class for content-based pages"""

    def __init__(self, renderer: TemplateRenderer, content_item: ContentItem):
        super().__init__(renderer)
        self.content_item = content_item

    @property
    def slug(self) -> str:
        return f"{self.content_type}-{self.content_item.slug}"

    @property
    def title(self) -> str:
        return self.content_item.title

    @property
    def meta_description(self) -> str:
        return self.content_item.meta_description

    @property
    def output_path(self) -> Path:
        return Path(f"{self.content_type}s/{self.content_item.slug}.html")

    @property
    @abstractmethod
    def content_type(self) -> str:
        """Type of content (blog, service, industry)"""
        pass

    def get_context(self) -> Dict[str, Any]:
        """Default context for content pages"""
        return {
            "title": self.title,
            f"{self.content_type}_content": self.content_item.content_html,
            "meta_des": self.meta_description,
        }


class BlogPostPage(ContentPage):
    """Individual blog post page"""

    def __init__(self, renderer: TemplateRenderer, post: BlogPost):
        super().__init__(renderer, post)
        self.post = post  # Keep reference for convenience

    @property
    def content_type(self) -> str:
        return "blog"

    @property
    def template(self) -> str:
        return "blog_post.html"

    @property
    def custom_css(self) -> str:
        return "blog_post"

    def get_context(self) -> Dict[str, Any]:
        context = super().get_context()
        context.update(
            {
                "category": self.post.category,
                "date": self.post.date.strftime("%B %d, %Y"),
                "blog_content": self.post.content_html,  # Add this for compatibility
            }
        )
        return context


class ServicePage(ContentPage):
    """Individual service page"""

    def __init__(self, renderer: TemplateRenderer, service: Service):
        super().__init__(renderer, service)
        self.service = service

    @property
    def content_type(self) -> str:
        return "service"

    @property
    def template(self) -> str:
        return "service_detail.html"

    @property
    def custom_css(self) -> str:
        return "services_details"

    def get_context(self) -> Dict[str, Any]:
        context = super().get_context()
        context.update(
            {
                "price": self.service.price,
                "image": self.service.image,
                "icon": self.service.icon,
                "features": self.service.features,
                "service_content": self.service.content_html,  # Add for compatibility
            }
        )
        return context


class IndustryPage(ContentPage):
    """Individual industry page"""

    def __init__(self, renderer: TemplateRenderer, industry: Industry):
        super().__init__(renderer, industry)
        self.industry = industry

    @property
    def content_type(self) -> str:
        return "industry"  # Note: singular, not plural

    @property
    def output_path(self) -> Path:
        # Override to use industries (plural) directory
        return Path(f"industries/{self.content_item.slug}.html")

    @property
    def template(self) -> str:
        return "industry_detail.html"

    @property
    def custom_css(self) -> str:
        return "industry_details"

    def get_context(self) -> Dict[str, Any]:
        context = super().get_context()
        context.update(
            {
                "image": self.industry.image,
                "icon": self.industry.icon,
                "challenge": self.industry.challenge,
                "solutions": self.industry.solutions,
                "case_studies": self.industry.case_studies,
                "industry_content": self.industry.content_html,  # Add for compatibility
            }
        )
        return context


class IndustryListingPage(Page):
    """Industries listing page"""

    def __init__(self, renderer: TemplateRenderer, industries: List[Industry]):
        super().__init__(renderer)
        self.industries = industries

    @property
    def slug(self) -> str:
        return "industries"

    @property
    def title(self) -> str:
        return "Industries We Serve"

    @property
    def template(self) -> str:
        return "industries.html"

    @property
    def output_path(self) -> Path:
        return Path("industries.html")

    @property
    def meta_description(self) -> str:
        return "Discover how Big0 delivers tailored AI and technology solutions across diverse industries including finance, healthcare, retail, and more."

    @property
    def custom_css(self) -> str:
        return "industries"

    def get_context(self) -> Dict[str, Any]:
        return {"industries": self.industries}


class PaginatedListingPage(Page):
    """Base class for paginated listing pages"""

    def __init__(
        self,
        renderer: TemplateRenderer,
        items: List[Any],
        page_num: int = 1,
        total_pages: int = 1,
    ):
        super().__init__(renderer)
        self.items = items
        self.page_num = page_num
        self.total_pages = total_pages

    @property
    def is_paginated(self) -> bool:
        return self.total_pages > 1

    @property
    def slug(self) -> str:
        base_slug = self.base_slug
        return base_slug if self.page_num == 1 else f"{base_slug}-{self.page_num}"

    @property
    def title(self) -> str:
        base_title = self.base_title
        return (
            base_title if self.page_num == 1 else f"{base_title} - Page {self.page_num}"
        )

    @property
    def output_path(self) -> Path:
        filename = (
            f"{self.base_slug}.html"
            if self.page_num == 1
            else f"{self.base_slug}-{self.page_num}.html"
        )
        return Path(filename)

    @property
    @abstractmethod
    def base_slug(self) -> str:
        pass

    @property
    @abstractmethod
    def base_title(self) -> str:
        pass

    def get_pagination_context(self) -> Dict[str, Any]:
        """Get pagination context"""
        if not self.is_paginated:
            return {}

        return {
            "pagination": {
                "current_page": self.page_num,
                "total_pages": self.total_pages,
                "has_prev": self.page_num > 1,
                "has_next": self.page_num < self.total_pages,
                "prev_url": f"./{self.base_slug}.html"
                if self.page_num == 2
                else f"./{self.base_slug}-{self.page_num - 1}.html",
                "next_url": f"./{self.base_slug}-{self.page_num + 1}.html",
            }
        }


class BlogListingPage(PaginatedListingPage):
    """Blog listing page with pagination"""

    @property
    def base_slug(self) -> str:
        return "blog"

    @property
    def base_title(self) -> str:
        return "Blog"

    @property
    def template(self) -> str:
        return "blog.html"

    @property
    def custom_css(self) -> str:
        return "blog"

    @property
    def meta_description(self) -> str:
        return "Explore cutting-edge insights on AI, Federated Learning, programming, big data, and robotics."

    def get_context(self) -> Dict[str, Any]:
        # Format blog posts for template
        blog_posts = []
        for post in self.items:
            blog_posts.append(
                {
                    "title": post.title,
                    "category": post.category,
                    "date": post.date.strftime("%B %d, %Y"),
                    "filename": f"./blogs/{post.slug}.html",
                    "image_url": f"./static/{post.image}"
                    if post.image
                    else "./static/default.jpg",
                    "meta_des": post.meta_description,
                }
            )

        context = {"blog_posts": blog_posts}
        context.update(self.get_pagination_context())
        return context


class GalleryListingPage(PaginatedListingPage):
    """Gallery listing page with pagination"""

    @property
    def base_slug(self) -> str:
        return "gallery"

    @property
    def base_title(self) -> str:
        return "Gallery"

    @property
    def template(self) -> str:
        return "gallery.html"

    @property
    def custom_css(self) -> str:
        return "gallery"

    @property
    def meta_description(self) -> str:
        return "Photo gallery showcasing Hassan Kamran's projects, experiences, and achievements in AI, robotics, and technology."

    def get_context(self) -> Dict[str, Any]:
        context = {
            "images": self.items,
            "gallery_url": f"{self.renderer.config.gallery_dir}",
        }
        context.update(self.get_pagination_context())
        return context


class CaseStudyPage(ContentPage):
    """Individual case study page"""

    def __init__(self, renderer: TemplateRenderer, case_study: CaseStudy):
        super().__init__(renderer, case_study)
        self.case_study = case_study

    @property
    def content_type(self) -> str:
        return "case_study"

    @property
    def output_path(self) -> Path:
        return Path(f"case-studies/{self.content_item.slug}.html")

    @property
    def template(self) -> str:
        return "case_study_detail.html"

    @property
    def custom_css(self) -> str:
        return "case_study_details"

    def get_context(self) -> Dict[str, Any]:
        context = super().get_context()
        context.update(
            {
                "industry": self.case_study.industry,
                "type": self.case_study.case_study_type,
                "challenge": self.case_study.challenge,
                "solution": self.case_study.solution,
                "results": self.case_study.results,
                "technologies": self.case_study.technologies,
                "icon": self.case_study.icon,
                "case_study_content": self.case_study.content_html,
            }
        )
        return context


class CaseStudyListingPage(PaginatedListingPage):
    """Case studies listing page with pagination"""

    @property
    def base_slug(self) -> str:
        return "case-studies"

    @property
    def base_title(self) -> str:
        return "Case Studies"

    @property
    def template(self) -> str:
        return "case_studies.html"

    @property
    def custom_css(self) -> str:
        return "case_studies"

    @property
    def meta_description(self) -> str:
        return "Real-world success stories and transformative solutions that drive business growth."

    def get_context(self) -> Dict[str, Any]:
        context = {"case_study_items": self.items}
        context.update(self.get_pagination_context())
        return context


class NewsListingPage(PaginatedListingPage):
    """News listing page with pagination"""

    @property
    def base_slug(self) -> str:
        return "news"

    @property
    def base_title(self) -> str:
        return "Latest News"

    @property
    def template(self) -> str:
        return "news.html"

    @property
    def custom_css(self) -> str:
        return "news"

    @property
    def meta_description(self) -> str:
        return "Stay updated with our latest announcements, achievements, and industry insights."

    def get_context(self) -> Dict[str, Any]:
        context = {"news_articles": self.items}
        context.update(self.get_pagination_context())
        return context
