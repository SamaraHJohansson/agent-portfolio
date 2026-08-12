# =============================================================
# MODULE 1: CONTEXT ANALYZER
# SamaraGlobal.com | Relevance Agent
#
# Takes the prospect's signals and identifies what they
# are likely prioritizing right now based on their
# specific business situation.
# =============================================================

import os

from dotenv import load_dotenv

from openai import OpenAI



load_dotenv()



client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_context(prospect: dict) -> str:
    """
    Analyzes the prospect's current business context
    and identifies their likely priorities, pressures,
    and decision-making environment right now.
    """

    print(f"   Analyzing context for {prospect['name']} at {prospect['company']}...")

    prompt = f"""
You are a senior B2B sales strategist with 20 years of experience 
reading business signals and understanding what they mean for 
buyer priorities.

Analyze the following prospect profile and identify:
1. What this prospect is most likely prioritizing RIGHT NOW 
   based on their business signals
2. What pressures they are navigating that shape their 
   decision-making
3. What success looks like for them in their current situation
4. What risks they are most worried about
5. The emotional context: are they in growth mode, 
   survival mode, transition mode, or optimization mode?

PROSPECT PROFILE:
Name: {prospect['name']}
Title: {prospect['title']}
Company: {prospect['company']}
Industry: {prospect['industry']}
Company Size: {prospect['size']}
Geography: {prospect['geography']}
Current Signal: {prospect['signal']}
Known Pain: {prospect['pain']}

Write a clear, specific context analysis of 200-250 words.
Do not use generic language. Be specific to this prospect's
actual situation. Write in plain prose, no bullet points.
This analysis will be used to craft highly relevant outreach.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a senior B2B sales strategist who specializes in understanding buyer context and crafting relevant outreach. You are direct, specific, and never generic."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=400
    )

    return response.choices[0].message.content