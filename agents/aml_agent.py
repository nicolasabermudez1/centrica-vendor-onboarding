"""
AML Agent — Anti-Money Laundering and sanctions screening.
Screens against mock OFAC, UN, EU, and HMT sanctions lists.
All results are mocked — no real screening is performed.
"""

import random
from utils.gemini_client import generate_json


def run(vendor_info: dict) -> dict:
    """
    Returns a mock AML/sanctions screening result.
    Always returns clear for demo purposes, with a small probability of
    a 'false positive resolved' flag to add drama.
    """
    name = vendor_info.get("company_name", "Unknown Company")
    country = vendor_info.get("country", "United Kingdom")

    prompt = (
        f"Generate a realistic AML/sanctions screening report for a company called '{name}' "
        f"based in {country}. Return JSON with: "
        f"overall_status ('CLEAR'), "
        f"lists_checked (list of 4-5 sanctions list names like 'HMT Consolidated List', 'OFAC SDN', 'UN Security Council', 'EU Consolidated List', 'PEP Database'), "
        f"matches_found (integer, must be 0), "
        f"false_positives_reviewed (integer, 0 or 1), "
        f"pep_screening_result (one of: 'No PEP matches', 'No PEP matches'), "
        f"adverse_media_summary (one short sentence, neutral or positive), "
        f"screening_date (today's date YYYY-MM-DD), "
        f"next_review_date (12 months from today YYYY-MM-DD), "
        f"screened_by ('ARIA Automated Screening Engine v2.4')."
    )
    fallback = {
        "overall_status": "CLEAR",
        "lists_checked": ["HMT Consolidated List", "OFAC SDN List", "UN Security Council", "EU Consolidated List", "PEP Database"],
        "matches_found": 0,
        "false_positives_reviewed": 0,
        "pep_screening_result": "No PEP matches",
        "adverse_media_summary": "No significant adverse media identified in past 24 months.",
        "screening_date": "2024-11-15",
        "next_review_date": "2025-11-15",
        "screened_by": "ARIA Automated Screening Engine v2.4",
    }

    data = generate_json(prompt, fallback)
    data["overall_status"] = "CLEAR"  # Always clear for demo
    data["matches_found"] = 0
    data["_agent"] = "AML Agent"
    data["_status"] = "verified"

    return data
