"""
Ariba Agent — Mock Ariba SLP submission and DocuSign pack generation.
Simulates the final hand-off of a validated vendor record to Centrica's
procurement systems. No real Ariba or DocuSign connection is made.
"""

import random
import string
from datetime import date, timedelta
from utils.gemini_client import generate_json


def _generate_ref() -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"VND-{date.today().year}-{suffix}"


def run(vendor_info: dict, agent_results: dict) -> dict:
    """
    Builds and 'submits' a vendor record to mock Ariba SLP.
    Returns a submission receipt with reference numbers.
    """
    name = vendor_info.get("company_name", "Unknown")
    industry = vendor_info.get("industry", "general")
    size = vendor_info.get("size", "small")
    kyc = agent_results.get("kyc", {})
    risk = agent_results.get("risk", {})

    ariba_ref = _generate_ref()
    docusign_ref = f"DS-{_generate_ref()[4:]}"
    payment_days = risk.get("recommended_payment_terms_days", 30)

    prompt = (
        f"Generate a realistic Ariba SLP vendor registration confirmation for a company "
        f"called '{name}' (industry: {industry.replace('_', ' ')}, size: {size}). "
        f"Return JSON with: "
        f"ariba_vendor_id (format: 'AV-' + 7 digits), "
        f"supplier_portal_url (fake ariba URL like 'https://service.ariba.com/Supplier.aw/...'), "
        f"category_codes (list of 2-3 UNSPSC category codes relevant to the industry as strings), "
        f"approved_spend_categories (list of 2-3 short category names), "
        f"preferred_currency ('GBP'), "
        f"tax_jurisdiction ('United Kingdom'), "
        f"onboarding_analyst ('Procurement Automation – ARIA'), "
        f"sap_vendor_number (format: 7 digits as string)."
    )
    fallback = {
        "ariba_vendor_id": f"AV-{random.randint(1000000, 9999999)}",
        "supplier_portal_url": "https://service.ariba.com/Supplier.aw/ad/negotiationList",
        "category_codes": ["81110000", "81111500"],
        "approved_spend_categories": ["IT Services", "Consultancy"],
        "preferred_currency": "GBP",
        "tax_jurisdiction": "United Kingdom",
        "onboarding_analyst": "Procurement Automation – ARIA",
        "sap_vendor_number": f"{random.randint(1000000, 9999999)}",
    }

    ariba_data = generate_json(prompt, fallback)

    submission_date = date.today()
    go_live_date = submission_date + timedelta(days=2)

    result = {
        "ariba_reference": ariba_ref,
        "docusign_reference": docusign_ref,
        "submission_timestamp": submission_date.isoformat() + "T09:34:17Z",
        "status": "REGISTERED",
        "go_live_date": go_live_date.isoformat(),
        "payment_terms_days": payment_days,
        "vendor_name_in_ariba": name,
        **ariba_data,
        "docusign_pack_contents": [
            "Vendor Registration Form (signed)",
            "KYC Verification Certificate",
            "AML Screening Report",
            "Risk Assessment Summary",
            "Payment Terms Confirmation",
            "Centrica Supplier Code of Conduct (countersigned)",
        ],
        "docusign_status": "Sent for signature",
        "next_steps": [
            f"DocuSign pack sent to {vendor_info.get('contact_email', 'procurement@supplier.com')}",
            f"Vendor live in Ariba SLP on {go_live_date.strftime('%d %B %Y')}",
            f"Payment terms: {payment_days} days from invoice date",
            "Annual re-verification scheduled automatically",
        ],
        "_agent": "Ariba Agent",
        "_status": "submitted",
    }

    return result
