"""
Configuration management for SEO Engine
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv


@dataclass
class Config:
    """SEO Engine configuration"""

    # OpenRouter / AI
    openrouter_api_key: str = ""
    ai_model: str = "xiaomi/mimo-v2-flash:free"  # Free Xiaomi MiMo model - follows instructions well

    # Google Search Console
    gsc_service_account_file: str = ""
    gsc_property_url: str = ""

    # Google Analytics 4
    ga4_service_account_file: str = ""
    ga4_property_id: str = ""

    # Microsoft Clarity
    clarity_project_id: str = ""
    clarity_api_token: str = ""
    clarity_api_endpoint: str = "https://www.clarity.ms/export-data/api/v1/project-live-insights"

    # SEO Tools
    dataforseo_login: str = ""
    dataforseo_password: str = ""
    serpapi_key: str = ""
    seo_tool_mode: str = "free"  # "free", "dataforseo", "serpapi"

    # Site Configuration
    site_domain: str = "https://big0.dev"
    site_name: str = "Big0"
    content_dir: Path = field(default_factory=lambda: Path("./content"))
    output_dir: Path = field(default_factory=lambda: Path("./seo_engine/reports"))
    cache_dir: Path = field(default_factory=lambda: Path("./seo_engine/cache"))

    # Analysis Settings
    min_impressions_threshold: int = 100
    low_ctr_threshold: float = 0.02  # 2%
    high_bounce_threshold: float = 0.70  # 70%
    position_opportunity_range: tuple = (4, 20)  # Quick wins

    @classmethod
    def load(cls, env_file: Optional[str] = None) -> "Config":
        """Load configuration from environment variables"""

        # Find .env file
        if env_file:
            env_path = Path(env_file)
        else:
            # Look in seo_engine directory first, then project root
            seo_engine_dir = Path(__file__).parent
            project_root = seo_engine_dir.parent

            if (seo_engine_dir / ".env").exists():
                env_path = seo_engine_dir / ".env"
            elif (project_root / ".env").exists():
                env_path = project_root / ".env"
            else:
                env_path = seo_engine_dir / ".env"

        load_dotenv(env_path)

        return cls(
            # OpenRouter
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
            ai_model=os.getenv("AI_MODEL", "xiaomi/mimo-v2-flash:free"),

            # GSC
            gsc_service_account_file=os.getenv("GSC_SERVICE_ACCOUNT_FILE", ""),
            gsc_property_url=os.getenv("GSC_PROPERTY_URL", "https://big0.dev/"),

            # GA4
            ga4_service_account_file=os.getenv("GA4_SERVICE_ACCOUNT_FILE", ""),
            ga4_property_id=os.getenv("GA4_PROPERTY_ID", ""),

            # Clarity
            clarity_project_id=os.getenv("CLARITY_PROJECT_ID", "t1zp8ama5q"),
            clarity_api_token=os.getenv("CLARITY_API_TOKEN", ""),
            clarity_api_endpoint=os.getenv("CLARITY_API_ENDPOINT", "https://www.clarity.ms/export-data/api/v1/project-live-insights"),

            # SEO Tools
            dataforseo_login=os.getenv("DATAFORSEO_LOGIN", ""),
            dataforseo_password=os.getenv("DATAFORSEO_PASSWORD", ""),
            serpapi_key=os.getenv("SERPAPI_KEY", ""),
            seo_tool_mode=os.getenv("SEO_TOOL_MODE", "free"),

            # Site
            site_domain=os.getenv("SITE_DOMAIN", "https://big0.dev"),
            site_name=os.getenv("SITE_NAME", "Big0"),
            content_dir=Path(os.getenv("CONTENT_DIR", "./content")),
            output_dir=Path(os.getenv("OUTPUT_DIR", "./seo_engine/reports")),
            cache_dir=Path(os.getenv("CACHE_DIR", "./seo_engine/cache")),
        )

    def validate(self) -> list[str]:
        """Validate configuration and return list of warnings"""
        warnings = []

        if not self.openrouter_api_key:
            warnings.append("OPENROUTER_API_KEY not set - AI features disabled")

        if not self.gsc_service_account_file:
            warnings.append("GSC_SERVICE_ACCOUNT_FILE not set - Search Console data unavailable")
        elif not Path(self.gsc_service_account_file).exists():
            warnings.append(f"GSC service account file not found: {self.gsc_service_account_file}")

        if not self.ga4_service_account_file:
            warnings.append("GA4_SERVICE_ACCOUNT_FILE not set - Analytics data unavailable")
        elif not Path(self.ga4_service_account_file).exists():
            warnings.append(f"GA4 service account file not found: {self.ga4_service_account_file}")

        if not self.content_dir.exists():
            warnings.append(f"Content directory not found: {self.content_dir}")

        return warnings


# Funnel stage definitions
FUNNEL_STAGES = {
    "tofu": {
        "name": "Top of Funnel (Awareness)",
        "keywords": ["what is", "how to", "guide", "tutorial", "introduction", "basics", "learn"],
        "content_types": ["blogs", "guides"],
        "weight": 1.0,
    },
    "mofu": {
        "name": "Middle of Funnel (Consideration)",
        "keywords": ["best", "vs", "comparison", "review", "features", "benefits", "solutions"],
        "content_types": ["services", "industries", "case_studies"],
        "weight": 1.5,
    },
    "bofu": {
        "name": "Bottom of Funnel (Decision)",
        "keywords": ["pricing", "cost", "hire", "company", "agency", "near me", "services in"],
        "content_types": ["contact", "locations"],
        "weight": 2.0,
    },
}

# Industry verticals for keyword targeting
INDUSTRY_VERTICALS = [
    "AI", "machine learning", "software development", "digital transformation",
    "fintech", "healthcare tech", "e-commerce", "enterprise software",
    "automation", "data analytics", "cloud computing", "cybersecurity",
]

# Geographic targets
GEO_TARGETS = {
    "usa": ["new york", "chicago", "san francisco", "los angeles", "boston", "seattle"],
    "pakistan": ["karachi", "lahore", "islamabad"],
    "uk": ["london", "manchester"],
    "uae": ["dubai", "abu dhabi"],
}
