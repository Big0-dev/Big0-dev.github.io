"""
Keyword Research Collector

Supports multiple sources:
1. Free: Google Autocomplete suggestions
2. Free: Google Trends (via pytrends)
3. Paid: DataForSEO API
4. Paid: SerpAPI
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import urllib.parse
import urllib.request

from ..config import Config, INDUSTRY_VERTICALS, GEO_TARGETS
from ..models import KeywordData, FunnelStage


@dataclass
class KeywordSuggestion:
    """Keyword suggestion with metadata"""
    keyword: str
    source: str  # "autocomplete", "trends", "dataforseo", "serpapi"
    search_volume: Optional[int] = None
    difficulty: Optional[float] = None
    trend: Optional[str] = None  # "rising", "stable", "declining", "breakout"
    cpc: Optional[float] = None
    competition: Optional[float] = None


class KeywordResearchCollector:
    """
    Collects keyword research data from multiple sources.
    Defaults to free sources, with optional paid integrations.
    """

    def __init__(self, config: Config):
        self.config = config
        self.cache_dir = config.cache_dir / "keywords"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, prefix: str, query: str) -> str:
        """Generate cache key for a query"""
        hash_val = hashlib.md5(query.encode()).hexdigest()[:8]
        return f"{prefix}_{hash_val}"

    def _get_cached(self, cache_key: str, max_age_hours: int = 24) -> Optional[dict]:
        """Get cached data if fresh enough"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None

        with open(cache_file) as f:
            data = json.load(f)

        cached_at = datetime.fromisoformat(data.get('cached_at', '2000-01-01'))
        if datetime.now() - cached_at > timedelta(hours=max_age_hours):
            return None

        return data

    def _set_cache(self, cache_key: str, data: dict) -> None:
        """Cache data"""
        data['cached_at'] = datetime.now().isoformat()
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)

    # =========================================================================
    # FREE: Google Autocomplete Suggestions
    # =========================================================================

    def get_autocomplete_suggestions(self, seed_keyword: str) -> list[KeywordSuggestion]:
        """
        Get keyword suggestions from Google Autocomplete.
        Free and doesn't require API key.
        """
        cache_key = self._get_cache_key("autocomplete", seed_keyword)
        cached = self._get_cached(cache_key, max_age_hours=168)  # Cache for 1 week

        if cached:
            return [KeywordSuggestion(**s) for s in cached.get('suggestions', [])]

        suggestions = []

        try:
            # Google autocomplete API
            encoded = urllib.parse.quote(seed_keyword)
            url = f"http://suggestqueries.google.com/complete/search?client=firefox&q={encoded}"

            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))

            if len(data) > 1 and isinstance(data[1], list):
                for suggestion in data[1]:
                    if suggestion.lower() != seed_keyword.lower():
                        suggestions.append(KeywordSuggestion(
                            keyword=suggestion,
                            source="autocomplete",
                        ))

            # Also try with modifiers for more suggestions
            modifiers = ['how to', 'best', 'what is', 'vs', 'for business']
            for mod in modifiers[:2]:  # Limit to avoid rate limiting
                modified_query = f"{seed_keyword} {mod}"
                encoded = urllib.parse.quote(modified_query)
                url = f"http://suggestqueries.google.com/complete/search?client=firefox&q={encoded}"

                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        data = json.loads(response.read().decode('utf-8'))

                    if len(data) > 1:
                        for suggestion in data[1][:3]:
                            suggestions.append(KeywordSuggestion(
                                keyword=suggestion,
                                source="autocomplete",
                            ))

                    time.sleep(0.5)  # Rate limiting
                except:
                    pass

            # Cache results
            self._set_cache(cache_key, {
                'seed': seed_keyword,
                'suggestions': [{'keyword': s.keyword, 'source': s.source} for s in suggestions],
            })

        except Exception as e:
            print(f"  [Keywords] Autocomplete error for '{seed_keyword}': {e}")

        return suggestions

    # =========================================================================
    # FREE: Google Trends
    # =========================================================================

    def get_trending_keywords(self, category: str = "technology") -> list[KeywordSuggestion]:
        """
        Get trending keywords from Google Trends.
        Requires pytrends library.
        """
        cache_key = self._get_cache_key("trends", category)
        cached = self._get_cached(cache_key, max_age_hours=24)

        if cached:
            return [KeywordSuggestion(**s) for s in cached.get('suggestions', [])]

        suggestions = []

        try:
            from pytrends.request import TrendReq

            pytrends = TrendReq(hl='en-US', tz=360)

            # Get trending searches
            trending = pytrends.trending_searches(pn='united_states')

            for keyword in trending[0].tolist()[:20]:
                suggestions.append(KeywordSuggestion(
                    keyword=keyword,
                    source="trends",
                    trend="rising",
                ))

            # Cache results
            self._set_cache(cache_key, {
                'category': category,
                'suggestions': [
                    {'keyword': s.keyword, 'source': s.source, 'trend': s.trend}
                    for s in suggestions
                ],
            })

        except ImportError:
            print("  [Keywords] pytrends not installed. Run: uv add pytrends")
        except Exception as e:
            print(f"  [Keywords] Trends error: {e}")

        return suggestions

    def get_keyword_interest(self, keywords: list[str]) -> dict[str, str]:
        """
        Get interest trend (rising/stable/declining) for keywords.
        """
        trends = {}

        try:
            from pytrends.request import TrendReq

            pytrends = TrendReq(hl='en-US', tz=360)

            # Process in batches of 5 (API limit)
            for i in range(0, len(keywords), 5):
                batch = keywords[i:i+5]

                try:
                    pytrends.build_payload(batch, timeframe='today 3-m')
                    interest = pytrends.interest_over_time()

                    if not interest.empty:
                        for kw in batch:
                            if kw in interest.columns:
                                values = interest[kw].tolist()
                                if len(values) >= 2:
                                    recent = sum(values[-4:]) / 4
                                    earlier = sum(values[:4]) / 4
                                    if recent > earlier * 1.2:
                                        trends[kw] = "rising"
                                    elif recent < earlier * 0.8:
                                        trends[kw] = "declining"
                                    else:
                                        trends[kw] = "stable"

                    time.sleep(1)  # Rate limiting

                except Exception as e:
                    print(f"  [Keywords] Trend check error for batch: {e}")

        except ImportError:
            pass

        return trends

    # =========================================================================
    # PAID: DataForSEO
    # =========================================================================

    def get_dataforseo_keywords(self, seed_keyword: str, location: str = "United States") -> list[KeywordSuggestion]:
        """
        Get keyword data from DataForSEO.
        Requires DataForSEO account (~$50/mo for basic).
        """
        if not self.config.dataforseo_login or not self.config.dataforseo_password:
            return []

        cache_key = self._get_cache_key("dataforseo", seed_keyword)
        cached = self._get_cached(cache_key, max_age_hours=168)

        if cached:
            return [KeywordSuggestion(**s) for s in cached.get('suggestions', [])]

        suggestions = []

        try:
            import base64

            # DataForSEO API endpoint
            url = "https://api.dataforseo.com/v3/keywords_data/google/search_volume/live"

            # Prepare credentials
            creds = base64.b64encode(
                f"{self.config.dataforseo_login}:{self.config.dataforseo_password}".encode()
            ).decode()

            headers = {
                'Authorization': f'Basic {creds}',
                'Content-Type': 'application/json',
            }

            payload = json.dumps([{
                "keywords": [seed_keyword],
                "location_name": location,
                "language_name": "English",
            }]).encode()

            req = urllib.request.Request(url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())

            if data.get('tasks'):
                for task in data['tasks']:
                    if task.get('result'):
                        for result in task['result']:
                            suggestions.append(KeywordSuggestion(
                                keyword=result.get('keyword', seed_keyword),
                                source="dataforseo",
                                search_volume=result.get('search_volume'),
                                difficulty=result.get('keyword_difficulty'),
                                cpc=result.get('cpc'),
                                competition=result.get('competition'),
                            ))

            # Cache results
            self._set_cache(cache_key, {
                'seed': seed_keyword,
                'suggestions': [
                    {
                        'keyword': s.keyword,
                        'source': s.source,
                        'search_volume': s.search_volume,
                        'difficulty': s.difficulty,
                    }
                    for s in suggestions
                ],
            })

        except Exception as e:
            print(f"  [Keywords] DataForSEO error: {e}")

        return suggestions

    # =========================================================================
    # PAID: SerpAPI (People Also Ask, Related Searches)
    # =========================================================================

    def get_serpapi_data(self, keyword: str) -> dict:
        """
        Get SERP data including People Also Ask and Related Searches.
        Requires SerpAPI key (~$50/mo for 5000 searches).
        """
        if not self.config.serpapi_key:
            return {}

        cache_key = self._get_cache_key("serpapi", keyword)
        cached = self._get_cached(cache_key, max_age_hours=168)

        if cached:
            return cached

        try:
            encoded = urllib.parse.quote(keyword)
            url = f"https://serpapi.com/search.json?q={encoded}&api_key={self.config.serpapi_key}"

            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())

            result = {
                'keyword': keyword,
                'people_also_ask': [
                    q.get('question', '')
                    for q in data.get('related_questions', [])
                ],
                'related_searches': [
                    r.get('query', '')
                    for r in data.get('related_searches', [])
                ],
            }

            self._set_cache(cache_key, result)
            return result

        except Exception as e:
            print(f"  [Keywords] SerpAPI error: {e}")
            return {}

    # =========================================================================
    # FREE: Google Related Searches
    # =========================================================================

    def get_related_searches(self, keyword: str) -> list[KeywordSuggestion]:
        """
        Scrape related searches from Google search results.
        Free but may be rate limited.
        """
        cache_key = self._get_cache_key("related", keyword)
        cached = self._get_cached(cache_key, max_age_hours=168)

        if cached:
            return [KeywordSuggestion(**s) for s in cached.get('suggestions', [])]

        suggestions = []

        try:
            import re

            encoded = urllib.parse.quote(keyword)
            url = f"https://www.google.com/search?q={encoded}&hl=en"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml',
            }

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='ignore')

            # Extract "People also search for" and related searches
            # Pattern for related searches at bottom
            patterns = [
                r'"([^"]+)" aria-label="[^"]*related',
                r'<div class="[^"]*">([^<]+)</div>\s*</a>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches[:5]:
                    if len(match) > 3 and len(match) < 100:
                        suggestions.append(KeywordSuggestion(
                            keyword=match.strip(),
                            source="google_related",
                        ))

            # Cache results
            if suggestions:
                self._set_cache(cache_key, {
                    'seed': keyword,
                    'suggestions': [{'keyword': s.keyword, 'source': s.source} for s in suggestions],
                })

            time.sleep(1)  # Rate limiting

        except Exception as e:
            pass  # Silently fail - this is a bonus source

        return suggestions

    # =========================================================================
    # FREE: Bing Autosuggest
    # =========================================================================

    def get_bing_suggestions(self, keyword: str) -> list[KeywordSuggestion]:
        """
        Get keyword suggestions from Bing Autosuggest.
        Free and often has different suggestions than Google.
        """
        cache_key = self._get_cache_key("bing", keyword)
        cached = self._get_cached(cache_key, max_age_hours=168)

        if cached:
            return [KeywordSuggestion(**s) for s in cached.get('suggestions', [])]

        suggestions = []

        try:
            encoded = urllib.parse.quote(keyword)
            url = f"https://api.bing.com/osjson.aspx?query={encoded}"

            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))

            if len(data) > 1 and isinstance(data[1], list):
                for suggestion in data[1]:
                    if suggestion.lower() != keyword.lower():
                        suggestions.append(KeywordSuggestion(
                            keyword=suggestion,
                            source="bing_autosuggest",
                        ))

            # Cache results
            if suggestions:
                self._set_cache(cache_key, {
                    'seed': keyword,
                    'suggestions': [{'keyword': s.keyword, 'source': s.source} for s in suggestions],
                })

            time.sleep(0.3)

        except Exception as e:
            pass

        return suggestions

    # =========================================================================
    # FREE: Question Keywords (What, How, Why, etc.)
    # =========================================================================

    def generate_question_keywords(self, seed: str) -> list[KeywordSuggestion]:
        """
        Generate question-based keywords for TOFU content.
        These target featured snippets and voice search.
        """
        prefixes = [
            "what is", "how to", "why", "when to", "where to find",
            "best", "top", "how much does", "is it worth", "can you",
        ]

        suffixes = [
            "for business", "for enterprise", "examples", "benefits",
            "vs", "alternatives", "pricing", "guide", "tutorial",
        ]

        suggestions = []

        for prefix in prefixes:
            suggestions.append(KeywordSuggestion(
                keyword=f"{prefix} {seed}",
                source="question_generated",
            ))

        for suffix in suffixes:
            suggestions.append(KeywordSuggestion(
                keyword=f"{seed} {suffix}",
                source="question_generated",
            ))

        return suggestions

    # =========================================================================
    # Main Collection Method
    # =========================================================================

    def collect_keywords(self, seed_keywords: list[str] = None) -> list[KeywordSuggestion]:
        """
        Collect keywords from all available sources.

        Args:
            seed_keywords: List of seed keywords. If None, uses industry verticals.
        """
        if seed_keywords is None:
            seed_keywords = INDUSTRY_VERTICALS[:5]  # Top 5 industry terms

        all_suggestions = []
        seen_keywords = set()

        print("  [Keywords] Collecting keyword data...")

        # Always use free sources
        for seed in seed_keywords:
            print(f"    Processing: {seed}")

            # Google Autocomplete (free)
            autocomplete = self.get_autocomplete_suggestions(seed)
            for s in autocomplete:
                if s.keyword.lower() not in seen_keywords:
                    seen_keywords.add(s.keyword.lower())
                    all_suggestions.append(s)

            # Bing Autosuggest (free, different suggestions)
            bing = self.get_bing_suggestions(seed)
            for s in bing:
                if s.keyword.lower() not in seen_keywords:
                    seen_keywords.add(s.keyword.lower())
                    all_suggestions.append(s)

            # Question keywords (generated, for TOFU content)
            questions = self.generate_question_keywords(seed)
            for s in questions:
                if s.keyword.lower() not in seen_keywords:
                    seen_keywords.add(s.keyword.lower())
                    all_suggestions.append(s)

            time.sleep(0.3)  # Rate limiting

        # Google Trends (free)
        try:
            trends = self.get_trending_keywords()
            for s in trends:
                if s.keyword.lower() not in seen_keywords:
                    seen_keywords.add(s.keyword.lower())
                    all_suggestions.append(s)
        except:
            pass

        # Paid sources if configured
        if self.config.seo_tool_mode == "dataforseo":
            for seed in seed_keywords[:3]:
                dataforseo = self.get_dataforseo_keywords(seed)
                all_suggestions.extend(dataforseo)

        elif self.config.seo_tool_mode == "serpapi":
            for seed in seed_keywords[:3]:
                serp_data = self.get_serpapi_data(seed)
                for question in serp_data.get('people_also_ask', []):
                    all_suggestions.append(KeywordSuggestion(
                        keyword=question,
                        source="serpapi_paa",
                    ))
                for related in serp_data.get('related_searches', []):
                    all_suggestions.append(KeywordSuggestion(
                        keyword=related,
                        source="serpapi_related",
                    ))

        print(f"  [Keywords] Collected {len(all_suggestions)} keyword suggestions")
        return all_suggestions

    def get_location_keywords(self, service: str, locations: list[str] = None) -> list[KeywordSuggestion]:
        """
        Generate location-specific keyword suggestions.
        """
        if locations is None:
            locations = []
            for country, cities in GEO_TARGETS.items():
                locations.extend(cities)

        suggestions = []
        templates = [
            "{service} in {location}",
            "{service} {location}",
            "{location} {service} company",
            "best {service} {location}",
            "{service} services {location}",
        ]

        for location in locations:
            for template in templates:
                keyword = template.format(service=service, location=location)
                suggestions.append(KeywordSuggestion(
                    keyword=keyword,
                    source="location_generated",
                ))

        return suggestions
