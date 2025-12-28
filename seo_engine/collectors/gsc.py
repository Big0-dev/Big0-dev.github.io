"""
Google Search Console API Collector
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from ..config import Config
from ..models import KeywordData, FunnelStage


@dataclass
class GSCPageData:
    """Raw GSC page data"""
    page: str
    clicks: int
    impressions: int
    ctr: float
    position: float


@dataclass
class GSCQueryData:
    """Raw GSC query data"""
    query: str
    clicks: int
    impressions: int
    ctr: float
    position: float
    page: Optional[str] = None


class GoogleSearchConsoleCollector:
    """
    Collects data from Google Search Console API

    Setup:
    1. Enable Search Console API in Google Cloud Console
    2. Create a service account and download JSON key
    3. Add service account email to your Search Console property
    """

    def __init__(self, config: Config):
        self.config = config
        self.service = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize the GSC API client"""
        if not self.config.gsc_service_account_file:
            print("  [GSC] No service account file configured")
            return False

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            credentials = service_account.Credentials.from_service_account_file(
                self.config.gsc_service_account_file,
                scopes=['https://www.googleapis.com/auth/webmasters.readonly']
            )

            self.service = build('searchconsole', 'v1', credentials=credentials)
            self._initialized = True
            print("  [GSC] Successfully initialized")
            return True

        except FileNotFoundError:
            print(f"  [GSC] Service account file not found: {self.config.gsc_service_account_file}")
            return False
        except Exception as e:
            print(f"  [GSC] Failed to initialize: {e}")
            return False

    def get_search_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        dimensions: list[str] = None,
        row_limit: int = 1000,
    ) -> list[dict]:
        """
        Fetch search analytics data from GSC

        Args:
            start_date: Start of date range (default: 28 days ago)
            end_date: End of date range (default: yesterday)
            dimensions: List of dimensions (query, page, device, country)
            row_limit: Maximum rows to return

        Returns:
            List of rows with metrics
        """
        if not self._initialized:
            if not self.initialize():
                return []

        if dimensions is None:
            dimensions = ['query', 'page']

        if end_date is None:
            end_date = datetime.now() - timedelta(days=1)
        if start_date is None:
            start_date = end_date - timedelta(days=28)

        request = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'dimensions': dimensions,
            'rowLimit': row_limit,
            'dataState': 'final',
        }

        try:
            response = self.service.searchanalytics().query(
                siteUrl=self.config.gsc_property_url,
                body=request
            ).execute()

            return response.get('rows', [])

        except Exception as e:
            print(f"  [GSC] Error fetching data: {e}")
            return []

    def get_top_queries(self, limit: int = 100) -> list[GSCQueryData]:
        """Get top performing queries"""
        rows = self.get_search_analytics(
            dimensions=['query'],
            row_limit=limit
        )

        return [
            GSCQueryData(
                query=row['keys'][0],
                clicks=row.get('clicks', 0),
                impressions=row.get('impressions', 0),
                ctr=row.get('ctr', 0),
                position=row.get('position', 0),
            )
            for row in rows
        ]

    def get_queries_by_page(self, page_url: str, limit: int = 50) -> list[GSCQueryData]:
        """Get queries for a specific page"""
        if not self._initialized:
            if not self.initialize():
                return []

        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=28)

        request = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'dimensions': ['query'],
            'dimensionFilterGroups': [{
                'filters': [{
                    'dimension': 'page',
                    'operator': 'equals',
                    'expression': page_url
                }]
            }],
            'rowLimit': limit,
        }

        try:
            response = self.service.searchanalytics().query(
                siteUrl=self.config.gsc_property_url,
                body=request
            ).execute()

            return [
                GSCQueryData(
                    query=row['keys'][0],
                    clicks=row.get('clicks', 0),
                    impressions=row.get('impressions', 0),
                    ctr=row.get('ctr', 0),
                    position=row.get('position', 0),
                    page=page_url,
                )
                for row in response.get('rows', [])
            ]

        except Exception as e:
            print(f"  [GSC] Error fetching page queries: {e}")
            return []

    def get_page_performance(self, limit: int = 500) -> list[GSCPageData]:
        """Get performance data for all pages"""
        rows = self.get_search_analytics(
            dimensions=['page'],
            row_limit=limit
        )

        return [
            GSCPageData(
                page=row['keys'][0],
                clicks=row.get('clicks', 0),
                impressions=row.get('impressions', 0),
                ctr=row.get('ctr', 0),
                position=row.get('position', 0),
            )
            for row in rows
        ]

    def get_opportunity_keywords(self) -> list[KeywordData]:
        """
        Find keyword opportunities:
        - Position 4-20 (close to page 1)
        - High impressions, low CTR
        - Rising trends
        """
        queries = self.get_top_queries(limit=500)

        opportunities = []
        for q in queries:
            # Position 4-20 = quick win potential
            if 4 <= q.position <= 20:
                opportunities.append(KeywordData(
                    keyword=q.query,
                    impressions=q.impressions,
                    clicks=q.clicks,
                    ctr=q.ctr,
                    position=q.position,
                ))

            # High impressions but low CTR = meta optimization needed
            elif q.impressions > 100 and q.ctr < 0.02:
                opportunities.append(KeywordData(
                    keyword=q.query,
                    impressions=q.impressions,
                    clicks=q.clicks,
                    ctr=q.ctr,
                    position=q.position,
                ))

        # Sort by opportunity score
        opportunities.sort(key=lambda x: x.opportunity_score, reverse=True)
        return opportunities

    def cache_data(self, cache_file: Path) -> None:
        """Cache collected data for offline analysis"""
        data = {
            'collected_at': datetime.now().isoformat(),
            'property': self.config.gsc_property_url,
            'queries': [
                {
                    'query': q.query,
                    'clicks': q.clicks,
                    'impressions': q.impressions,
                    'ctr': q.ctr,
                    'position': q.position,
                }
                for q in self.get_top_queries(limit=1000)
            ],
            'pages': [
                {
                    'page': p.page,
                    'clicks': p.clicks,
                    'impressions': p.impressions,
                    'ctr': p.ctr,
                    'position': p.position,
                }
                for p in self.get_page_performance(limit=500)
            ],
        }

        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"  [GSC] Data cached to {cache_file}")

    @classmethod
    def load_from_cache(cls, cache_file: Path, config: Config) -> Optional["GoogleSearchConsoleCollector"]:
        """Load collector with cached data"""
        if not cache_file.exists():
            return None

        collector = cls(config)
        with open(cache_file) as f:
            collector._cached_data = json.load(f)

        return collector
