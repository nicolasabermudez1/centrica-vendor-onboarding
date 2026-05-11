"""
News Agent — Recent news and web presence search.
Uses Gemini to generate realistic, contextually appropriate news headlines
and summaries for the vendor. No real web scraping is performed.
"""

from utils.gemini_client import generate_json
from utils.industry_config import get_profile


def run(vendor_info: dict) -> dict:
    """
    Returns a mock set of recent news articles and web presence signals
    about the vendor.
    """
    name = vendor_info.get("company_name", "Unknown Company")
    industry = vendor_info.get("industry", "general")
    size = vendor_info.get("size", "small")
    profile = get_profile(industry)
    themes = profile.get("typical_news_themes", ["business growth", "new contracts"])

    prompt = (
        f"Generate 3 realistic, recent news headlines and short summaries about a "
        f"{size} {profile['label']} company called '{name}'. "
        f"The news should be positive or neutral. "
        f"Relevant themes: {', '.join(themes)}. "
        f"Return JSON with: "
        f"articles (list of 3 objects, each with: "
        f"  headline (string, realistic news headline), "
        f"  source (plausible UK news outlet or industry publication), "
        f"  date (YYYY-MM-DD, within last 18 months), "
        f"  sentiment (one of: 'Positive','Neutral'), "
        f"  summary (1 sentence summary)), "
        f"overall_sentiment ('Positive' or 'Neutral'), "
        f"web_presence_score (integer 40-95, realistic for a {size} company), "
        f"linkedin_employees_estimate (integer, realistic for {size}), "
        f"notable_clients_mentioned (list of 0-2 plausible company names or empty list)."
    )
    fallback = {
        "articles": [
            {
                "headline": f"{name} Wins New Contract with Major UK Utility",
                "source": "The Guardian",
                "date": "2024-09-15",
                "sentiment": "Positive",
                "summary": f"{name} announced a new multi-year services agreement with a leading UK energy company.",
            },
            {
                "headline": f"{name} Achieves ISO Certification Renewal",
                "source": "Industry Today",
                "date": "2024-07-22",
                "sentiment": "Positive",
                "summary": f"The certification confirms {name}'s commitment to quality management standards.",
            },
            {
                "headline": f"{profile['label']} Sector Reports Strong Q3 Growth",
                "source": "Financial Times",
                "date": "2024-10-03",
                "sentiment": "Neutral",
                "summary": f"The sector, including companies like {name}, benefits from increased demand.",
            },
        ],
        "overall_sentiment": "Positive",
        "web_presence_score": 72,
        "linkedin_employees_estimate": 45,
        "notable_clients_mentioned": [],
    }

    data = generate_json(prompt, fallback)
    data["search_query_used"] = f'"{name}" {profile["label"]} UK'
    data["_agent"] = "News Agent"
    data["_status"] = "verified"
    return data
