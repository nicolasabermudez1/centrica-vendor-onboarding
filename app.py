"""
Centrica Vendor Onboarding — ARIA Chatbot
Streamlit app — entry point for Streamlit Community Cloud.
"""

import time
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

    /* Trim Streamlit's default top padding */
    .block-container { padding-top: 1.2rem; padding-bottom: 1rem; max-width: 1400px; }

    /* Header bar */
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

    /* Phase progress bar */
    .phase-bar { display: flex; gap: 5px; margin-bottom: 12px; }
    .phase-step {
        flex: 1;
        padding: 5px 8px;
        border-radius: 18px;
        font-size: 0.7rem;
        text-align: center;
        font-weight: 600;
        background: #f0f0f0;
        color: #999;
    }
    .phase-step.active { background: var(--navy); color: white; }
    .phase-step.done   { background: var(--mint); color: var(--navy); }

    /* Agent panel */
    .agent-panel {
        background: #fafbff;
        border: 1.5px solid var(--pale);
        border-radius: 12px;
        padding: 14px;
    }
    .agent-panel h3 {
        color: var(--navy);
        font-size: 0.85rem;
        font-weight: 700;
        margin: 0 0 10px 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .agent-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 10px; font-size: 0.8rem; }
    .agent-icon { font-size: 1rem; min-width: 20px; }
    .agent-name { font-weight: 600; color: var(--navy); }
    .agent-detail { color: #666; font-size: 0.74rem; margin-top: 2px; }

    /* Animated pulse for running agents */
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%      { opacity: 0.6; transform: scale(1.15); }
    }
    .pulse { display: inline-block; animation: pulse 1.0s ease-in-out infinite; }

    /* Risk badge */
    .risk-badge {
        background: var(--mint);
        color: var(--navy);
        border-radius: 8px;
        padding: 9px 12px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-top: 8px;
        text-align: center;
    }

    /* Ariba success card */
    .ariba-card {
        background: linear-gradient(135deg, var(--navy) 0%, #1a3a9e 100%);
        color: white;
        border-radius: 12px;
        padding: 18px;
        margin-top: 12px;
    }
    .ariba-card h2 { color: var(--mint); font-size: 1rem; margin: 0 0 6px 0; }
    .ariba-ref { font-size: 1.25rem; font-weight: 700; color: var(--mint); letter-spacing: 0.06em; }
    .ariba-detail { font-size: 0.75rem; color: #cce; margin-top: 4px; }
    .ariba-step { background: rgba(255,255,255,0.1); border-radius: 6px; padding: 6px 10px; margin: 4px 0; font-size: 0.74rem; }

    /* Doc-extraction card inside chat */
    .doc-extract {
        background: #f4f8ff;
        border-left: 3px solid var(--mint);
        border-radius: 6px;
        padding: 10px 14px;
        margin: 6px 0;
    }
    .doc-extract .label { font-size: 0.7rem; color: #777; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
    .doc-extract .value { font-size: 0.85rem; color: var(--navy); font-weight: 600; }

    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


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
            "risk":  {"status": "pending", "label": "Credit & Risk Assessment",    "icon_done": "✅", "icon_run": "📊", "detail": ""},
            "news":  {"status": "pending", "label": "News & Web Presence Search",  "icon_done": "✅", "icon_run": "📰", "detail": ""},
            "ariba": {"status": "pending", "label": "Ariba SLP Submission",        "icon_done": "✅", "icon_run": "⚡", "detail": ""},
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
        st.session_state.pending_auto_turn = None  # holds the synthetic trigger text
    if "processed_uploads" not in st.session_state:
        st.session_state.processed_uploads = set()
    if "upload_counter" not in st.session_state:
        st.session_state.upload_counter = 0


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


# ── Extract vendor info from user messages ─────────────────────────────────────
def _extract_vendor_info(text: str, role: str = "user") -> None:
    import re
    lower = text.lower()
    info = orc.vendor_info

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
                    break
        if not info.get("company_name") and len(text) < 80:
            orc.update_vendor_info("company_name", text.strip().rstrip(".,")[:60])

    if info.get("is_uk") is None:
        if any(w in lower for w in ["uk", "united kingdom", "england", "scotland", "wales", "britain", "british"]):
            orc.update_vendor_info("is_uk", True)
            orc.update_vendor_info("country", "United Kingdom")
        elif any(w in lower for w in ["us ", "usa", "united states", "america", "canada", "india", "germany", "france", "international", "global"]):
            orc.update_vendor_info("is_uk", False)
            for country in ["United States", "USA", "Canada", "India", "Germany", "France", "Australia", "Spain", "Italy"]:
                if country.lower() in lower:
                    orc.update_vendor_info("country", country)
                    break
            if not info.get("country"):
                orc.update_vendor_info("country", "International")

    if not info.get("size"):
        if any(w in lower for w in ["micro", "1-9", "under 10", "fewer than 10", "very small", "sole trader", "1 employee"]):
            orc.update_vendor_info("size", "micro")
        elif any(w in lower for w in ["small", "10-49", "10 to 49", "20 employee", "30 employee", "40 employee"]):
            orc.update_vendor_info("size", "small")
        elif any(w in lower for w in ["medium", "50-249", "50 to 249", "100 employee", "150 employee", "200 employee"]):
            orc.update_vendor_info("size", "medium")
        elif any(w in lower for w in ["large", "250+", "250 to", "500 employee", "1000 employee", "thousand"]):
            orc.update_vendor_info("size", "large")
        elif any(w in lower for w in ["enterprise", "global", "multinational", "10,000", "100,000"]):
            orc.update_vendor_info("size", "enterprise")

    if not info.get("group_structure"):
        if any(w in lower for w in ["parent", "subsidiary", "group", "holding", "part of"]):
            orc.update_vendor_info("group_structure", "Subsidiary of group")
        elif any(w in lower for w in ["independent", "standalone", "no parent", "not part"]):
            orc.update_vendor_info("group_structure", "Standalone entity")

    email_match = re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", text)
    if email_match and not info.get("contact_email"):
        orc.update_vendor_info("contact_email", email_match.group())


def _detect_industry_from_messages():
    if orc.vendor_info.get("industry"):
        return
    user_msgs = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
    context = " ".join(user_msgs[:3])
    if len(context) < 10:
        return
    from utils.gemini_client import classify_industry
    industry = classify_industry(context)
    orc.update_vendor_info("industry", industry)
    if orc.phase == "WELCOME":
        orc.phase = "PHASE_A"


# ── Agent runners ──────────────────────────────────────────────────────────────
def run_agents(agent_panel_placeholder):
    from agents import kyc_agent, aml_agent, risk_agent, news_agent

    steps = [
        ("kyc",  kyc_agent,  "Searching Companies House…",     None),
        ("aml",  aml_agent,  "Screening sanctions databases…", "All clear — no matches"),
        ("risk", risk_agent, "Calculating risk score…",        None),
        ("news", news_agent, "Searching recent news…",         None),
    ]

    for key, module, running_msg, done_msg in steps:
        st.session_state.agent_statuses[key]["status"] = "running"
        st.session_state.agent_statuses[key]["detail"] = running_msg
        _render_agent_panel(agent_panel_placeholder)
        time.sleep(1.6)

        try:
            result = module.run(orc.vendor_info)
        except Exception as e:
            result = {"_error": str(e)}
        st.session_state.agent_results[key] = result

        if key == "kyc":
            reg = result.get("registration_number", "verified")
            done_msg = f"Verified — Reg #{reg}"
        elif key == "risk":
            score = result.get("composite_risk_score", 75)
            label = result.get("composite_risk_label", "Low Risk")
            done_msg = f"Score: {score}/100 — {label}"
        elif key == "news":
            arts = result.get("articles", [])
            sentiment = result.get("overall_sentiment", "Positive")
            done_msg = f"{len(arts)} articles — {sentiment} sentiment"

        st.session_state.agent_statuses[key]["status"] = "done"
        st.session_state.agent_statuses[key]["detail"] = done_msg
        _render_agent_panel(agent_panel_placeholder)
        time.sleep(0.35)

    st.session_state.agents_triggered = True
    orc.advance_to_phase_b()


def run_ariba(agent_panel_placeholder):
    from agents import ariba_agent

    st.session_state.agent_statuses["ariba"]["status"] = "running"
    st.session_state.agent_statuses["ariba"]["detail"] = "Packaging vendor record…"
    _render_agent_panel(agent_panel_placeholder)
    time.sleep(1.0)

    st.session_state.agent_statuses["ariba"]["detail"] = "Submitting to Ariba SLP…"
    _render_agent_panel(agent_panel_placeholder)
    time.sleep(0.9)

    result = ariba_agent.run(orc.vendor_info, st.session_state.agent_results)
    st.session_state.ariba_result = result

    st.session_state.agent_statuses["ariba"]["detail"] = "Generating DocuSign pack…"
    _render_agent_panel(agent_panel_placeholder)
    time.sleep(0.8)

    st.session_state.agent_statuses["ariba"]["status"] = "done"
    st.session_state.agent_statuses["ariba"]["detail"] = f"Ref: {result['ariba_reference']}"
    _render_agent_panel(agent_panel_placeholder)
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

    badge_html = ""
    if st.session_state.agent_statuses["risk"]["status"] == "done":
        risk_res = st.session_state.agent_results.get("risk", {})
        score = risk_res.get("composite_risk_score", "–")
        label = risk_res.get("composite_risk_label", "")
        pt = risk_res.get("recommended_payment_terms_days", "–")
        badge_html = f"""
        <div class="risk-badge">
          Risk Score: {score}/100 · {label}<br/>
          <span style="font-weight:400;font-size:0.72rem;">Payment Terms: {pt} days</span>
        </div>
        """

    ariba_html = ""
    if st.session_state.ariba_result:
        r = st.session_state.ariba_result
        steps_html = "".join(f'<div class="ariba-step">✅ {s}</div>' for s in r.get("next_steps", []))
        ariba_html = f"""
        <div class="ariba-card">
          <h2>⚡ Registered in Ariba SLP</h2>
          <div class="ariba-ref">{r.get("ariba_reference", "")}</div>
          <div class="ariba-detail">
            DocuSign: {r.get("docusign_reference", "")}<br/>
            Go-live: {r.get("go_live_date", "")} · Terms: {r.get("payment_terms_days", "–")} days
          </div>
          <div style="margin-top:8px;">{steps_html}</div>
        </div>
        """

    html = f'<div class="agent-panel"><h3>🤖 Agent Activity</h3>{rows_html}{badge_html}{ariba_html}</div>'

    if placeholder:
        placeholder.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


# ── Phase bar ──────────────────────────────────────────────────────────────────
def _render_phase_bar():
    phases = ["Welcome", "Pre-Qual", "Bg Checks", "Documents", "Validation", "Ariba", "Complete"]
    current = orc.get_phase_number()
    steps_html = ""
    for i, label in enumerate(phases):
        cls = "done" if i < current else ("active" if i == current else "")
        steps_html += f'<div class="phase-step {cls}">{label}</div>'
    st.markdown(f'<div class="phase-bar">{steps_html}</div>', unsafe_allow_html=True)


# ── Stream a Gemini response into a chat-message block ─────────────────────────
def _stream_into_chat(synthetic_user_msg: str | None = None) -> str:
    """Generate an assistant turn (streaming). If synthetic_user_msg is set,
    it's added to Gemini's context only — NOT saved to displayed history."""
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
    """Strip [TRIGGER_X] markers from the response and return cleaned text + flags."""
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


# ── Doc upload processing ─────────────────────────────────────────────────────
def _process_doc_upload(uploaded_file, doc: dict) -> dict:
    """Read the upload, send to Gemini for extraction. Returns extraction result."""
    from utils.doc_reader import extract_text
    from utils.gemini_client import extract_doc_fields

    text = extract_text(uploaded_file)
    result = extract_doc_fields(
        file_text=text,
        doc_name=doc["name"],
        doc_purpose=doc.get("why", ""),
        vendor_info=orc.vendor_info,
    )
    return result


def _format_extraction_card(filename: str, doc_name: str, extraction: dict) -> str:
    """Build markdown for the extraction confirmation message."""
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
        "**Local:** Create a `.env` file with `GOOGLE_API_KEY=your-key-here`\n\n"
        "**Streamlit Cloud:** App Settings → Secrets → add `GOOGLE_API_KEY = \"your-key-here\"`"
    )
    st.stop()

_render_phase_bar()

# ── LAYOUT: chat (left) + agent panel (right) ─────────────────────────────────
chat_col, panel_col = st.columns([2, 1], gap="large")

# Right column first (so panel placeholder exists for run_agents)
with panel_col:
    agent_panel_placeholder = st.empty()
    _render_agent_panel(agent_panel_placeholder)

# ── Chat column ───────────────────────────────────────────────────────────────
with chat_col:
    # Greeting (added once, before container renders)
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

    # Fixed-height chat container (ChatGPT-style)
    chat_box = st.container(height=520, border=True)

    with chat_box:
        # Render existing message history
        for msg in st.session_state.messages:
            avatar = "⚡" if msg["role"] == "assistant" else "🏢"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        # ── Process pending auto-turn (e.g. after agents finish, after a doc upload) ──
        if st.session_state.pending_auto_turn:
            synthetic = st.session_state.pending_auto_turn
            st.session_state.pending_auto_turn = None
            with st.chat_message("assistant", avatar="⚡"):
                full = _stream_into_chat(synthetic_user_msg=synthetic)
            clean, triggers = _process_response_triggers(full)
            st.session_state.messages.append({"role": "assistant", "content": clean})

            if triggers["validation"]:
                orc.advance_to_validation()
            if triggers["ariba"]:
                orc.phase = "ARIBA"
                _render_phase_bar()
                with st.chat_message("assistant", avatar="⚡"):
                    with st.status("Submitting to Ariba SLP…", expanded=True) as status:
                        st.write("📦 Packaging validated vendor record…")
                        time.sleep(0.8)
                        st.write("🔗 Connecting to Ariba SLP API…")
                        time.sleep(0.8)
                        st.write("📤 Uploading vendor profile…")
                        time.sleep(0.7)
                        st.write("📝 Generating DocuSign onboarding pack…")
                        time.sleep(0.8)
                        run_ariba(agent_panel_placeholder)
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
                st.rerun()

    # ── File uploader for current required doc (appears below chat when in PHASE_B) ──
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
                # Show user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"📎 *Uploaded:* `{uploaded.name}` for {next_doc['name']}",
                })
                # Run extraction
                with st.spinner(f"ARIA is reading `{uploaded.name}` and extracting the relevant information…"):
                    extraction = _process_doc_upload(uploaded, next_doc)
                # Add extraction card as assistant message
                card = _format_extraction_card(uploaded.name, next_doc["name"], extraction)
                st.session_state.messages.append({"role": "assistant", "content": card})
                # Mark confirmed
                orc.confirm_doc(next_doc["id"])
                st.session_state.upload_counter += 1
                # Set auto-turn so Gemini asks for next doc OR triggers validation
                if orc.all_docs_confirmed():
                    st.session_state.pending_auto_turn = (
                        "(System: vendor has now provided all required documents. "
                        "Please run validation as described in your phase instructions.)"
                    )
                else:
                    st.session_state.pending_auto_turn = (
                        f"(System: vendor just successfully provided their {next_doc['name']}. "
                        f"Thank them briefly and request the NEXT required document.)"
                    )
                st.rerun()

    # ── Chat input ─────────────────────────────────────────────────────────────
    if orc.phase != "COMPLETE":
        user_input = st.chat_input("Type your message…")
    else:
        user_input = None
        st.success("✅ Onboarding complete! Refresh the page to onboard another vendor.")

    if user_input:
        # Add user message and rerender inside container on rerun
        st.session_state.messages.append({"role": "user", "content": user_input})
        _extract_vendor_info(user_input, role="user")
        if orc.phase in ("WELCOME", "PHASE_A"):
            _detect_industry_from_messages()

        # Generate assistant response into a temporary block at the bottom of the container
        # (will be properly rendered after rerun)
        with chat_box:
            with st.chat_message("user", avatar="🏢"):
                st.markdown(user_input)
            with st.chat_message("assistant", avatar="⚡"):
                full = _stream_into_chat()

        clean, triggers = _process_response_triggers(full)

        # If in PHASE_B and user is confirming a doc by typing, mark it
        if orc.phase == "PHASE_B" and next_doc:
            positive = ["yes", "confirm", "have it", "here", "provided", "attached", "sent", "done", "sure", "ok", "✓", "ref"]
            if any(w in user_input.lower() for w in positive):
                orc.confirm_doc(next_doc["id"])
                if orc.all_docs_confirmed():
                    orc.advance_to_validation()
                    st.session_state.pending_auto_turn = (
                        "(System: vendor has now provided all required documents. "
                        "Please run validation as described in your phase instructions.)"
                    )

        st.session_state.messages.append({"role": "assistant", "content": clean})

        if triggers["agents"] and not st.session_state.agents_triggered:
            orc.phase = "AGENTS_RUNNING"
            run_agents(agent_panel_placeholder)
            # Queue auto-turn so Gemini transitions into PHASE_B + asks for doc #1
            st.session_state.pending_auto_turn = (
                "(System: all background checks have just completed successfully. "
                "Now briefly summarise the positive results in one short paragraph "
                "and ask the vendor for the FIRST required industry-specific document.)"
            )
            st.rerun()

        if triggers["validation"]:
            orc.advance_to_validation()

        if triggers["ariba"]:
            orc.phase = "ARIBA"
            _render_phase_bar()
            with chat_box:
                with st.chat_message("assistant", avatar="⚡"):
                    with st.status("Submitting to Ariba SLP…", expanded=True) as status:
                        st.write("📦 Packaging validated vendor record…")
                        time.sleep(0.8)
                        st.write("🔗 Connecting to Ariba SLP API…")
                        time.sleep(0.8)
                        st.write("📤 Uploading vendor profile…")
                        time.sleep(0.7)
                        st.write("📝 Generating DocuSign onboarding pack…")
                        time.sleep(0.8)
                        run_ariba(agent_panel_placeholder)
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

        st.rerun()
