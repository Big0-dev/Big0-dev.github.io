"""
Opportunity Analyzer - Identifies SEO and conversion opportunities
"""

from dataclasses import dataclass, field
from typing import Optional

from ..config import Config
from ..models import PageData, KeywordData, FunnelStage, Priority
from .content_analyzer import ContentFile


@dataclass
class SEOOpportunity:
    """An SEO optimization opportunity"""
    opportunity_type: str
    priority: Priority
    page_url: Optional[str] = None
    keyword: Optional[str] = None
    current_value: Optional[str] = None
    recommended_action: str = ""
    expected_impact: str = ""  # "high", "medium", "low"
    effort: str = ""  # "quick", "medium", "significant"
    details: dict = field(default_factory=dict)


class OpportunityAnalyzer:
    """
    Analyzes data to identify high-impact SEO opportunities.
    Prioritizes based on:
    - Quick wins (low effort, high impact)
    - Funnel stage importance
    - Current performance gaps
    """

    def __init__(self, config: Config):
        self.config = config

    def analyze_opportunities(
        self,
        content_files: list[ContentFile],
        page_data: list[PageData],
        keyword_data: list[KeywordData]
    ) -> list[SEOOpportunity]:
        """Identify all SEO opportunities"""
        opportunities = []

        # Quick wins: Position 4-20 keywords
        opportunities.extend(self._find_position_opportunities(keyword_data))

        # CTR optimization
        opportunities.extend(self._find_ctr_opportunities(page_data))

        # Content gaps
        opportunities.extend(self._find_content_gaps(content_files, keyword_data))

        # Technical SEO
        opportunities.extend(self._find_technical_opportunities(content_files))

        # Sort by priority and impact
        opportunities.sort(key=lambda x: (
            0 if x.priority == Priority.CRITICAL else
            1 if x.priority == Priority.HIGH else
            2 if x.priority == Priority.MEDIUM else 3,
            0 if x.expected_impact == "high" else
            1 if x.expected_impact == "medium" else 2
        ))

        return opportunities

    def _find_position_opportunities(self, keyword_data: list[KeywordData]) -> list[SEOOpportunity]:
        """Find keywords in striking distance of page 1"""
        opportunities = []

        for kw in keyword_data:
            # Position 4-10: Just need a push
            if 4 <= kw.position <= 10 and kw.impressions > 50:
                opportunities.append(SEOOpportunity(
                    opportunity_type="position_boost",
                    priority=Priority.HIGH,
                    keyword=kw.keyword,
                    current_value=f"Position {kw.position:.1f}",
                    recommended_action=f"Optimize content for '{kw.keyword}' - add to H2/H3, increase keyword density slightly",
                    expected_impact="high",
                    effort="quick",
                    details={
                        'impressions': kw.impressions,
                        'clicks': kw.clicks,
                        'current_position': kw.position,
                    }
                ))

            # Position 11-20: Need more content/links
            elif 11 <= kw.position <= 20 and kw.impressions > 100:
                opportunities.append(SEOOpportunity(
                    opportunity_type="position_improvement",
                    priority=Priority.MEDIUM,
                    keyword=kw.keyword,
                    current_value=f"Position {kw.position:.1f}",
                    recommended_action=f"Create supporting content for '{kw.keyword}' - consider dedicated page or FAQ section",
                    expected_impact="medium",
                    effort="medium",
                    details={
                        'impressions': kw.impressions,
                        'clicks': kw.clicks,
                        'current_position': kw.position,
                    }
                ))

        return opportunities

    def _find_ctr_opportunities(self, page_data: list[PageData]) -> list[SEOOpportunity]:
        """Find pages with poor CTR that need meta optimization"""
        opportunities = []

        for page in page_data:
            # High impressions, low CTR = meta issue
            if page.impressions > 200 and page.ctr < 0.02:
                opportunities.append(SEOOpportunity(
                    opportunity_type="ctr_optimization",
                    priority=Priority.HIGH,
                    page_url=page.url,
                    current_value=f"{page.ctr*100:.1f}% CTR",
                    recommended_action="Rewrite meta title and description with power words, numbers, and clear value proposition",
                    expected_impact="high",
                    effort="quick",
                    details={
                        'impressions': page.impressions,
                        'clicks': page.clicks,
                        'current_title': page.title,
                        'current_meta': page.meta_description,
                    }
                ))

            # Good position but low CTR
            elif page.avg_position <= 5 and page.ctr < 0.04 and page.impressions > 100:
                opportunities.append(SEOOpportunity(
                    opportunity_type="featured_snippet",
                    priority=Priority.MEDIUM,
                    page_url=page.url,
                    current_value=f"Position {page.avg_position:.1f}, {page.ctr*100:.1f}% CTR",
                    recommended_action="Add structured data, FAQ schema, or table format to target featured snippets",
                    expected_impact="high",
                    effort="medium",
                    details={
                        'position': page.avg_position,
                        'ctr': page.ctr,
                    }
                ))

        return opportunities

    def _find_content_gaps(
        self,
        content_files: list[ContentFile],
        keyword_data: list[KeywordData]
    ) -> list[SEOOpportunity]:
        """Find keyword opportunities not covered by existing content"""
        opportunities = []

        # Get all keywords mentioned in existing content
        existing_keywords = set()
        for cf in content_files:
            existing_keywords.update(kw.lower() for kw in cf.target_keywords)
            # Also add words from titles
            existing_keywords.update(cf.title.lower().split())

        # Find high-value keywords not in content
        for kw in keyword_data:
            kw_lower = kw.keyword.lower()
            kw_words = set(kw_lower.split())

            # Check if keyword or its main words are covered
            is_covered = any(word in existing_keywords for word in kw_words if len(word) > 4)

            if not is_covered and kw.impressions > 50:
                opportunities.append(SEOOpportunity(
                    opportunity_type="content_gap",
                    priority=Priority.MEDIUM,
                    keyword=kw.keyword,
                    current_value="No dedicated content",
                    recommended_action=f"Create new content targeting '{kw.keyword}' or add section to existing page",
                    expected_impact="medium",
                    effort="significant",
                    details={
                        'impressions': kw.impressions,
                        'search_volume': kw.search_volume,
                        'suggested_funnel_stage': self._classify_keyword_intent(kw.keyword),
                    }
                ))

        return opportunities

    def _find_technical_opportunities(self, content_files: list[ContentFile]) -> list[SEOOpportunity]:
        """Find technical SEO opportunities"""
        opportunities = []

        for cf in content_files:
            # Missing meta description
            if not cf.meta_description:
                opportunities.append(SEOOpportunity(
                    opportunity_type="missing_meta",
                    priority=Priority.HIGH,
                    page_url=cf.url,
                    current_value="No meta description",
                    recommended_action="Add meta description (150-160 characters) with target keyword and CTA",
                    expected_impact="high",
                    effort="quick",
                    details={'file': str(cf.file_path)}
                ))

            # Too short meta description
            elif len(cf.meta_description) < 100:
                opportunities.append(SEOOpportunity(
                    opportunity_type="short_meta",
                    priority=Priority.MEDIUM,
                    page_url=cf.url,
                    current_value=f"{len(cf.meta_description)} characters",
                    recommended_action="Expand meta description to 150-160 characters for better SERP presence",
                    expected_impact="medium",
                    effort="quick",
                    details={'current_meta': cf.meta_description}
                ))

            # Thin content
            if cf.word_count < 300:
                opportunities.append(SEOOpportunity(
                    opportunity_type="thin_content",
                    priority=Priority.MEDIUM,
                    page_url=cf.url,
                    current_value=f"{cf.word_count} words",
                    recommended_action="Expand content to at least 800-1000 words with detailed information",
                    expected_impact="medium",
                    effort="significant",
                    details={'file': str(cf.file_path)}
                ))

            # Missing internal links (for non-blog content)
            if len(cf.internal_links) < 2 and cf.content_type.value != 'blog':
                opportunities.append(SEOOpportunity(
                    opportunity_type="internal_linking",
                    priority=Priority.LOW,
                    page_url=cf.url,
                    current_value=f"{len(cf.internal_links)} internal links",
                    recommended_action="Add 3-5 internal links to related services, industries, or case studies",
                    expected_impact="low",
                    effort="quick",
                    details={'file': str(cf.file_path)}
                ))

        return opportunities

    def _classify_keyword_intent(self, keyword: str) -> str:
        """Classify keyword by search intent/funnel stage"""
        kw_lower = keyword.lower()

        # BOFU signals
        bofu_words = ['hire', 'agency', 'company', 'services', 'cost', 'pricing', 'near me', 'in']
        if any(word in kw_lower for word in bofu_words):
            return 'bofu'

        # MOFU signals
        mofu_words = ['best', 'vs', 'comparison', 'review', 'solution', 'platform', 'tool']
        if any(word in kw_lower for word in mofu_words):
            return 'mofu'

        # TOFU signals (default)
        return 'tofu'

    def get_quick_wins(self, opportunities: list[SEOOpportunity], limit: int = 10) -> list[SEOOpportunity]:
        """Get quick wins - high impact, low effort opportunities"""
        quick_wins = [
            opp for opp in opportunities
            if opp.effort == "quick" and opp.expected_impact in ["high", "medium"]
        ]
        return quick_wins[:limit]

    def get_priority_summary(self, opportunities: list[SEOOpportunity]) -> dict:
        """Get summary of opportunities by priority"""
        return {
            'critical': len([o for o in opportunities if o.priority == Priority.CRITICAL]),
            'high': len([o for o in opportunities if o.priority == Priority.HIGH]),
            'medium': len([o for o in opportunities if o.priority == Priority.MEDIUM]),
            'low': len([o for o in opportunities if o.priority == Priority.LOW]),
            'quick_wins': len([o for o in opportunities if o.effort == "quick"]),
        }
