
# =============================================================
# MODULE 4: OUTREACH WRITER
# SamaraGlobal.com | Relevance Agent
#
# Takes the context analysis, competitive framing, and
# relevance map and produces three outreach variations:
# - A cold email (first touch)
# - A LinkedIn connection message
# - A follow-up email (one week later)
#
# Every piece of outreach leads with the prospect's
# context, not SamaraGlobal's product.
# =============================================================

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def write_outreach(prospect: dict, context: str,
                   competitive_frame: str, relevance_map: str) -> str:
    """
    Produces three outreach variations grounded in
    the prospect's specific context and situation.
    Each piece leads with their reality, not our pitch.
    """

    print(f"   Writing outreach for {prospect['name']}...")

    prompt = f"""
You are a senior B2B sales writer who specializes in
relevance-first outreach. You understand that the best
outreach does not lead with the vendor's product or
credentials. It leads with the buyer's situation,
demonstrating that the sender genuinely understands
what the buyer is navigating right now.

Your outreach is:
- Concise and respectful of the reader's time
- Specific to their situation, never generic
- Confident but not pushy
- Human and direct, never corporate or stiff
- Always leads with their context, not our pitch

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

Produce exactly three outreach pieces:

1. COLD EMAIL
Subject line: [specific, under 50 characters,
              references their situation not our product]
Body: 100-150 words maximum. Lead with their context.
One specific observation about their situation.
One sentence about why SamaraGlobal is relevant right now.
One clear, low-pressure call to action.
Sign off as Samara Johansson, SamaraGlobal.com

2. LINKEDIN CONNECTION MESSAGE
75 words maximum. Even more concise than the email.
Reference something specific about their situation.
No pitch. Just a relevant observation and a reason
to connect. This should feel like one senior
professional reaching out to another, not a sales message.

3. FOLLOW-UP EMAIL (one week after cold email, no response)
Subject line: [different angle from the first email]
Body: 75-100 words. Do not repeat the first email.
Bring one new, specific insight relevant to their
situation that adds value regardless of whether
they respond. End with a gentle, confident call to action.
Sign off as Samara Johansson, SamaraGlobal.com

Format your response exactly like this:

COLD EMAIL
Subject: [subject line]
[email body]

LINKEDIN MESSAGE
[message body]

FOLLOW-UP EMAIL
Subject: [subject line]
[email body]
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a senior B2B sales writer who specializes in relevance-first outreach. You write concise, specific, human outreach that leads with buyer context rather than vendor pitch. You never use corporate language, empty claims, or generic personalization."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=800
    )

    return response.choices[0].message.content