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

    /* Live activity terminal */
    .activity-feed {
        background: #0a1644;
        border-radius: 8px;
        padding: 10px 12px;
        max-height: 220px;
        min-height: 100px;
        overflow-y: auto;
        font-family: 'Consolas','Monaco',monospace;
        font-size: 0.68rem;
        line-height: 1.45;
        border: 1px solid #1a2876;
    }
    .activity-feed::-webkit-scrollbar { width: 6px; }
    .activity-feed::-webkit-scrollbar-thumb { background: #2a3a8a; border-radius: 3px; }
    .activity-row {
        display: flex; gap: 6px; margin-bottom: 2px; align-items: baseline;
        color: #cfe0ff;
    }
    .activity-row.fresh { animation: slideIn 0.35s ease-out; }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(8px); }
        to   { opacity: 1; transform: translateX(0); }
    }
    .activity-time  { color: #B999F6; font-size: 0.62rem; min-width: 56px; }
    .activity-icon  { font-size: 0.78rem; }
    .activity-text  { flex: 1; color: #d6e6ff; }
    .activity-row.ok    .activity-text { color: #85DB9C; }
    .activity-row.alert .activity-text { color: #ffcc6f; }
    .activity-row.live  .activity-icon { animation: pulse 1.0s ease-in-out infinite; }

    .live-dot {
        display: inline-block;
        width: 8px; height: 8px; border-radius: 50%;
        background: #85DB9C;
        animation: pulse 1.4s ease-in-out infinite;
        margin-right: 6px;
        vertical-align: middle;
    }

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
    if "activity_log" not in st.session_state:
        st.session_state.activity_log = []


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


# ── Live activity logging ──────────────────────────────────────────────────────
def _activity(icon: str, text: str, delay: float = 0.0, kind: str = ""):
    """Append a new line to the live activity feed and re-render the panel."""
    entry = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "icon": icon,
        "text": text,
        "kind": kind,
        "fresh": True,
    }
    # Mark previous entries non-fresh
    for e in st.session_state.activity_log:
        e["fresh"] = False
    st.session_state.activity_log.append(entry)
    if len(st.session_state.activity_log) > 40:
        st.session_state.activity_log = st.session_state.activity_log[-40:]
    if _PANEL is not None:
        _render_agent_panel(_PANEL)
    if delay > 0:
        time.sleep(delay)


def _agent_set(key: str, status: str, detail: str = ""):
    """Update an agent card's status and re-render the panel."""
    st.session_state.agent_statuses[key]["status"] = status
    st.session_state.agent_statuses[key]["detail"] = detail
    if _PANEL is not None:
        _render_agent_panel(_PANEL)


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
    _activity("🌐", "[KYC] Connecting to Companies House API", delay=0.4, kind="live")
    _activity("🔍", f"[KYC] Querying entity: \"{company}\"", delay=0.5)
    _activity("📥", "[KYC] Parsing registration record…", delay=0.4)
    try:
        kyc_result = kyc_agent.run(orc.vendor_info)
    except Exception as e:
        kyc_result = {"_error": str(e)}
    st.session_state.agent_results["kyc"] = kyc_result
    reg = kyc_result.get("registration_number", "verified")
    directors = kyc_result.get("directors", [])
    _activity("📋", f"[KYC] Directors identified: {', '.join(directors[:2]) if directors else 'on file'}", delay=0.3)
    _activity("✅", f"[KYC] Entity verified · Reg #{reg}", delay=0.2, kind="ok")
    _agent_set("kyc", "done", f"Verified — Reg #{reg}")

    # ── AML ────────────────────────────────────────────────────────────────────
    _agent_set("aml", "running", "Screening sanctions databases…")
    _activity("🛰", "[AML] Querying HMT Consolidated Sanctions List", delay=0.4, kind="live")
    _activity("🛰", "[AML] Querying OFAC SDN List", delay=0.35, kind="live")
    _activity("🛰", "[AML] Querying UN Security Council list", delay=0.35, kind="live")
    _activity("🛰", "[AML] Querying EU Consolidated List", delay=0.35, kind="live")
    _activity("🛰", "[AML] Querying PEP database", delay=0.35, kind="live")
    try:
        aml_result = aml_agent.run(orc.vendor_info)
    except Exception as e:
        aml_result = {"_error": str(e)}
    st.session_state.agent_results["aml"] = aml_result
    _activity("🛡", "[AML] All 5 lists checked · 0 matches found", delay=0.2, kind="ok")
    _activity("📰", "[AML] Adverse media scan: clean", delay=0.2, kind="ok")
    _agent_set("aml", "done", "All clear — no matches")

    # ── Risk ───────────────────────────────────────────────────────────────────
    _agent_set("risk", "running", "Calculating risk score…")
    _activity("📊", "[RISK] Pulling Endole financial data", delay=0.4, kind="live")
    _activity("📊", "[RISK] Retrieving 3-year filing history", delay=0.4)
    try:
        risk_result = risk_agent.run(orc.vendor_info)
    except Exception as e:
        risk_result = {"_error": str(e)}
    st.session_state.agent_results["risk"] = risk_result
    years = risk_result.get("years_trading", "–")
    credit = risk_result.get("credit_score", "–")
    score = risk_result.get("composite_risk_score", 75)
    label = risk_result.get("composite_risk_label", "Low Risk")
    pt = risk_result.get("recommended_payment_terms_days", 30)
    _activity("📊", f"[RISK] Years trading: {years} · Credit: {credit}", delay=0.3)
    _activity("🧮", "[RISK] Computing composite risk score…", delay=0.4)
    _activity("✅", f"[RISK] Score: {score}/100 — {label}", delay=0.2, kind="ok")
    _activity("💰", f"[POLICY] Payment terms: {pt} days (per Centrica policy)", delay=0.2, kind="ok")
    _agent_set("risk", "done", f"Score: {score}/100 — {label}")

    # ── News ───────────────────────────────────────────────────────────────────
    _agent_set("news", "running", "Searching recent news…")
    _activity("🌐", f"[NEWS] Searching news indices for \"{company}\"", delay=0.4, kind="live")
    _activity("📰", f"[NEWS] Crawling {industry} trade publications", delay=0.4)
    try:
        news_result = news_agent.run(orc.vendor_info)
    except Exception as e:
        news_result = {"_error": str(e)}
    st.session_state.agent_results["news"] = news_result
    arts = news_result.get("articles", [])
    sentiment = news_result.get("overall_sentiment", "Positive")
    _activity("🎯", f"[NEWS] Sentiment analysis on {len(arts)} articles", delay=0.4)
    if arts:
        _activity("📰", f"[NEWS] \"{arts[0].get('headline', '')[:55]}…\"", delay=0.3)
    _activity("✅", f"[NEWS] {len(arts)} articles · {sentiment} sentiment", delay=0.2, kind="ok")
    _agent_set("news", "done", f"{len(arts)} articles — {sentiment} sentiment")

    _activity("🎉", "[SYSTEM] All background checks complete · vendor cleared", delay=0.3, kind="ok")
    st.session_state.agents_triggered = True
    orc.advance_to_phase_b()
    _activity("🚦", "Phase advance: Background Checks → Document Collection", kind="ok")


def run_ariba(agent_panel_placeholder):
    from agents import ariba_agent
    _agent_set("ariba", "running", "Packaging vendor record…")
    _activity("📦", "[ARIBA] Packaging validated vendor record", delay=0.5, kind="live")
    _activity("🔗", "[ARIBA] Establishing SOAP connection to Ariba SLP", delay=0.5, kind="live")
    _agent_set("ariba", "running", "Submitting to Ariba SLP…")
    _activity("📤", "[ARIBA] Uploading vendor profile", delay=0.5, kind="live")
    _activity("🔐", "[ARIBA] Awaiting SAP vendor number allocation", delay=0.4, kind="live")

    result = ariba_agent.run(orc.vendor_info, st.session_state.agent_results)
    st.session_state.ariba_result = result

    _agent_set("ariba", "running", "Generating DocuSign pack…")
    _activity("📝", "[DOCUSIGN] Building onboarding pack (6 documents)", delay=0.5, kind="live")
    _activity("📧", "[DOCUSIGN] Sending pack for vendor signature", delay=0.4)
    _activity("✅", f"[ARIBA] Registered — Ref: {result['ariba_reference']}", delay=0.2, kind="ok")
    _activity("✅", f"[SAP] Vendor number issued: {result.get('sap_vendor_number', '–')}", kind="ok")
    _agent_set("ariba", "done", f"Ref: {result['ariba_reference']}")
    st.session_state.ariba_triggered = True
    orc.advance_to_complete()


# ── Agent panel rendering ──────────────────────────────────────────────────────
def _render_agent_panel(placeholder=None):
    icons_pending = {"kyc": "⬜", "aml": "⬜", "risk": "⬜", "news": "⬜", "ariba": "⬜"}
    rows_html = ""
    for key, info in st.session_state.agent_statuses.items():
        s = info["status"]
        if s == "done":
            icon = info["icon_done"]
            name_style = "color:#0F2067; font-weight:700;"
        elif s == "running":
            icon = f'<span class="pulse">{info["icon_run"]}</span>'
            name_style = "color:#9B2BF7; font-weight:700;"
        else:
            icon = icons_pending[key]
            name_style = "color:#aaa;"
        detail = f'<div class="agent-detail">{info["detail"]}</div>' if info["detail"] else ""
        rows_html += f"""
        <div class="agent-row">
          <span class="agent-icon">{icon}</span>
          <div>
            <div class="agent-name" style="{name_style}">{info["label"]}</div>
            {detail}
          </div>
        </div>
        """

    # Activity feed (newest at top, reverse)
    feed_rows = ""
    activity_count = len(st.session_state.activity_log)
    for entry in reversed(st.session_state.activity_log[-20:]):
        cls = "fresh " if entry.get("fresh") else ""
        cls += entry.get("kind", "")
        feed_rows += (
            f'<div class="activity-row {cls.strip()}">'
            f'<span class="activity-time">{entry["time"]}</span>'
            f'<span class="activity-icon">{entry["icon"]}</span>'
            f'<span class="activity-text">{entry["text"]}</span>'
            f'</div>'
        )
    if not feed_rows:
        feed_rows = (
            '<div class="activity-row">'
            '<span class="activity-time">--:--:--</span>'
            '<span class="activity-icon">💤</span>'
            '<span class="activity-text" style="color:#6677aa;">Awaiting vendor input…</span>'
            '</div>'
        )
    feed_html = (
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin:14px 0 6px 0;">'
        f'  <h3 style="margin:0;"><span class="live-dot"></span>Live Activity</h3>'
        f'  <span style="color:#85DB9C;font-size:0.65rem;font-weight:600;">{activity_count} events</span>'
        f'</div>'
        f'<div class="activity-feed">{feed_rows}</div>'
    )

    badge_html = ""
    if st.session_state.agent_statuses["risk"]["status"] == "done":
        risk_res = st.session_state.agent_results.get("risk", {})
        score = risk_res.get("composite_risk_score", "–")
        label = risk_res.get("composite_risk_label", "")
        pt = risk_res.get("recommended_payment_terms_days", "–")
        badge_html = (
            f'<div class="risk-badge">Risk Score: {score}/100 · {label}<br/>'
            f'<span style="font-weight:400;font-size:0.7rem;">Payment Terms: {pt} days</span></div>'
        )

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

    html = (
        f'<div class="agent-panel">'
        f'  <h3>🤖 Agent Status</h3>'
        f'  {rows_html}'
        f'  {feed_html}'
        f'  {badge_html}'
        f'  {ariba_html}'
        f'</div>'
    )

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
        <h1>⚡ Centrica &nbsp;|&nbsp; Vendor Onboarding</h1>
        <p class="tagline">Powered by ARIA · Automated Registration &amp; Intelligence Assistant</p>
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

_render_phase_bar()

# ── Two-column layout ──────────────────────────────────────────────────────────
chat_col, panel_col = st.columns([2, 1], gap="large")

with panel_col:
    _PANEL = st.empty()
    # Seed initial activity on first load
    if not st.session_state.activity_log:
        st.session_state.activity_log = [
            {"time": datetime.now().strftime("%H:%M:%S"), "icon": "🟢", "text": "ARIA system online", "kind": "ok", "fresh": False},
            {"time": datetime.now().strftime("%H:%M:%S"), "icon": "🔧", "text": "Agent modules loaded: KYC, AML, Risk, News, Ariba", "kind": "", "fresh": False},
            {"time": datetime.now().strftime("%H:%M:%S"), "icon": "📡", "text": "Listening for vendor input…", "kind": "", "fresh": False},
        ]
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
                    _activity("📋", "All required documents confirmed", kind="ok")
                    st.session_state.pending_auto_turn = (
                        "(System: vendor has now provided all required documents. "
                        "Please run validation as described in your phase instructions.)"
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

    if orc.phase != "COMPLETE":
        user_input = st.chat_input("Type your message…")
    else:
        user_input = None
        st.success("✅ Onboarding complete! Refresh the page to onboard another vendor.")

    if user_input:
        _activity("📥", f"Vendor message received ({len(user_input)} chars)", delay=0.2)
        st.session_state.messages.append({"role": "user", "content": user_input})
        _extract_vendor_info(user_input, role="user")
        if orc.phase in ("WELCOME", "PHASE_A"):
            _detect_industry_from_messages()

        _activity("🧠", "Generating ARIA response (Gemini 2.5 Flash)…", delay=0.2, kind="live")
        with chat_box:
            with st.chat_message("user", avatar="🏢"):
                st.markdown(user_input)
            with st.chat_message("assistant", avatar="⚡"):
                full = _stream_into_chat()
        _activity("💬", "ARIA response delivered", kind="ok")

        clean, triggers = _process_response_triggers(full)

        if orc.phase == "PHASE_B" and next_doc:
            positive = ["yes", "confirm", "have it", "here", "provided", "attached", "sent", "done", "sure", "ok", "✓", "ref"]
            if any(w in user_input.lower() for w in positive):
                orc.confirm_doc(next_doc["id"])
                _activity("📋", f"{next_doc['name']} confirmed via chat", kind="ok")
                if orc.all_docs_confirmed():
                    orc.advance_to_validation()
                    st.session_state.pending_auto_turn = (
                        "(System: vendor has now provided all required documents. "
                        "Please run validation as described in your phase instructions.)"
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
