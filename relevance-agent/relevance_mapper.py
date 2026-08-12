# =============================================================
# MODULE 3: RELEVANCE MAPPER
# SamaraGlobal.com | Relevance Agent
#
# Connects the prospect's current context to SamaraGlobal's
# specific value proposition. Not "we help companies like
# yours" but "given that you are navigating X right now,
# here is why this matters specifically to you."
# This is the core of relevance over personalization.
# =============================================================

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def map_relevance(prospect: dict, context: str, competitive_frame: str) -> str:
    """
    Maps the prospect's specific situation to SamaraGlobal's
    value proposition in a way that feels genuinely relevant
    rather than generically personalized.
    """

    print(f"   Mapping relevance for {prospect['name']}...")

    prompt = f"""
You are a senior B2B marketing strategist who specializes
in relevance-based messaging. You understand the critical
difference between personalization (putting the right name
on a generic message) and relevance (speaking directly to
what this specific buyer is navigating right now).

Your job is to create a relevance map: a specific, honest
connection between what this prospect is dealing with TODAY
and what SamaraGlobal offers that addresses it.

PROSPECT PROFILE:
Name: {prospect['name']}
Title: {prospect['title']}
Company: {prospect['company']}
Industry: {prospect['industry']}
Geography: {prospect['geography']}
Signal: {prospect['signal']}
Pain: {prospect['pain']}
SamaraGlobal Angle: {prospect['samara_angle']}

CONTEXT ANALYSIS:
{context}

COMPETITIVE FRAMING:
{competitive_frame}

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

Create a relevance map of 150-200 words that answers:
1. Given what this prospect is navigating RIGHT NOW,
   why does SamaraGlobal's offering matter to them
   specifically at this moment?
2. What is the cost of NOT addressing this now?
3. What does success look like if they engage SamaraGlobal?

This is not a sales pitch. It is a strategic connection
between their reality and our value. Be specific.
Be honest. Never be generic.
Write in plain prose. No bullet points.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a senior B2B marketing strategist who specializes in relevance-based messaging. You connect buyer reality to vendor value in specific, honest, non-generic ways."
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