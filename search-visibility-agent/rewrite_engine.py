"""
Module 6: Rewrite Engine
=========================
Takes underperforming pages identified by the Answer-Readiness Scorer
and produces optimized rewrites for both traditional SEO and AI search.

Requires: OPENAI_API_KEY
"""

import os
import json
from openai import OpenAI
from datetime import datetime


REWRITE_PROMPT = """You are an expert content optimizer specializing in both 
traditional SEO and AI search optimization.

You are rewriting a page to improve its performance in AI search results
while maintaining or improving its traditional SEO performance.

WEBSITE: {site_url}
PAGE URL: {page_url}
PAGE TITLE: {page_title}

CURRENT ANSWER-READINESS SCORES:
- Direct Answer Clarity: {score_direct_answer}/100
- Question Coverage: {score_question_coverage}/100
- Entity Clarity: {score_entity_clarity}/100
- Factual Structure: {score_factual_structure}/100
- Content Authority: {score_content_authority}/100
- Answer Format Readiness: {score_format_readiness}/100
- Overall Score: {overall_score}/100

CRITICAL WEAKNESS: {critical_weakness}

SPECIFIC RECOMMENDATIONS:
{recommendations}

ORIGINAL CONTENT:
{original_content}

Rewrite this content to address the identified weaknesses. Your rewrite should:
1. Open with a clear direct answer in the first 2-3 sentences
2. Use structured formatting (headers, lists, definitions)
3. Name and explain key entities clearly
4. Include specific extractable facts and data points
5. Cover natural questions a user would ask
6. Demonstrate genuine expertise

Respond in this exact JSON format:
{{
  "rewritten_title": "<optimized title tag, max 60 chars>",
  "rewritten_meta_description": "<optimized meta description, max 160 chars>",
  "rewritten_h1": "<optimized H1 heading>",
  "rewritten_content": "<full rewritten content in clean HTML>",
  "optimizations_made": [
    {{
      "optimization": "<what was changed>",
      "reason": "<why this improves AI search visibility>",
      "before": "<brief example of original text>",
      "after": "<brief example of rewritten text>"
    }}
  ],
  "ai_search_improvements": {{
    "direct_answer_added": "<describe the direct answer now at the top>",
    "entities_clarified": ["<entity 1>", "<entity 2>"],
    "facts_added": ["<fact or data point added>"],
    "format_changes": "<describe structural changes made>"
  }},
  "estimated_new_score": <0-100>,
  "score_improvement_rationale": "<why this rewrite should score higher>"
}}"""


REWRITE_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rewrite: {page_title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                max-width: 1100px; margin: 40px auto; padding: 0 24px;
                color: #1a1a1a; line-height: 1.7; }}
        .header {{ background: #0f4c81; color: white; padding: 28px 32px;
                   border-radius: 10px; margin-bottom: 32px; }}
        .header h1 {{ margin: 0 0 8px 0; font-size: 1.3em; }}
        .header .meta {{ font-size: 0.85em; opacity: 0.85; }}
        .score-bar {{ display: flex; align-items: center; gap: 16px;
                      background: white; color: #0f4c81; padding: 16px 20px;
                      border-radius: 8px; margin-top: 16px; }}
        .score {{ font-size: 2em; font-weight: 700; }}
        .score-new {{ font-size: 2em; font-weight: 700; color: #2e7d32; }}
        .comparison {{ display: grid; grid-template-columns: 1fr 1fr;
                       gap: 24px; margin: 32px 0; }}
        .panel {{ border-radius: 10px; overflow: hidden; }}
        .panel-header {{ padding: 14px 20px; font-weight: 600; font-size: 0.9em;
                         text-transform: uppercase; letter-spacing: 0.05em; }}
        .panel-before .panel-header {{ background: #fde8e8; color: #c62828; }}
        .panel-after .panel-header {{ background: #e8fde8; color: #2e7d32; }}
        .panel-content {{ background: #f8f9fa; padding: 20px; font-size: 0.9em;
                          min-height: 200px; border: 1px solid #e0e0e0;
                          border-top: none; border-radius: 0 0 10px 10px; }}
        .section {{ background: #f8f9fa; border-left: 4px solid #0f4c81;
                    padding: 20px 24px; margin: 24px 0;
                    border-radius: 0 8px 8px 0; }}
        .section h2 {{ color: #0f4c81; margin: 0 0 16px 0; font-size: 1em;
                       text-transform: uppercase; letter-spacing: 0.05em; }}
        .optimization-item {{ background: white; border: 1px solid #e0e0e0;
                               padding: 16px 20px; margin: 12px 0;
                               border-radius: 8px; }}
        .optimization-item h3 {{ margin: 0 0 8px 0; color: #0f4c81;
                                  font-size: 0.95em; }}
        .before-after {{ display: grid; grid-template-columns: 1fr 1fr;
                         gap: 12px; margin-top: 10px; }}
        .before-text {{ background: #fde8e8; padding: 10px 14px;
                        border-radius: 6px; font-size: 0.85em; font-style: italic; }}
        .after-text {{ background: #e8fde8; padding: 10px 14px;
                       border-radius: 6px; font-size: 0.85em; font-style: italic; }}
        .ai-section {{ background: #f0f7ff; border-left: 4px solid #1976d2;
                       padding: 20px 24px; margin: 24px 0;
                       border-radius: 0 8px 8px 0; }}
        .ai-section h2 {{ color: #1976d2; margin: 0 0 12px 0; font-size: 1em;
                          text-transform: uppercase; letter-spacing: 0.05em; }}
        .tag {{ display: inline-block; background: #e8f4fd; color: #0f4c81;
                padding: 3px 10px; border-radius: 4px; font-size: 0.82em;
                margin: 3px 3px 3px 0; }}
        code {{ background: #e8f4fd; padding: 3px 8px; border-radius: 4px; }}
        .footer {{ margin-top: 48px; padding-top: 20px;
                   border-top: 1px solid #e0e0e0; color: #999; font-size: 0.82em; }}
    </style>
</head>
<body>
<div class="header">
    <div class="meta">PAGE REWRITE &nbsp;·&nbsp; {site_url} &nbsp;·&nbsp; {date}</div>
    <h1>{page_title}</h1>
    <div class="meta">{page_url}</div>
    <div class="score-bar">
        <div>
            <div style="font-size:0.75em; color:#666;">Original Score</div>
            <div class="score">{original_score}</div>
        </div>
        <div style="font-size:1.5em;">→</div>
        <div>
            <div style="font-size:0.75em; color:#2e7d32;">Estimated New Score</div>
            <div class="score-new">{estimated_new_score}</div>
        </div>
        <div style="margin-left:16px; font-size:0.85em; color:#444; max-width:300px;">
            {score_improvement_rationale}
        </div>
    </div>
</div>

<div class="section">
    <h2>📝 Updated Metadata</h2>
    <p><strong>Title Tag:</strong><br><code>{rewritten_title}</code></p>
    <p><strong>Meta Description:</strong><br><code>{rewritten_meta_description}</code></p>
    <p><strong>H1:</strong><br><code>{rewritten_h1}</code></p>
</div>

<h2 style="color:#0f4c81; margin-top:32px;">Before / After Comparison</h2>
<div class="comparison">
    <div class="panel panel-before">
        <div class="panel-header">⚠ Original Content</div>
        <div class="panel-content">{original_content_html}</div>
    </div>
    <div class="panel panel-after">
        <div class="panel-header">✓ Rewritten Content</div>
        <div class="panel-content">{rewritten_content_html}</div>
    </div>
</div>

<div class="section">
    <h2>🔧 Optimizations Made</h2>
    {optimizations_html}
</div>

<div class="ai-section">
    <h2>🤖 AI Search Improvements</h2>
    <p><strong>Direct Answer Added:</strong><br>{direct_answer_added}</p>
    <p><strong>Entities Clarified:</strong><br>{entities_html}</p>
    <p><strong>Facts Added:</strong></p>
    <ul>{facts_html}</ul>
    <p><strong>Format Changes:</strong><br>{format_changes}</p>
</div>

<div class="footer">
    Generated by Search Visibility Agent &nbsp;·&nbsp;
    <a href="https://github.com/SamaraHJohansson/agent-portfolio">
    github.com/SamaraHJohansson/agent-portfolio</a>
</div>
</body>
</html>"""


def rewrite_page(client, site_url, page, score_data):
    """Generate a rewrite for a single underperforming page."""
    scores = score_data.get("scores", {})
    recommendations = score_data.get("recommendations", [])
    recommendations_text = "\n".join(f"- {r}" for r in recommendations)

    prompt = REWRITE_PROMPT.format(
        site_url=site_url,
        page_url=page.get("url", ""),
        page_title=page.get("title", "No title"),
        score_direct_answer=scores.get("direct_answer_clarity", 0),
        score_question_coverage=scores.get("question_coverage", 0),
        score_entity_clarity=scores.get("entity_clarity", 0),
        score_factual_structure=scores.get("factual_structure", 0),
        score_content_authority=scores.get("content_authority", 0),
        score_format_readiness=scores.get("answer_format_readiness", 0),
        overall_score=score_data.get("overall_score", 0),
        critical_weakness=score_data.get("critical_weakness", ""),
        recommendations=recommendations_text,
        original_content=page.get("body_text", "")[:3000]
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert content optimizer. "
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

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        return None


def render_rewrite_html(rewrite, page, score_data, site_url, date):
    """Render a rewrite as a clean before/after HTML comparison."""
    optimizations_html = ""
    for opt in rewrite.get("optimizations_made", []):
        optimizations_html += f"""
        <div class="optimization-item">
            <h3>{opt.get('optimization', '')}</h3>
            <p style="margin:0; font-size:0.9em; color:#444;">{opt.get('reason', '')}</p>
            <div class="before-after">
                <div class="before-text">
                    <strong style="color:#c62828;">Before:</strong><br>
                    {opt.get('before', '')}
                </div>
                <div class="after-text">
                    <strong style="color:#2e7d32;">After:</strong><br>
                    {opt.get('after', '')}
                </div>
            </div>
        </div>"""

    ai_improvements = rewrite.get("ai_search_improvements", {})
    entities_html = " ".join(
        f'<span class="tag">{e}</span>'
        for e in ai_improvements.get("entities_clarified", [])
    )
    facts_html = "".join(
        f"<li>{fact}</li>" for fact in ai_improvements.get("facts_added", [])
    )

    original_text = page.get("body_text", "")[:2000]
    original_content_html = "".join(
        f"<p>{para.strip()}</p>"
        for para in original_text.split("\n")
        if para.strip()
    )

    return REWRITE_HTML_TEMPLATE.format(
        page_title=page.get("title", "Page Rewrite"),
        site_url=site_url,
        page_url=page.get("url", ""),
        date=date,
        original_score=score_data.get("overall_score", 0),
        estimated_new_score=rewrite.get("estimated_new_score", 0),
        score_improvement_rationale=rewrite.get("score_improvement_rationale", ""),
        rewritten_title=rewrite.get("rewritten_title", ""),
        rewritten_meta_description=rewrite.get("rewritten_meta_description", ""),
        rewritten_h1=rewrite.get("rewritten_h1", ""),
        original_content_html=original_content_html,
        rewritten_content_html=rewrite.get("rewritten_content", ""),
        optimizations_html=optimizations_html,
        direct_answer_added=ai_improvements.get("direct_answer_added", ""),
        entities_html=entities_html,
        facts_html=facts_html,
        format_changes=ai_improvements.get("format_changes", "")
    )


def run(url):
    """Main entry point called by agent.py."""
    print(f"\n  Rewrite Engine starting...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "status": "skipped",
            "reason": "OPENAI_API_KEY not found in environment"
        }

    client = OpenAI(api_key=api_key)

    readiness_path = "outputs/answer_readiness.json"
    if not os.path.exists(readiness_path):
        return {
            "status": "error",
            "reason": "No answer readiness data found. Run answer_readiness module first."
        }

    with open(readiness_path, "r", encoding="utf-8") as f:
        readiness_data = json.load(f)

    rewrite_candidates = readiness_data.get("rewrite_candidates", [])
    page_scores = readiness_data.get("page_scores", [])

    if not rewrite_candidates:
        return {
            "status": "complete",
            "message": "No pages flagged for rewriting",
            "rewrites_generated": 0
        }

    crawl_data_path = "outputs/crawl_data.json"
    if not os.path.exists(crawl_data_path):
        return {
            "status": "error",
            "reason": "No crawl data found. Run site_crawler module first."
        }

    with open(crawl_data_path, "r", encoding="utf-8") as f:
        crawl_data = json.load(f)

    pages_by_url = {p["url"]: p for p in crawl_data.get("pages", [])}
    scores_by_url = {
        s["url"]: s for s in page_scores
        if s.get("status") == "complete"
    }

    print(f"  Rewriting {len(rewrite_candidates)} underperforming pages...")

    os.makedirs("outputs/rewrites", exist_ok=True)
    date = datetime.now().strftime("%B %d, %Y")
    rewrites_generated = []

    for i, candidate in enumerate(rewrite_candidates):
        page_url = candidate.get("url", "")
        print(f"  Rewriting ({i+1}/{len(rewrite_candidates)}): {page_url[:60]}...")

        page = pages_by_url.get(page_url)
        score_data = scores_by_url.get(page_url)

        if not page or not score_data:
            print(f"  ✗ Missing data for: {page_url[:40]}")
            continue

        rewrite = rewrite_page(client, url, page, score_data)

        if not rewrite:
            print(f"  ✗ Failed to rewrite: {page_url[:40]}")
            continue

        slug = page_url.rstrip("/").split("/")[-1] or "homepage"
        slug = slug.replace(".", "-")[:50]
        filename = f"outputs/rewrites/{slug}.html"

        html = render_rewrite_html(rewrite, page, score_data, url, date)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        rewrites_generated.append({
            "file": filename,
            "url": page_url,
            "title": page.get("title", ""),
            "original_score": score_data.get("overall_score", 0),
            "estimated_new_score": rewrite.get("estimated_new_score", 0)
        })

        print(f"  ✓ Saved: {filename}")

    results = {
        "status": "complete",
        "url": url,
        "rewrites_generated": len(rewrites_generated),
        "rewrites": rewrites_generated
    }

    with open("outputs/rewrites_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n  Rewrite Engine Results:")
    print(f"  Rewrites generated: {len(rewrites_generated)}")
    print(f"  Saved to: outputs/rewrites/")

    return results