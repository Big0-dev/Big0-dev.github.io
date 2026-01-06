# Manual Exports Directory

This folder stores manual exports from service dashboards that contain data **not available via API**.

## Why Manual Exports?

Each service's API only exposes a subset of the data available in their dashboard. This folder stores the rest.

---

## Google Search Console Exports

**Location:** `gsc/`

### Data NOT available via API:

| Report | What it contains | How to export |
|--------|------------------|---------------|
| **Index Coverage** | 404 errors, crawl errors, excluded pages, indexed pages | GSC → Pages → Export |
| **Core Web Vitals** | LCP, FID, CLS issues by URL | GSC → Core Web Vitals → Export |
| **Mobile Usability** | Mobile-specific issues | GSC → Mobile Usability → Export |
| **Sitemaps** | Sitemap submission status, errors | GSC → Sitemaps → Export |
| **Links** | Internal/external link reports | GSC → Links → Export Top linking sites |
| **Manual Actions** | Google penalties (if any) | GSC → Security & Manual Actions |
| **Rich Results** | Structured data issues | GSC → Enhancements → [type] → Export |

### How to Export:

1. Go to [Google Search Console](https://search.google.com/search-console)
2. Select `big0.dev` property
3. Navigate to the report (e.g., Pages for Coverage)
4. Click the **Export** button (top right)
5. Choose **Download CSV**
6. Save to `exports/gsc/` with descriptive name

### Recommended exports:

```
gsc/
├── coverage-drilldown-YYYY-MM-DD.csv      # All indexed/excluded URLs
├── core-web-vitals-YYYY-MM-DD.csv         # Performance issues
├── mobile-usability-YYYY-MM-DD.csv        # Mobile issues
├── internal-links-YYYY-MM-DD.csv          # Internal linking structure
└── external-links-YYYY-MM-DD.csv          # Backlinks
```

---

## Google Analytics 4 Exports

**Location:** `ga4/`

### Data NOT available via API:

| Report | What it contains | How to export |
|--------|------------------|---------------|
| **Funnel Exploration** | Step-by-step conversion funnels | Explorations → Share → Export |
| **Path Exploration** | User navigation paths | Explorations → Share → Export |
| **User Explorer** | Individual user journeys | User Explorer → Export |
| **Cohort Analysis** | Retention by cohort | Explorations → Share → Export |
| **Attribution** | Conversion attribution models | Advertising → Attribution → Export |
| **Predictive Metrics** | Churn/purchase probability | Only in dashboard |

### How to Export:

1. Go to [Google Analytics](https://analytics.google.com)
2. Select the Big0 property
3. Navigate to **Explore** for custom reports
4. Build your exploration, then **Export** (top right)
5. Save to `exports/ga4/`

### Recommended exports:

```
ga4/
├── funnel-contact-form-YYYY-MM-DD.csv     # Contact form funnel
├── user-paths-YYYY-MM-DD.csv              # Navigation patterns
├── top-conversion-paths-YYYY-MM-DD.csv    # Attribution paths
└── cohort-retention-YYYY-MM-DD.csv        # User retention
```

---

## Microsoft Clarity Exports

**Location:** `clarity/`

### Data NOT available via API:

| Report | What it contains | How to export |
|--------|------------------|---------------|
| **Heatmaps** | Click/scroll/area heatmaps | Heatmaps → Screenshot (PNG) |
| **Session Recordings** | Video of user sessions | Not exportable (watch in dashboard) |
| **Funnels** | Custom conversion funnels | Funnels → Export |
| **Smart Events** | Auto-detected events | Smart Events → Export |
| **Copilot Insights** | AI-generated insights | Copy from dashboard |

### How to Export:

1. Go to [Microsoft Clarity](https://clarity.microsoft.com)
2. Select project `t1zp8ama5q`
3. Navigate to the report
4. Click **Export** or screenshot for heatmaps
5. Save to `exports/clarity/`

### Recommended exports:

```
clarity/
├── heatmap-homepage-YYYY-MM-DD.png        # Homepage click heatmap
├── heatmap-contact-YYYY-MM-DD.png         # Contact page heatmap
├── funnel-lead-gen-YYYY-MM-DD.csv         # Lead generation funnel
└── insights-YYYY-MM-DD.txt                # Copilot insights (copy/paste)
```

---

## When to Update Exports

Run `uv run python -m seo_engine.run` and you'll be prompted to update exports if they're stale (>7 days old).

**Recommended schedule:**
- **Coverage report:** Weekly (to catch new 404s)
- **Core Web Vitals:** After site changes
- **Heatmaps:** Monthly or after major UI changes
- **Funnels:** Monthly

---

## File Naming Convention

Use this format: `{report-type}-{YYYY-MM-DD}.{ext}`

Examples:
- `coverage-drilldown-2026-01-06.csv`
- `heatmap-homepage-2026-01-06.png`
- `funnel-contact-2026-01-06.csv`
