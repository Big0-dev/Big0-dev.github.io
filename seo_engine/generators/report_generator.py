"""
Report Generator - Creates comprehensive SEO reports
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import Config
from ..models import (
    SEOReport, PageData, KeywordData, FunnelStage,
    ContentRecommendation, DesignRecommendation, Priority
)
from ..analyzers.content_analyzer import ContentFile
from ..analyzers.funnel_analyzer import FunnelAnalysis
from ..analyzers.opportunity_analyzer import SEOOpportunity


class ReportGenerator:
    """
    Generates comprehensive SEO reports in multiple formats.
    """

    def __init__(self, config: Config):
        self.config = config
        self.output_dir = config.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        content_files: list[ContentFile],
        page_data: list[PageData],
        keyword_data: list[KeywordData],
        funnel_analysis: FunnelAnalysis,
        opportunities: list[SEOOpportunity],
        content_recommendations: list[ContentRecommendation],
        design_recommendations: list[DesignRecommendation],
    ) -> SEOReport:
        """Generate complete SEO report"""

        # Calculate date range (last 28 days)
        end_date = datetime.now()
        start_date = datetime(end_date.year, end_date.month, end_date.day)

        # Aggregate metrics
        total_impressions = sum(p.impressions for p in page_data)
        total_clicks = sum(p.clicks for p in page_data)
        avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
        avg_position = (
            sum(p.avg_position * p.impressions for p in page_data) / total_impressions
            if total_impressions > 0 else 0
        )

        # Sort keywords
        top_keywords = sorted(keyword_data, key=lambda k: k.clicks, reverse=True)[:20]
        opportunity_keywords = sorted(
            [k for k in keyword_data if 4 <= k.position <= 20],
            key=lambda k: k.opportunity_score,
            reverse=True
        )[:20]

        # Critical issues
        critical_issues = []
        for opp in opportunities:
            if opp.priority == Priority.CRITICAL:
                critical_issues.append(opp.recommended_action)

        critical_issues.extend(funnel_analysis.critical_issues)

        # Quick wins
        quick_wins = [
            opp.recommended_action
            for opp in opportunities
            if opp.effort == "quick" and opp.expected_impact == "high"
        ][:10]

        report = SEOReport(
            generated_at=datetime.now(),
            date_range=(start_date, end_date),
            total_impressions=total_impressions,
            total_clicks=total_clicks,
            avg_ctr=avg_ctr,
            avg_position=avg_position,
            pages=page_data,
            top_keywords=top_keywords,
            opportunity_keywords=opportunity_keywords,
            content_recommendations=content_recommendations,
            design_recommendations=design_recommendations,
            funnel_metrics={
                'tofu': {
                    'pages': funnel_analysis.tofu.page_count,
                    'impressions': funnel_analysis.tofu.total_impressions,
                    'ctr': funnel_analysis.tofu.avg_ctr,
                },
                'mofu': {
                    'pages': funnel_analysis.mofu.page_count,
                    'impressions': funnel_analysis.mofu.total_impressions,
                    'ctr': funnel_analysis.mofu.avg_ctr,
                },
                'bofu': {
                    'pages': funnel_analysis.bofu.page_count,
                    'impressions': funnel_analysis.bofu.total_impressions,
                    'ctr': funnel_analysis.bofu.avg_ctr,
                },
                'health_score': funnel_analysis.funnel_health,
            },
            critical_issues=critical_issues,
            quick_wins=quick_wins,
        )

        return report

    def save_json_report(self, report: SEOReport, filename: str = None) -> Path:
        """Save report as JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"seo_report_{timestamp}.json"

        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(report.to_dict(), f, indent=2, default=str)

        print(f"  [Report] JSON saved: {filepath}")
        return filepath

    def save_markdown_report(self, report: SEOReport, filename: str = None) -> Path:
        """Save report as markdown for easy reading"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"seo_report_{timestamp}.md"

        filepath = self.output_dir / filename

        md = []
        md.append("# SEO Analysis Report")
        md.append(f"\n**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M')}")
        md.append(f"**Site:** {self.config.site_domain}")
        md.append("")

        # Executive Summary
        md.append("## Executive Summary")
        md.append("")
        md.append("| Metric | Value |")
        md.append("|--------|-------|")
        md.append(f"| Total Impressions | {report.total_impressions:,} |")
        md.append(f"| Total Clicks | {report.total_clicks:,} |")
        md.append(f"| Average CTR | {report.avg_ctr*100:.2f}% |")
        md.append(f"| Average Position | {report.avg_position:.1f} |")
        md.append(f"| Funnel Health | {report.funnel_metrics.get('health_score', 0):.0f}/100 |")
        md.append("")

        # Critical Issues
        if report.critical_issues:
            md.append("## Critical Issues")
            md.append("")
            for issue in report.critical_issues:
                md.append(f"- {issue}")
            md.append("")

        # Quick Wins
        if report.quick_wins:
            md.append("## Quick Wins (High Impact, Low Effort)")
            md.append("")
            for i, win in enumerate(report.quick_wins[:10], 1):
                md.append(f"{i}. {win}")
            md.append("")

        # Funnel Analysis
        md.append("## Sales Funnel Analysis")
        md.append("")
        md.append("| Stage | Pages | Impressions | CTR |")
        md.append("|-------|-------|-------------|-----|")
        for stage in ['tofu', 'mofu', 'bofu']:
            data = report.funnel_metrics.get(stage, {})
            stage_name = {'tofu': 'Awareness', 'mofu': 'Consideration', 'bofu': 'Decision'}[stage]
            md.append(f"| {stage_name} | {data.get('pages', 0)} | {data.get('impressions', 0):,} | {data.get('ctr', 0)*100:.2f}% |")
        md.append("")

        # Top Keywords
        md.append("## Top Performing Keywords")
        md.append("")
        md.append("| Keyword | Position | Impressions | Clicks | CTR |")
        md.append("|---------|----------|-------------|--------|-----|")
        for kw in report.top_keywords[:15]:
            md.append(f"| {kw.keyword[:40]} | {kw.position:.1f} | {kw.impressions:,} | {kw.clicks} | {kw.ctr*100:.2f}% |")
        md.append("")

        # Opportunity Keywords
        if report.opportunity_keywords:
            md.append("## Keyword Opportunities (Position 4-20)")
            md.append("")
            md.append("| Keyword | Position | Impressions | Opportunity Score |")
            md.append("|---------|----------|-------------|-------------------|")
            for kw in report.opportunity_keywords[:15]:
                md.append(f"| {kw.keyword[:40]} | {kw.position:.1f} | {kw.impressions:,} | {kw.opportunity_score:.0f} |")
            md.append("")

        # Content Recommendations
        if report.content_recommendations:
            md.append("## Content Recommendations")
            md.append("")
            for rec in report.content_recommendations[:20]:
                md.append(f"### {rec.page_url}")
                md.append(f"**Type:** {rec.recommendation_type}")
                md.append(f"**Priority:** {rec.priority.value}")
                md.append(f"**Keywords:** {', '.join(rec.target_keywords[:5])}")
                md.append("")
                if rec.current_value:
                    md.append(f"**Current:** {rec.current_value[:100]}")
                md.append(f"**Recommended:** {rec.recommended_value[:300]}")
                md.append("")

        # Design Recommendations
        if report.design_recommendations:
            md.append("## Design/UX Recommendations")
            md.append("")
            for rec in report.design_recommendations[:10]:
                md.append(f"### {rec.page_url}")
                md.append(f"- **Element:** {rec.element_type}")
                md.append(f"- **Action:** {rec.action}")
                md.append(f"- **Description:** {rec.description}")
                md.append(f"- **Based on:** {rec.based_on}")
                md.append("")

        # Page-by-Page Analysis
        md.append("## Page Performance Summary")
        md.append("")
        md.append("### Pages by Funnel Stage")
        md.append("")

        for stage in [FunnelStage.BOFU, FunnelStage.MOFU, FunnelStage.TOFU]:
            stage_pages = [p for p in report.pages if p.funnel_stage == stage]
            if stage_pages:
                md.append(f"#### {stage.value.upper()} Pages")
                md.append("")
                md.append("| Page | CTR | Position | Health |")
                md.append("|------|-----|----------|--------|")
                for page in sorted(stage_pages, key=lambda p: p.impressions, reverse=True)[:10]:
                    url_short = page.url.replace(self.config.site_domain, '')[:40]
                    md.append(f"| {url_short} | {page.ctr*100:.1f}% | {page.avg_position:.1f} | {page.health_score:.0f} |")
                md.append("")

        with open(filepath, 'w') as f:
            f.write('\n'.join(md))

        print(f"  [Report] Markdown saved: {filepath}")
        return filepath

    def save_content_update_file(
        self,
        content_recommendations: list[ContentRecommendation],
        filename: str = None
    ) -> Path:
        """
        Save a structured file for content updates.
        This can be used to track and implement recommendations.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"content_updates_{timestamp}.json"

        filepath = self.output_dir / filename

        updates = {
            "generated_at": datetime.now().isoformat(),
            "total_recommendations": len(content_recommendations),
            "updates": []
        }

        for rec in content_recommendations:
            updates["updates"].append({
                "page_url": rec.page_url,
                "type": rec.recommendation_type,
                "priority": rec.priority.value,
                "funnel_stage": rec.funnel_stage.value,
                "target_keywords": rec.target_keywords,
                "current_value": rec.current_value,
                "recommended_value": rec.recommended_value,
                "reasoning": rec.reasoning,
                "status": "pending",  # pending, approved, implemented, rejected
            })

        with open(filepath, 'w') as f:
            json.dump(updates, f, indent=2)

        print(f"  [Report] Content updates file saved: {filepath}")
        return filepath

    def save_page_tagging_file(
        self,
        content_files: list[ContentFile],
        filename: str = None
    ) -> Path:
        """
        Save page tagging information (funnel stage, keywords, etc.)
        Useful for CMS integration or content management.
        """
        if filename is None:
            filename = "page_tags.json"

        filepath = self.output_dir / filename

        tags = {
            "generated_at": datetime.now().isoformat(),
            "pages": []
        }

        for cf in content_files:
            tags["pages"].append({
                "url": cf.url,
                "file_path": str(cf.file_path),
                "title": cf.title,
                "content_type": cf.content_type.value,
                "funnel_stage": cf.funnel_stage.value,
                "target_keywords": cf.target_keywords,
                "word_count": cf.word_count,
                "has_cta": cf.has_cta,
                "has_faq": cf.has_faq,
                "internal_links_count": len(cf.internal_links),
                "meta_description_length": len(cf.meta_description) if cf.meta_description else 0,
            })

        with open(filepath, 'w') as f:
            json.dump(tags, f, indent=2)

        print(f"  [Report] Page tagging file saved: {filepath}")
        return filepath

    def generate_all_reports(
        self,
        report: SEOReport,
        content_files: list[ContentFile]
    ) -> dict[str, Path]:
        """Generate all report formats"""
        paths = {}

        # JSON report (full data)
        paths['json'] = self.save_json_report(report)

        # Markdown report (human readable)
        paths['markdown'] = self.save_markdown_report(report)

        # Content updates file
        if report.content_recommendations:
            paths['updates'] = self.save_content_update_file(report.content_recommendations)

        # Page tagging file
        paths['tags'] = self.save_page_tagging_file(content_files)

        return paths
