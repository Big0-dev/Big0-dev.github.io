# config.py
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Config:
    """Big0 website configuration"""

    # Paths
    gallery_dir: str = "./content/gallery"
    templates_dir: str = "./templates"
    output_dir: str = "./"
    static_dir: str = "./static"
    blog_dir: str = "./content/blogs"
    services_dir: str = "./content/services"
    industries_dir: str = "./content/industries"
    case_studies_dir: str = "./content/case_studies"
    news_dir: str = "./content/news"

    # Site info
    domain: str = "https://big0.dev"
    base_title: str = "Big0"

    # Features
    posts_per_page: int = 6
    gallery_imgs_per_page: int = 9

    # Redirects
    redirects: Dict[str, str] = field(default_factory=dict)
