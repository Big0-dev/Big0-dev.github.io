"""
Rank Tracker - Stores historical keyword rankings in SQLite

Tracks:
- Keyword positions over time
- Position changes (improvements/drops)
- Page-keyword associations
- Trend analysis
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from ..config import Config


@dataclass
class RankingRecord:
    """A single ranking data point"""
    keyword: str
    position: float
    impressions: int
    clicks: int
    ctr: float
    page: Optional[str] = None
    date: Optional[datetime] = None


@dataclass
class RankingTrend:
    """Trend analysis for a keyword"""
    keyword: str
    current_position: float
    previous_position: float
    position_change: float
    trend: str  # 'improving', 'declining', 'stable'
    avg_position_7d: float
    avg_position_30d: float
    impressions_trend: float  # % change
    clicks_trend: float  # % change


class RankTracker:
    """
    SQLite-based rank tracking for historical keyword data.

    Stores daily rankings and provides trend analysis.
    """

    def __init__(self, config: Config):
        self.config = config
        self.db_path = config.cache_dir / "rankings.db"
        self._ensure_database()

    def _ensure_database(self):
        """Create database and tables if they don't exist"""
        self.config.cache_dir.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Main rankings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rankings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    keyword TEXT NOT NULL,
                    position REAL NOT NULL,
                    impressions INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    ctr REAL DEFAULT 0,
                    page TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, keyword, page)
                )
            """)

            # Index for fast queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rankings_keyword
                ON rankings(keyword)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rankings_date
                ON rankings(date DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rankings_keyword_date
                ON rankings(keyword, date DESC)
            """)

            # Pages table for tracking URL changes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    first_seen DATE,
                    last_seen DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Snapshots table for tracking analysis runs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    total_keywords INTEGER,
                    avg_position REAL,
                    total_impressions INTEGER,
                    total_clicks INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def record_rankings(self, rankings: list[RankingRecord], date: datetime = None):
        """Store a batch of ranking records"""
        if date is None:
            date = datetime.now().date()
        elif isinstance(date, datetime):
            date = date.date()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Insert rankings (upsert to handle duplicates)
            for r in rankings:
                cursor.execute("""
                    INSERT INTO rankings (date, keyword, position, impressions, clicks, ctr, page)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(date, keyword, page) DO UPDATE SET
                        position = excluded.position,
                        impressions = excluded.impressions,
                        clicks = excluded.clicks,
                        ctr = excluded.ctr
                """, (date, r.keyword, r.position, r.impressions, r.clicks, r.ctr, r.page))

                # Track page
                if r.page:
                    cursor.execute("""
                        INSERT INTO pages (url, first_seen, last_seen)
                        VALUES (?, ?, ?)
                        ON CONFLICT(url) DO UPDATE SET last_seen = excluded.last_seen
                    """, (r.page, date, date))

            # Create snapshot
            if rankings:
                avg_pos = sum(r.position for r in rankings) / len(rankings)
                total_imp = sum(r.impressions for r in rankings)
                total_clicks = sum(r.clicks for r in rankings)

                cursor.execute("""
                    INSERT INTO snapshots (date, total_keywords, avg_position, total_impressions, total_clicks)
                    VALUES (?, ?, ?, ?, ?)
                """, (date, len(rankings), avg_pos, total_imp, total_clicks))

            conn.commit()

        return len(rankings)

    def get_keyword_history(
        self,
        keyword: str,
        days: int = 30,
        page: str = None
    ) -> list[dict]:
        """Get historical rankings for a specific keyword"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            since_date = (datetime.now() - timedelta(days=days)).date()

            if page:
                cursor.execute("""
                    SELECT date, position, impressions, clicks, ctr, page
                    FROM rankings
                    WHERE keyword = ? AND page = ? AND date >= ?
                    ORDER BY date ASC
                """, (keyword, page, since_date))
            else:
                cursor.execute("""
                    SELECT date, position, impressions, clicks, ctr, page
                    FROM rankings
                    WHERE keyword = ? AND date >= ?
                    ORDER BY date ASC
                """, (keyword, since_date))

            return [dict(row) for row in cursor.fetchall()]

    def get_trending_keywords(self, limit: int = 20) -> list[RankingTrend]:
        """Get keywords with significant position changes"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get keywords with data from last 7 days vs previous 7 days
            cursor.execute("""
                WITH recent AS (
                    SELECT
                        keyword,
                        AVG(position) as avg_pos_recent,
                        SUM(impressions) as imp_recent,
                        SUM(clicks) as clicks_recent
                    FROM rankings
                    WHERE date >= date('now', '-7 days')
                    GROUP BY keyword
                ),
                previous AS (
                    SELECT
                        keyword,
                        AVG(position) as avg_pos_prev,
                        SUM(impressions) as imp_prev,
                        SUM(clicks) as clicks_prev
                    FROM rankings
                    WHERE date >= date('now', '-14 days') AND date < date('now', '-7 days')
                    GROUP BY keyword
                ),
                monthly AS (
                    SELECT
                        keyword,
                        AVG(position) as avg_pos_30d
                    FROM rankings
                    WHERE date >= date('now', '-30 days')
                    GROUP BY keyword
                )
                SELECT
                    r.keyword,
                    r.avg_pos_recent as current_position,
                    COALESCE(p.avg_pos_prev, r.avg_pos_recent) as previous_position,
                    COALESCE(p.avg_pos_prev, r.avg_pos_recent) - r.avg_pos_recent as position_change,
                    r.avg_pos_recent as avg_position_7d,
                    COALESCE(m.avg_pos_30d, r.avg_pos_recent) as avg_position_30d,
                    CASE
                        WHEN p.imp_prev > 0 THEN ((r.imp_recent - p.imp_prev) * 100.0 / p.imp_prev)
                        ELSE 0
                    END as impressions_trend,
                    CASE
                        WHEN p.clicks_prev > 0 THEN ((r.clicks_recent - p.clicks_prev) * 100.0 / p.clicks_prev)
                        ELSE 0
                    END as clicks_trend
                FROM recent r
                LEFT JOIN previous p ON r.keyword = p.keyword
                LEFT JOIN monthly m ON r.keyword = m.keyword
                ORDER BY ABS(COALESCE(p.avg_pos_prev, r.avg_pos_recent) - r.avg_pos_recent) DESC
                LIMIT ?
            """, (limit,))

            trends = []
            for row in cursor.fetchall():
                change = row['position_change'] or 0
                if change > 1:
                    trend = 'improving'
                elif change < -1:
                    trend = 'declining'
                else:
                    trend = 'stable'

                trends.append(RankingTrend(
                    keyword=row['keyword'],
                    current_position=row['current_position'],
                    previous_position=row['previous_position'],
                    position_change=change,
                    trend=trend,
                    avg_position_7d=row['avg_position_7d'],
                    avg_position_30d=row['avg_position_30d'],
                    impressions_trend=row['impressions_trend'] or 0,
                    clicks_trend=row['clicks_trend'] or 0,
                ))

            return trends

    def get_improving_keywords(self, min_improvement: float = 2.0, limit: int = 20) -> list[RankingTrend]:
        """Get keywords that have improved in position"""
        all_trends = self.get_trending_keywords(limit=100)
        improving = [t for t in all_trends if t.position_change >= min_improvement]
        return sorted(improving, key=lambda x: x.position_change, reverse=True)[:limit]

    def get_declining_keywords(self, min_decline: float = 2.0, limit: int = 20) -> list[RankingTrend]:
        """Get keywords that have declined in position"""
        all_trends = self.get_trending_keywords(limit=100)
        declining = [t for t in all_trends if t.position_change <= -min_decline]
        return sorted(declining, key=lambda x: x.position_change)[:limit]

    def get_quick_win_opportunities(self, limit: int = 20) -> list[dict]:
        """Get keywords close to page 1 with high impressions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Keywords in positions 11-20 with decent impressions
            cursor.execute("""
                SELECT
                    keyword,
                    AVG(position) as avg_position,
                    SUM(impressions) as total_impressions,
                    SUM(clicks) as total_clicks,
                    page
                FROM rankings
                WHERE date >= date('now', '-7 days')
                GROUP BY keyword
                HAVING AVG(position) BETWEEN 11 AND 20 AND SUM(impressions) > 10
                ORDER BY SUM(impressions) DESC
                LIMIT ?
            """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

    def get_summary_stats(self, days: int = 30) -> dict:
        """Get summary statistics for the tracking period"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            since_date = (datetime.now() - timedelta(days=days)).date()

            # Overall stats
            cursor.execute("""
                SELECT
                    COUNT(DISTINCT keyword) as unique_keywords,
                    COUNT(DISTINCT page) as unique_pages,
                    COUNT(DISTINCT date) as tracking_days,
                    MIN(date) as first_record,
                    MAX(date) as last_record
                FROM rankings
                WHERE date >= ?
            """, (since_date,))

            overall = dict(cursor.fetchone())

            # Average metrics over time
            cursor.execute("""
                SELECT
                    AVG(avg_position) as avg_position,
                    SUM(total_impressions) as total_impressions,
                    SUM(total_clicks) as total_clicks
                FROM snapshots
                WHERE date >= ?
            """, (since_date,))

            metrics = dict(cursor.fetchone())

            # Position distribution
            cursor.execute("""
                SELECT
                    CASE
                        WHEN position <= 3 THEN 'top_3'
                        WHEN position <= 10 THEN 'page_1'
                        WHEN position <= 20 THEN 'page_2'
                        ELSE 'page_3_plus'
                    END as position_bucket,
                    COUNT(DISTINCT keyword) as keyword_count
                FROM rankings
                WHERE date = (SELECT MAX(date) FROM rankings)
                GROUP BY position_bucket
            """)

            distribution = {row['position_bucket']: row['keyword_count'] for row in cursor.fetchall()}

            return {
                'tracking_period_days': days,
                'unique_keywords': overall['unique_keywords'] or 0,
                'unique_pages': overall['unique_pages'] or 0,
                'tracking_days': overall['tracking_days'] or 0,
                'first_record': overall['first_record'],
                'last_record': overall['last_record'],
                'avg_position': metrics['avg_position'] or 0,
                'total_impressions': metrics['total_impressions'] or 0,
                'total_clicks': metrics['total_clicks'] or 0,
                'position_distribution': distribution,
            }

    def generate_tracking_report(self) -> str:
        """Generate a markdown report of ranking trends"""
        stats = self.get_summary_stats()
        improving = self.get_improving_keywords(limit=10)
        declining = self.get_declining_keywords(limit=10)
        quick_wins = self.get_quick_win_opportunities(limit=10)

        report = f"""# Rank Tracking Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary Statistics

| Metric | Value |
|--------|-------|
| Keywords Tracked | {stats['unique_keywords']} |
| Pages Tracked | {stats['unique_pages']} |
| Tracking Days | {stats['tracking_days']} |
| Average Position | {stats['avg_position']:.1f} |
| Total Impressions | {stats['total_impressions']:,} |
| Total Clicks | {stats['total_clicks']:,} |

### Position Distribution
"""
        dist = stats.get('position_distribution', {})
        if dist:
            report += f"""
| Position Range | Keywords |
|----------------|----------|
| Top 3 | {dist.get('top_3', 0)} |
| Page 1 (4-10) | {dist.get('page_1', 0)} |
| Page 2 (11-20) | {dist.get('page_2', 0)} |
| Page 3+ (21+) | {dist.get('page_3_plus', 0)} |
"""

        if improving:
            report += "\n## Improving Keywords (Last 7 Days)\n\n"
            report += "| Keyword | Position Change | Current Pos |\n"
            report += "|---------|-----------------|-------------|\n"
            for t in improving:
                report += f"| {t.keyword[:40]} | +{t.position_change:.1f} | {t.current_position:.1f} |\n"

        if declining:
            report += "\n## Declining Keywords (Last 7 Days)\n\n"
            report += "| Keyword | Position Change | Current Pos |\n"
            report += "|---------|-----------------|-------------|\n"
            for t in declining:
                report += f"| {t.keyword[:40]} | {t.position_change:.1f} | {t.current_position:.1f} |\n"

        if quick_wins:
            report += "\n## Quick Win Opportunities (Page 2)\n\n"
            report += "| Keyword | Position | Impressions |\n"
            report += "|---------|----------|-------------|\n"
            for qw in quick_wins:
                report += f"| {qw['keyword'][:40]} | {qw['avg_position']:.1f} | {qw['total_impressions']:,} |\n"

        return report


def sync_rankings_from_gsc(config: Config) -> int:
    """Helper function to sync current GSC data to rank tracker"""
    from ..collectors.gsc import GoogleSearchConsoleCollector

    gsc = GoogleSearchConsoleCollector(config)
    if not gsc.initialize():
        print("  Could not connect to GSC")
        return 0

    queries = gsc.get_top_queries(limit=500)

    tracker = RankTracker(config)

    records = [
        RankingRecord(
            keyword=q.query,
            position=q.position,
            impressions=q.impressions,
            clicks=q.clicks,
            ctr=q.ctr,
            page=q.page,
        )
        for q in queries
    ]

    count = tracker.record_rankings(records)
    return count
