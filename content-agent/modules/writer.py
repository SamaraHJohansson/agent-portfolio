# =============================================================
# MODULE 3: WRITER
# Writes the full blog post in Samara's voice
# using the research and content strategy as foundation
# =============================================================

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from voice_profile import VOICE_CONFIG
import os
from dotenv import load_dotenv

load_dotenv()

def write_blog(topic: str, research: str, strategy: str) -> str:
    """
    Takes the research and strategy blueprint and writes
    a complete, SEO-optimized blog post in Samara's voice.
    
    Output includes:
    - Full blog post (800-1200 words)
    - Meta description
    - SEO notes
    """
    
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    writer_prompt = PromptTemplate(
        input_variables=[
            "topic",
            "research",
            "strategy",
            "voice",
            "framework",
            "seo",
            "positioning",
            "author"
        ],
        template="""
You are writing AS {author} for SamaraGlobal.com.

You are a senior marketing strategist with 20+ years of experience
in B2B marketing, brand positioning, messaging strategy, and 
global marketing expansion. You write with authority, clarity,
and a practitioner's perspective.

BLOG TOPIC: {topic}

RESEARCH TO DRAW FROM: {research}

CONTENT STRATEGY BLUEPRINT: {strategy}

SAMARA'S VOICE & TONE RULES: {voice}

SAMARA'S CONTENT FRAMEWORK: {framework}

SEO REQUIREMENTS: {seo}

SAMARA'S POSITIONING CONTEXT: {positioning}

Write the complete blog post now. Follow these rules exactly:

WRITING RULES:
1. Open with a BOLD, PROVOCATIVE statement — not a question
   Challenge what most people believe about this topic
   
2. Follow Samara's 5-step framework:
   Challenge → Reframe → Insight → Examples → POV Close

3. Use H2 and H3 headers from the strategy blueprint
   Headers should be clear, benefit-driven, and SEO-friendly

4. Include ALL of these in the body:
   - At least 2 recognizable brand examples
   - At least 2 specific marketing tools with context
   - At least 1 statistic or data point with source
   - At least 1 internal link placeholder [LINK: topic]
   
5. NEVER use these phrases:
   - "In today's rapidly evolving landscape"
   - "Game-changing"
   - "Revolutionary"  
   - "Embrace this shift"
   - "In conclusion" as a header
   - Generic closing advice

6. END with Samara's POV — a clear, forward-looking statement
   that reflects her belief that AI augments great marketers,
   it does not replace them.

7. After the blog, provide:
   
   ---META---
   META DESCRIPTION: [150-160 character SEO description]
   PRIMARY KEYWORD: [main keyword]
   WORD COUNT: [approximate count]
   READING TIME: [X min read]

FORMAT:
- Use markdown formatting
- H1 for title (only one)
- H2 for main sections
- H3 for subsections
- Bold for key terms and emphasis
- Bullet points where they aid clarity

Write the complete blog post now. Make it worthy of 
a senior marketing strategist's byline.
"""
    )
    
    chain = writer_prompt | llm
    
    result = chain.invoke({
        "topic": topic,
        "research": research,
        "strategy": strategy,
        "voice": VOICE_CONFIG["voice"],
        "framework": VOICE_CONFIG["framework"],
        "seo": VOICE_CONFIG["seo"],
        "positioning": VOICE_CONFIG["positioning"],
        "author": VOICE_CONFIG["author"]
    })
    
    return result.content


if __name__ == "__main__":
    # Test the writer module independently
    test_topic = "Why firing your marketing department for AI agents is a strategic mistake"
    test_research = """
    Market Context: Companies are increasingly replacing marketing 
    teams with AI agents driven by cost cutting pressures.
    Key Stats: 67% of CMOs report budget cuts in 2024.
    Content Gap: No one is talking about the strategic cost 
    of losing institutional marketing knowledge.
    Suggested Opening: Firing your marketing team for AI agents 
    is not a bold move. It is an expensive mistake.
    """
    test_strategy = """
    Headline: Why Firing Your Marketing Department for AI Agents 
    Is a Strategic Mistake
    Framework: Challenge the cost-cutting narrative, Reframe as 
    strategic risk, Provide insight on what agents can and cannot 
    do, Ground with real examples, Close with augmentation POV.
    Headers: The Real Cost of Replacing Marketers with Agents,
    What AI Agents Actually Do Well, What They Cannot Replace,
    The Augmented Marketing Team Model
    """
    print("✍️  WRITING BLOG POST...")
    print("=" * 60)
    result = write_blog(test_topic, test_research, test_strategy)
    print(result)
    print("=" * 60)
    print("✅ Blog written!")