"""
Orchestrator — manages the conversation state machine and Gemini system prompts.

Phases:
  WELCOME       → collect company name + description
  PHASE_A       → confirm industry, collect size/location/group structure
  AGENTS_READY  → signal to run background agents (KYC/AML/risk/news)
  PHASE_B       → collect industry-specific documents one by one
  VALIDATION    → summarise findings, flag one mock issue
  ARIBA         → animate Ariba submission
  COMPLETE      → done
"""

from utils.industry_config import get_profile, INDUSTRY_PROFILES

# ── System prompt template ────────────────────────────────────────────────────

_BASE_SYSTEM = """
You are ARIA (Automated Registration & Intelligence Assistant), Centrica's AI-powered vendor onboarding assistant.

Your role: guide new vendors through Centrica's procurement onboarding process — professionally, warmly, and efficiently.

CENTRICA CONTEXT:
- Centrica is a leading UK energy and services company (British Gas, Hive, etc.)
- You represent the Procurement Transformation team
- All onboarding is subject to Centrica's Supplier Code of Conduct
- You speak British English

STYLE RULES:
- Professional but friendly and approachable
- Concise: 2–4 sentences per response in normal flow
- Never ask more than one question at a time
- Never mention this is a demo or that data is simulated
- Never say "As an AI" or reveal you are a language model
- Present all gathered data as real and verified
- Use "we" and "our" when referring to Centrica

CURRENT VENDOR INFO COLLECTED:
{vendor_info_summary}

CURRENT PHASE: {phase}

PHASE INSTRUCTIONS:
{phase_instructions}
"""

_PHASE_INSTRUCTIONS = {
    "WELCOME": """
Your goal: warmly greet the vendor and ask for (1) their company name and (2) a brief description of what they supply or what services they offer.
Keep the welcome short — one greeting paragraph, then ask the question.
Example opener: "Welcome to Centrica's supplier onboarding portal. I'm ARIA, and I'll be guiding you through the registration process today — it should only take a few minutes..."
""",

    "PHASE_A": """
You have detected the vendor's industry as: {industry_label}.
Your goal in this phase:
1. Confirm the industry classification with the vendor (one sentence, e.g. "I can see you're in the {industry_label} sector — is that right?")
2. Then ask: are they UK-based or international?
3. Then ask: roughly how many employees / what size is the business? (micro <10, small 10-49, medium 50-249, large 250+)
4. Then ask: are they part of a larger group or parent company?
Ask ONE question at a time. Move on once each is answered.
When you have all four answers, say: "Thank you — I now have enough to run the initial background checks. Give me a moment..."
Then output this exact marker on its own line: [TRIGGER_AGENTS]
""",

    "AGENTS_RUNNING": """
The background agents are currently running. Say something brief and reassuring, e.g.:
"I'm running our standard background checks in parallel — this covers company verification, sanctions screening, credit assessment, and a news search. I'll be back with you shortly."
Do not ask any questions in this message.
""",

    "PHASE_B": """
Background checks are complete and all clear.
Vendor industry: {industry_label}
Required documents for this industry: {required_docs_list}
Documents already confirmed: {confirmed_docs}

Your goal: request the required documents one at a time, conversationally.
- Start by briefly summarising the background check results (1-2 sentences, positive framing)
- Then say you now need a few industry-specific documents
- Request ONE document per message — give its name, what format it should be in, and WHY Centrica needs it
- When the vendor confirms, acknowledge warmly and move to the next document
- After all documents are confirmed, say: "Excellent — I have everything I need. Let me run a final validation check..."
  Then output: [TRIGGER_VALIDATION]
""",

    "VALIDATION": """
You are running a final validation. Present results as if you have just received them.
- Summarise the full picture briefly (2-3 sentences)
- Mention ONE minor flag (e.g. "I noticed the bank account holder name doesn't exactly match your registered company name — this is common and I've flagged it for a quick manual review, but it won't delay your registration.")
- Recommend proceeding
- Say: "I'm now going to submit your vendor record to Ariba SLP and generate your DocuSign onboarding pack."
Then output: [TRIGGER_ARIBA]
""",

    "COMPLETE": """
The Ariba submission is complete. The vendor record has been successfully registered.
Congratulate the vendor warmly.
Summarise: their Ariba reference, go-live date, payment terms, and that a DocuSign pack is on its way.
End with an offer to answer any questions.
""",
}


class Orchestrator:
    def __init__(self):
        self.phase = "WELCOME"
        self.vendor_info: dict = {}
        self.confirmed_docs: list[str] = []
        self.doc_index: int = 0

    def get_system_prompt(self) -> str:
        phase = self.phase
        info = self.vendor_info
        industry = info.get("industry", "general")
        profile = get_profile(industry)

        vendor_summary_parts = []
        if info.get("company_name"):
            vendor_summary_parts.append(f"Company: {info['company_name']}")
        if info.get("industry"):
            vendor_summary_parts.append(f"Industry: {profile['label']}")
        if info.get("size"):
            vendor_summary_parts.append(f"Size: {info['size']}")
        if info.get("is_uk") is not None:
            vendor_summary_parts.append(f"Location: {'UK' if info.get('is_uk') else info.get('country', 'International')}")
        if info.get("group_structure"):
            vendor_summary_parts.append(f"Group: {info['group_structure']}")
        vendor_summary = "\n".join(vendor_summary_parts) if vendor_summary_parts else "Nothing collected yet."

        instructions_template = _PHASE_INSTRUCTIONS.get(phase, "")
        instructions = instructions_template.format(
            industry_label=profile["label"],
            required_docs_list=", ".join(d["name"] for d in profile["required_docs"]),
            confirmed_docs=", ".join(self.confirmed_docs) if self.confirmed_docs else "None yet",
        )

        return _BASE_SYSTEM.format(
            vendor_info_summary=vendor_summary,
            phase=phase,
            phase_instructions=instructions,
        )

    def update_vendor_info(self, key: str, value) -> None:
        self.vendor_info[key] = value

    def advance_to_agents_running(self) -> None:
        self.phase = "AGENTS_RUNNING"

    def advance_to_phase_b(self) -> None:
        self.phase = "PHASE_B"

    def advance_to_validation(self) -> None:
        self.phase = "VALIDATION"

    def advance_to_complete(self) -> None:
        self.phase = "COMPLETE"

    def get_next_required_doc(self) -> dict | None:
        profile = get_profile(self.vendor_info.get("industry", "general"))
        docs = profile["required_docs"]
        remaining = [d for d in docs if d["id"] not in self.confirmed_docs]
        return remaining[0] if remaining else None

    def confirm_doc(self, doc_id: str) -> None:
        if doc_id not in self.confirmed_docs:
            self.confirmed_docs.append(doc_id)

    def all_docs_confirmed(self) -> bool:
        profile = get_profile(self.vendor_info.get("industry", "general"))
        return all(d["id"] in self.confirmed_docs for d in profile["required_docs"])

    def get_phase_label(self) -> str:
        labels = {
            "WELCOME": "Welcome",
            "PHASE_A": "Pre-Qualification",
            "AGENTS_RUNNING": "Background Checks",
            "PHASE_B": "Document Collection",
            "VALIDATION": "Validation",
            "ARIBA": "Ariba Submission",
            "COMPLETE": "Complete",
        }
        return labels.get(self.phase, self.phase)

    def get_phase_number(self) -> int:
        order = ["WELCOME", "PHASE_A", "AGENTS_RUNNING", "PHASE_B", "VALIDATION", "ARIBA", "COMPLETE"]
        try:
            return order.index(self.phase)
        except ValueError:
            return 0
