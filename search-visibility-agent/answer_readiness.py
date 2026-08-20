"""
Module 3: Answer-Readiness Scorer
===================================
Scores each page for AI search citation-worthiness.
This is the core of the AI search black hole problem.

Requires: OPENAI_API_KEY
"""

import os
import json
from openai import OpenAI


REWRITE_THRESHOLD = 60
MAX_PAGES_TO_SCORE = 20


SCORING_PROMPT = """You are an expert in AI search optimization. Your job is to evaluate 
how likely a reasoning engine (Google AI Overviews, ChatGPT Search, Perplexity) 
is to cite this page when answering questions related to its topic.

Score this page on six dimensions, each out of 100. Then provide an overall score 
(weighted average) and three specific, actionable recommendations.

PAGE URL: {url}
PAGE TITLE: {title}
PAGE CONTENT (first 3000 chars):
{content}

Score on these six dimensions:

1. DIRECT ANSWER CLARITY (0-100)
   Does the page state its core point clearly and early?

2. QUESTION COVERAGE (0-100)
   Does the page address the real questions users ask about this topic?

3. ENTITY CLARITY (0-100)
   Are key people, products, places, concepts named and explained clearly?

4. FACTUAL STRUCTURE (0-100)
   Are claims stated as clear, extractable facts?

5. CONTENT AUTHORITY (0-100)
   Does the content demonstrate genuine expertise?

6. ANSWER FORMAT READINESS (0-100)
   Is the content structured for AI answer extraction?

Respond in this exact JSON format:
{{
  "scores": {{
    "direct_answer_clarity": <0-100>,
    "question_coverage": <0-100>,
    "entity_clarity": <0-100>,
    "factual_structure": <0-100>,
    "content_authority": <0-100>,
    "answer_format_readiness": <0-100>
  }},
  "overall_score": <0-100>,
  "grade": "<A/B/C/D/F>",
  "top_strength": "<one sentence describing what this page does well>",
  "critical_weakness": "<one sentence describing the biggest gap>",
  "recommendations": [
    "<specific actionable recommendation 1>",
    "<specific actionable recommendation 2>",
    "<specific actionable recommendation 3>"
  ],
  "rewrite_priority": <true/false>,
  "rewrite_reason": "<one sentence explaining why this page should/should not be rewritten>"
}}"""


def score_page(client, page):
    """Score a single page for answer-readiness using OpenAI."""
    url = page.get("url", "")
    title = page.get("title", "No title")
    content = page.get("body_text", "")[:3000]

    if not content.strip():
        return {
            "url": url,
            "status": "skipped",
            "reason": "No content to analyze"
        }

    prompt = SCORING_PROMPT.format(
        url=url,
        title=title,
        content=content
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI search optimization expert. "
                               "Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        result["url"] = url
        result["title"] = title
        result["status"] = "complete"
        return result

    except json.JSONDecodeError as e:
        return {
            "url": url,
            "status": "error",
            "reason": f"JSON parse error: {str(e)}"
        }
    except Exception as e:
        return {
            "url": url,
            "status": "error",
            "reason": str(e)
        }


def prioritize_pages(pages):
    """Select which pages to score first."""
    skip_patterns = [
        "privacy", "terms", "cookie", "sitemap",
        "404", "login", "cart", "checkout"
    ]

    scored_pages = []
    for page in pages:
        url = page.get("url", "").lower()
        word_count = page.get("word_count", 0)

        if any(pattern in url for pattern in skip_patterns):
            continue

        if word_count < 100:
            continue

        scored_pages.append(page)

    scored_pages.sort(key=lambda p: p.get("word_count", 0), reverse=True)
    return scored_pages[:MAX_PAGES_TO_SCORE]


def calculate_site_readiness(page_scores):
    """Calculate overall site-level answer-readiness score."""
    valid_scores = [
        p["overall_score"] for p in page_scores
        if p.get("status") == "complete" and "overall_score" in p
    ]

    if not valid_scores:
        return 0

    return int(sum(valid_scores) / len(valid_scores))


def save_results(results):
    """Save answer readiness results to JSON for report generator."""
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/answer_readiness.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


def run(url):
    """Main entry point called by agent.py."""
    print(f"\n  Answer-Readiness Scorer starting...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "status": "skipped",
            "reason": "OPENAI_API_KEY not found in environment"
        }

    client = OpenAI(api_key=api_key)

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
            "reason": "No page data available to score"
        }

    pages_to_score = prioritize_pages(pages)
    print(f"  Scoring {len(pages_to_score)} pages for AI answer-readiness...")

    page_scores = []
    rewrite_candidates = []

    for i, page in enumerate(pages_to_score):
        print(f"  Scoring ({i+1}/{len(pages_to_score)}): {page.get('url', '')}")
        score = score_page(client, page)
        page_scores.append(score)

        if (score.get("status") == "complete" and
                score.get("overall_score", 100) < REWRITE_THRESHOLD):
            rewrite_candidates.append({
                "url": score["url"],
                "title": score.get("title", ""),
                "overall_score": score.get("overall_score", 0),
                "critical_weakness": score.get("critical_weakness", ""),
                "recommendations": score.get("recommendations", [])
            })

    site_score = calculate_site_readiness(page_scores)

    if site_score >= 80:
        site_grade = "A"
    elif site_score >= 65:
        site_grade = "B"
    elif site_score >= 50:
        site_grade = "C"
    elif site_score >= 35:
        site_grade = "D"
    else:
        site_grade = "F"

    results = {
        "status": "complete",
        "url": url,
        "pages_scored": len(page_scores),
        "site_answer_readiness_score": site_score,
        "site_grade": site_grade,
        "rewrite_threshold": REWRITE_THRESHOLD,
        "rewrite_candidates_count": len(rewrite_candidates),
        "rewrite_candidates": rewrite_candidates,
        "page_scores": page_scores
    }

    save_results(results)

    print(f"\n  Answer-Readiness Results:")
    print(f"  Site Score:          {site_score}/100 (Grade: {site_grade})")
    print(f"  Pages Scored:        {len(page_scores)}")
    print(f"  Rewrite Candidates:  {len(rewrite_candidates)}")

    return results