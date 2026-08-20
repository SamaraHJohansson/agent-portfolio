# Search Visibility Agent 

The Search Visibility Agent is an AI-powered website analysis tool built to evaluate how visible a website is in both traditional search engines and emerging AI search platforms such as Perplexity, ChatGPT Search, Gemini, and Google's AI Overviews.
 
Traditional SEO tools are excellent at measuring rankings, backlinks, technical SEO, and keyword performance. What they do not measure is whether a website is structured in a way that AI systems can easily retrieve, understand, trust, and cite.
 
This agent was built to fill that gap.
 
Rather than replacing platforms such as SEMrush, Ahrefs, Moz, or Screaming Frog, the Search Visibility Agent picks up where those tools stop. It analyses not only technical SEO foundations, but also Answer Engine Optimisation (AEO) and Generative Engine Optimisation (GEO) factors that influence whether content is likely to be surfaced, referenced, or cited by AI-powered search experiences. 

## Core Capabilities 

### Site Crawling 

The agent crawls a website and collects page content, metadata, structural information, and internal site architecture data. 

### Technical SEO Analysis 

The agent evaluates traditional technical SEO signals including:
 
- Meta titles and descriptions
- Heading structure
- Schema markup
- Image alt text
- Canonical tags
- Crawlability signals
- Technical health scoring 

### Answer Readiness Scoring 

The agent assesses whether content is structured in a way that AI systems can easily consume and cite. 

It evaluates: 

- Clarity of answers
- Question-and-answer structure
- Extractability of information
- Authority signals
- Content specificity
- Information completeness
 

### AI Search Gap Analysis 

The agent identifies gaps between the content currently available on a website and the types of content most likely to be retrieved by AI search systems. 

This helps identify:

- Missing topics
- Missing question coverage
- Weak answer structures
- Content opportunities
- AI citation risks 

### Content Brief Generation

For each identified gap, the agent can generate structured content briefs designed to improve AI search visibility. 

Each brief includes:
 
- Recommended topic coverage
- Key questions to answer
- Suggested structure
- Content guidance
- AI citation considerations
 
### Content Rewrite Recommendations 

Pages with low answer-readiness scores can be automatically analysed and rewritten into formats that are better suited for AI retrieval and citation.

These recommendations focus on improving clarity, authority, structure, and answer quality rather than simply editing wording.

---

## Project Structure

```text

search-visibility-agent/
├── modules/
├── outputs/
│ ├── briefs/
│ └── rewrites/
├── agent.py
├── requirements.txt
84
└── .gitignore
