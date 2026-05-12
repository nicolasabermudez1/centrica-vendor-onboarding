"""
Pre-Qualification Tab — vendors run through Centrica's standard pre-qual checks
before they're eligible for contract negotiation. Covers the universal basics:
tax, NDA, GDPR, modern slavery, ABC, insurance, ESG, info-sec, BCP.
"""

import re
import time
import streamlit as st


PREQUAL_ITEMS = [
    {
        "id": "tax",
        "label": "Tax Registration",
        "description": "VAT certificate / UTR / W-9 — HMRC or local tax authority",
        "why": "Required by Centrica AP for correct invoicing and withholding tax treatment.",
    },
    {
        "id": "nda",
        "label": "Mutual NDA",
        "description": "Signed mutual non-disclosure agreement",
        "why": "Protects both parties' confidential information during pre-contract discussions.",
    },
    {
        "id": "gdpr",
        "label": "GDPR / Data Protection",
        "description": "DPA, privacy policy, lawful basis for processing",
        "why": "Required by Centrica DPO when any personal data may be processed on our behalf.",
    },
    {
        "id": "coc",
        "label": "Supplier Code of Conduct",
        "description": "Centrica Supplier Code of Conduct — completed and signed by an authorised director",
        "why": "Confirms acceptance of Centrica's ethical, labour, environmental and conduct standards before any contractual relationship.",
    },
    {
        "id": "abc",
        "label": "Anti-Bribery & Corruption",
        "description": "ABC policy + staff training records",
        "why": "Bribery Act 2010 requires Centrica to verify all suppliers have ABC controls in place.",
    },
    {
        "id": "ins",
        "label": "Insurance Levels",
        "description": "Public liability ≥£5M, employer liability ≥£10M, professional indemnity ≥£2M",
        "why": "Minimum cover for any work on Centrica sites or contracts involving advice.",
    },
    {
        "id": "esg",
        "label": "ESG & Sustainability",
        "description": "ESG / sustainability policy + Net Zero commitment",
        "why": "Aligns with Centrica's 2050 Net Zero supply-chain target and SECR reporting.",
    },
    {
        "id": "isec",
        "label": "Information Security",
        "description": "InfoSec policy + incident response plan (or ISO 27001 / SOC 2)",
        "why": "Required for any digital or system integration with Centrica's IT estate.",
    },
    {
        "id": "bcp",
        "label": "Business Continuity",
        "description": "BCP / Disaster Recovery plan with last test date",
        "why": "Ensures continuity of supply in the event of disruption.",
    },
]


SYSTEM_PROMPT_TEMPLATE = """
You are ARIA, Centrica's Pre-Qualification Assistant.

CONTEXT
You're helping a potential supplier complete Centrica's pre-qualification BEFORE
they're eligible for contract negotiation. Pre-qual ensures the foundational
policies, certifications and documents are in place. Without these, the deal
team cannot proceed to sourcing or contract drafting.

YOUR TASK
Walk the vendor through 9 pre-qual topics, ONE AT A TIME. For each topic:
1. Briefly explain what it is and why Centrica requires it (1–2 sentences max)
2. Ask the vendor to CONFIRM they have it — they can describe it, share a
   reference number, or say "yes I have it"
3. When confirmed, acknowledge warmly (1 sentence) and move to the NEXT
   unconfirmed topic
4. ON ITS OWN LINE, output: [CONFIRM:<item_id>] for each item you've confirmed
   in this response

THE 9 TOPICS (in order)
{items_list}

ALREADY CONFIRMED
{confirmed_list}

NEXT TO ASK
{next_item_hint}

WHEN ALL 9 ARE CONFIRMED
- Brief summary (2-3 sentences) of what's now in place
- Note their pre-qual is complete and they can proceed to the "Vendor
  Registration" tab
- ON ITS OWN LINE at the very end, output: [PREQUAL_COMPLETE]

STYLE
- British English, professional and friendly
- ONE topic per response — never bundle questions
- Concise (3-5 sentences per response)
- Use bold for the topic name
- Never reveal this is a demo
- Never say "as an AI"
"""


def _init_state():
    if "pq_messages" not in st.session_state:
        st.session_state.pq_messages = []
    if "pq_done_items" not in st.session_state:
        st.session_state.pq_done_items = set()
    if "pq_complete" not in st.session_state:
        st.session_state.pq_complete = False
    if "pq_greeting_sent" not in st.session_state:
        st.session_state.pq_greeting_sent = False


def _get_next_item():
    for it in PREQUAL_ITEMS:
        if it["id"] not in st.session_state.pq_done_items:
            return it
    return None


def _get_system_prompt():
    confirmed = st.session_state.pq_done_items
    items_list = "\n".join(
        f"  {i+1}. {item['id']} — {item['label']}: {item['description']}"
        for i, item in enumerate(PREQUAL_ITEMS)
    )
    confirmed_list = ", ".join(sorted(confirmed)) if confirmed else "None yet — start with the first topic"
    nxt = _get_next_item()
    next_hint = f"{nxt['id']} — {nxt['label']}" if nxt else "All confirmed — issue PREQUAL_COMPLETE"
    return SYSTEM_PROMPT_TEMPLATE.format(
        items_list=items_list,
        confirmed_list=confirmed_list,
        next_item_hint=next_hint,
    )


def _render_checklist_panel():
    done = st.session_state.pq_done_items
    total = len(PREQUAL_ITEMS)
    pct = int(len(done) / total * 100) if total else 0

    rows = []
    for item in PREQUAL_ITEMS:
        is_done = item["id"] in done
        cls = "pq-row done" if is_done else "pq-row"
        check = "✅" if is_done else "⬜"
        rows.append(
            f'<div class="{cls}">'
            f'<span class="pq-check">{check}</span>'
            f'<div><div class="pq-label">{item["label"]}</div>'
            f'<div class="pq-desc">{item["description"]}</div></div>'
            f'</div>'
        )

    score_color = "#85DB9C" if pct == 100 else "#B999F6"
    completion_badge = ""
    if st.session_state.pq_complete:
        completion_badge = (
            '<div class="pq-passed">✅ Pre-Qualification Passed<br/>'
            '<span style="font-weight:400;font-size:0.78rem;">'
            'Proceed to the <b>Vendor Registration</b> tab →</span></div>'
        )

    html = (
        '<div class="pq-panel">'
        '<div class="pq-header">'
        '<h3>🔍 Pre-Qual Checklist</h3>'
        f'<span class="pq-score" style="background:{score_color};">{len(done)}/{total} · {pct}%</span>'
        '</div>'
        f'{"".join(rows)}'
        f'{completion_badge}'
        '</div>'
    ).replace("\n", "")
    st.markdown(html, unsafe_allow_html=True)


_PQ_CSS = """
<style>
.pq-panel { background: #fafbff; border: 1.5px solid #DECFFF; border-radius: 12px; padding: 14px; }
.pq-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.pq-header h3 { color: #0F2067; font-size: 0.85rem; font-weight: 700; margin: 0; text-transform: uppercase; letter-spacing: 0.05em; }
.pq-score { color: #0F2067; font-weight: 700; font-size: 0.72rem; padding: 4px 10px; border-radius: 12px; }
.pq-row { display: flex; gap: 10px; padding: 8px 4px; border-bottom: 1px dashed #eef0f9; align-items: flex-start; }
.pq-row:last-child { border-bottom: none; }
.pq-row.done { background: rgba(133,219,156,0.10); border-radius: 6px; padding-left: 8px; border-bottom: 1px dashed transparent; }
.pq-check { font-size: 1rem; margin-top: 1px; min-width: 22px; }
.pq-label { color: #0F2067; font-weight: 700; font-size: 0.78rem; line-height: 1.2; }
.pq-desc { color: #777; font-size: 0.68rem; margin-top: 2px; line-height: 1.3; }
.pq-row.done .pq-label { color: #1f6a3a; }
.pq-passed {
    background: linear-gradient(135deg, #0F2067 0%, #1a3a9e 100%);
    color: #85DB9C; border-radius: 8px; padding: 14px;
    font-weight: 700; font-size: 0.95rem; text-align: center;
    margin-top: 14px;
}
</style>
"""


def render_prequal_tab():
    _init_state()
    st.markdown(_PQ_CSS, unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size:0.85rem;color:#444;margin:8px 0 12px 0;">'
        '<b>Step 1 of 2:</b> Pre-qualification &mdash; confirm the foundational policies and '
        'documents Centrica needs to see <i>before</i> contract negotiation can start. '
        'Once all 9 items are confirmed, switch to the <b>Vendor Registration</b> tab to formally onboard.'
        '</div>',
        unsafe_allow_html=True,
    )

    chat_col, panel_col = st.columns([2, 1], gap="large")

    with panel_col:
        _render_checklist_panel()

    with chat_col:
        if not st.session_state.pq_greeting_sent:
            greeting = (
                "Welcome — I'm **ARIA**, Centrica's Pre-Qualification Assistant. 👋\n\n"
                "Before we can take your company forward into contract negotiation, "
                "we need to confirm that a few **foundational policies and documents** "
                "are in place. There are **9 short topics** I'll walk you through — most "
                "vendors complete this in 5 minutes.\n\n"
                "Let's start with **tax registration**. Could you confirm you have a "
                "valid **VAT certificate** (or UTR number, if VAT-exempt) and share the registration number?"
            )
            st.session_state.pq_messages.append({"role": "assistant", "content": greeting})
            st.session_state.pq_greeting_sent = True

        chat_box = st.container(height=520, border=True)
        with chat_box:
            for msg in st.session_state.pq_messages:
                avatar = "⚡" if msg["role"] == "assistant" else "🏢"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.markdown(msg["content"])

        if not st.session_state.pq_complete:
            user_input = st.chat_input("Type your message…", key="pq_chat_input")
        else:
            user_input = None
            st.success(
                "✅ Pre-qualification complete. Please switch to the **Vendor Registration** "
                "tab to formally onboard your company."
            )

        if user_input:
            from utils.gemini_client import stream_chat
            st.session_state.pq_messages.append({"role": "user", "content": user_input})
            with chat_box:
                with st.chat_message("user", avatar="🏢"):
                    st.markdown(user_input)
                with st.chat_message("assistant", avatar="⚡"):
                    placeholder = st.empty()
                    full = ""
                    try:
                        for chunk in stream_chat(st.session_state.pq_messages, _get_system_prompt()):
                            full += chunk
                            placeholder.markdown(full + "▌")
                        placeholder.markdown(full)
                    except Exception as e:
                        full = f"Sorry — a brief technical issue. ({str(e)[:80]})"
                        placeholder.markdown(full)

            # Parse [CONFIRM:xxx] markers
            valid_ids = {it["id"] for it in PREQUAL_ITEMS}
            confirms = re.findall(r'\[CONFIRM:(\w+)\]', full)
            for item_id in confirms:
                if item_id in valid_ids:
                    st.session_state.pq_done_items.add(item_id)

            if "[PREQUAL_COMPLETE]" in full:
                st.session_state.pq_complete = True
                for it in PREQUAL_ITEMS:
                    st.session_state.pq_done_items.add(it["id"])

            # Clean the visible message
            clean = re.sub(r'\[CONFIRM:\w+\]\s*', '', full)
            clean = clean.replace('[PREQUAL_COMPLETE]', '').strip()
            st.session_state.pq_messages.append({"role": "assistant", "content": clean})
            st.rerun()
