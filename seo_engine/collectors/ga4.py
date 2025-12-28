"""
Google Analytics 4 Data API Collector
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from ..config import Config


@dataclass
class GA4PageMetrics:
    """GA4 page-level metrics"""
    page_path: str
    page_title: str
    sessions: int = 0
    users: int = 0
    bounce_rate: float = 0.0
    avg_session_duration: float = 0.0
    conversions: int = 0
    page_views: int = 0


@dataclass
class GA4TrafficSource:
    """Traffic source breakdown"""
    source: str
    medium: str
    sessions: int = 0
    users: int = 0
    conversions: int = 0


class GoogleAnalyticsCollector:
    """
    Collects data from Google Analytics 4 Data API

    Setup:
    1. Enable Analytics Data API in Google Cloud Console
    2. Create/use service account with Viewer access
    3. Add service account email to GA4 property
    """

    def __init__(self, config: Config):
        self.config = config
        self.client = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize the GA4 API client"""
        if not self.config.ga4_service_account_file:
            print("  [GA4] No service account file configured")
            return False

        if not self.config.ga4_property_id:
            print("  [GA4] No property ID configured")
            return False

        try:
            from google.analytics.data_v1beta import BetaAnalyticsDataClient
            from google.oauth2 import service_account

            credentials = service_account.Credentials.from_service_account_file(
                self.config.ga4_service_account_file
            )

            self.client = BetaAnalyticsDataClient(credentials=credentials)
            self._initialized = True
            print("  [GA4] Successfully initialized")
            return True

        except FileNotFoundError:
            print(f"  [GA4] Service account file not found: {self.config.ga4_service_account_file}")
            return False
        except ImportError:
            print("  [GA4] google-analytics-data package not installed")
            print("  [GA4] Run: uv add google-analytics-data")
            return False
        except Exception as e:
            print(f"  [GA4] Failed to initialize: {e}")
            return False

    def _run_report(
        self,
        dimensions: list[str],
        metrics: list[str],
        start_date: str = "28daysAgo",
        end_date: str = "yesterday",
        limit: int = 100,
    ) -> list[dict]:
        """Run a GA4 report and return results"""
        if not self._initialized:
            if not self.initialize():
                return []

        try:
            from google.analytics.data_v1beta.types import (
                RunReportRequest,
                Dimension,
                Metric,
                DateRange,
            )

            request = RunReportRequest(
                property=f"properties/{self.config.ga4_property_id}",
                dimensions=[Dimension(name=d) for d in dimensions],
                metrics=[Metric(name=m) for m in metrics],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                limit=limit,
            )

            response = self.client.run_report(request)

            results = []
            for row in response.rows:
                result = {}
                for i, dim in enumerate(dimensions):
                    result[dim] = row.dimension_values[i].value
                for i, met in enumerate(metrics):
                    result[met] = row.metric_values[i].value
                results.append(result)

            return results

        except Exception as e:
            print(f"  [GA4] Error running report: {e}")
            return []

    def get_page_metrics(self, limit: int = 100) -> list[GA4PageMetrics]:
        """Get metrics for all pages"""
        results = self._run_report(
            dimensions=['pagePath', 'pageTitle'],
            metrics=[
                'sessions',
                'totalUsers',
                'bounceRate',
                'averageSessionDuration',
                'conversions',
                'screenPageViews',
            ],
            limit=limit,
        )

        return [
            GA4PageMetrics(
                page_path=r.get('pagePath', ''),
                page_title=r.get('pageTitle', ''),
                sessions=int(r.get('sessions', 0)),
                users=int(r.get('totalUsers', 0)),
                bounce_rate=float(r.get('bounceRate', 0)),
                avg_session_duration=float(r.get('averageSessionDuration', 0)),
                conversions=int(r.get('conversions', 0)),
                page_views=int(r.get('screenPageViews', 0)),
            )
            for r in results
        ]

    def get_landing_page_performance(self, limit: int = 50) -> list[GA4PageMetrics]:
        """Get landing page performance (entry points)"""
        results = self._run_report(
            dimensions=['landingPage'],
            metrics=[
                'sessions',
                'totalUsers',
                'bounceRate',
                'averageSessionDuration',
                'conversions',
            ],
            limit=limit,
        )

        return [
            GA4PageMetrics(
                page_path=r.get('landingPage', ''),
                page_title='',
                sessions=int(r.get('sessions', 0)),
                users=int(r.get('totalUsers', 0)),
                bounce_rate=float(r.get('bounceRate', 0)),
                avg_session_duration=float(r.get('averageSessionDuration', 0)),
                conversions=int(r.get('conversions', 0)),
            )
            for r in results
        ]

    def get_traffic_sources(self, limit: int = 50) -> list[GA4TrafficSource]:
        """Get traffic source breakdown"""
        results = self._run_report(
            dimensions=['sessionSource', 'sessionMedium'],
            metrics=['sessions', 'totalUsers', 'conversions'],
            limit=limit,
        )

        return [
            GA4TrafficSource(
                source=r.get('sessionSource', ''),
                medium=r.get('sessionMedium', ''),
                sessions=int(r.get('sessions', 0)),
                users=int(r.get('totalUsers', 0)),
                conversions=int(r.get('conversions', 0)),
            )
            for r in results
        ]

    def get_conversion_paths(self) -> list[dict]:
        """Get top conversion paths (pages leading to conversions)"""
        results = self._run_report(
            dimensions=['pagePath'],
            metrics=['conversions', 'sessions'],
            limit=50,
        )

        # Filter to pages with conversions and calculate conversion rate
        converting_pages = []
        for r in results:
            conversions = int(r.get('conversions', 0))
            sessions = int(r.get('sessions', 1))
            if conversions > 0:
                converting_pages.append({
                    'page': r.get('pagePath', ''),
                    'conversions': conversions,
                    'sessions': sessions,
                    'conversion_rate': conversions / sessions,
                })

        return sorted(converting_pages, key=lambda x: x['conversions'], reverse=True)

    def get_organic_performance(self) -> dict:
        """Get organic search performance summary"""
        results = self._run_report(
            dimensions=['sessionDefaultChannelGroup'],
            metrics=['sessions', 'totalUsers', 'conversions', 'bounceRate'],
            limit=20,
        )

        for r in results:
            if r.get('sessionDefaultChannelGroup', '').lower() == 'organic search':
                return {
                    'sessions': int(r.get('sessions', 0)),
                    'users': int(r.get('totalUsers', 0)),
                    'conversions': int(r.get('conversions', 0)),
                    'bounce_rate': float(r.get('bounceRate', 0)),
                }

        return {'sessions': 0, 'users': 0, 'conversions': 0, 'bounce_rate': 0}

    def get_high_exit_pages(self, min_sessions: int = 10) -> list[dict]:
        """Find pages with high exit rates (potential funnel leaks)"""
        # Note: GA4 doesn't have exit rate directly, using bounce rate as proxy
        pages = self.get_page_metrics(limit=200)

        high_exit = [
            {
                'page': p.page_path,
                'title': p.page_title,
                'sessions': p.sessions,
                'bounce_rate': p.bounce_rate,
            }
            for p in pages
            if p.sessions >= min_sessions and p.bounce_rate > 0.7
        ]

        return sorted(high_exit, key=lambda x: x['bounce_rate'], reverse=True)

    def cache_data(self, cache_file: Path) -> None:
        """Cache collected data for offline analysis"""
        data = {
            'collected_at': datetime.now().isoformat(),
            'property_id': self.config.ga4_property_id,
            'pages': [
                {
                    'page_path': p.page_path,
                    'page_title': p.page_title,
                    'sessions': p.sessions,
                    'users': p.users,
                    'bounce_rate': p.bounce_rate,
                    'avg_session_duration': p.avg_session_duration,
                    'conversions': p.conversions,
                }
                for p in self.get_page_metrics(limit=500)
            ],
            'traffic_sources': [
                {
                    'source': t.source,
                    'medium': t.medium,
                    'sessions': t.sessions,
                    'users': t.users,
                    'conversions': t.conversions,
                }
                for t in self.get_traffic_sources()
            ],
            'organic': self.get_organic_performance(),
            'conversion_paths': self.get_conversion_paths(),
        }

        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"  [GA4] Data cached to {cache_file}")
