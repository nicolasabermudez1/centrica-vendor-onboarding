"""
Industry profiles: required documents, agent checks, and Gemini prompt hints
per vendor category detected from the opening conversation.
"""

INDUSTRY_PROFILES = {
    "financial_services": {
        "label": "Financial Services",
        "emoji": "🏦",
        "description": "banks, insurance, investment management, fintech, payment processors",
        "required_docs": [
            {
                "id": "fca_reg",
                "name": "FCA Registration Number",
                "description": "Your Financial Conduct Authority registration number (if applicable)",
                "why": "Centrica is required to verify that all financial service suppliers are properly regulated by the FCA.",
            },
            {
                "id": "aml_policy",
                "name": "Anti-Money Laundering (AML) Policy",
                "description": "Your current AML policy document",
                "why": "UK regulations require us to confirm all suppliers have documented AML controls in place.",
            },
            {
                "id": "audited_accounts",
                "name": "Last 3 Years' Audited Accounts",
                "description": "Signed audited financial statements for the past 3 financial years",
                "why": "We assess financial stability to ensure continuity of service.",
            },
            {
                "id": "pii_policy",
                "name": "PII / Data Handling Policy",
                "description": "Your policy for handling personally identifiable information",
                "why": "You may process customer or employee data on our behalf, so we must verify GDPR compliance.",
            },
        ],
        "risk_areas": ["regulatory compliance", "financial stability", "data protection"],
        "typical_news_themes": ["regulatory updates", "market performance", "compliance milestones"],
    },
    "construction": {
        "label": "Construction & Engineering",
        "emoji": "🏗️",
        "description": "construction, civil engineering, building services, facilities management",
        "required_docs": [
            {
                "id": "cis_reg",
                "name": "CIS Registration",
                "description": "HMRC Construction Industry Scheme registration number",
                "why": "CIS registration is mandatory for all contractors working under Centrica's construction supply chain.",
            },
            {
                "id": "hs_policy",
                "name": "Health & Safety Policy",
                "description": "Your current H&S policy, signed by a director",
                "why": "We are required under CDM 2015 to verify that all contractors have adequate H&S management.",
            },
            {
                "id": "public_liability",
                "name": "Public Liability Insurance ≥£5M",
                "description": "Certificate of public liability insurance (minimum £5 million cover)",
                "why": "Centrica's minimum insurance requirement for on-site contractors is £5M public liability.",
            },
            {
                "id": "chas_cert",
                "name": "CHAS / SSIP Certification",
                "description": "Contractors Health and Safety Assessment Scheme or equivalent SSIP-member cert",
                "why": "CHAS/SSIP pre-qualifies your H&S standards and removes the need for repeated assessments.",
            },
        ],
        "risk_areas": ["health & safety", "CIS compliance", "insurance adequacy"],
        "typical_news_themes": ["project completions", "safety awards", "industry certifications"],
    },
    "maritime": {
        "label": "Maritime & Marine Services",
        "emoji": "⚓",
        "description": "boat maintenance, marine engineering, port services, vessel operations, offshore, waterway services",
        "required_docs": [
            {
                "id": "mca_cert",
                "name": "MCA Certification",
                "description": "Maritime & Coastguard Agency certification or equivalent flag state certification",
                "why": "All marine service providers operating in UK waters must hold valid MCA certification.",
            },
            {
                "id": "vessel_reg",
                "name": "Vessel Registration Documents",
                "description": "Registration documents for all vessels involved in Centrica service delivery",
                "why": "We need to record the vessels that will be operating under our contract for insurance and safety purposes.",
            },
            {
                "id": "stcw_license",
                "name": "Captain / Officer STCW Licenses",
                "description": "STCW (Standards of Training, Certification and Watchkeeping) certificates for all vessel operators",
                "why": "STCW compliance is a legal requirement for all personnel operating commercial vessels.",
            },
            {
                "id": "maritime_safety",
                "name": "Maritime Safety Certificate",
                "description": "Current safety management certificate (ISM Code compliance)",
                "why": "ISM Code compliance demonstrates your safety management system meets international standards.",
            },
        ],
        "risk_areas": ["vessel safety", "crew certification", "environmental compliance"],
        "typical_news_themes": ["offshore projects", "safety inspections", "environmental initiatives"],
    },
    "it_technology": {
        "label": "IT & Technology",
        "emoji": "💻",
        "description": "software, IT services, cloud, cybersecurity, data analytics, digital transformation",
        "required_docs": [
            {
                "id": "iso27001",
                "name": "ISO 27001 or SOC 2 Certification",
                "description": "Current ISO 27001 certificate or SOC 2 Type II audit report",
                "why": "Centrica's IT security policy requires all technology suppliers to hold recognised information security certifications.",
            },
            {
                "id": "pen_test",
                "name": "Penetration Test Report (<12 months)",
                "description": "Executive summary of your most recent third-party penetration test",
                "why": "We require evidence of regular security testing for any supplier handling our systems or data.",
            },
            {
                "id": "dpa",
                "name": "Data Processing Agreement (DPA)",
                "description": "A signed DPA covering GDPR Article 28 requirements",
                "why": "As a data processor, you must have a compliant DPA in place before handling any Centrica personal data.",
            },
            {
                "id": "bcdr",
                "name": "Business Continuity & DR Plan",
                "description": "Summary of your BC/DR procedures and last test date",
                "why": "We assess resilience to ensure continuity of critical IT services.",
            },
        ],
        "risk_areas": ["cybersecurity", "data protection", "service continuity"],
        "typical_news_themes": ["product launches", "security certifications", "partnerships"],
    },
    "energy_utilities": {
        "label": "Energy & Utilities",
        "emoji": "⚡",
        "description": "energy generation, renewables, grid services, metering, utilities infrastructure",
        "required_docs": [
            {
                "id": "ofgem_license",
                "name": "Ofgem Licence / Exemption",
                "description": "Your Ofgem supply or generation licence number, or exemption certificate",
                "why": "All energy suppliers and generators must be licensed or exempted by Ofgem to operate in the UK.",
            },
            {
                "id": "env_compliance",
                "name": "Environmental Compliance Certificate",
                "description": "Evidence of compliance with Environment Agency permits (EA permit number)",
                "why": "Centrica's sustainability policy requires all energy suppliers to demonstrate environmental compliance.",
            },
            {
                "id": "grid_agreement",
                "name": "Grid Connection Agreement",
                "description": "Copy of your grid connection agreement with National Grid or DNO",
                "why": "Required to verify your authorised connection points for service delivery.",
            },
        ],
        "risk_areas": ["regulatory compliance", "environmental impact", "grid stability"],
        "typical_news_themes": ["capacity contracts", "renewable projects", "ofgem decisions"],
    },
    "logistics_transport": {
        "label": "Logistics & Transport",
        "emoji": "🚚",
        "description": "logistics, freight, haulage, courier, fleet management, transport services",
        "required_docs": [
            {
                "id": "operator_license",
                "name": "Operator Licence",
                "description": "DVSA standard or restricted operator licence",
                "why": "UK law requires all commercial vehicle operators to hold a valid operator licence.",
            },
            {
                "id": "driver_cpc",
                "name": "Driver CPC Cards",
                "description": "List of all drivers with their Driver CPC qualification card numbers",
                "why": "Driver CPC is a legal requirement for all professional HGV and LGV drivers in the UK.",
            },
            {
                "id": "fleet_insurance",
                "name": "Fleet Insurance Certificate",
                "description": "Certificate of insurance covering all vehicles used in Centrica service delivery",
                "why": "We require evidence of adequate fleet insurance before vehicles operate on our behalf.",
            },
            {
                "id": "dvsa_compliance",
                "name": "DVSA Compliance Report",
                "description": "Your latest DVSA compliance score or OCRS (Operator Compliance Risk Score)",
                "why": "OCRS gives us visibility of your compliance history with DVSA traffic commissioners.",
            },
        ],
        "risk_areas": ["road safety", "driver compliance", "fleet management"],
        "typical_news_themes": ["fleet expansions", "sustainability initiatives", "route optimisations"],
    },
    "healthcare": {
        "label": "Healthcare & Life Sciences",
        "emoji": "🏥",
        "description": "healthcare, medical devices, pharmaceuticals, occupational health, wellbeing services",
        "required_docs": [
            {
                "id": "cqc_reg",
                "name": "CQC Registration",
                "description": "Care Quality Commission registration number and current rating",
                "why": "Any healthcare service provider engaged by Centrica must be registered with the CQC.",
            },
            {
                "id": "dbs_policy",
                "name": "DBS Checking Policy",
                "description": "Your policy for conducting enhanced DBS checks on staff",
                "why": "Staff may interact with vulnerable employees; we require evidence of appropriate background checking.",
            },
            {
                "id": "clinical_governance",
                "name": "Clinical Governance Framework",
                "description": "Summary of your clinical governance structure and named clinical lead",
                "why": "Centrica requires a documented governance framework for all clinical services.",
            },
        ],
        "risk_areas": ["patient safety", "data sensitivity", "regulatory standing"],
        "typical_news_themes": ["CQC inspections", "service expansions", "clinical partnerships"],
    },
    "professional_services": {
        "label": "Professional Services",
        "emoji": "💼",
        "description": "consulting, legal, accounting, recruitment, training, HR services, advisory",
        "required_docs": [
            {
                "id": "pi_insurance",
                "name": "Professional Indemnity Insurance ≥£2M",
                "description": "Certificate of professional indemnity insurance (minimum £2 million cover)",
                "why": "Centrica requires a minimum of £2M PI cover for all professional advisory suppliers.",
            },
            {
                "id": "reg_membership",
                "name": "Regulatory Body Membership",
                "description": "Evidence of membership with the relevant professional body (e.g., SRA, ICAEW, APSCo)",
                "why": "We verify regulatory standing to ensure all professional services meet the required standards of conduct.",
            },
            {
                "id": "conflict_policy",
                "name": "Conflict of Interest Policy",
                "description": "Your documented policy for identifying and managing conflicts of interest",
                "why": "Professional advisors must have a conflict of interest policy to protect Centrica's commercial interests.",
            },
        ],
        "risk_areas": ["professional liability", "regulatory standing", "conflict of interest"],
        "typical_news_themes": ["new partnerships", "industry rankings", "thought leadership"],
    },
    "general": {
        "label": "General Supply",
        "emoji": "📦",
        "description": "general goods, office supplies, facilities, catering, print, events",
        "required_docs": [
            {
                "id": "bank_details",
                "name": "Bank Account Verification",
                "description": "A bank letter or voided cheque confirming your company bank account details",
                "why": "We verify bank account details to prevent payment fraud and ensure correct remittance.",
            },
            {
                "id": "vat_cert",
                "name": "VAT Registration Certificate",
                "description": "Your HMRC VAT registration certificate (if VAT registered)",
                "why": "Required for correct VAT treatment of invoices under UK tax law.",
            },
            {
                "id": "companies_house",
                "name": "Companies House Confirmation",
                "description": "Confirmation of your registered company number and registered address",
                "why": "We verify legal entity details against Companies House to prevent fraud.",
            },
        ],
        "risk_areas": ["payment accuracy", "tax compliance", "entity verification"],
        "typical_news_themes": ["business growth", "new contracts", "awards"],
    },
}

# Keywords used for simple rule-based fallback (Gemini handles the primary detection)
INDUSTRY_KEYWORDS = {
    "financial_services": ["bank", "financ", "insurance", "invest", "fintech", "payment", "credit", "loan", "fund", "asset"],
    "construction": ["construct", "build", "civil", "engineer", "contractor", "facilities", "install", "demolit", "scaffold"],
    "maritime": ["marine", "maritime", "boat", "vessel", "ship", "offshore", "port", "harbour", "captain", "crew", "nautical", "water"],
    "it_technology": ["software", "tech", "digital", "cloud", "cyber", "data", "it service", "saas", "platform", "develop", "ai ", "machine learning"],
    "energy_utilities": ["energy", "power", "solar", "wind", "renewable", "grid", "utility", "electric", "gas supply", "meter", "ofgem"],
    "logistics_transport": ["logistics", "transport", "freight", "haulage", "courier", "delivery", "fleet", "distribution", "warehouse"],
    "healthcare": ["health", "medical", "clinical", "pharmacy", "nhs", "wellbeing", "occupational health", "care", "life science"],
    "professional_services": ["consult", "legal", "law firm", "accountan", "recruit", "training", "hr service", "advisory", "audit firm"],
}


def detect_industry_fallback(text: str) -> str:
    """Simple keyword-based industry detection as fallback if Gemini is unavailable."""
    text_lower = text.lower()
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return industry
    return "general"


def get_profile(industry: str) -> dict:
    return INDUSTRY_PROFILES.get(industry, INDUSTRY_PROFILES["general"])
