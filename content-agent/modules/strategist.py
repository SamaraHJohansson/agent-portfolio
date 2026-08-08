# =============================================================
# MODULE 2: STRATEGIST
# Applies Samara's content framework to the research
# and builds a structured content blueprint before writing
# =============================================================

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from voice_profile import VOICE_CONFIG
import os
from dotenv import load_dotenv

load_dotenv()

def build_content_strategy(topic: str, research: str) -> str:
    """
    Takes the research output and builds a detailed
    content blueprint using Samara's signature framework:
    Challenge → Reframe → Insight → Examples → POV Close
    """
    
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.4,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    strategy_prompt = PromptTemplate(
        input_variables=[
            "topic", 
            "research", 
            "framework", 
            "voice", 
            "seo",
            "series"
        ],
        template="""
You are a senior content strategist working for {author} 
at SamaraGlobal.com.

You have received research on a blog topic and must now build 
a detailed content blueprint that Samara will use to write 
her thought leadership article.

BLOG TOPIC: {topic}

RESEARCH FINDINGS: {research}

SAMARA'S CONTENT FRAMEWORK: {framework}

SAMARA'S VOICE & TONE: {voice}

SEO GUIDELINES: {seo}

CONTENT SERIES CONTEXT: {series}

Build a detailed content blueprint in this exact structure:

1. HEADLINE OPTIONS (3 variations)
   - Primary: SEO-optimized, keyword-rich
   - Provocative: Challenges conventional wisdom
   - Question-based: Sparks curiosity
   
2. META DESCRIPTION (150-160 characters)
   SEO-optimized, includes primary keyword

3. CONTENT ARC (Samara's 5-step framework applied)
   
   STEP 1 — CHALLENGE (Opening paragraph strategy)
   - The conventional wisdom we are challenging
   - The provocative opening statement
   - The tension we are creating
   
   STEP 2 — REFRAME (The real problem)
   - The deeper truth we are revealing
   - Samara's unique angle
   - The pivot sentence
   
   STEP 3 — STRUCTURED INSIGHT (The meat)
   - 3-4 key points to make
   - Supporting data for each point
   - Tools/platforms to reference
   
   STEP 4 — REAL EXAMPLES (Proof points)
   - Brand examples to use
   - How each example supports the argument
   
   STEP 5 — POV CLOSE (Samara's signature ending)
   - The forward-looking statement
   - Samara's clear point of view
   - Optional conversation-starting question

4. SUGGESTED H2 HEADERS (4-6 headers for the full article)

5. PRIMARY KEYWORD & SUPPORTING KEYWORDS
   - Primary keyword (appears in title + first paragraph)
   - 3-4 supporting keywords (woven naturally throughout)

6. INTERNAL LINK OPPORTUNITIES
   - 2-3 topics from SamaraGlobal.com to link to

7. ESTIMATED WORD COUNT TARGET
   - Section by section breakdown totaling 800-1200 words

Be precise. Be strategic. Every decision should serve 
Samara's voice, her audience, and her SEO goals.
"""
    )
    
    chain = strategy_prompt | llm
    
    result = chain.invoke({
        "topic": topic,
        "research": research,
        "framework": VOICE_CONFIG["framework"],
        "voice": VOICE_CONFIG["voice"],
        "seo": VOICE_CONFIG["seo"],
        "series": VOICE_CONFIG["series"],
        "author": VOICE_CONFIG["author"]
    })
    
    return result.content


if __name__ == "__main__":
    # Test the strategist module independently
    test_topic = "Why firing your marketing department for AI agents is a strategic mistake"
    test_research = """
    Market Context: Companies are increasingly replacing marketing 
    teams with AI agents, driven by cost-cutting pressures.
    Key Stats: 67% of CMOs report budget cuts in 2024.
    Content Gap: No one is talking about the strategic cost 
    of losing institutional marketing knowledge.
    """
    print("🎯 BUILDING CONTENT STRATEGY...")
    print("=" * 60)
    result = build_content_strategy(test_topic, test_research)
    print(result)
    print("=" * 60)
    print("✅ Strategy complete!")