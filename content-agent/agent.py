# =============================================================
# SAMARA CONTENT AGENT - MAIN BRAIN
# SamaraGlobal.com | B2B Thought Leadership
# 
# This agent takes a topic and produces:
# - A complete SEO-optimized blog post
# - 3 LinkedIn post variations
# - Pull quotes for social sharing
# - A full editorial review with quality score
#
# Built by: Samara H. Johansson
# Purpose: AI-augmented thought leadership content creation
# =============================================================

import os
import datetime
from dotenv import load_dotenv
from modules.researcher import research_topic
from modules.strategist import build_content_strategy
from modules.writer import write_blog
from modules.repurposer import repurpose_content
from modules.reviewer import review_content

load_dotenv()

def save_output(topic: str, content: dict) -> str:
    """
    Saves all generated content to a timestamped file
    in the outputs folder for easy reference
    """
    # Create outputs folder if it doesn't exist
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
    
    # Create clean filename from topic
    clean_topic = topic.lower()
    clean_topic = clean_topic.replace(" ", "-")
    clean_topic = clean_topic.replace("?", "")
    clean_topic = clean_topic.replace(":", "")
    clean_topic = clean_topic[:50]
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"outputs/{timestamp}-{clean_topic}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# SAMARA CONTENT AGENT OUTPUT\n")
        f.write(f"**Topic:** {topic}\n")
        f.write(f"**Generated:** {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}\n")
        f.write(f"**Website:** SamaraGlobal.com\n\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("## 📊 RESEARCH\n\n")
        f.write(content["research"])
        f.write("\n\n" + "=" * 60 + "\n\n")
        
        f.write("## 🎯 CONTENT STRATEGY\n\n")
        f.write(content["strategy"])
        f.write("\n\n" + "=" * 60 + "\n\n")
        
        f.write("## ✍️ BLOG POST\n\n")
        f.write(content["blog"])
        f.write("\n\n" + "=" * 60 + "\n\n")
        
        f.write("## 📱 LINKEDIN POSTS\n\n")
        f.write(content["linkedin"])
        f.write("\n\n" + "=" * 60 + "\n\n")
        
        f.write("## 🔍 EDITORIAL REVIEW\n\n")
        f.write(content["review"])
        f.write("\n\n")
    
    return filename


def run_agent(topic: str, audience: str = None) -> None:
    """
    Main agent workflow — runs all 5 modules in sequence:
    Research → Strategy → Write → Repurpose → Review
    
    Args:
        topic: The blog topic to write about
        audience: Optional custom audience override
    """
    
    print("\n")
    print("=" * 60)
    print("  SAMARA CONTENT AGENT")
    print("  SamaraGlobal.com")
    print("=" * 60)
    print(f"\n📌 TOPIC: {topic}\n")
    
    # ─────────────────────────────────────────
    # STEP 1: RESEARCH
    # ─────────────────────────────────────────
    print("🔍 STEP 1/5: Researching topic...")
    print("   Finding stats, sources, and content gaps...")
    research = research_topic(topic, audience)
    print("   ✅ Research complete!\n")
    
    # ─────────────────────────────────────────
    # STEP 2: STRATEGY
    # ─────────────────────────────────────────
    print("🎯 STEP 2/5: Building content strategy...")
    print("   Applying Samara's content framework...")
    strategy = build_content_strategy(topic, research)
    print("   ✅ Strategy complete!\n")
    
    # ─────────────────────────────────────────
    # STEP 3: WRITE
    # ─────────────────────────────────────────
    print("✍️  STEP 3/5: Writing blog post...")
    print("   Writing in Samara's voice...")
    blog = write_blog(topic, research, strategy)
    print("   ✅ Blog post written!\n")
    
    # ─────────────────────────────────────────
    # STEP 4: REPURPOSE
    # ─────────────────────────────────────────
    print("📱 STEP 4/5: Creating LinkedIn posts...")
    print("   Generating 3 variations + pull quotes...")
    linkedin = repurpose_content(topic, blog)
    print("   ✅ LinkedIn posts created!\n")
    
    # ─────────────────────────────────────────
    # STEP 5: REVIEW
    # ─────────────────────────────────────────
    print("🔍 STEP 5/5: Running editorial review...")
    print("   Checking voice, SEO, and quality standards...")
    review = review_content(topic, blog, linkedin)
    print("   ✅ Editorial review complete!\n")
    
    # ─────────────────────────────────────────
    # SAVE ALL OUTPUT
    # ─────────────────────────────────────────
    content = {
        "research": research,
        "strategy": strategy,
        "blog": blog,
        "linkedin": linkedin,
        "review": review
    }
    
    output_file = save_output(topic, content)
    
    # ─────────────────────────────────────────
    # FINAL SUMMARY
    # ─────────────────────────────────────────
    print("=" * 60)
    print("  🎉 CONTENT PACKAGE COMPLETE!")
    print("=" * 60)
    print(f"\n📁 Saved to: {output_file}")
    print("\n📦 YOUR CONTENT PACKAGE INCLUDES:")
    print("   ✅ Research & market context")
    print("   ✅ Content strategy blueprint")
    print("   ✅ Full SEO-optimized blog post")
    print("   ✅ 3 LinkedIn post variations")
    print("   ✅ Pull quotes for social sharing")
    print("   ✅ Editorial review & quality score")
    print("\n💡 NEXT STEPS:")
    print("   1. Open the output file and review the blog")
    print("   2. Check the editorial review score")
    print("   3. Make any suggested edits in your own voice")
    print("   4. Choose your favorite LinkedIn variation")
    print("   5. Publish to SamaraGlobal.com!")
    print("\n" + "=" * 60 + "\n")


# ─────────────────────────────────────────────────────────────
# RUN THE AGENT
# Change the topic below to generate any blog post!
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    
    # ✏️ CHANGE THIS TOPIC TO WHATEVER YOU WANT TO WRITE ABOUT
    TOPIC = "Why firing your marketing department for AI agents is a strategic mistake"
    
    # Optional: customize the target audience
    # Leave as None to use Samara's default audience profile
    AUDIENCE = None
    
    run_agent(TOPIC, AUDIENCE)