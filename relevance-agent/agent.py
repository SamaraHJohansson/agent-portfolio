# =============================================================
# SAMARA RELEVANCE AGENT - MAIN BRAIN
# SamaraGlobal.com | B2B Sales Enablement
#
# This agent takes a prospect profile and produces:
# - A context analysis of their current situation
# - A competitive framing against their evaluated alternative
# - A relevance map connecting their reality to SamaraGlobal
# - Three outreach variations (cold email, LinkedIn, follow-up)
# - Three objection anticipations with suggested responses
#
# Built by: Samara H. Johansson
# Purpose: Demonstrating relevance-first sales enablement
#
# NOTE: In a real company, prospect data would come from
# a CRM like HubSpot or Salesforce, LinkedIn Sales Navigator,
# and intent data tools. This portfolio demonstration uses
# three realistic fictional prospects to show what the
# agent produces with real data.
# =============================================================

import os
import datetime
from dotenv import load_dotenv
from modules.prospects import PROSPECTS
from modules.context_analyzer import analyze_context
from modules.competitive_framer import frame_competitive_position
from modules.relevance_mapper import map_relevance
from modules.outreach_writer import write_outreach
from modules.objection_anticipator import anticipate_objections

load_dotenv()

def save_output(prospect: dict, content: dict) -> str:
    """
    Saves all generated content to a timestamped file
    in the outputs folder for easy reference
    """
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    clean_name = prospect['name'].lower().replace(" ", "-")
    clean_company = prospect['company'].lower().replace(" ", "-")
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"outputs/{timestamp}-{clean_name}-{clean_company}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# SAMARA RELEVANCE AGENT OUTPUT\n")
        f.write(f"**Prospect:** {prospect['name']}, ")
        f.write(f"{prospect['title']} at {prospect['company']}\n")
        f.write(f"**Generated:** {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}\n")
        f.write(f"**Website:** SamaraGlobal.com\n\n")
        f.write("=" * 60 + "\n\n")

        f.write("## PROSPECT PROFILE\n\n")
        f.write(f"**Name:** {prospect['name']}\n")
        f.write(f"**Title:** {prospect['title']}\n")
        f.write(f"**Company:** {prospect['company']}\n")
        f.write(f"**Industry:** {prospect['industry']}\n")
        f.write(f"**Size:** {prospect['size']}\n")
        f.write(f"**Geography:** {prospect['geography']}\n")
        f.write(f"**Signal:** {prospect['signal']}\n")
        f.write(f"**Pain:** {prospect['pain']}\n")
        f.write(f"**Competitor Evaluated:** {prospect['competitor']}\n")
        f.write(f"**SamaraGlobal Angle:** {prospect['samara_angle']}\n")
        f.write("\n" + "=" * 60 + "\n\n")

        f.write("## CONTEXT ANALYSIS\n\n")
        f.write(content["context"])
        f.write("\n\n" + "=" * 60 + "\n\n")

        f.write("## COMPETITIVE FRAMING\n\n")
        f.write(content["competitive_frame"])
        f.write("\n\n" + "=" * 60 + "\n\n")

        f.write("## RELEVANCE MAP\n\n")
        f.write(content["relevance_map"])
        f.write("\n\n" + "=" * 60 + "\n\n")

        f.write("## OUTREACH PACKAGE\n\n")
        f.write(content["outreach"])
        f.write("\n\n" + "=" * 60 + "\n\n")

        f.write("## OBJECTION ANTICIPATOR\n\n")
        f.write(content["objections"])
        f.write("\n\n")

    return filename


def run_agent(prospect: dict) -> None:
    """
    Main agent workflow for one prospect.
    Runs all five modules in sequence:
    Context -> Competitive Frame -> Relevance Map
    -> Outreach -> Objections
    """

    print("\n")
    print("=" * 60)
    print("  SAMARA RELEVANCE AGENT")
    print("  SamaraGlobal.com")
    print("=" * 60)
    print(f"\n📌 PROSPECT: {prospect['name']}, "
          f"{prospect['title']} at {prospect['company']}\n")

    # ─────────────────────────────────────────
    # STEP 1: CONTEXT ANALYSIS
    # ─────────────────────────────────────────
    print("🔍 STEP 1/5: Analyzing prospect context...")
    context = analyze_context(prospect)
    print("   ✅ Context analysis complete!\n")

    # ─────────────────────────────────────────
    # STEP 2: COMPETITIVE FRAMING
    # ─────────────────────────────────────────
    print("⚔️  STEP 2/5: Framing competitive position...")
    competitive_frame = frame_competitive_position(
        prospect, context)
    print("   ✅ Competitive framing complete!\n")

    # ─────────────────────────────────────────
    # STEP 3: RELEVANCE MAPPING
    # ─────────────────────────────────────────
    print("🎯 STEP 3/5: Mapping relevance...")
    relevance_map = map_relevance(
        prospect, context, competitive_frame)
    print("   ✅ Relevance map complete!\n")

    # ─────────────────────────────────────────
    # STEP 4: OUTREACH WRITING
    # ─────────────────────────────────────────
    print("✍️  STEP 4/5: Writing outreach package...")
    outreach = write_outreach(
        prospect, context, competitive_frame, relevance_map)
    print("   ✅ Outreach package complete!\n")

    # ─────────────────────────────────────────
    # STEP 5: OBJECTION ANTICIPATION
    # ─────────────────────────────────────────
    print("🛡️  STEP 5/5: Anticipating objections...")
    objections = anticipate_objections(
        prospect, context, competitive_frame, relevance_map)
    print("   ✅ Objection anticipation complete!\n")

    # ─────────────────────────────────────────
    # SAVE ALL OUTPUT
    # ─────────────────────────────────────────
    content = {
        "context": context,
        "competitive_frame": competitive_frame,
        "relevance_map": relevance_map,
        "outreach": outreach,
        "objections": objections
    }

    output_file = save_output(prospect, content)

    # ─────────────────────────────────────────
    # FINAL SUMMARY
    # ─────────────────────────────────────────
    print("=" * 60)
    print("  🎉 RELEVANCE PACKAGE COMPLETE!")
    print("=" * 60)
    print(f"\n📁 Saved to: {output_file}")
    print("\n📦 YOUR RELEVANCE PACKAGE INCLUDES:")
    print("   ✅ Context analysis of prospect situation")
    print("   ✅ Competitive framing vs evaluated alternative")
    print("   ✅ Relevance map connecting their reality to your value")
    print("   ✅ Cold email, LinkedIn message, and follow-up email")
    print("   ✅ Three objections with suggested responses")
    print("\n💡 NEXT STEPS:")
    print("   1. Open the output file and review the context analysis")
    print("   2. Check the competitive framing for accuracy")
    print("   3. Personalize the outreach in your own voice")
    print("   4. Use the objection responses to prepare for the call")
    print("   5. Reach out to the prospect!")
    print("\n" + "=" * 60 + "\n")


# ─────────────────────────────────────────────────────────────
# RUN THE AGENT FOR ALL THREE PROSPECTS
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("  SAMARA RELEVANCE AGENT")
    print("  Running for all prospects...")
    print("=" * 60)

    for prospect in PROSPECTS:
        run_agent(prospect)

    print("\n✅ ALL PROSPECT PACKAGES COMPLETE!")
    print("📁 Check the outputs folder for all files.")
    print("\n" + "=" * 60 + "\n")