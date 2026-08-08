# =============================================================
# MODULE 4: REPURPOSER
# Takes the finished blog and creates:
# - 3 LinkedIn post variations
# - Pull quotes for social sharing
# - Content repurposing suggestions
# =============================================================

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from voice_profile import VOICE_CONFIG
import os
from dotenv import load_dotenv

load_dotenv()

def repurpose_content(topic: str, blog_post: str) -> str:
    """
    Takes the finished blog post and repurposes it into:
    - 3 LinkedIn post variations (different hooks)
    - 5 pull quotes for social sharing
    - 3 content repurposing suggestions
    """
    
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    repurpose_prompt = PromptTemplate(
        input_variables=[
            "topic",
            "blog_post",
            "voice",
            "author",
            "website"
        ],
        template="""
You are a senior social media strategist working for {author} 
at {website}.

You have just received a finished blog post and need to 
repurpose it into LinkedIn content that drives traffic 
back to the full article.

BLOG TOPIC: {topic}

FINISHED BLOG POST: {blog_post}

SAMARA'S VOICE & TONE RULES: {voice}

LINKEDIN POST RULES FOR SAMARA:
- Opens with bold emoji + provocative one-liner
- 150-300 words total
- Maximum 8 hashtags (choose the most targeted)
- Includes a teaser of the key insight (not the whole story)
- Drives curiosity to read the full blog
- Ends with engagement question OR strong CTA
- Never sounds like a press release
- Never uses "I am excited to share"
- Never uses "Check out my latest blog"
- Feels like a senior practitioner sharing a real insight

HASHTAG STRATEGY:
Choose maximum 8 from these themes:
- #AIinMarketing #AgenticAI #MarketingStrategy
- #ThoughtLeadership #ContentMarketing #B2BMarketing  
- #BrandPositioning #DemandGeneration #MarketingLeadership
- #FutureOfMarketing #CMO #MarTech #MessagingStrategy
- #SalesEnablement #GlobalMarketing #ModernMarketing

Please create the following:

═══════════════════════════════════════
LINKEDIN POST VARIATION 1: THE PROVOCATEUR
═══════════════════════════════════════
Hook style: Bold controversial statement that challenges 
conventional wisdom. Makes senior marketers stop scrolling.

[Write full LinkedIn post here]

═══════════════════════════════════════
LINKEDIN POST VARIATION 2: THE STORYTELLER  
═══════════════════════════════════════
Hook style: Opens with a brief real-world scenario or 
observation that the audience immediately recognizes.
Creates "that's exactly what I see happening" moment.

[Write full LinkedIn post here]

═══════════════════════════════════════
LINKEDIN POST VARIATION 3: THE DATA LEAD
═══════════════════════════════════════
Hook style: Opens with a surprising statistic or 
counterintuitive data point. Makes the reader question 
what they thought they knew.

[Write full LinkedIn post here]

═══════════════════════════════════════
PULL QUOTES FOR SOCIAL SHARING
═══════════════════════════════════════
5 standalone quotes from the blog that work as 
image text or tweet-style posts. Each should be 
punchy, standalone, and reflect Samara's POV.

1. "[Quote 1]"
2. "[Quote 2]"
3. "[Quote 3]"
4. "[Quote 4]"
5. "[Quote 5]"

═══════════════════════════════════════
CONTENT REPURPOSING SUGGESTIONS
═══════════════════════════════════════
3 ways this blog content could be repurposed further:
(e.g. podcast talking points, webinar outline, 
email newsletter, whitepaper section)

1. [Suggestion 1]
2. [Suggestion 2]
3. [Suggestion 3]

Make every LinkedIn variation feel authentically Samara —
authoritative, provocative, and genuinely useful to 
senior B2B marketers.
"""
    )
    
    chain = repurpose_prompt | llm
    
    result = chain.invoke({
        "topic": topic,
        "blog_post": blog_post,
        "voice": VOICE_CONFIG["voice"],
        "author": VOICE_CONFIG["author"],
        "website": VOICE_CONFIG["website"]
    })
    
    return result.content


if __name__ == "__main__":
    # Test the repurposer module independently
    test_topic = "Why firing your marketing department for AI agents is a strategic mistake"
    test_blog = """
    Firing your marketing team for AI agents is not a bold move. 
    It is an expensive mistake.
    
    In the past year, a growing number of executives have convinced 
    themselves that AI agents can replace the strategic thinking, 
    creative judgment, and institutional knowledge that experienced 
    marketers bring to the table. They cannot.
    
    AI agents are powerful tools. They can research, draft, 
    optimize, and distribute content at scale. But they cannot 
    build the positioning strategy that makes your product 
    matter. They cannot read the room in a board presentation. 
    They cannot build the relationships that turn prospects 
    into advocates.
    
    The companies that will win are not the ones that replace 
    their marketers with agents. They are the ones that give 
    their marketers agents to work with.
    """
    print("📱 REPURPOSING CONTENT...")
    print("=" * 60)
    result = repurpose_content(test_topic, test_blog)
    print(result)
    print("=" * 60)
    print("✅ Content repurposed!")