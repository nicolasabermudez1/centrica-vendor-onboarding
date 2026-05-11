"""
KYC Agent — Companies House / international equivalent lookup.
All data is Gemini-generated and contextually realistic for the given vendor.
"""

import random
from datetime import date, timedelta
from utils.gemini_client import generate_json


def run(vendor_info: dict) -> dict:
    """
    Returns a mock KYC record for the vendor.
    vendor_info keys used: company_name, industry, is_uk (bool), size
    """
    name = vendor_info.get("company_name", "Unknown Company")
    industry = vendor_info.get("industry", "general")
    is_uk = vendor_info.get("is_uk", True)
    size = vendor_info.get("size", "small")

    if is_uk:
        prompt = (
            f"Generate a realistic UK Companies House record for a {size} {industry.replace('_', ' ')} "
            f"company called '{name}'. Return JSON with these exact keys: "
            f"registration_number (format: 8 digits), incorporation_date (YYYY-MM-DD, between 2005-2023), "
            f"registered_address (plausible UK address), directors (list of 2 full names), "
            f"sic_code (realistic SIC code as string), sic_description (matching description), "
            f"filing_status (one of: 'Up to date', 'Up to date'), "
            f"company_status ('Active'), share_capital (realistic GBP figure as string)."
        )
        fallback = {
            "registration_number": f"{random.randint(10000000, 99999999)}",
            "incorporation_date": "2015-03-12",
            "registered_address": "14 Moorgate, London, EC2R 6DA",
            "directors": ["Sarah Thompson", "James Caldwell"],
            "sic_code": "62020",
            "sic_description": "Information technology consultancy activities",
            "filing_status": "Up to date",
            "company_status": "Active",
            "share_capital": "£100,000",
        }
        source = "Companies House"
    else:
        country = vendor_info.get("country", "United States")
        prompt = (
            f"Generate a realistic {country} business registry record for a {size} "
            f"{industry.replace('_', ' ')} company called '{name}'. Return JSON with: "
            f"registration_number, incorporation_date (YYYY-MM-DD), registered_address, "
            f"directors (list of 2 full names), entity_type ('Corporation' or 'LLC'), "
            f"registry_status ('Active'), annual_revenue_usd (realistic figure as string)."
        )
        fallback = {
            "registration_number": f"US-{random.randint(1000000, 9999999)}",
            "incorporation_date": "2012-07-18",
            "registered_address": "1440 Broadway, New York, NY 10018, USA",
            "directors": ["Michael Chen", "Laura Reyes"],
            "entity_type": "Corporation",
            "registry_status": "Active",
            "annual_revenue_usd": "$4,200,000",
        }
        source = f"{country} Business Registry"

    data = generate_json(prompt, fallback)
    data["_source"] = source
    data["_status"] = "verified"
    data["_agent"] = "KYC Agent"

    # Derive a group/parent if company name suggests it
    if any(word in name.lower() for word in ["ltd", "limited", "plc", "inc", "corp"]):
        data["parent_entity"] = None
        data["group_structure"] = "Standalone entity"
    else:
        data["parent_entity"] = f"{name.split()[0]} Holdings Ltd" if name.split() else None
        data["group_structure"] = "Subsidiary" if data["parent_entity"] else "Standalone entity"

    return data
