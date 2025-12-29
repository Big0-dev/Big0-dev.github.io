#!/usr/bin/env python3
"""
404 URL Fixer - Process GSC 404 exports and generate redirects

Usage:
    1. Export 404 URLs from GSC:
       - Go to Search Console > Pages > Not indexed
       - Select "Soft 404" or "Not found (404)"
       - Click Export > Download CSV

    2. Run this script:
       uv run python -m seo_engine.tools.fix_404s path/to/export.csv

    3. Review generated redirects and add to _redirects file
"""

import csv
import json
import sys
import re
from pathlib import Path
from difflib import SequenceMatcher
from typing import Optional
from dataclasses import dataclass


@dataclass
class RedirectSuggestion:
    """A suggested redirect for a 404 URL"""
    old_url: str
    new_url: str
    confidence: float  # 0-1 score
    reason: str


class Fix404Tool:
    """Tool to analyze 404 URLs and suggest redirects"""

    def __init__(self, build_dir: Path = Path('build')):
        self.build_dir = build_dir
        self.existing_pages = self._load_existing_pages()

    def _load_existing_pages(self) -> dict[str, str]:
        """Load all existing pages from build directory"""
        pages = {}
        for html_file in self.build_dir.rglob('*.html'):
            rel_path = '/' + str(html_file.relative_to(self.build_dir))
            # Store both with and without .html
            pages[rel_path] = rel_path
            pages[rel_path.replace('.html', '')] = rel_path

            # Also store the filename for fuzzy matching
            stem = html_file.stem
            pages[stem] = rel_path

        return pages

    def _extract_path(self, url: str) -> str:
        """Extract path from full URL"""
        # Remove domain
        path = url
        if '://' in url:
            path = '/' + url.split('://', 1)[1].split('/', 1)[-1]
        return path.rstrip('/')

    def _find_similar_page(self, path: str) -> Optional[RedirectSuggestion]:
        """Find the most similar existing page"""
        # Direct match
        if path in self.existing_pages:
            return RedirectSuggestion(
                old_url=path,
                new_url=self.existing_pages[path],
                confidence=1.0,
                reason="Exact match (needs .html)"
            )

        # Try with .html
        if path + '.html' in self.existing_pages:
            return RedirectSuggestion(
                old_url=path,
                new_url=self.existing_pages[path + '.html'],
                confidence=1.0,
                reason="Missing .html extension"
            )

        # Extract meaningful parts for fuzzy matching
        parts = path.strip('/').split('/')
        filename = parts[-1] if parts else ''

        # Fuzzy match on filename
        best_match = None
        best_score = 0.0

        for existing_path, canonical in self.existing_pages.items():
            if existing_path.startswith('/') and existing_path.endswith('.html'):
                existing_parts = existing_path.strip('/').split('/')
                existing_filename = existing_parts[-1].replace('.html', '')

                # Compare filenames
                score = SequenceMatcher(None, filename, existing_filename).ratio()

                # Boost score if directory structure matches
                if len(parts) > 1 and len(existing_parts) > 1:
                    if parts[0] == existing_parts[0]:  # Same top-level dir
                        score += 0.2
                    if len(parts) > 2 and len(existing_parts) > 2:
                        if parts[1] == existing_parts[1]:  # Same second-level
                            score += 0.1

                if score > best_score:
                    best_score = score
                    best_match = canonical

        if best_match and best_score > 0.6:
            return RedirectSuggestion(
                old_url=path,
                new_url=best_match,
                confidence=min(best_score, 1.0),
                reason=f"Fuzzy match (score: {best_score:.2f})"
            )

        # Check for common patterns
        patterns = self._check_common_patterns(path)
        if patterns:
            return patterns

        return None

    def _check_common_patterns(self, path: str) -> Optional[RedirectSuggestion]:
        """Check for common URL pattern mismatches"""

        # Old blog patterns
        if '/blog/' in path and not path.endswith('.html'):
            new_path = path + '.html'
            if new_path in self.existing_pages:
                return RedirectSuggestion(
                    old_url=path,
                    new_url=new_path,
                    confidence=0.95,
                    reason="Blog missing .html"
                )

        # Underscore vs hyphen in services
        if '_' in path:
            hyphen_path = path.replace('_', '-')
            if hyphen_path in self.existing_pages:
                return RedirectSuggestion(
                    old_url=path,
                    new_url=self.existing_pages[hyphen_path],
                    confidence=0.9,
                    reason="Underscore to hyphen"
                )
            if hyphen_path + '.html' in self.existing_pages:
                return RedirectSuggestion(
                    old_url=path,
                    new_url=self.existing_pages[hyphen_path + '.html'],
                    confidence=0.9,
                    reason="Underscore to hyphen + .html"
                )

        # Service/industry singular vs plural
        singular_plural = [
            ('/service/', '/services/'),
            ('/industry/', '/industries/'),
            ('/blog/', '/blogs/'),
        ]
        for old, new in singular_plural:
            if old in path:
                new_path = path.replace(old, new)
                if new_path in self.existing_pages:
                    return RedirectSuggestion(
                        old_url=path,
                        new_url=self.existing_pages[new_path],
                        confidence=0.85,
                        reason="Singular to plural"
                    )

        return None

    def _suggest_category_redirect(self, path: str) -> Optional[RedirectSuggestion]:
        """Suggest a category page if no specific match found"""

        # Map to category pages
        category_map = {
            '/services/': '/services.html',
            '/industries/': '/industries.html',
            '/blog/': '/blog.html',
            '/case-studies/': '/case-studies.html',
            '/news/': '/news.html',
            '/products/': '/products.html',
        }

        for pattern, target in category_map.items():
            if pattern in path:
                return RedirectSuggestion(
                    old_url=path,
                    new_url=target,
                    confidence=0.5,
                    reason="Fallback to category page"
                )

        # Default to homepage
        return RedirectSuggestion(
            old_url=path,
            new_url='/index.html',
            confidence=0.3,
            reason="Fallback to homepage"
        )

    def process_url(self, url: str) -> RedirectSuggestion:
        """Process a single 404 URL and suggest redirect"""
        path = self._extract_path(url)

        # Try to find a similar page
        suggestion = self._find_similar_page(path)

        # If no good match, suggest category page
        if not suggestion:
            suggestion = self._suggest_category_redirect(path)

        return suggestion

    def process_csv(self, csv_path: Path) -> list[RedirectSuggestion]:
        """Process a GSC export CSV file"""
        suggestions = []

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            # GSC exports have different formats, try to detect
            first_line = f.readline()
            f.seek(0)

            if ',' in first_line:
                reader = csv.DictReader(f)
            else:
                # Tab-separated or single column
                reader = csv.reader(f)
                # Skip header
                next(reader, None)
                reader = [{'URL': row[0] if isinstance(row, list) else row} for row in reader]

            for row in reader:
                # Handle different column names
                url = row.get('URL') or row.get('url') or row.get('Page') or row.get('page')
                if url:
                    suggestion = self.process_url(url.strip())
                    suggestions.append(suggestion)

        return suggestions

    def process_urls(self, urls: list[str]) -> list[RedirectSuggestion]:
        """Process a list of URLs"""
        return [self.process_url(url) for url in urls]

    def generate_redirects(self, suggestions: list[RedirectSuggestion], min_confidence: float = 0.7) -> str:
        """Generate _redirects file content from suggestions"""
        lines = [
            "# Generated redirects for 404 URLs",
            "# Review before adding to _redirects file",
            ""
        ]

        high_confidence = []
        low_confidence = []

        for s in suggestions:
            if s.confidence >= min_confidence:
                high_confidence.append(s)
            else:
                low_confidence.append(s)

        lines.append("# High confidence redirects (can add directly)")
        for s in high_confidence:
            # Clean paths
            old = s.old_url.rstrip('/')
            new = s.new_url
            lines.append(f"{old}  {new}  301  # {s.reason}")

        if low_confidence:
            lines.append("")
            lines.append("# Low confidence - review manually")
            for s in low_confidence:
                old = s.old_url.rstrip('/')
                new = s.new_url
                lines.append(f"# {old}  {new}  301  # {s.reason} (confidence: {s.confidence:.0%})")

        return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nNo input file provided.")
        print("\nYou can also paste URLs directly (one per line, Ctrl+D to finish):")

        urls = []
        try:
            for line in sys.stdin:
                line = line.strip()
                if line:
                    urls.append(line)
        except KeyboardInterrupt:
            pass

        if not urls:
            sys.exit(1)

        tool = Fix404Tool()
        suggestions = tool.process_urls(urls)

    else:
        csv_path = Path(sys.argv[1])
        if not csv_path.exists():
            print(f"File not found: {csv_path}")
            sys.exit(1)

        print(f"Processing: {csv_path}")
        tool = Fix404Tool()
        suggestions = tool.process_csv(csv_path)

    # Print results
    print(f"\nProcessed {len(suggestions)} URLs\n")

    # Group by confidence
    high = [s for s in suggestions if s.confidence >= 0.7]
    medium = [s for s in suggestions if 0.5 <= s.confidence < 0.7]
    low = [s for s in suggestions if s.confidence < 0.5]

    print(f"High confidence (>=70%): {len(high)}")
    print(f"Medium confidence (50-70%): {len(medium)}")
    print(f"Low confidence (<50%): {len(low)}")

    # Generate redirects
    redirects = tool.generate_redirects(suggestions)

    # Save to file
    output_path = Path('seo_engine/reports/suggested_redirects.txt')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(redirects)

    print(f"\nRedirects saved to: {output_path}")
    print("\nHigh confidence redirects:")
    for s in high[:20]:
        print(f"  {s.old_url} -> {s.new_url}")

    if len(high) > 20:
        print(f"  ... and {len(high) - 20} more")


if __name__ == '__main__':
    main()
