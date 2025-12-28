"""
Funnel Analyzer - Analyzes the sales funnel performance
"""

from dataclasses import dataclass, field
from typing import Optional

from ..config import Config, FUNNEL_STAGES
from ..models import PageData, FunnelStage, Priority
from .content_analyzer import ContentFile


@dataclass
class FunnelStageMetrics:
    """Metrics for a funnel stage"""
    stage: FunnelStage
    name: str
    page_count: int = 0
    total_impressions: int = 0
    total_clicks: int = 0
    total_sessions: int = 0
    total_conversions: int = 0
    avg_ctr: float = 0.0
    avg_bounce_rate: float = 0.0
    avg_position: float = 0.0
    top_pages: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


@dataclass
class FunnelAnalysis:
    """Complete funnel analysis"""
    tofu: FunnelStageMetrics
    mofu: FunnelStageMetrics
    bofu: FunnelStageMetrics
    funnel_health: float = 0.0  # 0-100 score
    critical_issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class FunnelAnalyzer:
    """
    Analyzes the sales funnel to identify:
    - Drop-off points
    - Stage imbalances
    - Conversion optimization opportunities
    """

    def __init__(self, config: Config):
        self.config = config

    def analyze_funnel(
        self,
        content_files: list[ContentFile],
        page_data: list[PageData]
    ) -> FunnelAnalysis:
        """Perform complete funnel analysis"""

        # Create lookup for page data
        page_metrics = {p.url: p for p in page_data}

        # Initialize stage metrics
        stages = {
            FunnelStage.TOFU: FunnelStageMetrics(
                stage=FunnelStage.TOFU,
                name=FUNNEL_STAGES['tofu']['name']
            ),
            FunnelStage.MOFU: FunnelStageMetrics(
                stage=FunnelStage.MOFU,
                name=FUNNEL_STAGES['mofu']['name']
            ),
            FunnelStage.BOFU: FunnelStageMetrics(
                stage=FunnelStage.BOFU,
                name=FUNNEL_STAGES['bofu']['name']
            ),
        }

        # Aggregate metrics by stage
        for cf in content_files:
            stage = stages[cf.funnel_stage]
            stage.page_count += 1

            # Get corresponding page metrics if available
            page = page_metrics.get(cf.url)
            if page:
                stage.total_impressions += page.impressions
                stage.total_clicks += page.clicks
                stage.total_sessions += page.sessions
                stage.total_conversions += page.conversions

        # Calculate averages
        for stage in stages.values():
            if stage.page_count > 0:
                if stage.total_impressions > 0:
                    stage.avg_ctr = stage.total_clicks / stage.total_impressions

        # Identify issues
        self._identify_stage_issues(stages, content_files, page_data)

        # Calculate funnel health
        health = self._calculate_funnel_health(stages)

        # Generate recommendations
        recommendations = self._generate_recommendations(stages, content_files)

        # Compile critical issues
        critical = []
        for stage in stages.values():
            critical.extend([i for i in stage.issues if 'critical' in i.lower()])

        return FunnelAnalysis(
            tofu=stages[FunnelStage.TOFU],
            mofu=stages[FunnelStage.MOFU],
            bofu=stages[FunnelStage.BOFU],
            funnel_health=health,
            critical_issues=critical,
            recommendations=recommendations,
        )

    def _identify_stage_issues(
        self,
        stages: dict[FunnelStage, FunnelStageMetrics],
        content_files: list[ContentFile],
        page_data: list[PageData]
    ) -> None:
        """Identify issues at each funnel stage"""

        total_pages = sum(s.page_count for s in stages.values())

        # TOFU issues
        tofu = stages[FunnelStage.TOFU]
        if total_pages > 0:
            tofu_pct = tofu.page_count / total_pages
            if tofu_pct < 0.25:
                tofu.issues.append("CRITICAL: Insufficient awareness content. Need more blog posts and guides.")
            if tofu.avg_ctr < 0.02 and tofu.total_impressions > 1000:
                tofu.issues.append("Low CTR on awareness content. Review meta titles and descriptions.")

        # MOFU issues
        mofu = stages[FunnelStage.MOFU]
        if total_pages > 0:
            mofu_pct = mofu.page_count / total_pages
            if mofu_pct < 0.3:
                mofu.issues.append("CRITICAL: Insufficient consideration content. Add more case studies and solution pages.")

            # Check conversion from TOFU to MOFU
            if tofu.total_sessions > 0 and mofu.total_sessions > 0:
                tofu_to_mofu = mofu.total_sessions / tofu.total_sessions
                if tofu_to_mofu < 0.1:
                    mofu.issues.append("Poor TOFU->MOFU conversion. Add stronger CTAs in awareness content.")

        # BOFU issues
        bofu = stages[FunnelStage.BOFU]
        if total_pages > 0:
            bofu_pct = bofu.page_count / total_pages
            if bofu_pct < 0.15:
                bofu.issues.append("Limited decision-stage content. Add location pages and pricing content.")

            if bofu.total_sessions > 0 and bofu.total_conversions == 0:
                bofu.issues.append("CRITICAL: No conversions from decision-stage content. Review CTAs and forms.")

    def _calculate_funnel_health(self, stages: dict[FunnelStage, FunnelStageMetrics]) -> float:
        """Calculate overall funnel health score (0-100)"""
        score = 50.0  # Start at neutral

        total_pages = sum(s.page_count for s in stages.values())
        if total_pages == 0:
            return 0.0

        # Balance scoring (ideal: 40% TOFU, 40% MOFU, 20% BOFU)
        tofu_pct = stages[FunnelStage.TOFU].page_count / total_pages
        mofu_pct = stages[FunnelStage.MOFU].page_count / total_pages
        bofu_pct = stages[FunnelStage.BOFU].page_count / total_pages

        # Penalize imbalance
        if 0.3 <= tofu_pct <= 0.5:
            score += 10
        if 0.3 <= mofu_pct <= 0.5:
            score += 10
        if 0.15 <= bofu_pct <= 0.3:
            score += 10

        # CTR scoring
        total_ctr = sum(s.avg_ctr for s in stages.values()) / 3
        if total_ctr >= 0.04:
            score += 15
        elif total_ctr >= 0.02:
            score += 5

        # Penalize issues
        total_issues = sum(len(s.issues) for s in stages.values())
        score -= total_issues * 5

        # Conversion bonus
        if stages[FunnelStage.BOFU].total_conversions > 0:
            score += 15

        return max(0, min(100, score))

    def _generate_recommendations(
        self,
        stages: dict[FunnelStage, FunnelStageMetrics],
        content_files: list[ContentFile]
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        tofu = stages[FunnelStage.TOFU]
        mofu = stages[FunnelStage.MOFU]
        bofu = stages[FunnelStage.BOFU]

        # Content balance recommendations
        total = sum(s.page_count for s in stages.values())
        if total > 0:
            if tofu.page_count / total < 0.3:
                recommendations.append(
                    "Add more awareness content: Create 5-10 educational blog posts targeting 'what is' and 'how to' queries"
                )

            if mofu.page_count / total < 0.3:
                recommendations.append(
                    "Add more consideration content: Create case studies for each major industry vertical"
                )

            if bofu.page_count / total < 0.15:
                recommendations.append(
                    "Add more decision content: Create location-specific landing pages for target markets"
                )

        # CTR recommendations
        if tofu.avg_ctr < 0.02 and tofu.total_impressions > 500:
            recommendations.append(
                "Improve TOFU CTR: Use power words and numbers in blog post titles (e.g., '7 Ways to...', 'Complete Guide')"
            )

        if mofu.avg_ctr < 0.03 and mofu.total_impressions > 500:
            recommendations.append(
                "Improve MOFU CTR: Add specific outcomes/results in meta descriptions (e.g., '50% cost reduction')"
            )

        if bofu.avg_ctr < 0.04 and bofu.total_impressions > 200:
            recommendations.append(
                "Improve BOFU CTR: Add location and urgency to meta titles (e.g., 'AI Services in NYC - Free Consultation')"
            )

        # Conversion recommendations
        if bofu.total_sessions > 50 and bofu.total_conversions == 0:
            recommendations.append(
                "URGENT: Decision pages getting traffic but no conversions. Review contact forms, add chat widget, simplify CTAs"
            )

        # Internal linking
        tofu_files = [cf for cf in content_files if cf.funnel_stage == FunnelStage.TOFU]
        no_links = [cf for cf in tofu_files if len(cf.internal_links) < 2]
        if len(no_links) > 3:
            recommendations.append(
                f"Add internal links: {len(no_links)} TOFU pages lack links to MOFU/BOFU content"
            )

        return recommendations

    def get_funnel_summary(self, analysis: FunnelAnalysis) -> dict:
        """Get a summary dictionary for the report"""
        return {
            'health_score': round(analysis.funnel_health, 1),
            'stages': {
                'tofu': {
                    'name': analysis.tofu.name,
                    'pages': analysis.tofu.page_count,
                    'impressions': analysis.tofu.total_impressions,
                    'clicks': analysis.tofu.total_clicks,
                    'ctr': round(analysis.tofu.avg_ctr * 100, 2),
                    'issues': analysis.tofu.issues,
                },
                'mofu': {
                    'name': analysis.mofu.name,
                    'pages': analysis.mofu.page_count,
                    'impressions': analysis.mofu.total_impressions,
                    'clicks': analysis.mofu.total_clicks,
                    'ctr': round(analysis.mofu.avg_ctr * 100, 2),
                    'issues': analysis.mofu.issues,
                },
                'bofu': {
                    'name': analysis.bofu.name,
                    'pages': analysis.bofu.page_count,
                    'impressions': analysis.bofu.total_impressions,
                    'clicks': analysis.bofu.total_clicks,
                    'ctr': round(analysis.bofu.avg_ctr * 100, 2),
                    'issues': analysis.bofu.issues,
                },
            },
            'critical_issues': analysis.critical_issues,
            'recommendations': analysis.recommendations,
        }
