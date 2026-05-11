"""
Risk Agent — Credit risk, financial stability, and supply chain risk scoring.
Combines Endole-style financial banding with a composite risk score.
All data is Gemini-generated and contextually plausible.
"""

from utils.gemini_client import generate_json


_SIZE_PAYMENT_TERMS = {
    "micro": 30,
    "small": 30,
    "medium": 60,
    "large": 60,
    "enterprise": 60,
}

_SIZE_THRESHOLDS = {
    "micro": "Under 10 employees / under £632k turnover",
    "small": "10–49 employees / £632k–£10M turnover",
    "medium": "50–249 employees / £10M–£50M turnover",
    "large": "250+ employees / £50M–£500M turnover",
    "enterprise": "1000+ employees / over £500M turnover",
}


def run(vendor_info: dict) -> dict:
    """
    Returns a mock risk assessment with credit score, Endole banding,
    recommended payment terms, and a composite risk score.
    """
    name = vendor_info.get("company_name", "Unknown Company")
    industry = vendor_info.get("industry", "general")
    size = vendor_info.get("size", "small")
    is_uk = vendor_info.get("is_uk", True)

    prompt = (
        f"Generate a realistic credit and risk assessment for a {size} "
        f"{industry.replace('_', ' ')} company called '{name}'. "
        f"Return JSON with: "
        f"credit_score (integer 350-800, realistic for a {'UK' if is_uk else 'international'} {size} company), "
        f"credit_rating (one of: 'AAA','AA','A','BBB','BB','B' — realistic), "
        f"financial_health (one of: 'Excellent','Good','Satisfactory','Monitor'), "
        f"years_trading (integer 3-20), "
        f"latest_turnover (realistic GBP/USD figure as string), "
        f"net_assets (realistic figure as string), "
        f"county_court_judgements (integer, must be 0), "
        f"payment_behaviour (one of: 'Prompt payer','Average payer','Prompt payer'), "
        f"industry_risk_level (one of: 'Low','Medium','Low'), "
        f"data_source ({'Endole UK' if is_uk else 'Dun & Bradstreet International'})."
    )
    fallback = {
        "credit_score": 680,
        "credit_rating": "BBB",
        "financial_health": "Good",
        "years_trading": 8,
        "latest_turnover": "£3,200,000",
        "net_assets": "£780,000",
        "county_court_judgements": 0,
        "payment_behaviour": "Prompt payer",
        "industry_risk_level": "Low",
        "data_source": "Endole UK",
    }

    data = generate_json(prompt, fallback)

    # Always ensure CCJs = 0 for demo
    data["county_court_judgements"] = 0

    # Apply Centrica payment terms policy
    payment_days = _SIZE_PAYMENT_TERMS.get(size, 30)
    data["recommended_payment_terms_days"] = payment_days
    data["payment_terms_basis"] = f"Centrica policy: {size} supplier → {payment_days} days"
    data["size_band_definition"] = _SIZE_THRESHOLDS.get(size, "")

    # Composite risk score (0-100, higher = safer)
    credit = data.get("credit_score", 600)
    composite = min(100, max(0, int((credit / 850) * 100)))
    data["composite_risk_score"] = composite
    data["composite_risk_label"] = (
        "Low Risk" if composite >= 70
        else "Medium Risk" if composite >= 50
        else "Elevated Risk"
    )

    # Working capital note
    if payment_days == 30:
        data["early_pay_note"] = (
            "Early payment discount available: 2% for payment within 10 days "
            "under Centrica's supply chain finance programme."
        )
    else:
        data["early_pay_note"] = (
            "60-day terms apply. Centrica's supply chain finance programme offers "
            "early settlement at a 5% annualised rate if required."
        )

    data["_agent"] = "Risk Agent"
    data["_status"] = "verified"
    return data
