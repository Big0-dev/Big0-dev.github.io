# Lighthouse Audit Report

**Generated:** 2025-12-05 16:04:36
**Site:** https://big0.dev

## Summary

| Page | Performance | Accessibility | Best Practices | SEO |
|------|-------------|---------------|----------------|-----|
| / | 🟡 81 | 🟢 100 | 🟢 100 | 🟢 100 |
| /about.html | 🟡 82 | 🟢 98 | 🟢 100 | 🟢 100 |
| /contact.html | 🟡 82 | 🟢 96 | 🟢 100 | 🟢 100 |
| /services.html | 🟡 81 | 🟢 100 | 🟢 100 | 🟢 100 |
| /industries.html | 🟡 81 | 🟢 100 | 🟢 100 | 🟢 100 |
| /case-studies.html | 🟡 74 | 🟢 100 | 🟢 100 | 🟢 100 |
| /blog.html | 🟡 84 | 🟢 98 | 🟢 100 | 🟢 100 |
| /news.html | 🟡 80 | 🟢 98 | 🟢 100 | 🟢 100 |
| /services/ai-ml-services.html | 🟡 87 | 🟢 96 | 🟢 100 | 🟢 100 |
| /services/cloud-services.html | 🟡 89 | 🟢 96 | 🟢 100 | 🟢 100 |
| /services/software-development.html | 🟡 87 | 🟢 96 | 🟢 100 | 🟢 100 |
| /industries/finance.html | 🟡 87 | 🟢 95 | 🟢 100 | 🟢 100 |
| /industries/healthcare.html | 🟡 88 | 🟢 96 | 🟢 100 | 🟢 100 |
| **Average** | 🟡 **83** | 🟢 **97** | 🟢 **100** | 🟢 **100** |

---

## Common Issues

Issues found across multiple pages, sorted by frequency:

### Avoid large layout shifts

- **Severity:** Critical
- **Affected pages:** 13
- **Description:** These are the largest layout shifts observed on the page. Each table item represents a single layout shift, and shows the element that shifted the most. Below each item are possible root causes that l...

### Reduce unused JavaScript

- **Severity:** Critical
- **Affected pages:** 13
- **Description:** Reduce unused JavaScript and defer loading scripts until they are required to decrease bytes consumed by network activity. [Learn how to reduce unused JavaScript](https://developer.chrome.com/docs/lig...

### Layout shift culprits

- **Severity:** Critical
- **Affected pages:** 13
- **Description:** Layout shifts occur when elements move absent any user interaction. [Investigate the causes of layout shifts](https://developer.chrome.com/docs/performance/insights/cls-culprit), such as elements bein...

### Network dependency tree

- **Severity:** Critical
- **Affected pages:** 13
- **Description:** [Avoid chaining critical requests](https://developer.chrome.com/docs/performance/insights/network-dependency-tree) by reducing the length of chains, reducing the download size of resources, or deferri...

### Render blocking requests

- **Severity:** Critical
- **Affected pages:** 13
- **Description:** Requests are blocking the page's initial render, which may delay LCP. [Deferring or inlining](https://developer.chrome.com/docs/performance/insights/render-blocking) can move these network requests ou...

### Cumulative Layout Shift

- **Severity:** Warning
- **Affected pages:** 13
- **Description:** Cumulative Layout Shift measures the movement of visible elements within the viewport. [Learn more about the Cumulative Layout Shift metric](https://web.dev/articles/cls).

### Use efficient cache lifetimes

- **Severity:** Minor
- **Affected pages:** 13
- **Description:** A long cache lifetime can speed up repeat visits to your page. [Learn more about caching](https://developer.chrome.com/docs/performance/insights/cache).

### Speed Index

- **Severity:** Minor
- **Affected pages:** 13
- **Description:** Speed Index shows how quickly the contents of a page are visibly populated. [Learn more about the Speed Index metric](https://developer.chrome.com/docs/lighthouse/performance/speed-index/).

### Time to Interactive

- **Severity:** Minor
- **Affected pages:** 13
- **Description:** Time to Interactive is the amount of time it takes for the page to become fully interactive. [Learn more about the Time to Interactive metric](https://developer.chrome.com/docs/lighthouse/performance/...

### Avoid multiple page redirects

- **Severity:** Critical
- **Affected pages:** 12
- **Description:** Redirects introduce additional delays before the page can be loaded. [Learn how to avoid page redirects](https://developer.chrome.com/docs/lighthouse/performance/redirects/).

### Document request latency

- **Severity:** Critical
- **Affected pages:** 12
- **Description:** Your first network request is the most important. [Reduce its latency](https://developer.chrome.com/docs/performance/insights/document-latency) by avoiding redirects, ensuring a fast server response, ...

### First Contentful Paint

- **Severity:** Minor
- **Affected pages:** 12
- **Description:** First Contentful Paint marks the time at which the first text or image is painted. [Learn more about the First Contentful Paint metric](https://developer.chrome.com/docs/lighthouse/performance/first-c...

### Reduce initial server response time

- **Severity:** Critical
- **Affected pages:** 5
- **Description:** Keep the server response time for the main document short because all other requests depend on it. [Learn more about the Time to First Byte metric](https://developer.chrome.com/docs/lighthouse/perform...

### Background and foreground colors do not have a sufficient contrast ratio.

- **Severity:** Critical
- **Affected pages:** 5
- **Description:** Low-contrast text is difficult or impossible for many users to read. [Learn how to provide sufficient color contrast](https://dequeuniversity.com/rules/axe/4.11/color-contrast).

### Heading elements are not in a sequentially-descending order

- **Severity:** Critical
- **Affected pages:** 4
- **Description:** Properly ordered headings that do not skip levels convey the semantic structure of the page, making it easier to navigate and understand when using assistive technologies. [Learn more about heading or...

### Max Potential First Input Delay

- **Severity:** Warning
- **Affected pages:** 3
- **Description:** The maximum potential First Input Delay that your users could experience is the duration of the longest task. [Learn more about the Maximum Potential First Input Delay metric](https://developer.chrome...

### Forced reflow

- **Severity:** Critical
- **Affected pages:** 2
- **Description:** A forced reflow occurs when JavaScript queries geometric properties (such as offsetWidth) after styles have been invalidated by a change to the DOM state. This can result in poor performance. Learn mo...

### Improve image delivery

- **Severity:** Minor
- **Affected pages:** 2
- **Description:** Reducing the download time of images can improve the perceived load time of the page and LCP. [Learn more about optimizing image size](https://developer.chrome.com/docs/performance/insights/image-deli...

### `<frame>` or `<iframe>` elements do not have a title

- **Severity:** Critical
- **Affected pages:** 1
- **Description:** Screen reader users rely on frame titles to describe the contents of frames. [Learn more about frame titles](https://dequeuniversity.com/rules/axe/4.11/frame-title).

### Largest Contentful Paint

- **Severity:** Minor
- **Affected pages:** 1
- **Description:** Largest Contentful Paint marks the time at which the largest text or image is painted. [Learn more about the Largest Contentful Paint metric](https://developer.chrome.com/docs/lighthouse/performance/l...

### Total Blocking Time

- **Severity:** Minor
- **Affected pages:** 1
- **Description:** Sum of all time periods between FCP and Time to Interactive, when task length exceeded 50ms, expressed in milliseconds. [Learn more about the Total Blocking Time metric](https://developer.chrome.com/d...

---

## Detailed Results by Page

### /

**Scores:** Performance: 81 | Accessibility: 100 | Best Practices: 100 | SEO: 100

**Critical Issues:**
- Avoid large layout shifts
- Reduce unused JavaScript
- Layout shift culprits
- Network dependency tree

### /about.html

**Scores:** Performance: 82 | Accessibility: 98 | Best Practices: 100 | SEO: 100

**Critical Issues:**
- Avoid multiple page redirects
- Avoid large layout shifts
- Heading elements are not in a sequentially-descending order
- Layout shift culprits
- Document request latency

### /contact.html

**Scores:** Performance: 82 | Accessibility: 96 | Best Practices: 100 | SEO: 100

**Critical Issues:**
- Avoid multiple page redirects
- Avoid large layout shifts
- `<frame>` or `<iframe>` elements do not have a title
- Layout shift culprits
- Document request latency

### /services.html

**Scores:** Performance: 81 | Accessibility: 100 | Best Practices: 100 | SEO: 100

**Critical Issues:**
- Reduce initial server response time
- Avoid multiple page redirects
- Avoid large layout shifts
- Layout shift culprits
- Document request latency

### /industries.html

**Scores:** Performance: 81 | Accessibility: 100 | Best Practices: 100 | SEO: 100

**Critical Issues:**
- Avoid multiple page redirects
- Avoid large layout shifts
- Layout shift culprits
- Document request latency
- Network dependency tree

### /case-studies.html

**Scores:** Performance: 74 | Accessibility: 100 | Best Practices: 100 | SEO: 100

**Critical Issues:**
- Reduce initial server response time
- Avoid multiple page redirects
- Avoid large layout shifts
- Layout shift culprits
- Document request latency

### /blog.html

**Scores:** Performance: 84 | Accessibility: 98 | Best Practices: 100 | SEO: 100

**Critical Issues:**
- Avoid multiple page redirects
- Avoid large layout shifts
- Heading elements are not in a sequentially-descending order
- Layout shift culprits
- Document request latency

### /news.html

**Scores:** Performance: 80 | Accessibility: 98 | Best Practices: 100 | SEO: 100

**Critical Issues:**
- Reduce initial server response time
- Avoid multiple page redirects
- Avoid large layout shifts
- Heading elements are not in a sequentially-descending order
- Layout shift culprits

### /services/ai-ml-services.html

**Scores:** Performance: 87 | Accessibility: 96 | Best Practices: 100 | SEO: 100

**Critical Issues:**
- Reduce initial server response time
- Avoid multiple page redirects
- Avoid large layout shifts
- Background and foreground colors do not have a sufficient contrast ratio.
- Layout shift culprits

### /services/cloud-services.html

**Scores:** Performance: 89 | Accessibility: 96 | Best Practices: 100 | SEO: 100

**Critical Issues:**
- Avoid multiple page redirects
- Avoid large layout shifts
- Background and foreground colors do not have a sufficient contrast ratio.
- Layout shift culprits
- Document request latency

### /services/software-development.html

**Scores:** Performance: 87 | Accessibility: 96 | Best Practices: 100 | SEO: 100

**Critical Issues:**
- Avoid multiple page redirects
- Avoid large layout shifts
- Background and foreground colors do not have a sufficient contrast ratio.
- Layout shift culprits
- Document request latency

### /industries/finance.html

**Scores:** Performance: 87 | Accessibility: 95 | Best Practices: 100 | SEO: 100

**Critical Issues:**
- Avoid multiple page redirects
- Avoid large layout shifts
- Background and foreground colors do not have a sufficient contrast ratio.
- Heading elements are not in a sequentially-descending order
- Layout shift culprits

### /industries/healthcare.html

**Scores:** Performance: 88 | Accessibility: 96 | Best Practices: 100 | SEO: 100

**Critical Issues:**
- Reduce initial server response time
- Avoid multiple page redirects
- Avoid large layout shifts
- Background and foreground colors do not have a sufficient contrast ratio.
- Layout shift culprits
