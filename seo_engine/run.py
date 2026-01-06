#!/usr/bin/env python3
"""
Big0 SEO Engine - Main Runner

A local SEO automation tool that:
1. Pulls data from GSC, GA4, and Clarity
2. Analyzes content and identifies opportunities
3. Uses DeepSeek AI to generate recommendations
4. Produces detailed reports with funnel tagging

Usage:
    uv run python -m seo_engine.run [options]

Options:
    --full          Run full analysis with AI recommendations
    --quick         Quick analysis without AI (faster, no API costs)
    --collect-only  Only collect data from APIs (cache for later)
    --analyze-only  Analyze cached data only
    --help          Show this help message
"""

import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from seo_engine.config import Config
from seo_engine.models import PageData, KeywordData, FunnelStage
from seo_engine.collectors import (
    GoogleSearchConsoleCollector,
    GoogleAnalyticsCollector,
    ClarityCollector,
    KeywordResearchCollector,
)
from seo_engine.analyzers import (
    ContentAnalyzer,
    FunnelAnalyzer,
    OpportunityAnalyzer,
)
from seo_engine.generators import (
    AIContentEngine,
    ReportGenerator,
    BlogGenerator,
)


def print_banner():
    """Print startup banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    Big0 SEO Engine v1.0                      ║
║          AI-Powered SEO Optimization & Lead Generation       ║
╚══════════════════════════════════════════════════════════════╝
""")


def check_exports_status(config: Config) -> dict:
    """
    Check the status of manual exports that contain data not available via API.
    Returns dict with export status for each service.
    """
    exports_dir = Path(__file__).parent / "exports"
    stale_days = 7  # Consider exports stale after 7 days
    now = datetime.now()

    status = {
        'gsc': {
            'name': 'Google Search Console',
            'dir': exports_dir / 'gsc',
            'exports': [],
            'stale': [],
            'missing': [
                'coverage-drilldown',  # 404s, crawl errors, excluded pages
                'core-web-vitals',     # LCP, FID, CLS issues
                'mobile-usability',    # Mobile issues
            ],
            'dashboard_url': 'https://search.google.com/search-console?resource_id=sc-domain%3Abig0.dev',
        },
        'ga4': {
            'name': 'Google Analytics 4',
            'dir': exports_dir / 'ga4',
            'exports': [],
            'stale': [],
            'missing': [
                'funnel-exploration',  # Conversion funnels
                'path-exploration',    # User paths
            ],
            'dashboard_url': 'https://analytics.google.com/analytics/web/#/p491064548/reports/intelligenthome',
        },
        'clarity': {
            'name': 'Microsoft Clarity',
            'dir': exports_dir / 'clarity',
            'exports': [],
            'stale': [],
            'missing': [
                'heatmaps',           # Click/scroll heatmaps
                'session-recordings',  # User session videos (not exportable)
            ],
            'dashboard_url': 'https://clarity.microsoft.com/projects/view/t1zp8ama5q/dashboard',
        },
    }

    for service_key, service in status.items():
        service_dir = service['dir']
        if service_dir.exists():
            for f in service_dir.iterdir():
                if f.is_file() and f.suffix in ['.csv', '.json', '.png', '.txt']:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    age_days = (now - mtime).days

                    export_info = {
                        'file': f.name,
                        'date': mtime.strftime('%Y-%m-%d'),
                        'age_days': age_days,
                    }

                    service['exports'].append(export_info)

                    if age_days > stale_days:
                        service['stale'].append(export_info)

                    # Remove from missing if we have a recent version
                    for missing_type in service['missing'][:]:
                        if missing_type in f.name.lower():
                            if age_days <= stale_days:
                                service['missing'].remove(missing_type)

    return status


def prompt_export_updates(config: Config, skip_prompt: bool = False) -> None:
    """
    Check for stale/missing exports and prompt user to update them.
    """
    status = check_exports_status(config)

    has_issues = False
    for service_key, service in status.items():
        if service['stale'] or service['missing']:
            has_issues = True
            break

    if not has_issues:
        return

    print("\n[Exports Check] Dashboard data not available via API:")
    print("-" * 60)

    for service_key, service in status.items():
        if not service['stale'] and not service['missing']:
            continue

        print(f"\n  {service['name']}:")

        if service['stale']:
            print("    Stale exports (>7 days old):")
            for exp in service['stale']:
                print(f"      - {exp['file']} ({exp['age_days']} days old)")

        if service['missing']:
            print("    Missing exports:")
            for missing in service['missing']:
                print(f"      - {missing}")

        print(f"    Dashboard: {service['dashboard_url']}")

    print("\n" + "-" * 60)
    print("  These reports contain data NOT available via API:")
    print("    - GSC: 404 errors, crawl errors, Core Web Vitals, mobile issues")
    print("    - GA4: Funnel visualizations, path explorations, cohort data")
    print("    - Clarity: Heatmaps, session recordings")
    print("\n  See: seo_engine/exports/README.md for export instructions")
    print("-" * 60)

    if skip_prompt:
        return

    # Ask user if they want to open dashboards
    try:
        response = input("\nOpen dashboards to update exports? [y/N]: ").strip().lower()
        if response == 'y':
            import webbrowser
            for service_key, service in status.items():
                if service['stale'] or service['missing']:
                    print(f"  Opening {service['name']}...")
                    webbrowser.open(service['dashboard_url'])
            print("\n  Export files to: seo_engine/exports/<service>/")
            input("  Press Enter when done exporting to continue...")
    except (EOFError, KeyboardInterrupt):
        print("\n  Skipping export update prompt.")


def show_exports_status(config: Config) -> None:
    """Display current exports status"""
    status = check_exports_status(config)

    print("\n" + "=" * 60)
    print("              MANUAL EXPORTS STATUS")
    print("=" * 60)

    for service_key, service in status.items():
        print(f"\n{service['name']}:")
        print(f"  Directory: {service['dir']}")

        if service['exports']:
            print("  Current exports:")
            for exp in service['exports']:
                stale_marker = " (STALE)" if exp['age_days'] > 7 else ""
                print(f"    - {exp['file']} [{exp['date']}]{stale_marker}")
        else:
            print("  No exports found")

        if service['missing']:
            print("  Missing/Stale:")
            for missing in service['missing']:
                print(f"    - {missing}")

    print("\n" + "=" * 60)
    print("Data available via Dashboard ONLY (not API):")
    print("-" * 60)
    print("""
Google Search Console:
  - Index Coverage (404s, crawl errors, excluded URLs)
  - Core Web Vitals (LCP, FID, CLS by URL)
  - Mobile Usability issues
  - Sitemaps status
  - Internal/External links report
  - Rich results status

Google Analytics 4:
  - Funnel Exploration (visual conversion funnels)
  - Path Exploration (user navigation flows)
  - User Explorer (individual journeys)
  - Cohort Analysis (retention by cohort)
  - Attribution modeling
  - Predictive metrics (churn/purchase probability)

Microsoft Clarity:
  - Session Recordings (video playback - not exportable)
  - Heatmaps (click, scroll, area maps)
  - Funnels (custom conversion funnels)
  - Copilot AI insights
""")
    print("=" * 60)


def run_full_analysis(config: Config, use_ai: bool = True):
    """Run complete SEO analysis"""

    print("\n[1/6] Loading Configuration...")
    warnings = config.validate()
    for warning in warnings:
        print(f"  ⚠️  {warning}")

    # Initialize collectors
    print("\n[2/6] Collecting Data...")

    gsc = GoogleSearchConsoleCollector(config)
    ga4 = GoogleAnalyticsCollector(config)
    clarity = ClarityCollector(config)
    keywords = KeywordResearchCollector(config)

    # Collect from each source
    gsc_initialized = gsc.initialize()
    ga4_initialized = ga4.initialize()
    clarity_initialized = clarity.initialize()

    # Get GSC data
    gsc_queries = []
    gsc_pages = []
    if gsc_initialized:
        print("  [GSC] Fetching search analytics...")
        gsc_queries = gsc.get_top_queries(limit=500)
        gsc_pages = gsc.get_page_performance(limit=300)
        gsc.cache_data(config.cache_dir / "gsc_data.json")
        print(f"  [GSC] Retrieved {len(gsc_queries)} queries, {len(gsc_pages)} pages")

    # Get GA4 data
    ga4_pages = []
    if ga4_initialized:
        print("  [GA4] Fetching analytics data...")
        ga4_pages = ga4.get_page_metrics(limit=200)
        ga4.cache_data(config.cache_dir / "ga4_data.json")
        print(f"  [GA4] Retrieved metrics for {len(ga4_pages)} pages")

    # Get Clarity data
    clarity_pages = []
    if clarity_initialized:
        clarity_pages = clarity.get_page_metrics()
        clarity.cache_data(config.cache_dir / "clarity_data.json")
        print(f"  [Clarity] Retrieved {len(clarity_pages)} page metrics")

    # Get keyword suggestions
    print("  [Keywords] Collecting keyword data...")
    keyword_suggestions = keywords.collect_keywords()
    print(f"  [Keywords] Collected {len(keyword_suggestions)} suggestions")

    # Analyze content
    print("\n[3/6] Analyzing Content...")

    content_analyzer = ContentAnalyzer(config)
    content_files = content_analyzer.scan_all_content()

    content_gaps = content_analyzer.get_content_gaps(content_files)
    optimization_opps = content_analyzer.get_optimization_opportunities(content_files)

    print(f"  Found {len(content_gaps)} content gaps")
    print(f"  Found {len(optimization_opps)} optimization opportunities")

    # Build PageData objects by merging data sources
    print("\n[4/6] Merging Data Sources...")

    page_data = []
    gsc_page_map = {p.page: p for p in gsc_pages}
    ga4_page_map = {p.page_path: p for p in ga4_pages}
    clarity_page_map = {p.page_url: p for p in clarity_pages}

    for cf in content_files:
        # Get relative path for matching
        url_path = cf.url.replace(config.site_domain, '')

        # Find matching GSC data
        gsc_match = gsc_page_map.get(cf.url)

        # Find matching GA4 data
        ga4_match = ga4_page_map.get(url_path)

        # Find matching Clarity data
        clarity_match = clarity_page_map.get(cf.url) or clarity_page_map.get(url_path)

        pd = PageData(
            url=cf.url,
            title=cf.title,
            meta_description=cf.meta_description,
            content_type=cf.content_type,
            funnel_stage=cf.funnel_stage,
            file_path=str(cf.file_path),
            target_keywords=cf.target_keywords,
        )

        if gsc_match:
            pd.impressions = gsc_match.impressions
            pd.clicks = gsc_match.clicks
            pd.ctr = gsc_match.ctr
            pd.avg_position = gsc_match.position

        if ga4_match:
            pd.sessions = ga4_match.sessions
            pd.bounce_rate = ga4_match.bounce_rate
            pd.avg_time_on_page = ga4_match.avg_session_duration
            pd.conversions = ga4_match.conversions

        if clarity_match:
            pd.scroll_depth = clarity_match.scroll_depth
            pd.rage_clicks = clarity_match.rage_clicks
            pd.dead_clicks = clarity_match.dead_clicks

        page_data.append(pd)

    print(f"  Merged data for {len(page_data)} pages")

    # Convert GSC queries to KeywordData
    keyword_data = [
        KeywordData(
            keyword=q.query,
            impressions=q.impressions,
            clicks=q.clicks,
            ctr=q.ctr,
            position=q.position,
        )
        for q in gsc_queries
    ]

    # Funnel analysis
    print("\n[5/6] Analyzing Sales Funnel...")

    funnel_analyzer = FunnelAnalyzer(config)
    funnel_analysis = funnel_analyzer.analyze_funnel(content_files, page_data)

    print(f"  Funnel health score: {funnel_analysis.funnel_health:.0f}/100")
    print(f"  TOFU pages: {funnel_analysis.tofu.page_count}")
    print(f"  MOFU pages: {funnel_analysis.mofu.page_count}")
    print(f"  BOFU pages: {funnel_analysis.bofu.page_count}")

    # Opportunity analysis
    opportunity_analyzer = OpportunityAnalyzer(config)
    opportunities = opportunity_analyzer.analyze_opportunities(
        content_files, page_data, keyword_data
    )

    quick_wins = opportunity_analyzer.get_quick_wins(opportunities)
    print(f"  Found {len(opportunities)} opportunities ({len(quick_wins)} quick wins)")

    # AI recommendations
    content_recommendations = []
    design_recommendations = []

    if use_ai and config.openrouter_api_key:
        print("\n[6/6] Generating AI Recommendations...")

        ai_engine = AIContentEngine(config)

        # Build keyword map for pages
        keyword_map = {}
        for cf in content_files:
            # Get keywords from GSC for this page
            page_keywords = [
                q.query for q in gsc_queries
                if q.page and (q.page == cf.url or cf.url.endswith(q.page.split('/')[-1] if '/' in q.page else ''))
            ][:10]
            keyword_map[cf.url] = page_keywords or cf.target_keywords

        content_recommendations = ai_engine.batch_generate_recommendations(
            content_files,
            keyword_map,
            limit=200  # Process all pages - using low-cost model
        )

        # Generate design recommendations for problem pages
        problem_pages = [
            pd for pd in page_data
            if pd.bounce_rate > 0.7 or pd.rage_clicks > 5 or pd.scroll_depth < 0.3
        ][:20]  # Analyze more problem pages

        for pd in problem_pages:
            clarity_issues = [
                {'description': f'High bounce rate: {pd.bounce_rate*100:.0f}%'}
                if pd.bounce_rate > 0.7 else None,
                {'description': f'Low scroll depth: {pd.scroll_depth*100:.0f}%'}
                if pd.scroll_depth < 0.3 else None,
                {'description': f'Rage clicks detected: {pd.rage_clicks}'}
                if pd.rage_clicks > 5 else None,
            ]
            clarity_issues = [i for i in clarity_issues if i]

            recs = ai_engine.generate_design_recommendations(pd, clarity_issues)
            design_recommendations.extend(recs)

    else:
        print("\n[6/6] Skipping AI Recommendations (API key not configured or quick mode)")

    # Generate reports
    print("\n[Report] Generating Reports...")

    report_generator = ReportGenerator(config)

    report = report_generator.generate_report(
        content_files=content_files,
        page_data=page_data,
        keyword_data=keyword_data,
        funnel_analysis=funnel_analysis,
        opportunities=opportunities,
        content_recommendations=content_recommendations,
        design_recommendations=design_recommendations,
    )

    report_paths = report_generator.generate_all_reports(report, content_files)

    # Summary
    print("\n" + "="*60)
    print("                    ANALYSIS COMPLETE")
    print("="*60)
    print(f"""
Summary:
  - Total Pages Analyzed: {len(content_files)}
  - Total Keywords Tracked: {len(keyword_data)}
  - Funnel Health Score: {funnel_analysis.funnel_health:.0f}/100
  - Critical Issues: {len(report.critical_issues)}
  - Quick Wins Identified: {len(report.quick_wins)}
  - AI Recommendations: {len(content_recommendations)}

Reports Generated:
""")
    for name, path in report_paths.items():
        print(f"  - {name}: {path}")

    print(f"""
Next Steps:
  1. Review the markdown report for quick insights
  2. Check content_updates.json for specific changes
  3. Implement quick wins first for fastest impact
  4. Run again after implementing changes to track progress
""")

    return report


def run_quick_analysis(config: Config):
    """Run quick analysis without AI (faster, no API costs)"""
    return run_full_analysis(config, use_ai=False)


def run_collect_only(config: Config):
    """Only collect and cache data from APIs"""
    print("\n[Collect Mode] Collecting data from all sources...")

    gsc = GoogleSearchConsoleCollector(config)
    ga4 = GoogleAnalyticsCollector(config)
    clarity = ClarityCollector(config)
    keywords = KeywordResearchCollector(config)

    if gsc.initialize():
        gsc.cache_data(config.cache_dir / "gsc_data.json")

    if ga4.initialize():
        ga4.cache_data(config.cache_dir / "ga4_data.json")

    if clarity.initialize():
        clarity.cache_data(config.cache_dir / "clarity_data.json")

    keywords.collect_keywords()

    print("\n[Complete] Data cached for later analysis")


def run_apply_recommendations(config: Config, dry_run: bool = False, auto_approve: bool = False):
    """Apply the latest AI recommendations to content files"""
    from .appliers.content_applier import apply_latest_recommendations
    apply_latest_recommendations(config, dry_run=dry_run, auto_approve=auto_approve)


def run_track_rankings(config: Config, report: bool = False):
    """Sync rankings from GSC and optionally generate report"""
    from .tracking import RankTracker
    from .tracking.rank_tracker import sync_rankings_from_gsc

    print("\n[Rank Tracking] Syncing rankings from GSC...")

    count = sync_rankings_from_gsc(config)
    print(f"  Recorded {count} keyword rankings")

    tracker = RankTracker(config)
    stats = tracker.get_summary_stats()

    print(f"""
  Summary:
    - Keywords tracked: {stats['unique_keywords']}
    - Pages tracked: {stats['unique_pages']}
    - Tracking days: {stats['tracking_days']}
    - Average position: {stats['avg_position']:.1f}
""")

    if report:
        report_content = tracker.generate_tracking_report()
        report_path = config.output_dir / f"rank_report_{datetime.now().strftime('%Y%m%d')}.md"
        report_path.write_text(report_content)
        print(f"  Report saved: {report_path}")

    # Show top movers
    improving = tracker.get_improving_keywords(limit=5)
    declining = tracker.get_declining_keywords(limit=5)

    if improving:
        print("  Top Improving Keywords:")
        for t in improving:
            print(f"    - {t.keyword[:35]}: +{t.position_change:.1f} (now #{t.current_position:.0f})")

    if declining:
        print("\n  Declining Keywords:")
        for t in declining:
            print(f"    - {t.keyword[:35]}: {t.position_change:.1f} (now #{t.current_position:.0f})")


def show_content_guide():
    """Display the content writing guide"""
    guide_path = Path(__file__).parent / "CONTENT_GUIDE.md"

    if guide_path.exists():
        print(guide_path.read_text())
    else:
        print("""
Content Writing Guide - Quick Reference
========================================

Location of content files:
  - Services:     content/services/*.md
  - Industries:   content/industries/*.md
  - Blogs:        content/blogs/*.md
  - Case Studies: content/case_studies/*.md
  - News:         content/news/*.md
  - Locations:    content/services/locations/[country]/*.md

Full guide: seo_engine/CONTENT_GUIDE.md

Key Frontmatter Fields:
-----------------------

Services:
  title, meta_description, description, icon, features

Industries:
  title, meta_description, description, icon, challenge, solutions

Blogs:
  title, category, date, meta_description, tags

Case Studies:
  title, industry, type, challenge, solution, results, technologies

Template Directives:
-------------------
  {{template:cta}}              - Generic CTA
  {{template:cta-service}}      - Service CTA
  {{template:cta-location-usa}} - Location CTA
  {{related-services:a,b}}      - Link services
  {{related-industries:a,b}}    - Link industries
""")


def run_generate_blogs(config: Config, count: int = 3):
    """Generate blog posts based on keyword opportunities"""
    print("\n[Blog Generation] Starting TOFU content generation...")

    # Get keyword data from GSC
    gsc = GoogleSearchConsoleCollector(config)
    if not gsc.initialize():
        print("  Could not connect to GSC for keyword data")
        return

    print("  [GSC] Fetching keyword opportunities...")
    gsc_queries = gsc.get_top_queries(limit=100)

    keywords = [
        KeywordData(
            keyword=q.query,
            impressions=q.impressions,
            clicks=q.clicks,
            ctr=q.ctr,
            position=q.position,
        )
        for q in gsc_queries
    ]

    print(f"  Found {len(keywords)} keywords to analyze")

    # Generate blogs
    generator = BlogGenerator(config)
    posts = generator.generate_batch(keywords, count=count, save=True)

    # Summary
    print("\n" + "=" * 60)
    print("              BLOG GENERATION COMPLETE")
    print("=" * 60)
    print(f"""
Generated {len(posts)} blog posts:
""")
    for post in posts:
        print(f"  - {post.title}")
        print(f"    File: content/blogs/{post.slug}.md")
        print(f"    Words: {post.word_count}")
        print()

    if posts:
        print("""
Next steps:
  1. Review generated posts in content/blogs/
  2. Edit as needed for quality and accuracy
  3. Rebuild site: uv run python generate.py
""")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Big0 SEO Engine - AI-Powered SEO Optimization"
    )
    parser.add_argument(
        '--full', action='store_true',
        help='Run full analysis with AI recommendations'
    )
    parser.add_argument(
        '--quick', action='store_true',
        help='Quick analysis without AI (faster, no API costs)'
    )
    parser.add_argument(
        '--collect-only', action='store_true',
        help='Only collect data from APIs (cache for later)'
    )
    parser.add_argument(
        '--apply', action='store_true',
        help='Apply latest AI recommendations to content files'
    )
    parser.add_argument(
        '--apply-all', action='store_true',
        help='Apply all recommendations without confirmation'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Show what would change without modifying files'
    )
    parser.add_argument(
        '--generate-blogs', type=int, nargs='?', const=3, metavar='COUNT',
        help='Generate blog posts from keyword opportunities (default: 3)'
    )
    parser.add_argument(
        '--track', action='store_true',
        help='Sync and track keyword rankings from GSC'
    )
    parser.add_argument(
        '--track-report', action='store_true',
        help='Sync rankings and generate a detailed report'
    )
    parser.add_argument(
        '--help-content', action='store_true',
        help='Show content writing guide for each markdown file type'
    )
    parser.add_argument(
        '--env', type=str, default=None,
        help='Path to .env file'
    )
    parser.add_argument(
        '--exports', action='store_true',
        help='Show status of manual dashboard exports'
    )
    parser.add_argument(
        '--no-export-check', action='store_true',
        help='Skip the export status check prompt'
    )

    args = parser.parse_args()

    print_banner()

    # Load configuration
    config = Config.load(args.env)

    # Determine mode
    if args.help_content:
        show_content_guide()
    elif args.exports:
        show_exports_status(config)
    elif args.apply or args.apply_all:
        run_apply_recommendations(config, dry_run=args.dry_run, auto_approve=args.apply_all)
    elif args.generate_blogs is not None:
        run_generate_blogs(config, count=args.generate_blogs)
    elif args.track or args.track_report:
        run_track_rankings(config, report=args.track_report)
    elif args.collect_only:
        run_collect_only(config)
    elif args.quick:
        # Check exports before running analysis
        if not args.no_export_check:
            prompt_export_updates(config)
        run_quick_analysis(config)
    else:
        # Check exports before running full analysis
        if not args.no_export_check:
            prompt_export_updates(config)
        # Default to full analysis
        run_full_analysis(config)


if __name__ == "__main__":
    main()
