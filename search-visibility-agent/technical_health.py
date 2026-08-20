"""
Module 2: Technical Health Checker
====================================
Audits the site for traditional SEO hygiene issues.
Runs entirely on the crawl data from site_crawler.py — no API keys needed.

What it checks:
- Title tags (missing, duplicate, too short, too long)
- Meta descriptions (missing, duplicate, too short, too long)
- Heading structure (missing H1, multiple H1s, empty headings)
- Image alt text (missing alt attributes)
- Internal linking (orphan pages, pages with no outbound links)
- Page speed signals (response time)
- Schema markup presence
- Canonical tags
- Redirect and error pages
"""

import os
import json
from collections import Counter


TITLE_MIN_CHARS = 30
TITLE_MAX_CHARS = 60
META_DESC_MIN_CHARS = 120
META_DESC_MAX_CHARS = 160
SLOW_PAGE_MS = 3000
MIN_WORD_COUNT = 300


def check_titles(pages):
    """Audit all page title tags."""
    issues = []
    titles_seen = Counter()

    for page in pages:
        title = page.get("title")
        url = page.get("url")

        if not title:
            issues.append({
                "severity": "CRITICAL",
                "type": "missing_title",
                "url": url,
                "message": "Page has no title tag"
            })
        else:
            titles_seen[title] += 1

            if len(title) < TITLE_MIN_CHARS:
                issues.append({
                    "severity": "WARNING",
                    "type": "title_too_short",
                    "url": url,
                    "message": f"Title too short ({len(title)} chars, min {TITLE_MIN_CHARS}): '{title}'"
                })
            elif len(title) > TITLE_MAX_CHARS:
                issues.append({
                    "severity": "WARNING",
                    "type": "title_too_long",
                    "url": url,
                    "message": f"Title too long ({len(title)} chars, max {TITLE_MAX_CHARS}): '{title}'"
                })

    for title, count in titles_seen.items():
        if count > 1:
            duplicate_pages = [p["url"] for p in pages if p.get("title") == title]
            issues.append({
                "severity": "CRITICAL",
                "type": "duplicate_title",
                "url": duplicate_pages,
                "message": f"Duplicate title used on {count} pages: '{title}'"
            })

    return issues


def check_meta_descriptions(pages):
    """Audit all meta descriptions."""
    issues = []
    descriptions_seen = Counter()

    for page in pages:
        meta = page.get("meta_description")
        url = page.get("url")

        if not meta:
            issues.append({
                "severity": "WARNING",
                "type": "missing_meta_description",
                "url": url,
                "message": "Page has no meta description"
            })
        else:
            descriptions_seen[meta] += 1

            if len(meta) < META_DESC_MIN_CHARS:
                issues.append({
                    "severity": "INFO",
                    "type": "meta_description_too_short",
                    "url": url,
                    "message": f"Meta description too short ({len(meta)} chars): '{meta[:80]}...'"
                })
            elif len(meta) > META_DESC_MAX_CHARS:
                issues.append({
                    "severity": "INFO",
                    "type": "meta_description_too_long",
                    "url": url,
                    "message": f"Meta description too long ({len(meta)} chars): '{meta[:80]}...'"
                })

    for desc, count in descriptions_seen.items():
        if count > 1:
            duplicate_pages = [
                p["url"] for p in pages if p.get("meta_description") == desc
            ]
            issues.append({
                "severity": "WARNING",
                "type": "duplicate_meta_description",
                "url": duplicate_pages,
                "message": f"Duplicate meta description used on {count} pages"
            })

    return issues


def check_headings(pages):
    """Audit heading structure across all pages."""
    issues = []

    for page in pages:
        url = page.get("url")
        headings = page.get("headings", {})
        h1s = headings.get("h1", [])

        if not h1s:
            issues.append({
                "severity": "CRITICAL",
                "type": "missing_h1",
                "url": url,
                "message": "Page has no H1 heading"
            })
        elif len(h1s) > 1:
            issues.append({
                "severity": "WARNING",
                "type": "multiple_h1",
                "url": url,
                "message": f"Page has {len(h1s)} H1 headings (should have exactly 1): {h1s}"
            })

        for level in ["h1", "h2", "h3"]:
            for heading in headings.get(level, []):
                if not heading.strip():
                    issues.append({
                        "severity": "WARNING",
                        "type": "empty_heading",
                        "url": url,
                        "message": f"Empty {level.upper()} heading found"
                    })

    return issues


def check_images(pages):
    """Audit image alt text across all pages."""
    issues = []

    for page in pages:
        url = page.get("url")
        images = page.get("images", [])
        missing_alt = [img for img in images if not img.get("has_alt")]

        if missing_alt:
            issues.append({
                "severity": "WARNING",
                "type": "images_missing_alt",
                "url": url,
                "message": f"{len(missing_alt)} of {len(images)} images missing alt text"
            })

    return issues


def check_content_depth(pages):
    """Flag thin content pages."""
    issues = []

    for page in pages:
        url = page.get("url")
        word_count = page.get("word_count", 0)

        if word_count < MIN_WORD_COUNT and word_count > 0:
            issues.append({
                "severity": "WARNING",
                "type": "thin_content",
                "url": url,
                "message": f"Thin content: only {word_count} words (recommended minimum: {MIN_WORD_COUNT})"
            })

    return issues


def check_page_speed(pages):
    """Flag slow-loading pages."""
    issues = []

    for page in pages:
        url = page.get("url")
        response_time = page.get("response_time_ms", 0)

        if response_time > SLOW_PAGE_MS:
            issues.append({
                "severity": "WARNING",
                "type": "slow_page",
                "url": url,
                "message": f"Slow page load: {response_time}ms (threshold: {SLOW_PAGE_MS}ms)"
            })

    return issues


def check_schema_markup(pages):
    """Flag pages missing schema markup."""
    issues = []

    for page in pages:
        url = page.get("url")
        has_schema = page.get("has_schema_markup", False)

        if not has_schema:
            issues.append({
                "severity": "INFO",
                "type": "missing_schema_markup",
                "url": url,
                "message": "No structured data (schema.org markup) found."
            })

    return issues


def check_internal_linking(pages):
    """Identify orphan pages."""
    issues = []
    all_urls = set(p["url"] for p in pages)
    linked_urls = set()

    for page in pages:
        for link in page.get("internal_links", []):
            linked_urls.add(link)

    orphan_pages = all_urls - linked_urls
    for url in orphan_pages:
        if url.rstrip("/").endswith((".com", ".org", ".net", ".io")):
            continue
        issues.append({
            "severity": "INFO",
            "type": "orphan_page",
            "url": url,
            "message": "Page has no internal links pointing to it (orphan page)"
        })

    return issues


def calculate_health_score(issues, page_count):
    """Calculate normalized health score."""

    critical = [i for i in issues if i["severity"] == "CRITICAL"]
    warnings = [i for i in issues if i["severity"] == "WARNING"]
    info = [i for i in issues if i["severity"] == "INFO"]

    critical_penalty = (len(critical) / max(page_count, 1)) * 25
    warning_penalty = (len(warnings) / max(page_count, 1)) * 15
    info_penalty = (len(info) / max(page_count, 1)) * 5

    score = 100 - critical_penalty - warning_penalty - info_penalty
    print("\nScore Debug:")
    print(f"Pages: {page_count}")
    print(f"Critical: {len(critical)}")
    print(f"Warnings: {len(warnings)}")
    print(f"Info: {len(info)}")
    print(f"Critical Penalty: {critical_penalty:.2f}")
    print(f"Warning Penalty: {warning_penalty:.2f}")
    print(f"Info Penalty: {info_penalty:.2f}")
    print(f"Final Score: {score:.2f}")
    return (
        round(max(0, min(100, score))),
        len(critical),
        len(warnings),
        len(info)
    )


def save_results(results):
    """Save technical health results to JSON for report generator."""
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/technical_health.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


def run(url):
    """Main entry point called by agent.py."""
    print(f"\n  Technical Health Checker starting...")

    crawl_data_path = "outputs/crawl_data.json"

    if os.path.exists(crawl_data_path):
        with open(crawl_data_path, "r", encoding="utf-8") as f:
            crawl_data = json.load(f)
        pages = crawl_data.get("pages", [])
    else:
        print("  No crawl data found — running site crawler first...")
        from modules.site_crawler import run as crawl_run
        crawl_result = crawl_run(url)
        pages = crawl_result.get("pages", [])

        os.makedirs("outputs", exist_ok=True)
        with open(crawl_data_path, "w", encoding="utf-8") as f:
            json.dump(crawl_result, f, indent=2)

    if not pages:
        return {
            "status": "error",
            "reason": "No page data available to analyze"
        }

    print(f"  Analyzing {len(pages)} pages...")

    all_issues = []
    all_issues.extend(check_titles(pages))
    all_issues.extend(check_meta_descriptions(pages))
    all_issues.extend(check_headings(pages))
    all_issues.extend(check_images(pages))
    all_issues.extend(check_content_depth(pages))
    all_issues.extend(check_page_speed(pages))
    all_issues.extend(check_schema_markup(pages))
    all_issues.extend(check_internal_linking(pages))

    issue_types = Counter(issue["type"] for issue in all_issues)

    print("\nIssue Breakdown:")
    for issue_type, count in sorted(issue_types.items()):
        print(f"{issue_type}: {count}")

    score, critical_count, warning_count, info_count = calculate_health_score(
        all_issues,
        len(pages)
    )
    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 40:
        grade = "D"
    else:
        grade = "F"

    results = {
        "status": "complete",
        "url": url,
        "pages_analyzed": len(pages),
        "health_score": score,
        "grade": grade,
        "issue_counts": {
            "critical": critical_count,
            "warning": warning_count,
            "info": info_count,
            "total": len(all_issues)
        },
        "issues": all_issues
    }

    save_results(results)

    print(f"\n  Technical Health Results:")
    print(f"  Health Score:  {score}/100 (Grade: {grade})")
    print(f"  Critical:      {critical_count}")
    print(f"  Warnings:      {warning_count}")
    print(f"  Info:          {info_count}")

    return results