# =============================================================
# MODULE 1: RESEARCHER
# Searches the web for stats, sources, and content gaps
# to ground every blog in real, credible information
# =============================================================

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from voice_profile import VOICE_CONFIG
import os
from dotenv import load_dotenv

load_dotenv()

def research_topic(topic: str, audience: str = None) -> str:
    """
    Takes a blog topic and returns structured research:
    - Key statistics and data points
    - Credible sources to reference
    - Current conversation in the market
    - Content gaps we can fill
    - Suggested angle based on Samara's framework
    """
    
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    audience_context = audience or VOICE_CONFIG["audience"]
    
    research_prompt = PromptTemplate(
        input_variables=["topic", "audience", "series", "framework"],
        template="""
You are a senior B2B marketing research analyst working for 
{author} at SamaraGlobal.com.

Your job is to research the following blog topic and return 
structured findings that will be used to write a thought 
leadership article.

BLOG TOPIC: {topic}

TARGET AUDIENCE: {audience}

CONTENT SERIES CONTEXT: {series}

SAMARA'S CONTENT FRAMEWORK: {framework}

Please provide research in this exact structure:

1. MARKET CONTEXT (2-3 sentences on why this topic matters RIGHT NOW)

2. KEY STATISTICS & DATA POINTS (5-7 real, credible stats with sources)

3. CURRENT MARKET CONVERSATION 
   (What are people saying about this? What's the dominant narrative?)

4. CONTENT GAP & SAMARA'S ANGLE
   (What is NOT being said that Samara should say? 
   What conventional wisdom should she challenge?)

5. REAL BRAND EXAMPLES TO REFERENCE (3-4 recognizable companies)

6. SPECIFIC TOOLS TO MENTION (3-4 relevant marketing tools)

7. SUGGESTED PROVOCATIVE OPENING LINE
   (One bold statement that challenges conventional wisdom)

8. SUGGESTED META DESCRIPTION (150-160 characters, SEO optimized)

Be specific, be current, be credible. 
No generic observations — only sharp, useful insights.
"""
    )
    
    chain = research_prompt | llm
    
    result = chain.invoke({
        "topic": topic,
        "audience": audience_context,
        "series": VOICE_CONFIG["series"],
        "framework": VOICE_CONFIG["framework"],
        "author": VOICE_CONFIG["author"]
    })
    
    return result.content


if __name__ == "__main__":
    # Test the researcher module independently
    test_topic = "Why firing your marketing department for AI agents is a strategic mistake"
    print("🔍 RESEARCHING TOPIC...")
    print("=" * 60)
    result = research_topic(test_topic)
    print(result)
    print("=" * 60)
    print("✅ Research complete!")