from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime
from .core import Page, TemplateRenderer


class HomePage(Page):
    def __init__(
        self, renderer: TemplateRenderer, services: List = None, blog_posts: List = None
    ):
        super().__init__(renderer)
        self._services = services or []
        self._blog_posts = blog_posts or []

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
            # Add missing URLs for template
            "services_page": "./services.html",
            "about": "./about.html",
            "blog": "./blog.html",
        }


class ContactPage(Page):
    @property
    def slug(self) -> str:
        return "contact"

    @property
    def title(self) -> str:
        return "Get in Touch"

    @property
    def template(self) -> str:
        return "contact.html"

    @property
    def output_path(self) -> Path:
        return Path("contact.html")

    @property
    def meta_description(self) -> str:
        return "Get in touch with Big0. Contact us for AI consulting, cloud solutions, and digital transformation services."

    @property
    def custom_css(self) -> str:
        return "contact"


class CareersPage(Page):
    @property
    def slug(self) -> str:
        return "careers"

    @property
    def title(self) -> str:
        return "Careers"

    @property
    def template(self) -> str:
        return "careers.html"

    @property
    def output_path(self) -> Path:
        return Path("careers.html")

    @property
    def meta_description(self) -> str:
        return "Join the Big0 team. Explore career opportunities in AI, machine learning, cloud computing, and data analytics."

    @property
    def custom_css(self) -> str:
        return "careers"


class ResourcesPage(Page):
    @property
    def slug(self) -> str:
        return "resources"

    @property
    def title(self) -> str:
        return "Resources"

    @property
    def template(self) -> str:
        return "resources.html"

    @property
    def output_path(self) -> Path:
        return Path("resources.html")

    @property
    def meta_description(self) -> str:
        return "Access whitepapers, guides, case studies, and tools to help your business succeed with AI and digital transformation."

    @property
    def custom_css(self) -> str:
        return "resources"


class AboutPage(Page):
    @property
    def slug(self) -> str:
        return "about"

    @property
    def title(self) -> str:
        return "About Us"

    @property
    def template(self) -> str:
        return "about.html"

    @property
    def output_path(self) -> Path:
        return Path("about.html")

    @property
    def meta_description(self) -> str:
        return "Learn about Big0's mission to transform businesses through responsible AI innovation. Meet our team and discover our values."

    @property
    def custom_css(self) -> str:
        return "about"


class PrivacyPage(Page):
    @property
    def slug(self) -> str:
        return "privacy"

    @property
    def title(self) -> str:
        return "Privacy Policy"

    @property
    def template(self) -> str:
        return "privacy.html"

    @property
    def output_path(self) -> Path:
        return Path("privacy.html")

    @property
    def meta_description(self) -> str:
        return "Big0's privacy policy. Learn how we collect, use, and protect your personal information."

    @property
    def custom_css(self) -> str:
        return "legal"


class TermsPage(Page):
    @property
    def slug(self) -> str:
        return "terms"

    @property
    def title(self) -> str:
        return "Terms of Service"

    @property
    def template(self) -> str:
        return "terms.html"

    @property
    def output_path(self) -> Path:
        return Path("terms.html")

    @property
    def meta_description(self) -> str:
        return "Terms of Service for Big0. Understand the legal agreements that govern the use of our services."

    @property
    def custom_css(self) -> str:
        return "legal"


class ServicesPage(Page):
    """Services listing page"""

    def __init__(self, renderer: TemplateRenderer):
        super().__init__(renderer)
        self._services = []

    def set_services(self, services: List):
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


class NotFoundPage(Page):
    @property
    def slug(self) -> str:
        return "404"

    @property
    def title(self) -> str:
        return "OOPs Not Found"

    @property
    def template(self) -> str:
        return "404.html"

    @property
    def output_path(self) -> Path:
        return Path("404.html")

    @property
    def meta_description(self) -> str:
        return "Page not found"

    def get_context(self) -> Dict[str, Any]:
        return {}

    @property
    def custom_css(self) -> str:
        return "about"


class PartnersPage(Page):
    @property
    def slug(self) -> str:
        return "partners"

    @property
    def title(self) -> str:
        return "Our Partners"

    @property
    def template(self) -> str:
        return "partners.html"

    @property
    def output_path(self) -> Path:
        return Path("partners.html")

    @property
    def meta_description(self) -> str:
        return "Big0 partners with leading technology companies to deliver comprehensive solutions. Explore our strategic partnerships and ecosystem."

    @property
    def custom_css(self) -> str:
        return "partners"
