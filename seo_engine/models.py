"""
Data models for SEO Engine
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class FunnelStage(Enum):
    TOFU = "tofu"  # Top of Funnel - Awareness
    MOFU = "mofu"  # Middle of Funnel - Consideration
    BOFU = "bofu"  # Bottom of Funnel - Decision


class ContentType(Enum):
    SERVICE = "service"
    INDUSTRY = "industry"
    BLOG = "blog"
    CASE_STUDY = "case_study"
    NEWS = "news"
    LOCATION = "location"
    STATIC = "static"


class Priority(Enum):
    CRITICAL = "critical"  # Immediate action needed
    HIGH = "high"          # Should address soon
    MEDIUM = "medium"      # Good opportunity
    LOW = "low"            # Nice to have


@dataclass
class KeywordData:
    """Keyword performance data"""
    keyword: str
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    position: float = 0.0
    search_volume: Optional[int] = None
    difficulty: Optional[float] = None
    trend: Optional[str] = None  # "rising", "stable", "declining"
    funnel_stage: Optional[FunnelStage] = None

    @property
    def opportunity_score(self) -> float:
        """Calculate opportunity score for this keyword"""
        # Higher score = better opportunity
        score = 0.0

        # Position 4-20 = quick win opportunity
        if 4 <= self.position <= 20:
            score += (20 - self.position) * 5

        # High impressions but low CTR = title/description issue
        if self.impressions > 100 and self.ctr < 0.02:
            score += 30

        # Trending keywords get bonus
        if self.trend == "rising":
            score += 20

        # Search volume bonus
        if self.search_volume:
            score += min(self.search_volume / 100, 50)

        # Lower difficulty = easier win
        if self.difficulty:
            score += (100 - self.difficulty) / 2

        return score


@dataclass
class PageData:
    """Page performance and metadata"""
    url: str
    title: str
    meta_description: str = ""
    content_type: ContentType = ContentType.STATIC
    funnel_stage: FunnelStage = FunnelStage.TOFU
    file_path: Optional[str] = None

    # GSC Metrics
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    avg_position: float = 0.0

    # GA4 Metrics
    sessions: int = 0
    bounce_rate: float = 0.0
    avg_time_on_page: float = 0.0
    conversions: int = 0

    # Clarity Metrics
    scroll_depth: float = 0.0
    rage_clicks: int = 0
    dead_clicks: int = 0

    # Keywords
    target_keywords: list[str] = field(default_factory=list)
    ranking_keywords: list[KeywordData] = field(default_factory=list)

    # Analysis
    issues: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    priority: Priority = Priority.MEDIUM

    @property
    def health_score(self) -> float:
        """Calculate overall page health (0-100)"""
        score = 50.0  # Start neutral

        # CTR scoring
        if self.ctr >= 0.05:
            score += 15
        elif self.ctr >= 0.03:
            score += 10
        elif self.ctr < 0.01:
            score -= 15

        # Bounce rate scoring
        if self.bounce_rate <= 0.4:
            score += 15
        elif self.bounce_rate <= 0.6:
            score += 5
        elif self.bounce_rate > 0.8:
            score -= 15

        # Position scoring
        if self.avg_position <= 3:
            score += 20
        elif self.avg_position <= 10:
            score += 10
        elif self.avg_position > 20:
            score -= 10

        # Engagement scoring
        if self.scroll_depth >= 0.7:
            score += 10
        if self.rage_clicks > 5:
            score -= 10

        return max(0, min(100, score))


@dataclass
class ContentRecommendation:
    """AI-generated content recommendation"""
    page_url: str
    recommendation_type: str  # "meta_title", "meta_description", "content", "design"
    current_value: str
    recommended_value: str
    target_keywords: list[str]
    reasoning: str
    priority: Priority
    estimated_impact: str  # "high", "medium", "low"
    funnel_stage: FunnelStage


@dataclass
class DesignRecommendation:
    """Design/UX recommendation based on analytics"""
    page_url: str
    element_type: str  # "cta", "hero", "form", "navigation", "content_block"
    action: str  # "add", "remove", "modify", "reposition"
    description: str
    reasoning: str
    priority: Priority
    based_on: str  # "clarity_heatmap", "bounce_rate", "scroll_depth", etc.


@dataclass
class SEOReport:
    """Complete SEO analysis report"""
    generated_at: datetime
    date_range: tuple[datetime, datetime]

    # Overall metrics
    total_impressions: int = 0
    total_clicks: int = 0
    avg_ctr: float = 0.0
    avg_position: float = 0.0

    # Page analysis
    pages: list[PageData] = field(default_factory=list)

    # Keyword analysis
    top_keywords: list[KeywordData] = field(default_factory=list)
    opportunity_keywords: list[KeywordData] = field(default_factory=list)
    trending_keywords: list[KeywordData] = field(default_factory=list)

    # Recommendations
    content_recommendations: list[ContentRecommendation] = field(default_factory=list)
    design_recommendations: list[DesignRecommendation] = field(default_factory=list)

    # Funnel analysis
    funnel_metrics: dict = field(default_factory=dict)

    # Summary
    critical_issues: list[str] = field(default_factory=list)
    quick_wins: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert report to dictionary for JSON serialization"""
        return {
            "generated_at": self.generated_at.isoformat(),
            "date_range": {
                "start": self.date_range[0].isoformat(),
                "end": self.date_range[1].isoformat(),
            },
            "overview": {
                "total_impressions": self.total_impressions,
                "total_clicks": self.total_clicks,
                "avg_ctr": round(self.avg_ctr * 100, 2),
                "avg_position": round(self.avg_position, 1),
            },
            "pages": [
                {
                    "url": p.url,
                    "title": p.title,
                    "funnel_stage": p.funnel_stage.value,
                    "content_type": p.content_type.value,
                    "health_score": p.health_score,
                    "metrics": {
                        "impressions": p.impressions,
                        "clicks": p.clicks,
                        "ctr": round(p.ctr * 100, 2),
                        "position": round(p.avg_position, 1),
                        "bounce_rate": round(p.bounce_rate * 100, 1),
                    },
                    "target_keywords": p.target_keywords,
                    "issues": p.issues,
                    "opportunities": p.opportunities,
                    "priority": p.priority.value,
                }
                for p in self.pages
            ],
            "keywords": {
                "top": [
                    {
                        "keyword": k.keyword,
                        "impressions": k.impressions,
                        "clicks": k.clicks,
                        "ctr": round(k.ctr * 100, 2),
                        "position": round(k.position, 1),
                        "opportunity_score": round(k.opportunity_score, 1),
                    }
                    for k in self.top_keywords[:20]
                ],
                "opportunities": [
                    {
                        "keyword": k.keyword,
                        "impressions": k.impressions,
                        "position": round(k.position, 1),
                        "opportunity_score": round(k.opportunity_score, 1),
                    }
                    for k in self.opportunity_keywords[:20]
                ],
            },
            "recommendations": {
                "content": [
                    {
                        "page": r.page_url,
                        "type": r.recommendation_type,
                        "current": r.current_value[:100] + "..." if len(r.current_value) > 100 else r.current_value,
                        "recommended": r.recommended_value,
                        "keywords": r.target_keywords,
                        "priority": r.priority.value,
                        "impact": r.estimated_impact,
                    }
                    for r in self.content_recommendations
                ],
                "design": [
                    {
                        "page": r.page_url,
                        "element": r.element_type,
                        "action": r.action,
                        "description": r.description,
                        "priority": r.priority.value,
                    }
                    for r in self.design_recommendations
                ],
            },
            "funnel_analysis": self.funnel_metrics,
            "action_items": {
                "critical": self.critical_issues,
                "quick_wins": self.quick_wins,
            },
        }
