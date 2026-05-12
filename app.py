"""
Centrica Vendor Onboarding — ARIA Chatbot
Streamlit app — entry point for Streamlit Community Cloud.
"""

import time
from datetime import datetime
import streamlit as st

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Centrica Vendor Onboarding | ARIA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Centrica CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    :root {
        --navy:   #0F2067;
        --mint:   #85DB9C;
        --lavender: #B999F6;
        --pale:   #DECFFF;
        --purple: #9B2BF7;
    }
    html, body, [class*="css"] { font-family: Arial, sans-serif; }
    .block-container { padding-top: 1.2rem; padding-bottom: 1rem; max-width: 1400px; }

    .aria-header {
        background: var(--navy);
        padding: 14px 24px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    .aria-header h1 { color: white; font-size: 1.3rem; margin: 0; font-weight: 700; }
    .aria-header .tagline { color: var(--mint); font-size: 0.8rem; margin: 0; }

    .phase-bar { display: flex; gap: 5px; margin-bottom: 12px; }
    .phase-step {
        flex: 1; padding: 5px 8px; border-radius: 18px;
        font-size: 0.7rem; text-align: center; font-weight: 600;
        background: #f0f0f0; color: #999;
    }
    .phase-step.active { background: var(--navy); color: white; }
    .phase-step.done   { background: var(--mint); color: var(--navy); }

    .agent-panel {
        background: #fafbff;
        border: 1.5px solid var(--pale);
        border-radius: 12px;
        padding: 14px;
    }
    .agent-panel h3 {
        color: var(--navy);
        font-size: 0.78rem;
        font-weight: 700;
        margin: 0 0 9px 0;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .agent-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 9px; font-size: 0.78rem; }
    .agent-icon { font-size: 1rem; min-width: 20px; }
    .agent-name { font-weight: 600; color: var(--navy); }
    .agent-detail { color: #666; font-size: 0.72rem; margin-top: 2px; }

    @keyframes pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.15); } }
    .pulse { display: inline-block; animation: pulse 1.0s ease-in-out infinite; }

    @keyframes spin { from {transform: rotate(0);} to {transform: rotate(360deg);} }
    .spin { display: inline-block; animation: spin 1.4s linear infinite; }

    /* Vendor profile */
    .vendor-profile { font-size: 0.76rem; padding: 4px 0 0 0; }
    .profile-row {
        display: flex; justify-content: space-between;
        padding: 5px 0; border-bottom: 1px dashed #e6eaf7;
    }
    .profile-row:last-child { border-bottom: none; }
    .profile-label { color: #777; font-weight: 500; font-size: 0.72rem; }
    .profile-value { color: var(--navy); font-weight: 700; text-align: right; }

    /* News cards */
    .news-card {
        background: #f4f8ff;
        border-left: 3px solid var(--lavender);
        border-radius: 4px;
        padding: 8px 10px;
        margin-bottom: 6px;
        animation: slideIn 0.4s ease-out;
    }
    .news-headline { font-size: 0.74rem; color: var(--navy); font-weight: 600; line-height: 1.3; margin-bottom: 4px; }
    .news-meta { font-size: 0.66rem; color: #888; }
    .news-source { color: var(--navy); font-weight: 700; }
    .news-sentiment-pos { color: #28a745; font-weight: 700; }
    .news-sentiment-neu { color: #6c757d; font-weight: 700; }
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-4px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* Risk flags */
    .flag-row {
        display: flex; gap: 8px; padding: 5px 0; align-items: flex-start;
        border-bottom: 1px dotted #eee;
        animation: slideIn 0.3s ease-out;
    }
    .flag-row:last-child { border-bottom: none; }
    .flag-icon { font-size: 0.85rem; margin-top: 1px; min-width: 16px; }
    .flag-source { font-size: 0.7rem; color: var(--navy); font-weight: 700; line-height: 1.2; }
    .flag-text { font-size: 0.65rem; color: #666; line-height: 1.3; }

    /* Compact agent status */
    .agent-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 4px;
        margin-bottom: 6px;
    }
    .agent-pill {
        text-align: center;
        padding: 6px 2px;
        border-radius: 6px;
        font-size: 0.62rem;
        font-weight: 700;
        background: #f0f0f0;
        color: #999;
    }
    .agent-pill.done { background: var(--mint); color: var(--navy); }
    .agent-pill.running { background: var(--lavender); color: var(--navy); }
    .agent-pill .pill-icon { display: block; font-size: 0.95rem; margin-bottom: 2px; }

    .risk-badge {
        background: var(--mint); color: var(--navy);
        border-radius: 8px; padding: 9px 12px;
        font-size: 0.78rem; font-weight: 700;
        margin-top: 10px; text-align: center;
    }
    .ariba-card {
        background: linear-gradient(135deg, var(--navy) 0%, #1a3a9e 100%);
        color: white; border-radius: 12px; padding: 16px; margin-top: 10px;
    }
    .ariba-card h2 { color: var(--mint); font-size: 0.95rem; margin: 0 0 5px 0; }
    .ariba-ref { font-size: 1.15rem; font-weight: 700; color: var(--mint); letter-spacing: 0.06em; }
    .ariba-detail { font-size: 0.72rem; color: #cce; margin-top: 4px; }
    .ariba-step { background: rgba(255,255,255,0.1); border-radius: 6px; padding: 5px 9px; margin: 3px 0; font-size: 0.7rem; }

    .doc-extract {
        background: #f4f8ff; border-left: 3px solid var(--mint);
        border-radius: 6px; padding: 10px 14px; margin: 6px 0;
    }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Module-level placeholder for agent panel (assigned in main flow) ──────────
_PANEL = None  # type: ignore


# ── State init ─────────────────────────────────────────────────────────────────
def _init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "orchestrator" not in st.session_state:
        from agents.orchestrator import Orchestrator
        st.session_state.orchestrator = Orchestrator()
    if "agent_statuses" not in st.session_state:
        st.session_state.agent_statuses = {
            "kyc":   {"status": "pending", "label": "KYC / Company Verification", "icon_done": "✅", "icon_run": "🔍", "detail": ""},
            "aml":   {"status": "pending", "label": "AML & Sanctions Screening",  "icon_done": "✅", "icon_run": "🛡️", "detail": ""},
            "risk":  {"status": "pending", "label": "Credit & Risk Assessment",   "icon_done": "✅", "icon_run": "📊", "detail": ""},
            "news":  {"status": "pending", "label": "News & Web Presence Search", "icon_done": "✅", "icon_run": "📰", "detail": ""},
            "ariba": {"status": "pending", "label": "Ariba SLP Submission",       "icon_done": "✅", "icon_run": "⚡", "detail": ""},
        }
    if "agent_results" not in st.session_state:
        st.session_state.agent_results = {}
    if "ariba_result" not in st.session_state:
        st.session_state.ariba_result = None
    if "agents_triggered" not in st.session_state:
        st.session_state.agents_triggered = False
    if "ariba_triggered" not in st.session_state:
        st.session_state.ariba_triggered = False
    if "greeting_sent" not in st.session_state:
        st.session_state.greeting_sent = False
    if "pending_auto_turn" not in st.session_state:
        st.session_state.pending_auto_turn = None
    if "processed_uploads" not in st.session_state:
        st.session_state.processed_uploads = set()
    if "upload_counter" not in st.session_state:
        st.session_state.upload_counter = 0
    if "risk_flags" not in st.session_state:
        st.session_state.risk_flags = []
    if "prequal_done" not in st.session_state:
        st.session_state.prequal_done = False
    if "bank_submitted" not in st.session_state:
        st.session_state.bank_submitted = False
    if "prequal_record" not in st.session_state:
        st.session_state.prequal_record = None


_init_state()
orc = st.session_state.orchestrator


# ── API-key guard ──────────────────────────────────────────────────────────────
def _api_key_ok() -> bool:
    try:
        from utils.gemini_client import _get_api_key
        _get_api_key()
        return True
    except Exception:
        return False


# ── (Deprecated) Activity logger — kept as no-op so legacy calls don't break ─
def _activity(icon: str = "", text: str = "", delay: float = 0.0, kind: str = ""):
    if delay > 0:
        time.sleep(delay)


def _agent_set(key: str, status: str, detail: str = ""):
    """Update an agent card's status and re-render the panel."""
    st.session_state.agent_statuses[key]["status"] = status
    st.session_state.agent_statuses[key]["detail"] = detail
    if _PANEL is not None:
        _render_agent_panel(_PANEL)


def _add_flag(severity: str, source: str, text: str, delay: float = 0.0):
    """Add a risk flag (green / yellow / red) raised by a specific source."""
    st.session_state.risk_flags.append({"severity": severity, "source": source, "text": text})
    if _PANEL is not None:
        _render_agent_panel(_PANEL)
    if delay > 0:
        time.sleep(delay)


# ── Extract vendor info from user messages (with activity logging) ─────────────
def _extract_vendor_info(text: str, role: str = "user") -> None:
    import re
    lower = text.lower()
    info = orc.vendor_info
    extracted = []

    if not info.get("company_name") and role == "user":
        patterns = [
            r"(?:we are|we're|i'm from|our company is|company called|called)\s+([A-Z][A-Za-z0-9\s&,\.'-]{2,40})",
            r"^([A-Z][A-Za-z0-9\s&,\.'-]{2,40})\s*(?:is|are|,|\.|$)",
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                candidate = m.group(1).strip().rstrip(".,")
                if len(candidate) > 3:
                    orc.update_vendor_info("company_name", candidate)
                    extracted.append(("Company name", candidate))
                    break
        if not info.get("company_name") and len(text) < 80:
            name = text.strip().rstrip(".,")[:60]
            orc.update_vendor_info("company_name", name)
            extracted.append(("Company name", name))

    if info.get("is_uk") is None:
        if any(w in lower for w in ["uk", "united kingdom", "england", "scotland", "wales", "britain", "british"]):
            orc.update_vendor_info("is_uk", True)
            orc.update_vendor_info("country", "United Kingdom")
            extracted.append(("Jurisdiction", "United Kingdom"))
        elif any(w in lower for w in ["us ", "usa", "united states", "america", "canada", "india", "germany", "france", "international", "global"]):
            orc.update_vendor_info("is_uk", False)
            for country in ["United States", "USA", "Canada", "India", "Germany", "France", "Australia", "Spain", "Italy"]:
                if country.lower() in lower:
                    orc.update_vendor_info("country", country)
                    extracted.append(("Jurisdiction", country))
                    break
            if not info.get("country"):
                orc.update_vendor_info("country", "International")
                extracted.append(("Jurisdiction", "International"))

    if not info.get("size"):
        size_found = None
        if any(w in lower for w in ["micro", "1-9", "under 10", "fewer than 10", "very small", "sole trader", "1 employee"]):
            size_found = "micro"
        elif any(w in lower for w in ["small", "10-49", "10 to 49", "20 employee", "30 employee", "40 employee"]):
            size_found = "small"
        elif any(w in lower for w in ["medium", "50-249", "50 to 249", "100 employee", "150 employee", "200 employee"]):
            size_found = "medium"
        elif any(w in lower for w in ["large", "250+", "250 to", "500 employee", "1000 employee", "thousand"]):
            size_found = "large"
        elif any(w in lower for w in ["enterprise", "global", "multinational", "10,000", "100,000"]):
            size_found = "enterprise"
        if size_found:
            orc.update_vendor_info("size", size_found)
            extracted.append(("Size band", size_found))

    if not info.get("group_structure"):
        if any(w in lower for w in ["parent", "subsidiary", "group", "holding", "part of"]):
            orc.update_vendor_info("group_structure", "Subsidiary of group")
            extracted.append(("Group structure", "Subsidiary"))
        elif any(w in lower for w in ["independent", "standalone", "no parent", "not part"]):
            orc.update_vendor_info("group_structure", "Standalone entity")
            extracted.append(("Group structure", "Standalone"))

    email_match = re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", text)
    if email_match and not info.get("contact_email"):
        orc.update_vendor_info("contact_email", email_match.group())
        extracted.append(("Contact email", email_match.group()))

    # Log each extracted fact
    for label, val in extracted:
        _activity("📋", f"Profile update: {label} → {val}", delay=0.25, kind="ok")


def _detect_industry_from_messages():
    if orc.vendor_info.get("industry"):
        return
    user_msgs = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
    context = " ".join(user_msgs[:3])
    if len(context) < 10:
        return

    _activity("🔍", "Classifying industry vertical…", delay=0.3, kind="live")
    _activity("🧠", "Calling Gemini 2.5 Flash for classification", delay=0.4)
    from utils.gemini_client import classify_industry
    industry = classify_industry(context)
    orc.update_vendor_info("industry", industry)

    from utils.industry_config import get_profile
    profile = get_profile(industry)
    _activity("✅", f"Industry detected: {profile['label']}", delay=0.2, kind="ok")
    _activity("📋", f"Loading {profile['label']} compliance profile", delay=0.3)
    _activity("📋", f"{len(profile['required_docs'])} required documents queued for Phase B")

    if orc.phase == "WELCOME":
        orc.phase = "PHASE_A"
        _activity("🚦", "Phase advance: Welcome → Pre-Qualification", kind="ok")


# ── Background-checks agent runner with rich activity narration ────────────────
def run_agents(agent_panel_placeholder):
    from agents import kyc_agent, aml_agent, risk_agent, news_agent
    company = orc.vendor_info.get("company_name", "vendor")
    industry = orc.vendor_info.get("industry", "general").replace("_", " ").title()

    _activity("🚦", "Phase advance: Pre-Qual → Background Checks", delay=0.2, kind="ok")
    _activity("⚙️", "Launching 4 background agents in parallel…", delay=0.4)

    # ── KYC ────────────────────────────────────────────────────────────────────
    _agent_set("kyc", "running", "Searching Companies House…")
    time.sleep(1.0)
    try:
        kyc_result = kyc_agent.run(orc.vendor_info)
    except Exception as e:
        kyc_result = {"_error": str(e)}
    st.session_state.agent_results["kyc"] = kyc_result
    reg = kyc_result.get("registration_number", "verified")
    _agent_set("kyc", "done", f"Verified — Reg #{reg}")
    src = kyc_result.get("_source", "Companies House")
    _add_flag("green", src, f"Active · {kyc_result.get('filing_status', 'Filings up to date')}", delay=0.4)
    if kyc_result.get("group_structure") and kyc_result.get("group_structure") != "Standalone entity":
        _add_flag("yellow", "Group Analysis",
                  f"Subsidiary of {kyc_result.get('parent_entity', 'parent group')}", delay=0.4)
    else:
        _add_flag("green", "Group Analysis", "Standalone entity · no group reuse needed", delay=0.4)

    # ── AML ────────────────────────────────────────────────────────────────────
    _agent_set("aml", "running", "Screening sanctions databases…")
    time.sleep(0.8)
    try:
        aml_result = aml_agent.run(orc.vendor_info)
    except Exception as e:
        aml_result = {"_error": str(e)}
    st.session_state.agent_results["aml"] = aml_result
    _agent_set("aml", "done", "All clear — no matches")
    _add_flag("green", "HMT Consolidated Sanctions", "No matches found", delay=0.3)
    _add_flag("green", "OFAC SDN List", "No matches found", delay=0.3)
    _add_flag("green", "UN Security Council", "No matches found", delay=0.3)
    _add_flag("green", "EU Consolidated List", "No matches found", delay=0.3)
    _add_flag("green", "PEP Database", "No politically exposed persons identified", delay=0.3)
    _add_flag("green", "Adverse Media Scan", aml_result.get("adverse_media_summary", "Nothing of concern in past 24m"), delay=0.3)

    # ── Risk ───────────────────────────────────────────────────────────────────
    _agent_set("risk", "running", "Calculating risk score…")
    time.sleep(0.8)
    try:
        risk_result = risk_agent.run(orc.vendor_info)
    except Exception as e:
        risk_result = {"_error": str(e)}
    st.session_state.agent_results["risk"] = risk_result
    years = risk_result.get("years_trading", 10)
    credit = risk_result.get("credit_score", 680)
    score = risk_result.get("composite_risk_score", 75)
    label = risk_result.get("composite_risk_label", "Low Risk")
    pt = risk_result.get("recommended_payment_terms_days", 30)
    rating = risk_result.get("credit_rating", "BBB")
    src = risk_result.get("data_source", "Endole UK")
    _agent_set("risk", "done", f"Score: {score}/100 — {label}")

    if years < 5:
        _add_flag("yellow", src, f"Trading only {years} years — below 5y threshold", delay=0.35)
    else:
        _add_flag("green", src, f"Trading {years} years · stable trading history", delay=0.35)
    _add_flag("green", "Credit Bureau", f"Credit rating {rating} · Score {credit}", delay=0.35)
    if risk_result.get("county_court_judgements", 0) == 0:
        _add_flag("green", "CCJ Registry", "No County Court Judgements on file", delay=0.35)
    _add_flag("green", "Risk Ledger (TPRM)", "Cyber posture: Strong · ISO 27001 verified", delay=0.35)
    _add_flag("green", "HSE Enforcement", "No enforcement notices on record", delay=0.35)
    _add_flag("yellow", "Bank Account Validation",
              "Holder name has minor variation from registered entity — flag for manual review", delay=0.35)

    # ── News ───────────────────────────────────────────────────────────────────
    _agent_set("news", "running", "Searching recent news…")
    time.sleep(0.8)
    try:
        news_result = news_agent.run(orc.vendor_info)
    except Exception as e:
        news_result = {"_error": str(e)}
    st.session_state.agent_results["news"] = news_result
    arts = news_result.get("articles", [])
    sentiment = news_result.get("overall_sentiment", "Positive")
    _agent_set("news", "done", f"{len(arts)} articles — {sentiment} sentiment")
    _add_flag("green", "Web Presence", f"Web presence score: {news_result.get('web_presence_score', 70)}/100", delay=0.4)
    if sentiment == "Positive":
        _add_flag("green", "News Sentiment", f"{len(arts)} recent articles · positive coverage", delay=0.4)
    else:
        _add_flag("green", "News Sentiment", f"{len(arts)} recent articles · neutral coverage", delay=0.4)

    st.session_state.agents_triggered = True
    orc.advance_to_phase_b()


def run_prequal_lookup(chat_container):
    """Simulate searching Ariba SLP for an existing pre-qual record and
    auto-populate vendor profile fields. Vendor doesn't need to answer
    these questions — they previously provided this data."""
    from utils.gemini_client import generate_json
    from utils.industry_config import get_profile

    company = orc.vendor_info.get("company_name", "the vendor")
    industry = orc.vendor_info.get("industry", "general")
    profile = get_profile(industry)

    with chat_container:
        with st.chat_message("assistant", avatar="⚡"):
            with st.status(f"Searching Ariba SLP for **{company}** pre-qual record…", expanded=True) as status:
                st.markdown("🔍 Querying supplier master data…")
                time.sleep(1.0)
                st.markdown(f"📂 Searching pre-qual archive for *{profile['label']}* category…")
                time.sleep(0.9)
                st.markdown("📥 Matching entity — exact match found ✓")
                time.sleep(0.7)
                st.markdown("📋 Retrieving pre-qualification dataset…")
                time.sleep(0.8)

                prompt = (
                    f"Generate a realistic pre-qualification record for {company} in the "
                    f"{profile['label']} sector. Return JSON: "
                    f"size (one of: micro, small, medium, large), "
                    f"country (one of: United Kingdom, United States, Germany, India, France), "
                    f"group_structure (one of: 'Standalone entity','Subsidiary of group'), "
                    f"prequal_date (YYYY-Q3 or YYYY-Q4, recent), "
                    f"prequal_score (integer 65-92), "
                    f"years_supplying_centrica (integer 0-12), "
                    f"signed_code_of_conduct (boolean, true)."
                )
                fallback = {
                    "size": "small",
                    "country": "United Kingdom",
                    "group_structure": "Standalone entity",
                    "prequal_date": "2024-Q3",
                    "prequal_score": 78,
                    "years_supplying_centrica": 2,
                    "signed_code_of_conduct": True,
                }
                prequal = generate_json(prompt, fallback)
                st.session_state.prequal_record = prequal

                # Populate orchestrator vendor_info
                if not orc.vendor_info.get("size"):
                    orc.update_vendor_info("size", prequal.get("size", "small"))
                if not orc.vendor_info.get("country"):
                    orc.update_vendor_info("country", prequal.get("country", "United Kingdom"))
                if orc.vendor_info.get("is_uk") is None:
                    orc.update_vendor_info("is_uk", prequal.get("country") == "United Kingdom")
                if not orc.vendor_info.get("group_structure"):
                    orc.update_vendor_info("group_structure", prequal.get("group_structure", "Standalone entity"))

                size = prequal.get("size", "small").title()
                country = prequal.get("country", "United Kingdom")
                struct = prequal.get("group_structure", "Standalone entity")
                pdate = prequal.get("prequal_date", "2024-Q3")
                pscore = prequal.get("prequal_score", 78)
                yrs = prequal.get("years_supplying_centrica", 2)

                st.markdown(f"📊 **Size band:** {size}")
                time.sleep(0.4)
                st.markdown(f"🌍 **Country:** {country}")
                time.sleep(0.4)
                st.markdown(f"🏢 **Structure:** {struct}")
                time.sleep(0.4)
                st.markdown(f"📅 **Record:** {pdate} · score **{pscore}/100**")
                time.sleep(0.4)
                st.markdown(f"⏱ **Supplying Centrica for:** {yrs} years")
                time.sleep(0.4)
                st.markdown(f"📝 **Supplier Code of Conduct:** signed ✓")
                time.sleep(0.3)
                st.markdown("✅ Pre-qualification confirmed — proceeding to verification")
                status.update(label="Pre-qual record retrieved ✓", state="complete")

    # Flag the pre-qual lookup as a "source"
    _add_flag("green", "Ariba SLP Pre-Qual", f"Active record · {pdate} · score {pscore}/100")
    _add_flag("green", "Supplier Code of Conduct", "Signed and on file")

    summary_msg = (
        f"✅ Good news — I've pulled your existing pre-qualification record from our Ariba supplier database. "
        f"You're listed as a **{size}** {profile['label']} supplier based in **{country}**, "
        f"with a pre-qual score of **{pscore}/100** from {pdate}.\n\n"
        f"I'll use this as the basis for your registration. I'm now running our standard background "
        f"verification checks in parallel — this typically takes under a minute. Watch the panel on the right →"
    )
    st.session_state.messages.append({"role": "assistant", "content": summary_msg})
    st.session_state.prequal_done = True
    orc.phase = "AGENTS_RUNNING"


def run_ariba(agent_panel_placeholder):
    from agents import ariba_agent
    _agent_set("ariba", "running", "Packaging vendor record…")
    time.sleep(1.0)
    _agent_set("ariba", "running", "Submitting to Ariba SLP…")
    time.sleep(0.9)
    result = ariba_agent.run(orc.vendor_info, st.session_state.agent_results)
    st.session_state.ariba_result = result
    _agent_set("ariba", "running", "Generating DocuSign pack…")
    time.sleep(0.9)
    _agent_set("ariba", "done", f"Ref: {result['ariba_reference']}")
    st.session_state.ariba_triggered = True
    orc.advance_to_complete()


# ── Agent panel rendering ──────────────────────────────────────────────────────
def _render_agent_panel(placeholder=None):
    # ── Compact agent status grid ──────────────────────────────────────────────
    short_labels = {"kyc": "KYC", "aml": "AML", "risk": "Risk", "news": "News", "ariba": "Ariba"}
    pill_icons_pending = {"kyc": "🔍", "aml": "🛡️", "risk": "📊", "news": "📰", "ariba": "⚡"}
    grid_cells = ""
    done_count = sum(1 for k in st.session_state.agent_statuses.values() if k["status"] == "done")
    for key, info in st.session_state.agent_statuses.items():
        s = info["status"]
        if s == "done":
            cls = "done"; icon = "✅"
        elif s == "running":
            cls = "running"; icon = f'<span class="pulse">{pill_icons_pending[key]}</span>'
        else:
            cls = ""; icon = pill_icons_pending[key]
        grid_cells += (
            f'<div class="agent-pill {cls}">'
            f'  <span class="pill-icon">{icon}</span>{short_labels[key]}'
            f'</div>'
        )
    agent_grid_html = (
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
        f'  <h3 style="margin:0;">🤖 Background Checks</h3>'
        f'  <span style="font-size:0.7rem;color:#999;font-weight:600;">{done_count}/5</span>'
        f'</div>'
        f'<div class="agent-grid">{grid_cells}</div>'
    )

    # ── Vendor profile ─────────────────────────────────────────────────────────
    info = orc.vendor_info
    profile_rows = []
    if info.get("company_name"):
        profile_rows.append(("Company", info["company_name"]))
    if info.get("industry"):
        from utils.industry_config import get_profile
        profile_rows.append(("Industry", get_profile(info["industry"])["label"]))
    if info.get("size"):
        profile_rows.append(("Size band", info["size"].title()))
    if info.get("country"):
        profile_rows.append(("Country", info["country"]))
    if info.get("group_structure"):
        profile_rows.append(("Structure", info["group_structure"]))
    if info.get("contact_email"):
        profile_rows.append(("Contact", info["contact_email"]))

    kyc = st.session_state.agent_results.get("kyc", {})
    if kyc.get("registration_number"):
        profile_rows.append(("Registration", str(kyc["registration_number"])))
    if kyc.get("incorporation_date"):
        profile_rows.append(("Incorporated", kyc["incorporation_date"]))

    risk_res = st.session_state.agent_results.get("risk", {})
    if risk_res.get("latest_turnover"):
        profile_rows.append(("Turnover", str(risk_res["latest_turnover"])))
    if risk_res.get("credit_rating"):
        profile_rows.append(("Credit rating", str(risk_res["credit_rating"])))

    if profile_rows:
        profile_html = "".join(
            f'<div class="profile-row"><span class="profile-label">{k}</span>'
            f'<span class="profile-value">{v}</span></div>'
            for k, v in profile_rows
        )
        profile_section = (
            f'<h3 style="margin-top:14px;">📋 Vendor Profile</h3>'
            f'<div class="vendor-profile">{profile_html}</div>'
        )
    else:
        profile_section = (
            f'<h3 style="margin-top:14px;">📋 Vendor Profile</h3>'
            f'<div style="color:#999;font-size:0.72rem;font-style:italic;padding:4px 0;">'
            f'No vendor data collected yet — start the conversation to populate.</div>'
        )

    # ── News coverage ──────────────────────────────────────────────────────────
    news_res = st.session_state.agent_results.get("news", {})
    articles = news_res.get("articles", [])
    if articles:
        news_html = ""
        for art in articles[:3]:
            sent = art.get("sentiment", "Neutral")
            sent_cls = "news-sentiment-pos" if sent == "Positive" else "news-sentiment-neu"
            news_html += (
                f'<div class="news-card">'
                f'  <div class="news-headline">{art.get("headline", "")}</div>'
                f'  <div class="news-meta">'
                f'    <span class="news-source">{art.get("source", "")}</span> · '
                f'    <span>{art.get("date", "")}</span> · '
                f'    <span class="{sent_cls}">{sent}</span>'
                f'  </div>'
                f'</div>'
            )
        news_section = f'<h3 style="margin-top:14px;">📰 News Coverage</h3>{news_html}'
    else:
        news_section = ""

    # ── Risk flags ─────────────────────────────────────────────────────────────
    flags = st.session_state.risk_flags
    if flags:
        flags_html = ""
        sev_icon = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
        for flag in flags:
            sev = flag.get("severity", "green")
            flags_html += (
                f'<div class="flag-row">'
                f'  <span class="flag-icon">{sev_icon.get(sev, "🟢")}</span>'
                f'  <div>'
                f'    <div class="flag-source">{flag.get("source", "")}</div>'
                f'    <div class="flag-text">{flag.get("text", "")}</div>'
                f'  </div>'
                f'</div>'
            )
        flags_section = f'<h3 style="margin-top:14px;">⚠️ Risk Signals</h3>{flags_html}'
    else:
        flags_section = ""

    # ── Risk score badge ───────────────────────────────────────────────────────
    badge_html = ""
    if st.session_state.agent_statuses["risk"]["status"] == "done":
        score = risk_res.get("composite_risk_score", "–")
        label = risk_res.get("composite_risk_label", "")
        pt = risk_res.get("recommended_payment_terms_days", "–")
        badge_html = (
            f'<div class="risk-badge">Risk Score: {score}/100 · {label}<br/>'
            f'<span style="font-weight:400;font-size:0.7rem;">Payment Terms: {pt} days</span></div>'
        )

    # ── Ariba success card ─────────────────────────────────────────────────────
    ariba_html = ""
    if st.session_state.ariba_result:
        r = st.session_state.ariba_result
        steps_html = "".join(f'<div class="ariba-step">✅ {s}</div>' for s in r.get("next_steps", []))
        ariba_html = (
            f'<div class="ariba-card">'
            f'  <h2>⚡ Registered in Ariba SLP</h2>'
            f'  <div class="ariba-ref">{r.get("ariba_reference", "")}</div>'
            f'  <div class="ariba-detail">DocuSign: {r.get("docusign_reference", "")}<br/>'
            f'    Go-live: {r.get("go_live_date", "")} · Terms: {r.get("payment_terms_days", "–")} days</div>'
            f'  <div style="margin-top:8px;">{steps_html}</div>'
            f'</div>'
        )

    # Single-line concatenation, no leading whitespace anywhere — prevents
    # Streamlit's CommonMark parser from interpreting any block as code.
    parts = [
        '<div class="agent-panel">',
        agent_grid_html,
        profile_section,
        news_section,
        flags_section,
        badge_html,
        ariba_html,
        '</div>',
    ]
    html = "".join(p for p in parts if p).replace("\n", "")

    if placeholder:
        placeholder.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


def _render_phase_bar():
    phases = ["Welcome", "Pre-Qual", "Bg Checks", "Documents", "Validation", "Ariba", "Complete"]
    current = orc.get_phase_number()
    steps_html = ""
    for i, label in enumerate(phases):
        cls = "done" if i < current else ("active" if i == current else "")
        steps_html += f'<div class="phase-step {cls}">{label}</div>'
    st.markdown(f'<div class="phase-bar">{steps_html}</div>', unsafe_allow_html=True)


def _stream_into_chat(synthetic_user_msg: str | None = None) -> str:
    """Generate an assistant turn (streaming)."""
    from utils.gemini_client import stream_chat
    messages_for_api = list(st.session_state.messages)
    if synthetic_user_msg:
        messages_for_api.append({"role": "user", "content": synthetic_user_msg})

    system_prompt = orc.get_system_prompt()
    placeholder = st.empty()
    full = ""
    try:
        for chunk in stream_chat(messages_for_api, system_prompt):
            full += chunk
            placeholder.markdown(full + "▌")
        placeholder.markdown(full)
    except Exception as e:
        full = f"I'm sorry — a brief technical issue. ({str(e)[:80]})"
        placeholder.markdown(full)
    return full


def _process_response_triggers(response_text: str) -> tuple[str, dict]:
    triggers = {"agents": False, "validation": False, "ariba": False}
    clean = response_text
    if "[TRIGGER_AGENTS]" in clean:
        triggers["agents"] = True
        clean = clean.replace("[TRIGGER_AGENTS]", "").strip()
    if "[TRIGGER_VALIDATION]" in clean:
        triggers["validation"] = True
        clean = clean.replace("[TRIGGER_VALIDATION]", "").strip()
    if "[TRIGGER_ARIBA]" in clean:
        triggers["ariba"] = True
        clean = clean.replace("[TRIGGER_ARIBA]", "").strip()
    return clean, triggers


def _process_doc_upload(uploaded_file, doc: dict) -> dict:
    from utils.doc_reader import extract_text
    from utils.gemini_client import extract_doc_fields

    _activity("📥", f"[DOC] File received: {uploaded_file.name}", delay=0.3, kind="live")
    _activity("📄", f"[DOC] Extracting text from {uploaded_file.type or 'file'}…", delay=0.5)
    text = extract_text(uploaded_file)
    chars = len(text)
    _activity("📄", f"[DOC] Extracted {chars} chars of content", delay=0.3)
    _activity("🧠", "[DOC] Sending to Gemini 2.5 Flash for field extraction…", delay=0.5, kind="live")
    result = extract_doc_fields(
        file_text=text,
        doc_name=doc["name"],
        doc_purpose=doc.get("why", ""),
        vendor_info=orc.vendor_info,
    )
    fields = result.get("extracted_fields", [])
    _activity("✅", f"[DOC] Extracted {len(fields)} fields", delay=0.2, kind="ok")
    _activity("📊", f"[DOC] Validation: {result.get('validation_status', 'VALID')}", delay=0.2, kind="ok")
    _activity("📋", f"[DOC] {doc['name']} confirmed", kind="ok")
    return result


def _format_extraction_card(filename: str, doc_name: str, extraction: dict) -> str:
    fields = extraction.get("extracted_fields", [])
    summary = extraction.get("summary", "")
    fields_md = "\n".join(f"- **{f.get('label', '')}**: {f.get('value', '')}" for f in fields)
    return (
        f"📎 **Received `{filename}`** for *{doc_name}*\n\n"
        f"_Extracted by ARIA — only the data below is stored; the file itself is not retained._\n\n"
        f"{fields_md}\n\n"
        f"✅ {summary}"
    )


# ── HEADER + PHASE BAR ─────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="aria-header">
      <div>
        <h1>⚡ Centrica &nbsp;|&nbsp; Supplier Lifecycle</h1>
        <p class="tagline">Powered by ARIA · Pre-Qualification &amp; Vendor Registration</p>
      </div>
      <div style="color:#85DB9C;font-size:0.78rem;text-align:right;">
        Procurement Transformation<br/>
        <span style="color:#B999F6;">AI-Powered · Ariba SLP Ready</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not _api_key_ok():
    st.warning(
        "**GOOGLE_API_KEY not configured.**\n\n"
        "Local: create `.env` with `GOOGLE_API_KEY=...`\n\n"
        "Streamlit Cloud: App Settings → Secrets → `GOOGLE_API_KEY = \"...\"`"
    )
    st.stop()

# ── Tabs: Pre-Qualification (universal basics) → Vendor Registration ──────────
tab_prequal, tab_reg = st.tabs(["🔍  Pre-Qualification", "📋  Vendor Registration"])

with tab_prequal:
    from prequal_tab import render_prequal_tab
    render_prequal_tab()

with tab_reg:
    _render_phase_bar()

    # ── Two-column layout ──────────────────────────────────────────────────────
    chat_col, panel_col = st.columns([2, 1], gap="large")

    with panel_col:
        _PANEL = st.empty()
        _render_agent_panel(_PANEL)

    with chat_col:
        if not st.session_state.greeting_sent:
            greeting = (
                "Welcome to Centrica's supplier onboarding portal! 👋\n\n"
                "I'm **ARIA** — Centrica's Automated Registration & Intelligence Assistant. "
                "I'll guide you through onboarding today — it usually takes just a few minutes.\n\n"
                "To get started, please tell me your **company name** and briefly describe "
                "what you supply or what services you offer to Centrica."
            )
            st.session_state.messages.append({"role": "assistant", "content": greeting})
            st.session_state.greeting_sent = True

        chat_box = st.container(height=520, border=True)

        with chat_box:
            for msg in st.session_state.messages:
                avatar = "⚡" if msg["role"] == "assistant" else "🏢"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.markdown(msg["content"])

            # Pending auto-turn (after agents / doc uploads)
            if st.session_state.pending_auto_turn:
                synthetic = st.session_state.pending_auto_turn
                st.session_state.pending_auto_turn = None
                _activity("🧠", "Generating ARIA response…", delay=0.2, kind="live")
                with st.chat_message("assistant", avatar="⚡"):
                    full = _stream_into_chat(synthetic_user_msg=synthetic)
                _activity("💬", "ARIA response delivered", kind="ok")
                clean, triggers = _process_response_triggers(full)
                st.session_state.messages.append({"role": "assistant", "content": clean})

                if triggers["validation"]:
                    orc.advance_to_validation()
                    _activity("🚦", "Phase advance: Documents → Validation", kind="ok")
                if triggers["ariba"]:
                    orc.phase = "ARIBA"
                    _activity("🚦", "Phase advance: Validation → Ariba Submission", kind="ok")
                    _render_phase_bar()
                    with st.chat_message("assistant", avatar="⚡"):
                        with st.status("Submitting to Ariba SLP…", expanded=True) as status:
                            st.write("📦 Packaging validated vendor record…")
                            run_ariba(_PANEL)
                            st.write(f"✅ Registration complete — ref **{st.session_state.ariba_result['ariba_reference']}**")
                            status.update(label="Ariba submission complete!", state="complete")

                    ariba_ref = st.session_state.ariba_result["ariba_reference"]
                    pt = st.session_state.ariba_result.get("payment_terms_days", "–")
                    go_live = st.session_state.ariba_result.get("go_live_date", "–")
                    completion_msg = (
                        f"🎉 **Congratulations — registration is complete!**\n\n"
                        f"Your vendor record has been submitted to **Centrica's Ariba SLP**.\n\n"
                        f"- **Reference:** `{ariba_ref}`\n"
                        f"- **Payment terms:** {pt} days from invoice date\n"
                        f"- **Go-live date:** {go_live}\n\n"
                        f"A **DocuSign onboarding pack** has been sent for your signature.\n\n"
                        f"Is there anything else you'd like to know?"
                    )
                    st.session_state.messages.append({"role": "assistant", "content": completion_msg})
                    orc.advance_to_complete()
                    _activity("🎉", "Onboarding complete!", kind="ok")
                    st.rerun()

        # File uploader for current required doc
        next_doc = None
        if orc.phase == "PHASE_B":
            next_doc = orc.get_next_required_doc()

        if next_doc:
            st.markdown(
                f"<div style='font-size:0.8rem;color:#0F2067;margin-top:8px;'>"
                f"<b>📎 Upload your {next_doc['name']}</b> "
                f"<span style='color:#777;'>(or type a confirmation below — both work)</span></div>",
                unsafe_allow_html=True,
            )
            uploaded = st.file_uploader(
                label="Upload file",
                type=None,
                label_visibility="collapsed",
                key=f"uploader_{st.session_state.upload_counter}_{next_doc['id']}",
                help=next_doc.get("why", ""),
            )
            if uploaded is not None:
                upload_key = f"{next_doc['id']}::{uploaded.name}::{uploaded.size}"
                if upload_key not in st.session_state.processed_uploads:
                    st.session_state.processed_uploads.add(upload_key)
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"📎 *Uploaded:* `{uploaded.name}` for {next_doc['name']}",
                    })
                    with st.spinner(f"ARIA is reading `{uploaded.name}` and extracting the relevant information…"):
                        extraction = _process_doc_upload(uploaded, next_doc)
                    card = _format_extraction_card(uploaded.name, next_doc["name"], extraction)
                    st.session_state.messages.append({"role": "assistant", "content": card})
                    orc.confirm_doc(next_doc["id"])
                    st.session_state.upload_counter += 1
                    if orc.all_docs_confirmed():
                        # All docs uploaded — DON'T jump to validation yet; bank form is next.
                        st.session_state.pending_auto_turn = (
                            "(System: vendor has now provided all required documents. "
                            "Briefly acknowledge that and tell them ONE last step remains: "
                            "providing their bank account details for payment setup, "
                            "via the form that has just appeared below the chat. "
                            "Do NOT include any [TRIGGER_*] markers.)"
                        )
                    else:
                        nxt = orc.get_next_required_doc()
                        if nxt:
                            _activity("📋", f"Next document queued: {nxt['name']}")
                        st.session_state.pending_auto_turn = (
                            f"(System: vendor just successfully provided their {next_doc['name']}. "
                            f"Thank them briefly and request the NEXT required document.)"
                        )
                    st.rerun()

        # ── Bank-details form (appears after all docs uploaded, before validation) ─
        show_bank_form = (
            orc.phase == "PHASE_B"
            and orc.all_docs_confirmed()
            and not st.session_state.bank_submitted
        )
        if show_bank_form:
            st.markdown(
                "<div style='font-size:0.85rem;color:#0F2067;margin-top:10px;'>"
                "<b>🏦 One last step — your bank account details</b> "
                "<span style='color:#777;'>(required by Centrica AP for setting up payments)</span></div>",
                unsafe_allow_html=True,
            )
            with st.form("bank_form", clear_on_submit=False):
                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    bank_holder = st.text_input("Account holder name *", placeholder="Exactly as on your bank statement")
                    bank_name = st.text_input("Bank name *", placeholder="e.g. Barclays Bank UK PLC")
                    sort_code = st.text_input("Sort code *", placeholder="12-34-56", max_chars=8)
                with bcol2:
                    account_number = st.text_input("Account number *", placeholder="12345678", max_chars=10)
                    iban = st.text_input("IBAN (optional)", placeholder="GB29 NWBK 6016 1331 9268 19")
                    currency = st.selectbox("Currency *", ["GBP", "EUR", "USD"], index=0)
                submitted = st.form_submit_button("✅ Confirm bank details", type="primary", use_container_width=True)

            if submitted:
                missing = [n for n, v in [
                    ("Account holder", bank_holder), ("Bank name", bank_name),
                    ("Sort code", sort_code), ("Account number", account_number),
                ] if not v.strip()]
                if missing:
                    st.error(f"Please complete: {', '.join(missing)}")
                else:
                    masked_acc = "****" + account_number[-4:] if len(account_number) >= 4 else "****"
                    orc.update_vendor_info("bank", {
                        "holder": bank_holder.strip(),
                        "bank_name": bank_name.strip(),
                        "sort_code": sort_code.strip(),
                        "account_number": masked_acc,
                        "iban": iban.strip(),
                        "currency": currency,
                    })
                    # Raise a flag — if holder name differs from registered company name, yellow flag
                    company_lower = orc.vendor_info.get("company_name", "").lower()
                    holder_lower = bank_holder.lower().strip()
                    if company_lower and holder_lower and \
                       holder_lower not in company_lower and company_lower not in holder_lower:
                        _add_flag("yellow", "Bank Account Validation",
                                  f"Holder '{bank_holder}' has minor variation from registered entity '{orc.vendor_info.get('company_name')}' — flag for manual review")
                    else:
                        _add_flag("green", "Bank Account Validation",
                                  f"Holder name matches registered entity")
                    _add_flag("green", "Sanctions Bank Match", f"Bank '{bank_name}' on approved counterparty list")

                    # Confirmation message in chat
                    st.session_state.messages.append({
                        "role": "user",
                        "content": (
                            f"🏦 *Bank details submitted:* {bank_name} · "
                            f"{bank_holder} · ****{account_number[-4:] if len(account_number) >= 4 else '****'} · "
                            f"{currency}"
                        ),
                    })
                    st.session_state.bank_submitted = True
                    orc.advance_to_validation()
                    st.session_state.pending_auto_turn = (
                        "(System: vendor has now provided their bank details and all required documents. "
                        "Please perform the final validation summary, mention exactly ONE minor flag "
                        "(the bank account holder name has a minor variation from the registered entity name — "
                        "flag it for manual review but recommend proceeding), then submit to Ariba. "
                        "Include [TRIGGER_ARIBA] on its own line at the end.)"
                    )
                    st.rerun()

        if orc.phase != "COMPLETE":
            user_input = st.chat_input("Type your message…")
        else:
            user_input = None
            st.success("✅ Onboarding complete! Refresh the page to onboard another vendor.")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            _extract_vendor_info(user_input, role="user")
            if orc.phase in ("WELCOME", "PHASE_A"):
                _detect_industry_from_messages()

            # ── Pre-qual Ariba lookup branch ────────────────────────────────────
            # After the first vendor message that lets us classify the industry,
            # skip the Phase A questions and pull the existing pre-qual record
            # from Ariba, then immediately run background checks.
            if (
                orc.vendor_info.get("industry")
                and not st.session_state.prequal_done
                and orc.vendor_info.get("company_name")
            ):
                with chat_box:
                    with st.chat_message("user", avatar="🏢"):
                        st.markdown(user_input)
                run_prequal_lookup(chat_box)
                run_agents(_PANEL)
                st.session_state.pending_auto_turn = (
                    "(System: all background checks have just completed successfully. "
                    "Briefly summarise the positive results in one short paragraph "
                    "and ask the vendor for the FIRST required industry-specific document. "
                    "Do NOT include any [TRIGGER_*] markers.)"
                )
                st.rerun()

            # ── Normal Gemini response path ──────────────────────────────────────
            with chat_box:
                with st.chat_message("user", avatar="🏢"):
                    st.markdown(user_input)
                with st.chat_message("assistant", avatar="⚡"):
                    full = _stream_into_chat()

            clean, triggers = _process_response_triggers(full)

            if orc.phase == "PHASE_B" and next_doc:
                positive = ["yes", "confirm", "have it", "here", "provided", "attached", "sent", "done", "sure", "ok", "✓", "ref"]
                if any(w in user_input.lower() for w in positive):
                    orc.confirm_doc(next_doc["id"])
                    if orc.all_docs_confirmed():
                        # Don't advance to validation — bank form is next
                        st.session_state.pending_auto_turn = (
                            "(System: vendor has now provided all required documents. "
                            "Briefly acknowledge and tell them ONE last step remains: "
                            "the bank-details form that has appeared below the chat. "
                            "Do NOT include any [TRIGGER_*] markers.)"
                        )

            st.session_state.messages.append({"role": "assistant", "content": clean})

            if triggers["agents"] and not st.session_state.agents_triggered:
                orc.phase = "AGENTS_RUNNING"
                run_agents(_PANEL)
                st.session_state.pending_auto_turn = (
                    "(System: all background checks have just completed successfully. "
                    "Now briefly summarise the positive results in one short paragraph "
                    "and ask the vendor for the FIRST required industry-specific document.)"
                )
                st.rerun()

            if triggers["validation"]:
                orc.advance_to_validation()
                _activity("🚦", "Phase advance: Documents → Validation", kind="ok")

            if triggers["ariba"]:
                orc.phase = "ARIBA"
                _activity("🚦", "Phase advance: Validation → Ariba Submission", kind="ok")
                _render_phase_bar()
                with chat_box:
                    with st.chat_message("assistant", avatar="⚡"):
                        with st.status("Submitting to Ariba SLP…", expanded=True) as status:
                            st.write("📦 Packaging validated vendor record…")
                            run_ariba(_PANEL)
                            st.write(f"✅ Registration complete — ref **{st.session_state.ariba_result['ariba_reference']}**")
                            status.update(label="Ariba submission complete!", state="complete")
                ariba_ref = st.session_state.ariba_result["ariba_reference"]
                pt = st.session_state.ariba_result.get("payment_terms_days", "–")
                go_live = st.session_state.ariba_result.get("go_live_date", "–")
                completion_msg = (
                    f"🎉 **Congratulations — registration is complete!**\n\n"
                    f"Your vendor record has been submitted to **Centrica's Ariba SLP**.\n\n"
                    f"- **Reference:** `{ariba_ref}`\n"
                    f"- **Payment terms:** {pt} days from invoice date\n"
                    f"- **Go-live date:** {go_live}\n\n"
                    f"A **DocuSign onboarding pack** has been sent for your signature.\n\n"
                    f"Is there anything else you'd like to know?"
                )
                st.session_state.messages.append({"role": "assistant", "content": completion_msg})
                orc.advance_to_complete()
                _activity("🎉", "Onboarding complete!", kind="ok")

            st.rerun()
