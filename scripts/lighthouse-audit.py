#!/usr/bin/env python3
"""
Lighthouse Audit Script for Big0.dev
Runs Lighthouse audits on all pages and generates a markdown report.
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
SITE_URL = "https://big0.dev"
OUTPUT_DIR = Path(__file__).parent.parent / "lighthouse-reports"
REPORT_FILE = OUTPUT_DIR / "lighthouse-report.md"

# Pages to audit (relative paths)
PAGES = [
    "/",
    "/about.html",
    "/contact.html",
    "/services.html",
    "/industries.html",
    "/case-studies.html",
    "/blog.html",
    "/news.html",
    # Sample detail pages
    "/services/ai-ml-services.html",
    "/services/cloud-services.html",
    "/services/software-development.html",
    "/industries/finance.html",
    "/industries/healthcare.html",
]


def run_lighthouse(url: str, output_path: Path) -> dict | None:
    """Run Lighthouse audit on a URL and return the results."""
    try:
        cmd = [
            "npx", "lighthouse",
            url,
            "--output=json",
            "--output-path=" + str(output_path),
            "--chrome-flags=--headless --no-sandbox",
            "--only-categories=performance,accessibility,best-practices,seo",
            "--quiet",
        ]

        subprocess.run(cmd, capture_output=True, timeout=120)

        if output_path.exists():
            with open(output_path) as f:
                return json.load(f)
    except subprocess.TimeoutExpired:
        print(f"  Timeout: {url}")
    except Exception as e:
        print(f"  Error auditing {url}: {e}")

    return None


def extract_scores(report: dict) -> dict:
    """Extract category scores from Lighthouse report."""
    categories = report.get("categories", {})
    return {
        "performance": int((categories.get("performance", {}).get("score") or 0) * 100),
        "accessibility": int((categories.get("accessibility", {}).get("score") or 0) * 100),
        "best_practices": int((categories.get("best-practices", {}).get("score") or 0) * 100),
        "seo": int((categories.get("seo", {}).get("score") or 0) * 100),
    }


def extract_issues(report: dict) -> list[dict]:
    """Extract failed audits from Lighthouse report."""
    issues = []
    audits = report.get("audits", {})

    for audit_id, audit in audits.items():
        score = audit.get("score")
        if score is not None and score < 1:
            issues.append({
                "id": audit_id,
                "title": audit.get("title", audit_id),
                "description": audit.get("description", ""),
                "score": score,
                "display_value": audit.get("displayValue", ""),
            })

    # Sort by score (worst first)
    issues.sort(key=lambda x: x["score"] if x["score"] is not None else 0)
    return issues


def get_score_emoji(score: int) -> str:
    """Get emoji indicator for score."""
    if score >= 90:
        return "🟢"
    elif score >= 50:
        return "🟡"
    else:
        return "🔴"


def generate_markdown_report(results: list[dict]) -> str:
    """Generate markdown report from audit results."""
    lines = [
        "# Lighthouse Audit Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Site:** {SITE_URL}",
        "",
        "## Summary",
        "",
        "| Page | Performance | Accessibility | Best Practices | SEO |",
        "|------|-------------|---------------|----------------|-----|",
    ]

    # Summary table
    for result in results:
        if result["scores"]:
            s = result["scores"]
            lines.append(
                f"| {result['page']} | "
                f"{get_score_emoji(s['performance'])} {s['performance']} | "
                f"{get_score_emoji(s['accessibility'])} {s['accessibility']} | "
                f"{get_score_emoji(s['best_practices'])} {s['best_practices']} | "
                f"{get_score_emoji(s['seo'])} {s['seo']} |"
            )
        else:
            lines.append(f"| {result['page']} | ❌ Failed | - | - | - |")

    # Calculate averages
    valid_results = [r for r in results if r["scores"]]
    if valid_results:
        avg_perf = sum(r["scores"]["performance"] for r in valid_results) // len(valid_results)
        avg_a11y = sum(r["scores"]["accessibility"] for r in valid_results) // len(valid_results)
        avg_bp = sum(r["scores"]["best_practices"] for r in valid_results) // len(valid_results)
        avg_seo = sum(r["scores"]["seo"] for r in valid_results) // len(valid_results)

        lines.append(
            f"| **Average** | "
            f"{get_score_emoji(avg_perf)} **{avg_perf}** | "
            f"{get_score_emoji(avg_a11y)} **{avg_a11y}** | "
            f"{get_score_emoji(avg_bp)} **{avg_bp}** | "
            f"{get_score_emoji(avg_seo)} **{avg_seo}** |"
        )

    lines.extend(["", "---", ""])

    # Collect all unique issues across pages
    all_issues = {}
    for result in results:
        for issue in result.get("issues", []):
            issue_id = issue["id"]
            if issue_id not in all_issues:
                all_issues[issue_id] = {
                    "title": issue["title"],
                    "description": issue["description"],
                    "pages": [],
                    "worst_score": 1,
                }
            all_issues[issue_id]["pages"].append(result["page"])
            if issue["score"] is not None:
                all_issues[issue_id]["worst_score"] = min(
                    all_issues[issue_id]["worst_score"],
                    issue["score"]
                )

    # Sort issues by frequency and severity
    sorted_issues = sorted(
        all_issues.items(),
        key=lambda x: (-len(x[1]["pages"]), x[1]["worst_score"])
    )

    lines.extend([
        "## Common Issues",
        "",
        "Issues found across multiple pages, sorted by frequency:",
        "",
    ])

    for issue_id, issue in sorted_issues[:30]:  # Top 30 issues
        page_count = len(issue["pages"])
        severity = "Critical" if issue["worst_score"] == 0 else "Warning" if issue["worst_score"] < 0.5 else "Minor"

        lines.extend([
            f"### {issue['title']}",
            "",
            f"- **Severity:** {severity}",
            f"- **Affected pages:** {page_count}",
            f"- **Description:** {issue['description'][:200]}..." if len(issue['description']) > 200 else f"- **Description:** {issue['description']}",
            "",
        ])

    lines.extend([
        "---",
        "",
        "## Detailed Results by Page",
        "",
    ])

    # Detailed per-page issues
    for result in results:
        lines.append(f"### {result['page']}")
        lines.append("")

        if result["scores"]:
            s = result["scores"]
            lines.append(f"**Scores:** Performance: {s['performance']} | Accessibility: {s['accessibility']} | Best Practices: {s['best_practices']} | SEO: {s['seo']}")
            lines.append("")

            critical_issues = [i for i in result.get("issues", []) if i["score"] == 0]
            if critical_issues:
                lines.append("**Critical Issues:**")
                for issue in critical_issues[:5]:
                    lines.append(f"- {issue['title']}")
                lines.append("")
        else:
            lines.append("*Audit failed*")
            lines.append("")

    return "\n".join(lines)


def main():
    """Run Lighthouse audits and generate report."""
    print("🔍 Starting Lighthouse Audit for Big0.dev")
    print("=" * 50)

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    results = []

    for i, page in enumerate(PAGES):
        url = SITE_URL + page
        print(f"[{i+1}/{len(PAGES)}] Auditing: {page}")

        output_path = OUTPUT_DIR / f"lighthouse-{page.replace('/', '_').replace('.html', '')}.json"
        report = run_lighthouse(url, output_path)

        if report:
            scores = extract_scores(report)
            issues = extract_issues(report)
            print(f"  ✓ Performance: {scores['performance']} | A11y: {scores['accessibility']} | BP: {scores['best_practices']} | SEO: {scores['seo']}")
        else:
            scores = None
            issues = []
            print(f"  ✗ Failed")

        results.append({
            "page": page,
            "url": url,
            "scores": scores,
            "issues": issues,
        })

    print("")
    print("📝 Generating report...")

    report_content = generate_markdown_report(results)

    with open(REPORT_FILE, "w") as f:
        f.write(report_content)

    print(f"✅ Report saved to: {REPORT_FILE}")
    print("")

    # Print summary
    valid = [r for r in results if r["scores"]]
    if valid:
        avg_perf = sum(r["scores"]["performance"] for r in valid) // len(valid)
        avg_a11y = sum(r["scores"]["accessibility"] for r in valid) // len(valid)
        print(f"📊 Average Scores:")
        print(f"   Performance: {avg_perf}")
        print(f"   Accessibility: {avg_a11y}")


if __name__ == "__main__":
    main()
