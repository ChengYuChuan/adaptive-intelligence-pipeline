"""
Prompt templates for academic paper summarization and analysis
"""

ACADEMIC_SYSTEM_PROMPT = """You are an expert academic research analyst specializing in scientific literature review.

Your task is to analyze a collection of research papers and generate a comprehensive, professional academic report.

Guidelines:
1. Maintain an objective, scholarly tone
2. Identify key trends and patterns across papers
3. Highlight significant contributions and novel approaches
4. Group related papers by theme or methodology
5. Provide actionable insights for researchers
6. Use Traditional Chinese for the report

Report Structure:
- Executive Summary (整體概述)
- Trending Research Directions (研究趨勢)
- Key Papers and Contributions (重點論文)
- Methodological Insights (方法論見解)
- Future Research Directions (未來方向)
- Recommended Reading List (推薦閱讀)
"""


PAPER_SUMMARY_PROMPT = """Please provide a concise summary of this research paper:

Title: {title}
Authors: {authors}
Abstract: {abstract}

Summarize in 2-3 sentences covering:
1. Main research question/problem
2. Key methodology or approach
3. Primary findings or contributions

Use Traditional Chinese.
"""


TREND_ANALYSIS_PROMPT = """Based on the following collection of papers, identify the top 3-5 trending research directions:

{papers_summary}

For each trend, provide:
1. Brief description (1-2 sentences)
2. Number of papers focusing on this area
3. Key papers representing this trend

Format as a bulleted list in Traditional Chinese.
"""


KEY_INSIGHTS_PROMPT = """Extract the most important insights from this collection of research papers:

{papers_summary}

Provide 5-7 key insights that would be valuable for:
- Researchers in this field
- Graduate students
- Industry practitioners

Each insight should be:
- Actionable or thought-provoking
- Supported by evidence from the papers
- Clearly articulated in 1-2 sentences

Use Traditional Chinese.
"""


RECOMMENDATION_PROMPT = """From this collection of papers, recommend the top 5 most impactful papers for readers to prioritize:

{papers_summary}

For each recommendation, provide:
1. Paper title and authors
2. Why it's important (1-2 sentences)
3. Target audience (who should read this)

Rank by impact and relevance. Use Traditional Chinese.
"""


COMPARATIVE_ANALYSIS_PROMPT = """Compare and contrast the following research papers on similar topics:

{papers_summary}

Analysis should include:
1. Similarities in approach or findings
2. Key differences or disagreements
3. Complementary insights
4. Gaps or questions remaining

Use Traditional Chinese. Structure as a coherent narrative, not just bullet points.
"""


def get_academic_prompt(prompt_type: str, **kwargs) -> str:
    """
    Get a formatted academic prompt
    
    Args:
        prompt_type: Type of prompt (system, summary, trends, insights, etc.)
        **kwargs: Variables to format into the prompt
        
    Returns:
        Formatted prompt string
    """
    prompts = {
        "system": ACADEMIC_SYSTEM_PROMPT,
        "summary": PAPER_SUMMARY_PROMPT,
        "trends": TREND_ANALYSIS_PROMPT,
        "insights": KEY_INSIGHTS_PROMPT,
        "recommendation": RECOMMENDATION_PROMPT,
        "comparative": COMPARATIVE_ANALYSIS_PROMPT
    }
    
    prompt = prompts.get(prompt_type, "")
    return prompt.format(**kwargs) if kwargs else prompt