"""
Module 7: Report Generator
============================
Assembles all module outputs into a single clean HTML audit report.
Opens in any browser. Print to PDF with File → Print → Save as PDF.

No API keys required.
"""

import os
import json
from datetime import datetime


REPORT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Visibility Audit — {site_url}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                max-width: 960px; margin: 0 auto; padding: 0 24px 60px;
                color: #1a1a1a; line-height: 1.7; }}
        .cover {{ background: linear-gradient(135deg, #0f4c81 0%, #1976d2 100%);
                  color: white; padding: 48px 40px; border-radius: 12px;
                  margin: 40px 0; }}
        .cover h1 {{ margin: 0 0 8px; font-size: 2em; font-weight: 700; }}
        .cover .subtitle {{ font-size: 1.1em; opacity: 0.85; margin-bottom: 32px; }}
        .cover .meta {{ font-size: 0.85em; opacity: 0.75; }}
        .score-grid {{ display: grid; grid-template-columns: repeat(3, 1fr);
                       gap: 16px; margin: 32px 0; }}
        .score-card {{ background: #f8f9fa; border-radius: 10px; padding: 20px;
                       text-align: center; border: 1px solid #e0e0e0; }}
        .score-card .label {{ font-size: 0.78em; text-transform: uppercase;
                               letter-spacing: 0.06em; color: #666; margin-bottom: 8px; }}
        .score-card .value {{ font-size: 2.4em; font-weight: 700; line-height: 1; }}
        .score-card .grade {{ font-size: 0.85em; color: #666; margin-top: 4px; }}
        .score-a {{ color: #2e7d32; }} .score-b {{ color: #558b2f; }}
        .score-c {{ color: #f57c00; }} .score-d {{ color: #e65100; }}
        .score-f {{ color: #c62828; }}
        .section-header {{ border-left: 5px solid #0f4c81; padding: 4px 0 4px 16px;
                           margin: 48px 0 24px; }}
        .section-header h2 {{ margin: 0; color: #0f4c81; font-size: 1.3em; }}
        .section-header p {{ margin: 4px 0 0; color: #666; font-size: 0.9em; }}
        .issue {{ padding: 14px 18px; margin: 10px 0; border-radius: 8px;
                  font-size: 0.9em; }}
        .issue-critical {{ background: #fde8e8; border-left: 4px solid #c62828; }}
        .issue-warning {{ background: #fff8e1; border-left: 4px solid #f57c00; }}
        .issue-info {{ background: #e8f4fd; border-left: 4px solid #1976d2; }}
        .severity {{ font-weight: 700; font-size: 0.75em; text-transform: uppercase;
                     letter-spacing: 0.05em; }}
        .severity-critical {{ color: #c62828; }}
        .severity-warning {{ color: #f57c00; }}
        .severity-info {{ color: #1976d2; }}
        .page-score-row {{ display: grid; grid-template-columns: 1fr auto auto;
                           gap: 16px; align-items: center; padding: 14px 18px;
                           background: #f8f9fa; border-radius: 8px; margin: 8px 0;
                           font-size: 0.9em; }}
        .score-pill {{ padding: 4px 12px; border-radius: 20px; font-weight: 700;
                       font-size: 0.85em; white-space: nowrap; }}
        .pill-good {{ background: #e8fde8; color: #2e7d32; }}
        .pill-ok {{ background: #fff8e1; color: #f57c00; }}
        .pill-poor {{ background: #fde8e8; color: #c62828; }}
        .gap-item {{ background: #f8f9fa; border-radius: 10px; padding: 18px 20px;
                     margin: 12px 0; border: 1px solid #e0e0e0; }}
        .gap-item h3 {{ margin: 0 0 8px; font-size: 0.95em; }}
        .gap-badge {{ display: inline-block; padding: 3px 10px; border-radius: 20px;
                      font-size: 0.75em; font-weight: 600; margin-bottom: 8px; }}
        .badge-competitor {{ background: #fde8e8; color: #c62828; }}
        .badge-content {{ background: #e8f4fd; color: #0f4c81; }}
        .badge-opportunity {{ background: #e8fde8; color: #2e7d32; }}
        .stat-row {{ display: grid; grid-template-columns: repeat(4, 1fr);
                     gap: 12px; margin: 20px 0; }}
        .stat {{ background: #f8f9fa; border-radius: 8px; padding: 16px;
                 text-align: center; }}
        .stat .num {{ font-size: 1.8em; font-weight: 700; color: #0f4c81; }}
        .stat .lbl {{ font-size: 0.78em; color: #666; text-transform: uppercase;
                      letter-spacing: 0.04em; }}
        .action-item {{ display: grid; grid-template-columns: auto 1fr; gap: 16px;
                        padding: 16px 18px; background: #f8f9fa; border-radius: 8px;
                        margin: 10px 0; align-items: start; }}
        .action-number {{ background: #0f4c81; color: white; width: 28px; height: 28px;
                          border-radius: 50%; display: flex; align-items: center;
                          justify-content: center; font-weight: 700; font-size: 0.85em;
                          flex-shrink: 0; }}
        .action-text strong {{ color: #0f4c81; }}
        .action-text p {{ margin: 4px 0 0; font-size: 0.88em; color: #444; }}
        .footer {{ margin-top: 60px; padding-top: 20px; border-top: 1px solid #e0e0e0;
                   color: #999; font-size: 0.82em; text-align: center; }}
        a {{ color: #0f4c81; }}
        @media print {{
            .cover {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        }}
    </style>
</head>
<body>

<div class="cover">
    <div class="subtitle">Search Visibility Audit Report</div>
    <h1>{site_url}</h1>
    <div class="meta">
        Generated: {date} &nbsp;·&nbsp;
        Pages crawled: {pages_crawled} &nbsp;·&nbsp;
        Search Visibility Agent v1.0
    </div>
</div>

<div class="section-header">
    <h2>Executive Summary</h2>
    <p>Overall scores across traditional SEO and AI search visibility</p>
</div>

<div class="score-grid">
    <div class="score-card">
        <div class="label">Technical Health</div>
        <div class="value {tech_score_class}">{tech_score}</div>
        <div class="grade">Grade: {tech_grade} &nbsp;·&nbsp;
            {tech_critical} critical issues</div>
    </div>
    <div class="score-card">
        <div class="label">AI Answer-Readiness</div>
        <div class="value {ai_score_class}">{ai_score}</div>
        <div class="grade">Grade: {ai_grade} &nbsp;·&nbsp;
            {rewrite_count} pages need rewriting</div>
    </div>
    <div class="score-card">
        <div class="label">AI Search Gaps</div>
        <div class="value {gap_score_class}">{gap_count}</div>
        <div class="grade">gaps identified &nbsp;·&nbsp;
            {opportunity_count} opportunities</div>
    </div>
</div>

<div class="section-header">
    <h2>Technical Health</h2>
    <p>Traditional SEO hygiene issues found across {pages_crawled} pages</p>
</div>

<div class="stat-row">
    <div class="stat">
        <div class="num" style="color:#c62828;">{tech_critical}</div>
        <div class="lbl">Critical</div>
    </div>
    <div class="stat">
        <div class="num" style="color:#f57c00;">{tech_warnings}</div>
        <div class="lbl">Warnings</div>
    </div>
    <div class="stat">
        <div class="num" style="color:#1976d2;">{tech_info}</div>
        <div class="lbl">Info</div>
    </div>
    <div class="stat">
        <div class="num">{tech_score}/100</div>
        <div class="lbl">Health Score</div>
    </div>
</div>

{technical_issues_html}

<div class="section-header">
    <h2>AI Answer-Readiness</h2>
    <p>How likely each page is to be cited by AI search engines</p>
</div>

{page_scores_html}

<div class="section-header">
    <h2>AI Search Gap Analysis</h2>
    <p>What AI search surfaces for your topics — and where you are missing</p>
</div>

<div class="stat-row">
    <div class="stat">
        <div class="num" style="color:#c62828;">{competitor_gaps}</div>
        <div class="lbl">Competitor Gaps</div>
    </div>
    <div class="stat">
        <div class="num" style="color:#f57c00;">{content_gaps}</div>
        <div class="lbl">Content Gaps</div>
    </div>
    <div class="stat">
        <div class="num" style="color:#2e7d32;">{opportunity_gaps}</div>
        <div class="lbl">Opportunities</div>
    </div>
    <div class="stat">
        <div class="num">{no_gaps}</div>
        <div class="lbl">Already Visible</div>
    </div>
</div>

{gaps_html}

<div class="section-header">
    <h2>Generated Outputs</h2>
    <p>Content briefs and page rewrites created by this audit</p>
</div>

{outputs_summary_html}

<div class="section-header">
    <h2>Recommended Next Steps</h2>
    <p>Prioritized actions based on this audit</p>
</div>

{next_steps_html}

<div class="footer">
    Search Visibility Agent &nbsp;·&nbsp;
    Built by Samara H. Johansson &nbsp;·&nbsp;
    <a href="https://github.com/SamaraHJohansson/agent-portfolio">
    github.com/SamaraHJohansson/agent-portfolio</a><br><br>
    To save as PDF: File → Print → Save as PDF
</div>

</body>
</html>"""


def score_class(score):
    if score >= 80: return "score-a"
    elif score >= 65: return "score-b"
    elif score >= 50: return "score-c"
    elif score >= 35: return "score-d"
    else: return "score-f"


def pill_class(score):
    if score >= 70: return "pill-good"
    elif score >= 50: return "pill-ok"
    else: return "pill-poor"


def build_technical_issues_html(tech_data):
    if not tech_data or tech_data.get("status") != "complete":
        return "<p style='color:#999;'>Technical health data not available.</p>"

    issues = tech_data.get("issues", [])
    if not issues:
        return "<p style='color:#2e7d32;'>✓ No technical issues found.</p>"

    sorted_issues = sorted(
        issues,
        key=lambda x: {"CRITICAL": 0, "WARNING": 1, "INFO": 2}.get(
            x.get("severity", "INFO"), 3)
    )[:20]

    html = ""
    for issue in sorted_issues:
        severity = issue.get("severity", "INFO")
        css_class = {"CRITICAL": "issue-critical", "WARNING": "issue-warning",
                     "INFO": "issue-info"}.get(severity, "issue-info")
        severity_class = f"severity-{severity.lower()}"
        url = issue.get("url", "")
        if isinstance(url, list):
            url = ", ".join(url[:3])

        html += f"""
        <div class="issue {css_class}">
            <span class="severity {severity_class}">{severity}</span>
            &nbsp;·&nbsp; {issue.get('message', '')}
            <div style="font-size:0.82em; color:#666; margin-top:4px;">{url}</div>
        </div>"""

    if len(issues) > 20:
        html += f"<p style='color:#666; font-size:0.88em;'>... and {len(issues) - 20} more issues.</p>"

    return html


def build_page_scores_html(readiness_data):
    if not readiness_data or readiness_data.get("status") != "complete":
        return "<p style='color:#999;'>Answer-readiness data not available.</p>"

    page_scores = readiness_data.get("page_scores", [])
    if not page_scores:
        return "<p style='color:#999;'>No pages scored.</p>"

    html = ""
    for page in sorted(page_scores, key=lambda x: x.get("overall_score", 100)):
        if page.get("status") != "complete":
            continue
        score = page.get("overall_score", 0)
        url = page.get("url", "")
        title = page.get("title", url)
        weakness = page.get("critical_weakness", "")

        html += f"""
        <div class="page-score-row">
            <div>
                <div style="color:#0f4c81;">{title}</div>
                <div style="font-size:0.82em; color:#666;">{url}</div>
                {f'<div style="font-size:0.82em; color:#c62828; margin-top:4px;">⚠ {weakness}</div>' if weakness and score < 60 else ''}
            </div>
            <div class="score-pill {pill_class(score)}">{score}/100</div>
            <div style="font-size:0.82em; color:#666;">{page.get('grade', '')}</div>
        </div>"""

    return html


def build_gaps_html(gap_data):
    if not gap_data or gap_data.get("status") != "complete":
        return "<p style='color:#999;'>AI search gap data not available.</p>"

    all_gaps = gap_data.get("all_gaps", [])
    actionable = [g for g in all_gaps
                  if g.get("gap_type") in ["COMPETITOR_GAP", "CONTENT_GAP", "OPPORTUNITY_GAP"]][:10]

    if not actionable:
        return "<p style='color:#2e7d32;'>✓ No significant AI search gaps found.</p>"

    badge_map = {
        "COMPETITOR_GAP": ("badge-competitor", "Competitor Gap"),
        "CONTENT_GAP": ("badge-content", "Content Gap"),
        "OPPORTUNITY_GAP": ("badge-opportunity", "Opportunity")
    }

    html = ""
    for gap in actionable:
        gap_type = gap.get("gap_type", "")
        badge_class, badge_label = badge_map.get(gap_type, ("badge-content", "Gap"))
        html += f"""
        <div class="gap-item">
            <span class="gap-badge {badge_class}">{badge_label}</span>
            <h3>{gap.get('question', '')}</h3>
            <p style="margin:0; font-size:0.88em; color:#444;">{gap.get('gap_explanation', '')}</p>
            <p style="margin:6px 0 0; font-size:0.85em; color:#0f4c81;">
                → {gap.get('recommendation', '')}</p>
        </div>"""

    return html


def build_outputs_summary_html(briefs_data, rewrites_data):
    html = "<div style='display:grid; grid-template-columns:1fr 1fr; gap:20px;'>"

    briefs_count = briefs_data.get("briefs_generated", 0) if briefs_data else 0
    html += f"""
    <div style="background:#f8f9fa; border-radius:10px; padding:20px;">
        <div style="font-size:2em; font-weight:700; color:#0f4c81;">{briefs_count}</div>
        <div style="font-weight:600; margin-bottom:8px;">Content Briefs Generated</div>
        <div style="font-size:0.85em; color:#666;">Saved to outputs/briefs/</div>
    </div>"""

    rewrites_count = rewrites_data.get("rewrites_generated", 0) if rewrites_data else 0
    html += f"""
    <div style="background:#f8f9fa; border-radius:10px; padding:20px;">
        <div style="font-size:2em; font-weight:700; color:#0f4c81;">{rewrites_count}</div>
        <div style="font-weight:600; margin-bottom:8px;">Page Rewrites Generated</div>
        <div style="font-size:0.85em; color:#666;">Saved to outputs/rewrites/</div>
    </div>"""

    html += "</div>"
    return html


def build_next_steps_html(tech_data, readiness_data, gap_data):
    actions = []

    if tech_data and tech_data.get("issue_counts", {}).get("critical", 0) > 0:
        count = tech_data["issue_counts"]["critical"]
        actions.append({
            "title": f"Fix {count} critical technical SEO issues",
            "detail": "Missing titles, duplicate content, and missing H1 tags "
                      "directly hurt your rankings. Address these first."
        })

    if readiness_data:
        rewrite_count = readiness_data.get("rewrite_candidates_count", 0)
        if rewrite_count > 0:
            actions.append({
                "title": f"Implement {rewrite_count} page rewrites",
                "detail": "Pages scoring below 60/100 are unlikely to be cited "
                          "by AI search. Rewritten versions are ready in outputs/rewrites/"
            })

    if gap_data:
        competitor_count = gap_data.get("competitor_gaps_count", 0)
        opportunity_count = gap_data.get("opportunity_gaps_count", 0)

        if competitor_count > 0:
            actions.append({
                "title": f"Address {competitor_count} competitor gaps in AI search",
                "detail": "Competitors are being cited instead of you. "
                          "Content briefs are ready in outputs/briefs/"
            })

        if opportunity_count > 0:
            actions.append({
                "title": f"Capture {opportunity_count} unclaimed AI search opportunities",
                "detail": "These topics have weak AI search coverage — nobody owns them yet."
            })

    actions.append({
        "title": "Add schema markup to key pages",
        "detail": "Structured data helps AI search engines understand and cite your content."
    })

    if not actions:
        actions.append({
            "title": "Monitor AI search visibility monthly",
            "detail": "Your site is in good shape. Run this audit monthly to track changes."
        })

    html = ""
    for i, action in enumerate(actions, 1):
        html += f"""
        <div class="action-item">
            <div class="action-number">{i}</div>
            <div class="action-text">
                <strong>{action['title']}</strong>
                <p>{action['detail']}</p>
            </div>
        </div>"""

    return html


def generate_index(url, tech_data, readiness_data, gap_data, briefs_data):
    """Generates outputs/index.html — the entry point for all agent outputs."""

    date = datetime.now().strftime("%B %d, %Y")

    tech_score = tech_data.get("health_score", 0) if tech_data else 0
    tech_grade = tech_data.get("grade", "N/A") if tech_data else "N/A"
    ai_score = readiness_data.get("site_answer_readiness_score", 0) if readiness_data else 0
    ai_grade = readiness_data.get("site_grade", "N/A") if readiness_data else "N/A"
    gap_summary = gap_data.get("gap_summary", {}) if gap_data else {}
    gap_count = (gap_summary.get("COMPETITOR_GAP", 0) +
                 gap_summary.get("CONTENT_GAP", 0) +
                 gap_summary.get("OPPORTUNITY_GAP", 0))
    briefs_count = briefs_data.get("briefs_generated", 0) if briefs_data else 0

    briefs_dir = "outputs/briefs"
    brief_links_html = ""
    if os.path.exists(briefs_dir):
        brief_files = sorted([
            f for f in os.listdir(briefs_dir) if f.endswith(".html")
        ])
        if brief_files:
            for fname in brief_files:
                label = fname.replace(".html", "").replace("_", " ").replace("-", " ").title()
                brief_links_html += f"""
                <a href="briefs/{fname}" style="display:block; padding:12px 16px;
                   background:#f8f9fa; border-radius:8px; margin:8px 0;
                   color:#0f4c81; text-decoration:none; font-size:0.92em;
                   border:1px solid #e0e0e0;">
                   📄 {label}
                </a>"""
        else:
            brief_links_html = "<p style='color:#999; font-size:0.9em;'>No briefs generated yet.</p>"
    else:
        brief_links_html = "<p style='color:#999; font-size:0.9em;'>No briefs folder found.</p>"

    rewrites_dir = "outputs/rewrites"
    rewrites_links_html = ""
    if os.path.exists(rewrites_dir):
        rewrite_files = sorted([
            f for f in os.listdir(rewrites_dir) if f.endswith(".html")
        ])
        if rewrite_files:
            for fname in rewrite_files:
                label = fname.replace(".html", "").replace("_", " ").replace("-", " ").title()
                rewrites_links_html += f"""
                <a href="rewrites/{fname}" style="display:block; padding:12px 16px;
                   background:#f8f9fa; border-radius:8px; margin:8px 0;
                   color:#0f4c81; text-decoration:none; font-size:0.92em;
                   border:1px solid #e0e0e0;">
                   ✏️ {label}
                </a>"""
        else:
            rewrites_links_html = "<p style='color:#999; font-size:0.9em;'>No rewrites generated in this run.</p>"
    else:
        rewrites_links_html = "<p style='color:#999; font-size:0.9em;'>No rewrites folder found.</p>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Visibility Agent — Outputs</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                max-width: 960px; margin: 0 auto; padding: 0 24px 60px;
                color: #1a1a1a; line-height: 1.7; }}
        .cover {{ background: linear-gradient(135deg, #0f4c81 0%, #1976d2 100%);
                  color: white; padding: 48px 40px; border-radius: 12px;
                  margin: 40px 0; }}
        .cover h1 {{ margin: 0 0 8px; font-size: 2em; font-weight: 700; }}
        .cover .subtitle {{ font-size: 1.1em; opacity: 0.85; margin-bottom: 32px; }}
        .cover .meta {{ font-size: 0.85em; opacity: 0.75; }}
        .score-grid {{ display: grid; grid-template-columns: repeat(3, 1fr);
                       gap: 16px; margin: 32px 0; }}
        .score-card {{ background: #f8f9fa; border-radius: 10px; padding: 20px;
                       text-align: center; border: 1px solid #e0e0e0; }}
        .score-card .label {{ font-size: 0.78em; text-transform: uppercase;
                               letter-spacing: 0.06em; color: #666; margin-bottom: 8px; }}
        .score-card .value {{ font-size: 2.4em; font-weight: 700; line-height: 1; }}
        .score-card .grade {{ font-size: 0.85em; color: #666; margin-top: 4px; }}
        .score-a {{ color: #2e7d32; }} .score-b {{ color: #558b2f; }}
        .score-c {{ color: #f57c00; }} .score-d {{ color: #e65100; }}
        .score-f {{ color: #c62828; }}
        .section-header {{ border-left: 5px solid #0f4c81; padding: 4px 0 4px 16px;
                           margin: 48px 0 24px; }}
        .section-header h2 {{ margin: 0; color: #0f4c81; font-size: 1.3em; }}
        .section-header p {{ margin: 4px 0 0; color: #666; font-size: 0.9em; }}
        .cta-button {{ display: inline-block; background: #0f4c81; color: white;
                       padding: 14px 28px; border-radius: 8px; text-decoration: none;
                       font-weight: 600; font-size: 1em; margin: 8px 0; }}
        .cta-button:hover {{ background: #1976d2; }}
        .footer {{ margin-top: 60px; padding-top: 20px; border-top: 1px solid #e0e0e0;
                   color: #999; font-size: 0.82em; text-align: center; }}
        a {{ color: #0f4c81; }}
    </style>
</head>
<body>

<div class="cover">
    <div class="subtitle">Search Visibility Agent — Outputs</div>
    <h1>{url}</h1>
    <div class="meta">Generated: {date} &nbsp;·&nbsp; Search Visibility Agent v1.0</div>
</div>

<div class="score-grid">
    <div class="score-card">
        <div class="label">Technical Health</div>
        <div class="value {score_class(tech_score)}">{tech_score}</div>
        <div class="grade">Grade: {tech_grade}</div>
    </div>
    <div class="score-card">
        <div class="label">AI Answer-Readiness</div>
        <div class="value {score_class(ai_score)}">{ai_score}</div>
        <div class="grade">Grade: {ai_grade}</div>
    </div>
    <div class="score-card">
        <div class="label">AI Search Gaps</div>
        <div class="value {score_class(max(0, 100 - gap_count * 5))}">{gap_count}</div>
        <div class="grade">gaps identified</div>
    </div>
</div>

<div class="section-header">
    <h2>Full Audit Report</h2>
    <p>Complete findings across all modules</p>
</div>
<a href="audit_report.html" class="cta-button">📊 View Full Audit Report</a>

<div class="section-header">
    <h2>Content Briefs</h2>
    <p>{briefs_count} briefs generated — one per AI search gap identified</p>
</div>
{brief_links_html}

<div class="section-header">
    <h2>Page Rewrites</h2>
    <p>AI-optimised rewrites for pages scoring below 60/100</p>
</div>
{rewrites_links_html}

<div class="footer">
    Search Visibility Agent &nbsp;·&nbsp;
    Built by Samara H. Johansson &nbsp;·&nbsp;
    <a href="https://github.com/SamaraHJohansson/agent-portfolio">
    github.com/SamaraHJohansson/agent-portfolio</a>
</div>

</body>
</html>"""

    index_path = "outputs/index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    return index_path


def generate(url, results):
    """Main entry point. Assembles all module results into the audit report."""
    date = datetime.now().strftime("%B %d, %Y")

    def load_json(path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    tech_data = load_json("outputs/technical_health.json")
    readiness_data = load_json("outputs/answer_readiness.json")
    gap_data = load_json("outputs/ai_search_gaps.json")
    briefs_data = load_json("outputs/briefs_summary.json")
    rewrites_data = load_json("outputs/rewrites_summary.json")

    if not tech_data and "technical_health" in results:
        tech_data = results["technical_health"]
    if not readiness_data and "answer_readiness" in results:
        readiness_data = results["answer_readiness"]
    if not gap_data and "ai_search_gap" in results:
        gap_data = results["ai_search_gap"]

    pages_crawled = tech_data.get("pages_analyzed", 0) if tech_data else 0
    tech_score = tech_data.get("health_score", 0) if tech_data else 0
    tech_grade = tech_data.get("grade", "N/A") if tech_data else "N/A"
    tech_critical = tech_data.get("issue_counts", {}).get("critical", 0) if tech_data else 0
    tech_warnings = tech_data.get("issue_counts", {}).get("warning", 0) if tech_data else 0
    tech_info = tech_data.get("issue_counts", {}).get("info", 0) if tech_data else 0

    ai_score = readiness_data.get("site_answer_readiness_score", 0) if readiness_data else 0
    ai_grade = readiness_data.get("site_grade", "N/A") if readiness_data else "N/A"
    rewrite_count = readiness_data.get("rewrite_candidates_count", 0) if readiness_data else 0

    gap_summary = gap_data.get("gap_summary", {}) if gap_data else {}
    competitor_gaps = gap_summary.get("COMPETITOR_GAP", 0)
    content_gaps = gap_summary.get("CONTENT_GAP", 0)
    opportunity_gaps = gap_summary.get("OPPORTUNITY_GAP", 0)
    no_gaps = gap_summary.get("NO_GAP", 0)
    gap_count = competitor_gaps + content_gaps + opportunity_gaps

    report_html = REPORT_HTML.format(
        site_url=url,
        date=date,
        pages_crawled=pages_crawled,
        tech_score=tech_score,
        tech_score_class=score_class(tech_score),
        tech_grade=tech_grade,
        tech_critical=tech_critical,
        tech_warnings=tech_warnings,
        tech_info=tech_info,
        ai_score=ai_score,
        ai_score_class=score_class(ai_score),
        ai_grade=ai_grade,
        rewrite_count=rewrite_count,
        gap_count=gap_count,
        gap_score_class=score_class(max(0, 100 - gap_count * 5)),
        competitor_gaps=competitor_gaps,
        content_gaps=content_gaps,
        opportunity_gaps=opportunity_gaps,
        no_gaps=no_gaps,
        opportunity_count=opportunity_gaps,
        technical_issues_html=build_technical_issues_html(tech_data),
        page_scores_html=build_page_scores_html(readiness_data),
        gaps_html=build_gaps_html(gap_data),
        outputs_summary_html=build_outputs_summary_html(briefs_data, rewrites_data),
        next_steps_html=build_next_steps_html(tech_data, readiness_data, gap_data)
    )

    report_path = "outputs/audit_report.html"
    os.makedirs("outputs", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_html)

    generate_index(url, tech_data, readiness_data, gap_data, briefs_data)

    return report_path