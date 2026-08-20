"""
Module 1: Site Crawler
======================
Entry point for all analysis. Takes a URL, maps the full site structure,
and extracts all content needed by downstream modules.

What it does:
- Crawls all pages on the site (up to a configurable limit)
- Extracts page content, headings, meta data, links, images
- Builds a structured map of the site
- Passes clean data to technical_health, answer_readiness, and other modules

No API keys required.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time
import os
import json

# Maximum pages to crawl (keeps runtime reasonable for large sites)
MAX_PAGES = 50

# Polite crawl delay in seconds (avoids hammering the server)
CRAWL_DELAY = 0.5

HEADERS = {
    "User-Agent": "SearchVisibilityAgent/1.0 (SEO audit bot; "
                  "github.com/SamaraHJohansson/agent-portfolio)"
}

def normalize_domain(domain):
    return domain.lower().replace("www.", "")


def extract_page_data(url, soup):
    """
    Extract all relevant SEO and content data from a single page.
    Returns a structured dictionary of page data.
    """

    # --- Meta data ---
    title = soup.find("title")
    meta_desc = soup.find("meta", attrs={"name": "description"})
    meta_robots = soup.find("meta", attrs={"name": "robots"})
    canonical = soup.find("link", attrs={"rel": "canonical"})

    # --- Headings ---
    headings = {}
    for level in ["h1", "h2", "h3", "h4"]:
        headings[level] = [h.get_text(strip=True) for h in soup.find_all(level)]

    # --- Body text ---
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    body_text = soup.get_text(separator=" ", strip=True)
    word_count = len(body_text.split())

    # --- Links ---
    all_links = soup.find_all("a", href=True)
    print(f"Found {len(all_links)} links on {url}")
    internal_links = []
    external_links = []
    base_domain = normalize_domain(urlparse(url).netloc)

    for link in all_links:
        href = link.get("href", "").strip()
        if not href or href.startswith("#") or href.startswith("mailto:"):
            continue
        absolute = urljoin(url, href)
        print("LINK FOUND:", absolute)
        link_domain = normalize_domain(urlparse(absolute).netloc)
        if link_domain == base_domain:
            internal_links.append(absolute)
        else:
            external_links.append(absolute)

    # --- Images ---
    images = []
    for img in soup.find_all("img"):
        images.append({
            "src": img.get("src", ""),
            "alt": img.get("alt", ""),
            "has_alt": bool(img.get("alt", "").strip())
        })

    # --- Structured data ---
    schema_tags = soup.find_all("script", attrs={"type": "application/ld+json"})
    has_schema = len(schema_tags) > 0

    return {
        "url": url,
        "title": title.get_text(strip=True) if title else None,
        "meta_description": meta_desc.get("content", "").strip() if meta_desc else None,
        "meta_robots": meta_robots.get("content", "").strip() if meta_robots else None,
        "canonical": canonical.get("href", "").strip() if canonical else None,
        "headings": headings,
        "word_count": word_count,
        "body_text": body_text[:5000],
        "internal_links": list(set(internal_links)),
        "external_links": list(set(external_links)),
        "images": images,
        "has_schema_markup": has_schema,
        "schema_count": len(schema_tags)
    }


def crawl(start_url):
    """
    Crawl a website starting from start_url.
    Returns a list of page data dictionaries.
    """
    visited = set()
    queue = deque([start_url])
    pages = []
    
    base_domain = normalize_domain(urlparse(start_url).netloc)
    failed_urls = []

    print(f"  Starting crawl: {start_url}")
    print(f"  Max pages: {MAX_PAGES}")

    while queue and len(pages) < MAX_PAGES:
        url = queue.popleft()

        if url in visited:
            continue

        skip_extensions = (
            ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg",
            ".css", ".js", ".zip", ".xml", ".json"
        )
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            continue

        visited.add(url)

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=10,
                allow_redirects=True
            )

            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type:
                continue

            if response.status_code != 200:
                failed_urls.append({
                    "url": url,
                    "status_code": response.status_code
                })
                continue

            soup = BeautifulSoup(response.text, "lxml")
            page_data = extract_page_data(url, soup)
            page_data["status_code"] = response.status_code
            page_data["response_time_ms"] = int(
                response.elapsed.total_seconds() * 1000
            )
            pages.append(page_data)

            print(f"  ✓ Crawled ({len(pages)}/{MAX_PAGES}): {url}")

            for link in page_data["internal_links"]:
                link_domain = normalize_domain(urlparse(link).netloc)
                if link_domain == base_domain and link not in visited:
                    queue.append(link)

            time.sleep(CRAWL_DELAY)

        except requests.exceptions.Timeout:
            failed_urls.append({"url": url, "error": "timeout"})
            print(f"  ✗ Timeout: {url}")
        except requests.exceptions.ConnectionError:
            failed_urls.append({"url": url, "error": "connection error"})
            print(f"  ✗ Connection error: {url}")
        except Exception as e:
            failed_urls.append({"url": url, "error": str(e)})
            print(f"  ✗ Error: {url} — {str(e)}")

    return pages, failed_urls


def summarize(pages, failed_urls, start_url):
    """Build a summary of the crawl for reporting."""
    total_words = sum(p.get("word_count", 0) for p in pages)
    pages_missing_title = [p for p in pages if not p.get("title")]
    pages_missing_meta = [p for p in pages if not p.get("meta_description")]
    pages_missing_h1 = [p for p in pages if not p.get("headings", {}).get("h1")]
    pages_with_schema = [p for p in pages if p.get("has_schema_markup")]
    all_images = [img for p in pages for img in p.get("images", [])]
    images_missing_alt = [img for img in all_images if not img.get("has_alt")]

    return {
        "start_url": start_url,
        "total_pages_crawled": len(pages),
        "total_pages_failed": len(failed_urls),
        "total_word_count": total_words,
        "avg_word_count": int(total_words / len(pages)) if pages else 0,
        "pages_missing_title": len(pages_missing_title),
        "pages_missing_meta_description": len(pages_missing_meta),
        "pages_missing_h1": len(pages_missing_h1),
        "pages_with_schema_markup": len(pages_with_schema),
        "total_images": len(all_images),
        "images_missing_alt_text": len(images_missing_alt),
        "failed_urls": failed_urls
    }


def run(url):
    """
    Main entry point called by agent.py.
    Returns structured crawl data for use by all downstream modules.
    """
    print(f"\n  Site Crawler starting...")

    pages, failed_urls = crawl(url)

    if not pages:
        return {
            "status": "error",
            "reason": "No pages could be crawled. Check the URL and try again.",
            "pages": [],
            "summary": {}
        }

    summary = summarize(pages, failed_urls, url)

    print(f"\n  Crawl complete:")
    print(f"  Pages crawled:  {summary['total_pages_crawled']}")
    print(f"  Pages failed:   {summary['total_pages_failed']}")
    print(f"  Avg word count: {summary['avg_word_count']}")
    print("\n Crawl Coverage Note:")
    print(" If your website contains substantially more pages")
    print(" than were crawled, check site navigation,")
    print(" internal linking, sitemap availability,")
    print(" and JavaScript-rendered content.")

    result = {
        "status": "complete",
        "pages": pages,
        "summary": summary
    }

    os.makedirs("outputs", exist_ok=True)

    with open("outputs/crawl_data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return result