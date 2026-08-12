# =============================================================
# MODULE 2: COMPETITIVE FRAMER
# SamaraGlobal.com | Relevance Agent
#
# Takes the competitor the prospect has likely evaluated
# and identifies the specific gaps or weaknesses in that
# competitor's approach that SamaraGlobal addresses.
# =============================================================

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def frame_competitive_position(prospect: dict, context: str) -> str:
    """
    Analyzes the competitive situation and develops
    a specific, honest differentiation narrative
    based on the competitor the prospect evaluated.
    """

    print(f"   Framing competitive position against {prospect['competitor']}...")

    prompt = f"""
You are a senior B2B positioning strategist who specializes
in competitive differentiation. You never use generic claims
like "we are better" or "we are more experienced."
You identify specific, credible, honest differences that
matter to this particular buyer in their particular situation.

Based on the prospect profile and context analysis below,
develop a competitive framing that explains specifically
why SamaraGlobal is the stronger choice over the competitor
this prospect has likely evaluated.

PROSPECT PROFILE:
Name: {prospect['name']}
Title: {prospect['title']}
Company: {prospect['company']}
Industry: {prospect['industry']}
Geography: {prospect['geography']}
Signal: {prospect['signal']}
Pain: {prospect['pain']}
Competitor Evaluated: {prospect['competitor']}
SamaraGlobal Angle: {prospect['samara_angle']}

CONTEXT ANALYSIS:
{context}

ABOUT SAMAGLOBAL:
Samara H. Johansson is a senior B2B marketing consultant
specializing in global brand positioning, messaging frameworks,
and AI-augmented marketing strategy. She has 20+ years of
experience across US and European markets including significant
time in Stockholm. She works with companies navigating growth,
repositioning, and international market expansion.
She is not a large agency. She is a senior practitioner
who does the work herself, bringing strategic depth without
agency overhead, bureaucracy, or junior team handoffs.

Develop a competitive framing of 150-200 words that:
1. Identifies the specific gap in what the competitor offers
   for THIS prospect's situation
2. Explains specifically how SamaraGlobal addresses that gap
3. Is honest and credible, not boastful
4. Speaks to the prospect's current context and priorities

Write in plain prose. No bullet points. No generic claims.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a senior B2B positioning strategist who develops specific, honest, credible competitive differentiation narratives. You never use generic language or empty claims."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=350
    )

    return response.choices[0].message.content