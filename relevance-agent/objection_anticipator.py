# =============================================================
# MODULE 5: OBJECTION ANTICIPATOR
# SamaraGlobal.com | Relevance Agent
#
# Based on the prospect's role, company stage, and the
# competitor they evaluated, produces the three most likely
# objections and suggested responses for each.
#
# This gives the sales conversation a head start by
# anticipating resistance before it happens and preparing
# honest, specific, non-defensive responses.
# =============================================================

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def anticipate_objections(prospect: dict, context: str,
                          competitive_frame: str, 
                          relevance_map: str) -> str:
    """
    Identifies the three most likely objections this
    specific prospect will raise and produces honest,
    specific, non-defensive responses to each.
    """

    print(f"   Anticipating objections for {prospect['name']}...")

    prompt = f"""
You are a senior B2B sales strategist with deep experience
in handling objections in consultative selling situations.
You understand that the best objection responses are:
- Honest and never dismissive
- Specific to the prospect's actual situation
- Non-defensive and confident
- Focused on the buyer's outcome, not the vendor's defense
- Brief and direct, never over-explained

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

COMPETITIVE FRAMING:
{competitive_frame}

RELEVANCE MAP:
{relevance_map}

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
Website: SamaraGlobal.com

Identify the THREE most likely objections this specific
prospect will raise based on their role, company situation,
and the competitor they evaluated.

For each objection provide:
- The exact words the prospect might use
- A specific, honest, confident response of 2-3 sentences
- One follow-up question to keep the conversation moving

Format exactly like this:

OBJECTION 1
Prospect says: "[exact words]"
Response: [2-3 sentence response]
Follow-up question: [one question]

OBJECTION 2
Prospect says: "[exact words]"
Response: [2-3 sentence response]
Follow-up question: [one question]

OBJECTION 3
Prospect says: "[exact words]"
Response: [2-3 sentence response]
Follow-up question: [one question]
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a senior B2B sales strategist who specializes in objection handling for consultative selling situations. Your responses are always honest, specific, confident, and focused on the buyer's outcome rather than the vendor's defense."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=600
    )

    return response.choices[0].message.content