# =============================================================
# MODULE 5: REVIEWER
# Quality checks the finished blog and LinkedIn posts
# against Samara's voice, SEO criteria, and brand standards
# Returns a score and specific improvement notes
# =============================================================

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from voice_profile import VOICE_CONFIG
import os
from dotenv import load_dotenv

load_dotenv()

def review_content(topic: str, blog_post: str, linkedin_posts: str) -> str:
    """
    Reviews the finished blog and LinkedIn posts against:
    - Samara's voice and tone standards
    - SEO requirements
    - Content framework compliance
    - Quality standards
    
    Returns:
    - Overall quality score (1-10)
    - Detailed feedback by category
    - Specific lines to improve
    - Final recommendation (publish / revise)
    """
    
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.2,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    review_prompt = PromptTemplate(
        input_variables=[
            "topic",
            "blog_post",
            "linkedin_posts",
            "voice",
            "framework",
            "seo",
            "quality"
        ],
        template="""
You are a senior editorial director and brand guardian 
for SamaraGlobal.com.

Your job is to review finished content with a critical eye
and ensure it meets the highest standards before publishing.
You are honest, specific, and constructive.

BLOG TOPIC: {topic}

FINISHED BLOG POST: {blog_post}

LINKEDIN POSTS: {linkedin_posts}

SAMARA'S VOICE & TONE RULES: {voice}

SAMARA'S CONTENT FRAMEWORK: {framework}

SEO REQUIREMENTS: {seo}

QUALITY STANDARDS CHECKLIST: {quality}

Please provide a complete editorial review:

═══════════════════════════════════════
OVERALL QUALITY SCORE
═══════════════════════════════════════
Blog Post Score: [X/10]
LinkedIn Posts Score: [X/10]
Overall Score: [X/10]

═══════════════════════════════════════
VOICE & TONE REVIEW
═══════════════════════════════════════
✓ What is working well (be specific, quote the text)
✗ What needs improvement (be specific, quote the text)
→ Specific suggested rewrites for weak sections

═══════════════════════════════════════
CONTENT FRAMEWORK REVIEW
═══════════════════════════════════════
CHALLENGE opening: [Pass/Needs Work] — [specific note]
REFRAME section: [Pass/Needs Work] — [specific note]
STRUCTURED INSIGHT: [Pass/Needs Work] — [specific note]
REAL EXAMPLES: [Pass/Needs Work] — [specific note]
POV CLOSE: [Pass/Needs Work] — [specific note]

═══════════════════════════════════════
SEO REVIEW
═══════════════════════════════════════
Word count: [X words] [Pass/Needs Work]
Primary keyword placement: [Pass/Needs Work]
Header structure: [Pass/Needs Work]
Meta description: [Pass/Needs Work]
Overall SEO score: [X/10]

═══════════════════════════════════════
LINKEDIN POSTS REVIEW
═══════════════════════════════════════
Variation 1 — The Provocateur:
  Hook strength: [1-10] — [specific note]
  Voice compliance: [Pass/Needs Work]
  Hashtag count: [X] [Pass/Needs Work]
  
Variation 2 — The Storyteller:
  Hook strength: [1-10] — [specific note]
  Voice compliance: [Pass/Needs Work]
  Hashtag count: [X] [Pass/Needs Work]

Variation 3 — The Data Lead:
  Hook strength: [1-10] — [specific note]
  Voice compliance: [Pass/Needs Work]
  Hashtag count: [X] [Pass/Needs Work]

Best LinkedIn variation for Samara: Variation [X]
Reason: [specific explanation]

═══════════════════════════════════════
TOP 3 IMPROVEMENTS NEEDED
═══════════════════════════════════════
1. [Most important improvement — be specific]
2. [Second improvement — be specific]
3. [Third improvement — be specific]

═══════════════════════════════════════
PHRASES TO REMOVE OR REPLACE
═══════════════════════════════════════
List any generic, weak, or off-brand phrases found:
- "[phrase found]" → Replace with: "[suggested replacement]"

═══════════════════════════════════════
FINAL RECOMMENDATION
═══════════════════════════════════════
[ ] PUBLISH READY — Minor polish only
[ ] REVISE FIRST — Specific sections need work
[ ] SIGNIFICANT REVISION — Core argument needs strengthening

Editorial note: [2-3 sentence overall assessment]

Be honest. Be specific. Great content requires great editing.
"""
    )
    
    chain = review_prompt | llm
    
    result = chain.invoke({
        "topic": topic,
        "blog_post": blog_post,
        "linkedin_posts": linkedin_posts,
        "voice": VOICE_CONFIG["voice"],
        "framework": VOICE_CONFIG["framework"],
        "seo": VOICE_CONFIG["seo"],
        "quality": VOICE_CONFIG["quality"]
    })
    
    return result.content


if __name__ == "__main__":
    # Test the reviewer module independently
    test_topic = "Why firing your marketing department for AI agents is a strategic mistake"
    test_blog = """
    Firing your marketing team for AI agents is not a bold move.
    It is an expensive mistake.
    AI agents are powerful tools but they cannot replace strategic
    thinking, creative judgment, and institutional knowledge.
    The companies that win will give their marketers agents 
    to work with — not replace marketers with agents.
    """
    test_linkedin = """
    POST 1: Firing your marketing team for AI? 
    That is not innovation. That is a very expensive experiment.
    Read why in my latest blog.
    #AIinMarketing #MarketingStrategy
    """
    print("🔍 REVIEWING CONTENT...")
    print("=" * 60)
    result = review_content(test_topic, test_blog, test_linkedin)
    print(result)
    print("=" * 60)
    print("✅ Review complete!")