"""
Module 4: AI Search Gap Detector
==================================
Finds what AI search surfaces for your topics — and where you are missing.
This is the black hole solver.

Requires: OPENAI_API_KEY, PERPLEXITY_API_KEY
"""

import os
import json
import requests
from openai import OpenAI


MAX_TOPICS = 8
QUESTIONS_PER_TOPIC = 3


TOPIC_EXTRACTION_PROMPT = """You are analyzing a website to identify its core topic territory 
for SEO and AI search optimization.

Based on the site content below, identify the {max_topics} most important topics 
this website covers or should own in search results.

For each topic, generate {questions_per_topic} specific questions that a real user 
would type into Google, ChatGPT, or Perplexity when looking for information 
on this topic.

SITE URL: {url}
SITE CONTENT SUMMARY:
{content_summary}

Respond in this exact JSON format:
{{
  "site_description": "<one sentence describing what this site is about>",
  "target_audience": "<who this site serves>",
  "topics": [
    {{
      "topic": "<topic name>",
      "importance": "<why this topic matters for this site>",
      "questions": [
        "<specific user question 1>",
        "<specific user question 2>",
        "<specific user question 3>"
      ]
    }}
  ]
}}"""


GAP_ANALYSIS_PROMPT = """You are an AI search visibility analyst.

THEIR WEBSITE: {site_url}
THEIR SITE DESCRIPTION: {site_description}

QUESTION BEING ANALYZED: "{question}"
TOPIC: {topic}

AI SEARCH RESPONSE TO THIS QUESTION:
{ai_response}

Analyze this AI search response and determine:
1. Is the site owner's website cited or referenced in this response?
2. Are any competitors or other sites cited instead?
3. What type of gap does this represent?
4. What would the site need to do to be cited in this response?

Gap types:
- COMPETITOR_GAP: A direct competitor is cited instead of this site
- CONTENT_GAP: The question is answered but this site has no relevant content
- OPPORTUNITY_GAP: The AI response is weak — nobody owns this topic well
- NO_GAP: This site is already cited or the question is not relevant

Respond in this exact JSON format:
{{
  "question": "{question}",
  "topic": "{topic}",
  "gap_type": "<COMPETITOR_GAP|CONTENT_GAP|OPPORTUNITY_GAP|NO_GAP>",
  "site_cited": <true|false>,
  "competitors_cited": ["<competitor url or name if any>"],
  "ai_response_quality": "<strong|moderate|weak>",
  "gap_explanation": "<one sentence explaining the gap>",
  "recommendation": "<specific action this site should take to be cited>",
  "content_opportunity": "<title of a page or article that would address this gap>"
}}"""


def extract_content_summary(pages):
    """Build a content summary from crawled pages for topic extraction."""
    summaries = []
    for page in pages[:10]:
        title = page.get("title", "")
        h1s = page.get("headings", {}).get("h1", [])
        h2s = page.get("headings", {}).get("h2", [])[:5]
        text_snippet = page.get("body_text", "")[:500]

        summary = f"PAGE: {page.get('url', '')}\n"
        if title:
            summary += f"Title: {title}\n"
        if h1s:
            summary += f"H1: {', '.join(h1s)}\n"
        if h2s:
            summary += f"H2s: {', '.join(h2s)}\n"
        summary += f"Content: {text_snippet}\n"
        summaries.append(summary)

    return "\n---\n".join(summaries)


def extract_topics(client, url, pages):
    """Use OpenAI to identify core topics and generate questions."""
    print(f"  Extracting core topics from site content...")

    content_summary = extract_content_summary(pages)

    prompt = TOPIC_EXTRACTION_PROMPT.format(
        max_topics=MAX_TOPICS,
        questions_per_topic=QUESTIONS_PER_TOPIC,
        url=url,
        content_summary=content_summary[:4000]
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an SEO and AI search expert. "
                               "Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        print(f"  Error extracting topics: {str(e)}")
        return None


def query_perplexity(question, perplexity_api_key):
    """Query Perplexity API to see what AI search surfaces."""
    headers = {
        "Authorization": f"Bearer {perplexity_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-sonar-large-128k-online",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer concisely and cite sources."
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "max_tokens": 500,
        "temperature": 0.2,
        "return_citations": True
    }

    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        citations = data.get("citations", [])
        return {
            "response": content,
            "citations": citations,
            "source": "perplexity"
        }
    except Exception as e:
        return {
            "response": f"Error querying Perplexity: {str(e)}",
            "citations": [],
            "source": "perplexity_error"
        }


def query_openai_search(question, client):
    """Query OpenAI with web search as fallback."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-search-preview",
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=500
        )
        content = response.choices[0].message.content
        return {
            "response": content,
            "citations": [],
            "source": "openai_search"
        }
    except Exception as e:
        return {
            "response": f"Search query: {question} (OpenAI search unavailable: {str(e)})",
            "citations": [],
            "source": "openai_fallback"
        }


def analyze_gap(client, site_url, site_description, topic, question, ai_response):
    """Use OpenAI to analyze the gap between AI search results and site content."""
    prompt = GAP_ANALYSIS_PROMPT.format(
        site_url=site_url,
        site_description=site_description,
        question=question,
        topic=topic,
        ai_response=ai_response[:2000]
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI search visibility analyst. "
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
        return result

    except Exception as e:
        return {
            "question": question,
            "topic": topic,
            "gap_type": "ERROR",
            "error": str(e)
        }


def save_results(results):
    """Save AI search gap results to JSON."""
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/ai_search_gaps.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


def run(url):
    """Main entry point called by agent.py."""
    print(f"\n  AI Search Gap Detector starting...")

    openai_key = os.getenv("OPENAI_API_KEY")
    perplexity_key = os.getenv("PERPLEXITY_API_KEY")

    if not openai_key:
        return {
            "status": "skipped",
            "reason": "OPENAI_API_KEY not found in environment"
        }

    client = OpenAI(api_key=openai_key)

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

    topic_data = extract_topics(client, url, pages)
    if not topic_data:
        return {
            "status": "error",
            "reason": "Could not extract topics from site content"
        }

    site_description = topic_data.get("site_description", "")
    topics = topic_data.get("topics", [])
    print(f"  Identified {len(topics)} core topics")
    print(f"  Site description: {site_description}")

    all_gaps = []
    gap_summary = {
        "COMPETITOR_GAP": 0,
        "CONTENT_GAP": 0,
        "OPPORTUNITY_GAP": 0,
        "NO_GAP": 0
    }

    total_questions = sum(len(t.get("questions", [])) for t in topics)
    question_count = 0

    for topic_item in topics:
        topic_name = topic_item.get("topic", "")
        questions = topic_item.get("questions", [])

        print(f"\n  Topic: {topic_name}")

        for question in questions:
            question_count += 1
            print(f"  Querying ({question_count}/{total_questions}): {question[:60]}...")

            if perplexity_key:
                ai_result = query_perplexity(question, perplexity_key)
            else:
                ai_result = query_openai_search(question, client)
                print(f"  (Using OpenAI search — add PERPLEXITY_API_KEY for richer results)")

            ai_response_text = ai_result.get("response", "")
            citations = ai_result.get("citations", [])

            gap = analyze_gap(
                client, url, site_description,
                topic_name, question, ai_response_text
            )

            gap["ai_response_snippet"] = ai_response_text[:500]
            gap["ai_citations"] = citations
            gap["query_source"] = ai_result.get("source", "")

            all_gaps.append(gap)

            gap_type = gap.get("gap_type", "ERROR")
            if gap_type in gap_summary:
                gap_summary[gap_type] += 1

    opportunity_gaps = [
        g for g in all_gaps
        if g.get("gap_type") in ["CONTENT_GAP", "OPPORTUNITY_GAP"]
    ]
    competitor_gaps = [
        g for g in all_gaps
        if g.get("gap_type") == "COMPETITOR_GAP"
    ]

    results = {
        "status": "complete",
        "url": url,
        "site_description": site_description,
        "target_audience": topic_data.get("target_audience", ""),
        "topics_analyzed": len(topics),
        "questions_queried": question_count,
        "gap_summary": gap_summary,
        "competitor_gaps_count": len(competitor_gaps),
        "opportunity_gaps_count": len(opportunity_gaps),
        "all_gaps": all_gaps,
        "top_opportunities": opportunity_gaps[:5],
        "competitor_threats": competitor_gaps[:5]
    }

    save_results(results)

    print(f"\n  AI Search Gap Results:")
    print(f"  Topics analyzed:     {len(topics)}")
    print(f"  Questions queried:   {question_count}")
    print(f"  Competitor gaps:     {gap_summary['COMPETITOR_GAP']}")
    print(f"  Content gaps:        {gap_summary['CONTENT_GAP']}")
    print(f"  Opportunity gaps:    {gap_summary['OPPORTUNITY_GAP']}")
    print(f"  Already visible:     {gap_summary['NO_GAP']}")

    return results