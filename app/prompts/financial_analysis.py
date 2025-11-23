"""
Prompt templates for financial news analysis and investment insights
"""

FINANCIAL_SYSTEM_PROMPT = """You are an expert financial analyst specializing in market analysis and investment research.

Your task is to analyze news articles and market data to generate comprehensive investment insights.

Guidelines:
1. Maintain objectivity while providing actionable insights
2. Identify market trends and sentiment shifts
3. Assess potential impacts on relevant companies and sectors
4. Highlight both opportunities and risks
5. Consider supply chain and industry dynamics
6. Provide evidence-based analysis
7. Use Traditional Chinese for the report

Report Structure:
- Market Summary (市場概況)
- Key Developments (重要動態)
- Sentiment Analysis (情緒分析)
- Company/Sector Impact (公司影響)
- Risk Factors (風險因素)
- Investment Implications (投資啟示)
"""


SENTIMENT_ANALYSIS_PROMPT = """Analyze the overall market sentiment from these news articles:

{articles_summary}

Provide:
1. Overall sentiment (Bullish/Bearish/Neutral)
2. Confidence level (0-100%)
3. Key factors driving the sentiment
4. Sentiment breakdown by company/topic if applicable

Use Traditional Chinese. Be specific and evidence-based.
"""


COMPANY_IMPACT_PROMPT = """Analyze the potential impact on {company_name} based on these news articles:

{articles_summary}

Assessment should include:
1. Direct impacts (mentioned explicitly)
2. Indirect impacts (supply chain, competition, regulations)
3. Short-term vs Long-term implications
4. Magnitude of impact (High/Medium/Low)

Use Traditional Chinese. Provide balanced analysis.
"""


RISK_ASSESSMENT_PROMPT = """Identify key risk factors from the following market news:

{articles_summary}

For each risk factor, provide:
1. Description of the risk
2. Potential impact magnitude
3. Affected companies/sectors
4. Mitigation strategies or considerations

Prioritize by importance. Use Traditional Chinese.
"""


OPPORTUNITY_ANALYSIS_PROMPT = """Identify investment opportunities based on these market developments:

{articles_summary}

For each opportunity, specify:
1. Nature of the opportunity
2. Timeframe (short/medium/long-term)
3. Companies or sectors that could benefit
4. Key catalysts to watch

Use Traditional Chinese. Be specific and actionable.
"""


SUPPLY_CHAIN_ANALYSIS_PROMPT = """Analyze supply chain implications from these news articles:

{articles_summary}

Focus on:
1. Upstream impacts (suppliers, raw materials)
2. Downstream impacts (customers, end-markets)
3. Bottlenecks or constraints
4. Companies positioned to benefit/suffer

Use Traditional Chinese. Think systematically about the value chain.
"""


COMPETITIVE_LANDSCAPE_PROMPT = """Analyze the competitive dynamics based on this news:

{articles_summary}

Assessment should cover:
1. Market share shifts
2. New competitive threats or advantages
3. Strategic moves (M&A, partnerships, products)
4. Winners and losers

Use Traditional Chinese. Provide strategic insights.
"""


MACRO_TRENDS_PROMPT = """Identify broader macro trends from these market developments:

{articles_summary}

Consider:
1. Economic trends (growth, inflation, policy)
2. Technological shifts
3. Regulatory changes
4. Geopolitical factors

Link trends to specific investment implications. Use Traditional Chinese.
"""


def get_financial_prompt(prompt_type: str, **kwargs) -> str:
    """
    Get a formatted financial analysis prompt
    
    Args:
        prompt_type: Type of prompt (system, sentiment, impact, etc.)
        **kwargs: Variables to format into the prompt
        
    Returns:
        Formatted prompt string
    """
    prompts = {
        "system": FINANCIAL_SYSTEM_PROMPT,
        "sentiment": SENTIMENT_ANALYSIS_PROMPT,
        "impact": COMPANY_IMPACT_PROMPT,
        "risk": RISK_ASSESSMENT_PROMPT,
        "opportunity": OPPORTUNITY_ANALYSIS_PROMPT,
        "supply_chain": SUPPLY_CHAIN_ANALYSIS_PROMPT,
        "competitive": COMPETITIVE_LANDSCAPE_PROMPT,
        "macro": MACRO_TRENDS_PROMPT
    }
    
    prompt = prompts.get(prompt_type, "")
    return prompt.format(**kwargs) if kwargs else prompt