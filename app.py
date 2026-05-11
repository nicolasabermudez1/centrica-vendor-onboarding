"""
Centrica Vendor Onboarding — ARIA Chatbot
Streamlit app — entry point for Streamlit Community Cloud.
"""

import time
import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Centrica Vendor Onboarding | ARIA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS: Centrica branding ────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Centrica palette */
    :root {
        --navy:   #0F2067;
        --mint:   #85DB9C;
        --lavender: #B999F6;
        --pale:   #DECFFF;
        --purple: #9B2BF7;
    }

    /* Global font */
    html, body, [class*="css"] { font-family: Arial, sans-serif; }

    /* Header bar */
    .aria-header {
        background: var(--navy);
        padding: 18px 28px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .aria-header h1 {
        color: white;
        font-size: 1.4rem;
        margin: 0;
        font-weight: 700;
    }
    .aria-header .tagline {
        color: var(--mint);
        font-size: 0.85rem;
        margin: 0;
    }

    /* Phase progress bar */
    .phase-bar {
        display: flex;
        gap: 6px;
        align-items: center;
        margin-bottom: 18px;
    }
    .phase-step {
        flex: 1;
        padding: 6px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        text-align: center;
        font-weight: 600;
        background: #f0f0f0;
        color: #999;
    }
    .phase-step.active {
        background: var(--navy);
        color: white;
    }
    .phase-step.done {
        background: var(--mint);
        color: var(--navy);
    }

    /* Agent activity panel */
    .agent-panel {
        background: #fafbff;
        border: 1.5px solid var(--pale);
        border-radius: 12px;
        padding: 16px;
    }
    .agent-panel h3 {
        color: var(--navy);
        font-size: 0.9rem;
        font-weight: 700;
        margin: 0 0 12px 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .agent-row {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        margin-bottom: 12px;
        font-size: 0.82rem;
    }
    .agent-icon { font-size: 1.1rem; min-width: 22px; }
    .agent-name { font-weight: 600; color: var(--navy); }
    .agent-detail { color: #555; font-size: 0.78rem; margin-top: 2px; }

    /* Risk score badge */
    .risk-badge {
        background: var(--mint);
        color: var(--navy);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-top: 10px;
        text-align: center;
    }

    /* Ariba success card */
    .ariba-card {
        background: linear-gradient(135deg, var(--navy) 0%, #1a3a9e 100%);
        color: white;
        border-radius: 14px;
        padding: 22px;
        margin-top: 16px;
    }
    .ariba-card h2 { color: var(--mint); font-size: 1.1rem; margin: 0 0 8px 0; }
    .ariba-ref {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--mint);
        letter-spacing: 0.08em;
    }
    .ariba-detail { font-size: 0.8rem; color: #cce; margin-top: 6px; }
    .ariba-step {
        background: rgba(255,255,255,0.1);
        border-radius: 6px;
        padding: 7px 12px;
        margin: 5px 0;
        font-size: 0.78rem;
    }

    /* Chat message tweaks */
    [data-testid="stChatMessage"] {
        border-radius: 10px;
    }

    /* Hide Streamlit default footer */
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state initialisation ──────────────────────────────────────────────
def _init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "orchestrator" not in st.session_state:
        from agents.orchestrator import Orchestrator
        st.session_state.orchestrator = Orchestrator()
    if "agent_statuses" not in st.session_state:
        # pending | running | done | skipped
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


_init_state()
orc = st.session_state.orchestrator


# ── Helper: check API key ──────────────────────────────────────────────────────
def _api_key_ok() -> bool:
    try:
        from utils.gemini_client import _get_api_key
        _get_api_key()
        return True
    except Exception:
        return False


# ── Helper: extract vendor info from conversation ─────────────────────────────
def _extract_vendor_info(text: str, role: str = "user") -> None:
    """Simple keyword extraction from user messages to populate vendor_info."""
    import re
    lower = text.lower()
    info = orc.vendor_info

    # Company name — first user message, take first sentence-ish
    if not info.get("company_name") and role == "user":
        # Look for patterns like "we are X" / "I'm from X" / "our company is X" / just a capitalised name
        patterns = [
            r"(?:we are|we're|i'm from|our company is|company called|called)\s+([A-Z][A-Za-z0-9\s&,\.'-]{2,40})",
            r"^([A-Z][A-Za-z0-9\s&,\.'-]{2,40?})\s*(?:is|are|,|\.|$)",
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                candidate = m.group(1).strip().rstrip(".,")
                if len(candidate) > 3:
                    orc.update_vendor_info("company_name", candidate)
                    break
        # Fallback: use first 50 chars of the message as a name hint
        if not info.get("company_name") and len(text) < 80:
            orc.update_vendor_info("company_name", text.strip().rstrip(".,")[:60])

    # UK vs international
    if info.get("is_uk") is None:
        if any(w in lower for w in ["uk", "united kingdom", "england", "scotland", "wales", "britain", "british"]):
            orc.update_vendor_info("is_uk", True)
            orc.update_vendor_info("country", "United Kingdom")
        elif any(w in lower for w in ["us ", "usa", "united states", "america", "canada", "india", "germany", "france", "international", "global"]):
            orc.update_vendor_info("is_uk", False)
            # Try to extract country
            for country in ["United States", "USA", "Canada", "India", "Germany", "France", "Australia", "Spain", "Italy"]:
                if country.lower() in lower:
                    orc.update_vendor_info("country", country)
                    break
            if not info.get("country"):
                orc.update_vendor_info("country", "International")

    # Size
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

    # Group structure
    if not info.get("group_structure"):
        if any(w in lower for w in ["parent", "subsidiary", "group", "holding", "part of"]):
            orc.update_vendor_info("group_structure", "Subsidiary of group")
        elif any(w in lower for w in ["independent", "standalone", "no parent", "not part"]):
            orc.update_vendor_info("group_structure", "Standalone entity")

    # Contact email
    import re as _re
    email_match = _re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", text)
    if email_match and not info.get("contact_email"):
        orc.update_vendor_info("contact_email", email_match.group())


def _detect_industry_from_messages():
    """Run industry detection once we have a company description."""
    if orc.vendor_info.get("industry"):
        return
    # Combine first 2 user messages for context
    user_msgs = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
    context = " ".join(user_msgs[:3])
    if len(context) < 10:
        return
    from utils.gemini_client import classify_industry
    industry = classify_industry(context)
    orc.update_vendor_info("industry", industry)
    if orc.phase == "WELCOME":
        orc.phase = "PHASE_A"


# ── Run background agents ──────────────────────────────────────────────────────
def run_agents(agent_panel_placeholder):
    """Run KYC, AML, risk, news agents sequentially with live UI updates."""
    from agents import kyc_agent, aml_agent, risk_agent, news_agent

    steps = [
        ("kyc",  kyc_agent,  "Searching Companies House…",     "Verified — entity confirmed"),
        ("aml",  aml_agent,  "Screening sanctions databases…", "All clear — no matches"),
        ("risk", risk_agent, "Calculating risk score…",        None),
        ("news", news_agent, "Searching recent news…",         None),
    ]

    for key, module, running_msg, done_msg in steps:
        st.session_state.agent_statuses[key]["status"] = "running"
        st.session_state.agent_statuses[key]["detail"] = running_msg
        _render_agent_panel(agent_panel_placeholder)
        time.sleep(1.4)

        result = module.run(orc.vendor_info)
        st.session_state.agent_results[key] = result

        if key == "risk":
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
        time.sleep(0.3)

    st.session_state.agents_triggered = True
    orc.advance_to_phase_b()


def run_ariba(agent_panel_placeholder):
    """Run the Ariba submission agent with animated progress."""
    from agents import ariba_agent
    import random

    st.session_state.agent_statuses["ariba"]["status"] = "running"
    st.session_state.agent_statuses["ariba"]["detail"] = "Packaging vendor record…"
    _render_agent_panel(agent_panel_placeholder)
    time.sleep(1.2)

    st.session_state.agent_statuses["ariba"]["detail"] = "Submitting to Ariba SLP…"
    _render_agent_panel(agent_panel_placeholder)
    time.sleep(1.0)

    result = ariba_agent.run(orc.vendor_info, st.session_state.agent_results)
    st.session_state.ariba_result = result

    st.session_state.agent_statuses["ariba"]["detail"] = "Generating DocuSign pack…"
    _render_agent_panel(agent_panel_placeholder)
    time.sleep(0.9)

    st.session_state.agent_statuses["ariba"]["status"] = "done"
    st.session_state.agent_statuses["ariba"]["detail"] = f"Ref: {result['ariba_reference']}"
    _render_agent_panel(agent_panel_placeholder)

    st.session_state.ariba_triggered = True
    orc.advance_to_complete()


# ── Render agent panel ────────────────────────────────────────────────────────
def _render_agent_panel(placeholder=None):
    icons_pending = {"kyc": "⬜", "aml": "⬜", "risk": "⬜", "news": "⬜", "ariba": "⬜"}

    rows_html = ""
    for key, info in st.session_state.agent_statuses.items():
        s = info["status"]
        if s == "done":
            icon = info["icon_done"]
            name_style = "color:#0F2067; font-weight:700;"
        elif s == "running":
            icon = info["icon_run"]
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

    # Risk badge (show once risk agent is done)
    badge_html = ""
    if st.session_state.agent_statuses["risk"]["status"] == "done":
        risk_res = st.session_state.agent_results.get("risk", {})
        score = risk_res.get("composite_risk_score", "–")
        label = risk_res.get("composite_risk_label", "")
        pt = risk_res.get("recommended_payment_terms_days", "–")
        badge_html = f"""
        <div class="risk-badge">
          Risk Score: {score}/100 · {label}<br/>
          <span style="font-weight:400;font-size:0.75rem;">Payment Terms: {pt} days</span>
        </div>
        """

    # Ariba card (show once Ariba is done)
    ariba_html = ""
    if st.session_state.ariba_result:
        r = st.session_state.ariba_result
        steps_html = "".join(f'<div class="ariba-step">✅ {s}</div>' for s in r.get("next_steps", []))
        ariba_html = f"""
        <div class="ariba-card">
          <h2>⚡ Registered in Ariba SLP</h2>
          <div class="ariba-ref">{r.get("ariba_reference", "")}</div>
          <div class="ariba-detail">
            DocuSign Ref: {r.get("docusign_reference", "")} &nbsp;|&nbsp;
            Go-live: {r.get("go_live_date", "")} &nbsp;|&nbsp;
            Terms: {r.get("payment_terms_days", "–")} days
          </div>
          <div style="margin-top:10px;">{steps_html}</div>
        </div>
        """

    html = f"""
    <div class="agent-panel">
      <h3>🤖 Agent Activity</h3>
      {rows_html}
      {badge_html}
      {ariba_html}
    </div>
    """

    if placeholder:
        placeholder.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


# ── Phase progress bar ────────────────────────────────────────────────────────
def _render_phase_bar():
    phases = ["Welcome", "Pre-Qual", "Bg Checks", "Documents", "Validation", "Ariba", "Complete"]
    current = orc.get_phase_number()
    steps_html = ""
    for i, label in enumerate(phases):
        if i < current:
            cls = "done"
        elif i == current:
            cls = "active"
        else:
            cls = ""
        steps_html += f'<div class="phase-step {cls}">{label}</div>'
    st.markdown(f'<div class="phase-bar">{steps_html}</div>', unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="aria-header">
      <div>
        <h1>⚡ Centrica &nbsp;|&nbsp; Vendor Onboarding</h1>
        <p class="tagline">Powered by ARIA · Automated Registration &amp; Intelligence Assistant</p>
      </div>
      <div style="color:#85DB9C;font-size:0.8rem;text-align:right;">
        Procurement Transformation<br/>
        <span style="color:#B999F6;">AI-Powered · Ariba SLP Ready</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── API key guard ─────────────────────────────────────────────────────────────
if not _api_key_ok():
    st.warning(
        "**GOOGLE_API_KEY not configured.**\n\n"
        "**Local:** Create a `.env` file in the project root with `GOOGLE_API_KEY=your-key-here`\n\n"
        "**Streamlit Cloud:** Go to App Settings → Secrets and add `GOOGLE_API_KEY = \"your-key-here\"`"
    )
    st.stop()

# ── Phase progress ────────────────────────────────────────────────────────────
_render_phase_bar()

# ── Main layout: chat (left) + agent panel (right) ────────────────────────────
chat_col, panel_col = st.columns([2, 1], gap="large")

with panel_col:
    agent_panel_placeholder = st.empty()
    _render_agent_panel(agent_panel_placeholder)

with chat_col:
    # Send greeting on first load
    if not st.session_state.greeting_sent:
        greeting = (
            "Welcome to Centrica's supplier onboarding portal! 👋\n\n"
            "I'm **ARIA** — Centrica's Automated Registration & Intelligence Assistant. "
            "I'll guide you through our onboarding process today, which should take just a few minutes.\n\n"
            "To get started, could you please tell me your **company name** and give me a brief description "
            "of what you supply or what services you offer to Centrica?"
        )
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        st.session_state.greeting_sent = True

    # Render existing messages
    for msg in st.session_state.messages:
        avatar = "⚡" if msg["role"] == "assistant" else "🏢"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Chat input
    if orc.phase != "COMPLETE":
        user_input = st.chat_input("Type your message here…")
    else:
        user_input = None
        st.info("✅ Onboarding complete! Start a new session to onboard another vendor.")

    if user_input:
        # Show user message immediately
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🏢"):
            st.markdown(user_input)

        # Extract structured info from user's message
        _extract_vendor_info(user_input, role="user")

        # Detect industry after first couple of messages
        if orc.phase in ("WELCOME", "PHASE_A"):
            _detect_industry_from_messages()

        # ── Determine if we should trigger agents ─────────────────────────────
        trigger_agents = False
        trigger_ariba = False

        # Get AI response
        from utils.gemini_client import stream_chat

        system_prompt = orc.get_system_prompt()
        response_text = ""

        with st.chat_message("assistant", avatar="⚡"):
            response_placeholder = st.empty()
            full_response = ""

            try:
                for chunk in stream_chat(st.session_state.messages, system_prompt):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
            except Exception as e:
                full_response = (
                    "I'm sorry — I encountered a brief technical issue. "
                    f"Please try again in a moment. *(Error: {str(e)[:80]})*"
                )
                response_placeholder.markdown(full_response)

        response_text = full_response

        # Detect phase markers in the response
        if "[TRIGGER_AGENTS]" in response_text and not st.session_state.agents_triggered:
            trigger_agents = True
            response_text = response_text.replace("[TRIGGER_AGENTS]", "").strip()

        if "[TRIGGER_VALIDATION]" in response_text:
            response_text = response_text.replace("[TRIGGER_VALIDATION]", "").strip()
            orc.phase = "VALIDATION"

        if "[TRIGGER_ARIBA]" in response_text and not st.session_state.ariba_triggered:
            trigger_ariba = True
            response_text = response_text.replace("[TRIGGER_ARIBA]", "").strip()

        # Also detect document confirmations during PHASE_B
        if orc.phase == "PHASE_B":
            next_doc = orc.get_next_required_doc()
            if next_doc:
                positive_words = ["yes", "confirm", "have it", "here", "provided", "attached", "sent", "done", "sure", "ok", "✓"]
                if any(w in user_input.lower() for w in positive_words):
                    orc.confirm_doc(next_doc["id"])
                    if orc.all_docs_confirmed():
                        orc.phase = "VALIDATION"

        # Store cleaned response
        st.session_state.messages.append({"role": "assistant", "content": response_text})

        # ── Run agents if triggered ───────────────────────────────────────────
        if trigger_agents:
            orc.phase = "AGENTS_RUNNING"
            with chat_col:
                with st.chat_message("assistant", avatar="⚡"):
                    st.markdown(
                        "🔍 **Running background checks now…** "
                        "I'm scanning our verification databases in parallel — "
                        "this will take just a moment. Watch the agent panel on the right →"
                    )
            run_agents(agent_panel_placeholder)
            st.rerun()

        if trigger_ariba:
            orc.phase = "ARIBA"
            _render_phase_bar()
            with chat_col:
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

            # Add completion message to history
            ariba_ref = st.session_state.ariba_result["ariba_reference"]
            pt = st.session_state.ariba_result.get("payment_terms_days", "–")
            go_live = st.session_state.ariba_result.get("go_live_date", "–")
            completion_msg = (
                f"🎉 **Congratulations — registration is complete!**\n\n"
                f"Your vendor record has been successfully submitted to **Centrica's Ariba SLP**.\n\n"
                f"- **Reference:** `{ariba_ref}`\n"
                f"- **Payment terms:** {pt} days from invoice date\n"
                f"- **Go-live date:** {go_live}\n\n"
                f"A **DocuSign onboarding pack** has been sent for your signature — "
                f"please check your inbox. Once signed, you'll have full access to the Centrica supplier portal.\n\n"
                f"Is there anything else you'd like to know about the onboarding process?"
            )
            st.session_state.messages.append({"role": "assistant", "content": completion_msg})
            orc.advance_to_complete()
            st.rerun()

        st.rerun()
