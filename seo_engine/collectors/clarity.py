"""
Microsoft Clarity Data Collector

Supports:
1. Clarity Export API (with JWT token)
2. Fallback to manual CSV export
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from ..config import Config


@dataclass
class ClarityPageMetrics:
    """Clarity metrics for a page"""
    page_url: str
    sessions: int = 0
    scroll_depth: float = 0.0  # Average scroll depth (0-1)
    rage_clicks: int = 0       # Frustrated clicking
    dead_clicks: int = 0       # Clicks with no response
    quick_backs: int = 0       # Users who left immediately
    javascript_errors: int = 0
    engagement_score: float = 0.0


@dataclass
class ClarityInsight:
    """UX insight from Clarity"""
    insight_type: str  # "rage_click", "dead_click", "scroll_issue", etc.
    page_url: str
    element: Optional[str] = None
    count: int = 0
    description: str = ""


class ClarityCollector:
    """
    Collects data from Microsoft Clarity API.
    """

    def __init__(self, config: Config):
        self.config = config
        self.cache_dir = config.cache_dir / "clarity"
        self._data: dict = {}
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize the Clarity API client"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        if self.config.clarity_api_token:
            # Try API first
            if self._fetch_from_api():
                self._initialized = True
                print("  [Clarity] Successfully connected via API")
                return True
            else:
                print("  [Clarity] API connection failed, checking for CSV exports...")

        # Fallback to CSV exports
        csv_files = list(self.cache_dir.glob("*.csv"))
        if csv_files:
            print(f"  [Clarity] Found {len(csv_files)} CSV export file(s)")
            self._load_csv_exports()
            self._initialized = True
            return True

        print("  [Clarity] No API token or CSV exports found")
        return False

    def _fetch_from_api(self) -> bool:
        """Fetch data from Clarity Export API"""
        try:
            url = f"{self.config.clarity_api_endpoint}?projectId={self.config.clarity_project_id}"

            headers = {
                "Authorization": f"Bearer {self.config.clarity_api_token}",
                "Content-Type": "application/json",
            }

            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=30) as response:
                raw_data = json.loads(response.read().decode())

            # Parse the list of metrics into a structured dict
            self._data = self._parse_api_response(raw_data)
            self._cache_api_data(self._data)
            return True

        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else str(e)
            print(f"  [Clarity] API error {e.code}: {error_body[:200]}")
            return False
        except Exception as e:
            print(f"  [Clarity] API error: {e}")
            return False

    def _parse_api_response(self, raw_data: list) -> dict:
        """Parse the Clarity API response into a structured dict"""
        parsed = {
            'totalSessions': 0,
            'totalUsers': 0,
            'pagesPerSession': 0,
            'avgScrollDepth': 0,
            'rageClickCount': 0,
            'deadClickCount': 0,
            'quickBackCount': 0,
            'jsErrorCount': 0,
            'engagementTime': 0,
        }

        for metric in raw_data:
            name = metric.get('metricName', '')
            info = metric.get('information', [{}])[0] if metric.get('information') else {}

            if name == 'Traffic':
                parsed['totalSessions'] = int(info.get('totalSessionCount', 0))
                parsed['totalUsers'] = int(info.get('distinctUserCount', 0))
                parsed['pagesPerSession'] = float(info.get('pagesPerSessionPercentage', 0))

            elif name == 'ScrollDepth':
                parsed['avgScrollDepth'] = float(info.get('averageScrollDepth', 0))

            elif name == 'RageClickCount':
                parsed['rageClickCount'] = int(info.get('subTotal', 0))

            elif name == 'DeadClickCount':
                parsed['deadClickCount'] = int(info.get('subTotal', 0))

            elif name == 'QuickbackClick':
                parsed['quickBackCount'] = int(info.get('subTotal', 0))

            elif name == 'ScriptErrorCount':
                parsed['jsErrorCount'] = int(info.get('subTotal', 0))

            elif name == 'EngagementTime':
                parsed['engagementTime'] = info.get('totalTime', 0)

        return parsed

    def _cache_api_data(self, data: dict) -> None:
        """Cache API response"""
        cache_file = self.cache_dir / "api_response.json"
        with open(cache_file, 'w') as f:
            json.dump({
                'fetched_at': datetime.now().isoformat(),
                'data': data
            }, f, indent=2)

    def _load_csv_exports(self) -> None:
        """Load CSV exports from cache directory"""
        import csv

        for csv_file in self.cache_dir.glob("*.csv"):
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    filename = csv_file.stem.lower()

                    if 'page' in filename:
                        self._data['pages'] = list(reader)
                    elif 'click' in filename:
                        self._data['clicks'] = list(reader)
                    else:
                        self._data[filename] = list(reader)

                print(f"  [Clarity] Loaded {csv_file.name}")
            except Exception as e:
                print(f"  [Clarity] Error loading {csv_file}: {e}")

    def get_page_metrics(self) -> list[ClarityPageMetrics]:
        """Get page-level metrics"""
        metrics = []

        # From API response
        if 'pages' in self._data and isinstance(self._data['pages'], list):
            for page in self._data['pages']:
                metrics.append(ClarityPageMetrics(
                    page_url=page.get('url', page.get('URL', '')),
                    sessions=int(page.get('sessions', page.get('totalSessions', 0))),
                    scroll_depth=float(page.get('scrollDepth', page.get('avgScrollDepth', 0))) / 100 if page.get('scrollDepth', page.get('avgScrollDepth', 0)) else 0,
                    rage_clicks=int(page.get('rageClicks', page.get('rageClickCount', 0))),
                    dead_clicks=int(page.get('deadClicks', page.get('deadClickCount', 0))),
                    quick_backs=int(page.get('quickBacks', page.get('quickBackCount', 0))),
                ))

        # Try different API response structures
        if 'pageMetrics' in self._data:
            for page in self._data['pageMetrics']:
                metrics.append(ClarityPageMetrics(
                    page_url=page.get('url', ''),
                    sessions=int(page.get('sessions', 0)),
                    scroll_depth=float(page.get('scrollDepth', 0)) / 100,
                    rage_clicks=int(page.get('rageClicks', 0)),
                    dead_clicks=int(page.get('deadClicks', 0)),
                ))

        # From top-level metrics
        if 'totalSessions' in self._data:
            # Single project-level data
            metrics.append(ClarityPageMetrics(
                page_url='/',
                sessions=int(self._data.get('totalSessions', 0)),
                scroll_depth=float(self._data.get('avgScrollDepth', 0)) / 100 if self._data.get('avgScrollDepth') else 0,
                rage_clicks=int(self._data.get('rageClickCount', 0)),
                dead_clicks=int(self._data.get('deadClickCount', 0)),
                quick_backs=int(self._data.get('quickBackCount', 0)),
            ))

        return metrics

    def get_project_summary(self) -> dict:
        """Get project-level summary metrics"""
        return {
            'total_sessions': self._data.get('totalSessions', 0),
            'total_users': self._data.get('totalUsers', 0),
            'pages_per_session': self._data.get('pagesPerSession', 0),
            'scroll_depth': self._data.get('avgScrollDepth', 0),
            'rage_clicks': self._data.get('rageClickCount', 0),
            'dead_clicks': self._data.get('deadClickCount', 0),
            'quick_backs': self._data.get('quickBackCount', 0),
            'js_errors': self._data.get('jsErrorCount', 0),
        }

    def get_ux_issues(self) -> list[ClarityInsight]:
        """Identify UX issues from Clarity data"""
        issues = []
        summary = self.get_project_summary()

        # High rage clicks
        if summary.get('rage_clicks', 0) > 10:
            issues.append(ClarityInsight(
                insight_type="rage_clicks",
                page_url="/",
                count=summary['rage_clicks'],
                description=f"{summary['rage_clicks']} rage clicks detected - users frustrated with unresponsive elements",
            ))

        # High dead clicks
        if summary.get('dead_clicks', 0) > 20:
            issues.append(ClarityInsight(
                insight_type="dead_clicks",
                page_url="/",
                count=summary['dead_clicks'],
                description=f"{summary['dead_clicks']} dead clicks - users clicking non-interactive elements",
            ))

        # Quick backs
        if summary.get('quick_backs', 0) > 10:
            issues.append(ClarityInsight(
                insight_type="quick_backs",
                page_url="/",
                count=summary['quick_backs'],
                description=f"{summary['quick_backs']} quick backs - content not matching user expectations",
            ))

        # Low scroll depth
        scroll_depth = summary.get('scroll_depth', 0)
        if scroll_depth and scroll_depth < 40:
            issues.append(ClarityInsight(
                insight_type="low_scroll",
                page_url="/",
                count=int(scroll_depth),
                description=f"Average scroll depth only {scroll_depth:.0f}% - users not engaging with content",
            ))

        # JS errors
        if summary.get('js_errors', 0) > 0:
            issues.append(ClarityInsight(
                insight_type="js_errors",
                page_url="/",
                count=summary['js_errors'],
                description=f"{summary['js_errors']} JavaScript errors detected - affecting user experience",
            ))

        # Analyze page-level metrics
        for page in self.get_page_metrics():
            if page.rage_clicks > 5:
                issues.append(ClarityInsight(
                    insight_type="page_rage_clicks",
                    page_url=page.page_url,
                    count=page.rage_clicks,
                    description=f"Page has {page.rage_clicks} rage clicks",
                ))

            if page.scroll_depth < 0.3 and page.sessions > 10:
                issues.append(ClarityInsight(
                    insight_type="page_low_scroll",
                    page_url=page.page_url,
                    count=int(page.scroll_depth * 100),
                    description=f"Only {page.scroll_depth*100:.0f}% scroll depth with {page.sessions} sessions",
                ))

        return sorted(issues, key=lambda x: x.count, reverse=True)

    def get_engagement_summary(self) -> dict:
        """Get overall engagement summary"""
        pages = self.get_page_metrics()
        summary = self.get_project_summary()

        if not pages and not summary.get('total_sessions'):
            return {
                "total_sessions": 0,
                "avg_scroll_depth": 0,
                "total_rage_clicks": 0,
                "total_dead_clicks": 0,
                "pages_analyzed": 0,
            }

        return {
            "total_sessions": summary.get('total_sessions', sum(p.sessions for p in pages)),
            "avg_scroll_depth": summary.get('scroll_depth', 0) / 100 if summary.get('scroll_depth') else (sum(p.scroll_depth for p in pages) / len(pages) if pages else 0),
            "total_rage_clicks": summary.get('rage_clicks', sum(p.rage_clicks for p in pages)),
            "total_dead_clicks": summary.get('dead_clicks', sum(p.dead_clicks for p in pages)),
            "pages_analyzed": len(pages),
        }

    def cache_data(self, cache_file: Path) -> None:
        """Cache current data state"""
        data = {
            'collected_at': datetime.now().isoformat(),
            'project_id': self.config.clarity_project_id,
            'raw_data': self._data,
            'summary': self.get_project_summary(),
            'pages': [
                {
                    'page_url': p.page_url,
                    'sessions': p.sessions,
                    'scroll_depth': p.scroll_depth,
                    'rage_clicks': p.rage_clicks,
                    'dead_clicks': p.dead_clicks,
                    'quick_backs': p.quick_backs,
                }
                for p in self.get_page_metrics()
            ],
            'issues': [
                {
                    'type': i.insight_type,
                    'page': i.page_url,
                    'count': i.count,
                    'description': i.description,
                }
                for i in self.get_ux_issues()
            ],
        }

        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"  [Clarity] Data cached to {cache_file}")
