"""
Module 5: Content Brief Generator
====================================
Takes gaps identified by the AI Search Gap Detector and produces
structured content briefs for new pages optimized for AI search.

Requires: OPENAI_API_KEY
"""

import os
import json
from openai import OpenAI
from datetime import datetime


BRIEF_GENERATION_PROMPT = """You are a senior content strategist specializing in 
AI search optimization. Create a detailed content brief for a new page that will 
perform well in both traditional search and AI search.

WEBSITE: {site_url}
SITE DESCRIPTION: {site_description}
TARGET AUDIENCE: {target_audience}

GAP TO ADDRESS:
- Topic: {topic}
- Question to answer: {question}
- Gap type: {gap_type}
- Gap explanation: {gap_explanation}
- Content opportunity identified: {content_opportunity}

Respond in this exact JSON format:
{{
  "brief_title": "<recommended page/article title>",
  "target_url_slug": "<recommended URL slug>",
  "primary_question": "<the main question this content answers>",
  "secondary_questions": [
    "<supporting question 1>",
    "<supporting question 2>",
    "<supporting question 3>"
  ],
  "target_audience": "<specific description of who this is for>",
  "search_intent": "<informational|navigational|commercial|transactional>",
  "recommended_word_count": "<e.g. 800-1200 words>",
  "title_tag": "<recommended title tag, max 60 chars>",
  "meta_description": "<recommended meta description, max 160 chars>",
  "h1": "<recommended H1 heading>",
  "page_structure": [
    {{
      "section": "Introduction",
      "h2": "<H2 heading>",
      "content_guidance": "<what to cover in this section>",
      "ai_optimization_note": "<how to structure this section for AI citation>"
    }}
  ],
  "ai_search_optimization": {{
    "direct_answer_placement": "<where and how to place the direct answer>",
    "entity_requirements": ["<key entity 1 to define>", "<key entity 2>"],
    "fact_requirements": ["<specific fact or data point to include>"],
    "format_recommendations": "<lists, definitions, steps, or Q&A format>"
  }},
  "traditional_seo_notes": {{
    "primary_keyword": "<main keyword to target>",
    "secondary_keywords": ["<keyword 2>", "<keyword 3>"],
    "internal_linking_suggestions": ["<page on site to link from>"],
    "schema_markup_recommended": "<Article|FAQ|HowTo|None>"
  }},
  "competitive_context": "<what competitors are doing and how to differentiate>",
  "unique_angle": "<what perspective would make this content stand out>"
}}"""


BRIEF_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Brief: {brief_title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                max-width: 860px; margin: 40px auto; padding: 0 24px;
                color: #1a1a1a; line-height: 1.7; }}
        .header {{ background: #0f4c81; color: white; padding: 28px 32px;
                   border-radius: 10px; margin-bottom: 32px; }}
        .header h1 {{ margin: 0 0 8px 0; font-size: 1.4em; font-weight: 700; }}
        .header .meta {{ font-size: 0.85em; opacity: 0.85; }}
        .section {{ background: #f8f9fa; border-left: 4px solid #0f4c81;
                    padding: 20px 24px; margin: 24px 0;
                    border-radius: 0 8px 8px 0; }}
        .section h2 {{ color: #0f4c81; margin: 0 0 12px 0; font-size: 1em;
                       text-transform: uppercase; letter-spacing: 0.05em; }}
        .ai-section {{ background: #f0f7ff; border-left: 4px solid #1976d2;
                       padding: 20px 24px; margin: 24px 0;
                       border-radius: 0 8px 8px 0; }}
        .ai-section h2 {{ color: #1976d2; margin: 0 0 12px 0; font-size: 1em;
                          text-transform: uppercase; letter-spacing: 0.05em; }}
        .structure-item {{ background: white; border: 1px solid #e0e0e0;
                           padding: 16px 20px; margin: 12px 0; border-radius: 8px; }}
        .structure-item h3 {{ margin: 0 0 6px 0; color: #0f4c81; font-size: 0.95em; }}
        .ai-note {{ margin-top: 8px; padding: 8px 12px; background: #f0f7ff;
                    border-radius: 4px; font-size: 0.85em; color: #1976d2; }}
        .tag {{ display: inline-block; background: #e8f4fd; color: #0f4c81;
                padding: 3px 10px; border-radius: 4px; font-size: 0.82em;
                margin: 3px 3px 3px 0; }}
        .footer {{ margin-top: 48px; padding-top: 20px;
                   border-top: 1px solid #e0e0e0; color: #999; font-size: 0.82em; }}
        code {{ background: #e8f4fd; padding: 3px 8px; border-radius: 4px; }}
        ul {{ padding-left: 20px; }} li {{ margin: 6px 0; }}
        strong {{ color: #0f4c81; }}
    </style>
</head>
<body>
<div class="header">
    <div class="meta">CONTENT BRIEF &nbsp;·&nbsp; {site_url} &nbsp;·&nbsp; {date}</div>
    <h1>{brief_title}</h1>
</div>

<div class="section">
    <h2>📋 Brief Overview</h2>
    <p><strong>Primary Question:</strong><br>{primary_question}</p>
    <p><strong>Target Audience:</strong> {target_audience}</p>
    <p><strong>Search Intent:</strong> {search_intent}</p>
    <p><strong>Recommended Word Count:</strong> {recommended_word_count}</p>
    <p><strong>Unique Angle:</strong> {unique_angle}</p>
</div>

<div class="section">
    <h2>🔍 SEO Metadata</h2>
    <p><strong>Title Tag:</strong><br><code>{title_tag}</code></p>
    <p><strong>Meta Description:</strong><br><code>{meta_description}</code></p>
    <p><strong>H1:</strong><br><code>{h1}</code></p>
    <p><strong>Primary Keyword:</strong> {primary_keyword}</p>
    <p><strong>Secondary Keywords:</strong><br>{secondary_keywords_html}</p>
    <p><strong>Schema Markup:</strong> {schema_markup}</p>
</div>

<div class="section">
    <h2>❓ Questions This Content Must Answer</h2>
    <p><strong>Primary:</strong> {primary_question}</p>
    <ul>{secondary_questions_html}</ul>
</div>

<div class="section">
    <h2>📐 Recommended Page Structure</h2>
    {page_structure_html}
</div>

<div class="ai-section">
    <h2>🤖 AI Search Optimization</h2>
    <p><strong>Direct Answer Placement:</strong><br>{direct_answer_placement}</p>
    <p><strong>Format Recommendation:</strong><br>{format_recommendations}</p>
    <p><strong>Key Entities to Define:</strong><br>{entities_html}</p>
    <p><strong>Facts to Include:</strong></p>
    <ul>{facts_html}</ul>
</div>

<div class="section">
    <h2>🔗 Internal Linking</h2>
    <ul>{internal_linking_html}</ul>
</div>

<div class="section">
    <h2>🏆 Competitive Context</h2>
    <p>{competitive_context}</p>
</div>

<div class="footer">
    Generated by Search Visibility Agent &nbsp;·&nbsp;
    <a href="https://github.com/SamaraHJohansson/agent-portfolio">
    github.com/SamaraHJohansson/agent-portfolio</a>
</div>
</body>
</html>"""


def generate_brief(client, site_url, site_description, target_audience, gap):
    """Generate a content brief for a single gap."""
    prompt = BRIEF_GENERATION_PROMPT.format(
        site_url=site_url,
        site_description=site_description,
        target_audience=target_audience,
        topic=gap.get("topic", ""),
        question=gap.get("question", ""),
        gap_type=gap.get("gap_type", ""),
        gap_explanation=gap.get("gap_explanation", ""),
        content_opportunity=gap.get("content_opportunity", "")
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior content strategist. "
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


def render_brief_html(brief, site_url, date):
    """Render a brief dictionary as a clean HTML file."""
    seo = brief.get("traditional_seo_notes", {})
    ai_opt = brief.get("ai_search_optimization", {})

    secondary_questions_html = "".join(
        f"<li>{q}</li>" for q in brief.get("secondary_questions", [])
    )

    page_structure_html = ""
    for section in brief.get("page_structure", []):
        ai_note = section.get("ai_optimization_note", "")
        page_structure_html += f"""
        <div class="structure-item">
            <h3>{section.get('h2', '')}</h3>
            <p style="margin:0; font-size:0.9em; color:#444;">
                {section.get('content_guidance', '')}
            </p>
            {f'<div class="ai-note">🤖 AI Note: {ai_note}</div>' if ai_note else ''}
        </div>"""

    secondary_keywords_html = " ".join(
        f'<span class="tag">{kw}</span>'
        for kw in seo.get("secondary_keywords", [])
    )
    internal_linking_html = "".join(
        f"<li>{link}</li>"
        for link in seo.get("internal_linking_suggestions", [])
    ) or "<li>No internal linking suggestions identified</li>"

    entities_html = " ".join(
        f'<span class="tag">{e}</span>'
        for e in ai_opt.get("entity_requirements", [])
    )
    facts_html = "".join(
        f"<li>{fact}</li>" for fact in ai_opt.get("fact_requirements", [])
    )

    return BRIEF_HTML_TEMPLATE.format(
        brief_title=brief.get("brief_title", "Content Brief"),
        site_url=site_url,
        date=date,
        primary_question=brief.get("primary_question", ""),
        target_audience=brief.get("target_audience", ""),
        search_intent=brief.get("search_intent", ""),
        recommended_word_count=brief.get("recommended_word_count", ""),
        unique_angle=brief.get("unique_angle", ""),
        title_tag=brief.get("title_tag", ""),
        meta_description=brief.get("meta_description", ""),
        h1=brief.get("h1", ""),
        primary_keyword=seo.get("primary_keyword", ""),
        secondary_keywords_html=secondary_keywords_html,
        schema_markup=seo.get("schema_markup_recommended", "Article"),
        secondary_questions_html=secondary_questions_html,
        page_structure_html=page_structure_html,
        direct_answer_placement=ai_opt.get("direct_answer_placement", ""),
        format_recommendations=ai_opt.get("format_recommendations", ""),
        entities_html=entities_html,
        facts_html=facts_html,
        internal_linking_html=internal_linking_html,
        competitive_context=brief.get("competitive_context", "")
    )


def run(url):
    """Main entry point called by agent.py."""
    print(f"\n  Content Brief Generator starting...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "status": "skipped",
            "reason": "OPENAI_API_KEY not found in environment"
        }

    client = OpenAI(api_key=api_key)

    gaps_path = "outputs/ai_search_gaps.json"
    if not os.path.exists(gaps_path):
        return {
            "status": "error",
            "reason": "No AI search gap data found. Run ai_search_gap module first."
        }

    with open(gaps_path, "r", encoding="utf-8") as f:
        gap_data = json.load(f)

    site_description = gap_data.get("site_description", "")
    target_audience = gap_data.get("target_audience", "")

    all_gaps = gap_data.get("all_gaps", [])
    actionable_gaps = [
        g for g in all_gaps
        if g.get("gap_type") in ["CONTENT_GAP", "OPPORTUNITY_GAP", "COMPETITOR_GAP"]
    ]

    if not actionable_gaps:
        return {
            "status": "complete",
            "message": "No content gaps identified",
            "briefs_generated": 0
        }

    print(f"  Generating briefs for {len(actionable_gaps)} identified gaps...")

    os.makedirs("outputs/briefs", exist_ok=True)
    date = datetime.now().strftime("%B %d, %Y")
    briefs_generated = []

    for i, gap in enumerate(actionable_gaps):
        question = gap.get("question", "")
        print(f"  Brief ({i+1}/{len(actionable_gaps)}): {question[:60]}...")

        brief = generate_brief(client, url, site_description, target_audience, gap)

        if not brief:
            print(f"  ✗ Failed to generate brief for: {question[:40]}")
            continue

        slug = brief.get("target_url_slug", f"brief-{i+1}").strip("/").replace("/", "-")
        filename = f"outputs/briefs/{slug}.html"

        html = render_brief_html(brief, url, date)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        briefs_generated.append({
            "file": filename,
            "title": brief.get("brief_title", ""),
            "primary_question": brief.get("primary_question", "")
        })

        print(f"  ✓ Saved: {filename}")

    results = {
        "status": "complete",
        "url": url,
        "briefs_generated": len(briefs_generated),
        "briefs": briefs_generated
    }

    with open("outputs/briefs_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n  Content Brief Results:")
    print(f"  Briefs generated: {len(briefs_generated)}")
    print(f"  Saved to: outputs/briefs/")

    return results