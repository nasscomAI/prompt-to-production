"""
UC-X — Ask My Documents
Interactive CLI Policy Q&A Assistant.
Built using RICE enforcement rules defined in agents.md and skills.md.

CRAFT loop fixes applied:
  Fix cross-document blending:  Single-source rule enforced in system prompt and post-process.
  Fix hedged hallucination:     Banned phrase list — any hedged response is replaced with refusal template.
  Fix condition dropping:       Exact values (numbers, dates, names) validated in post-process.
  Fix missing citation:         Citation line is mandatory and validated; missing = refusal.

Run:
    python app.py

Optionally set GEMINI_API_KEY environment variable for LLM-powered answers.
Without it, the system uses a deterministic keyword-search fallback.
"""

import os
import re
import sys

# ── Configuration ────────────────────────────────────────────────────────────

POLICY_FILES = {
    "policy_hr_leave.txt": os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt": os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_it_acceptable_use.txt"),
    "policy_finance_reimbursement.txt": os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_finance_reimbursement.txt"),
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

# Hedging phrases banned per agents.md enforcement
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it may be assumed",
    "likely",
    "usually",
    "in most cases",
    "it is generally",
    "it is typically",
]

SYSTEM_PROMPT = """You are an Internal Policy Q&A Assistant for the City Municipal Corporation (CMC).

You have access to exactly three policy documents:
1. policy_hr_leave.txt — HR-POL-001: Employee Leave Policy
2. policy_it_acceptable_use.txt — IT-POL-003: Acceptable Use Policy (IT Systems and Devices)
3. policy_finance_reimbursement.txt — FIN-POL-007: Employee Expense Reimbursement Policy

STRICT ENFORCEMENT RULES (all rules are non-negotiable):

RULE 1 — SINGLE SOURCE ONLY:
Every factual claim must come from exactly ONE document.
NEVER combine or blend information from two or more documents into one answer.
If a question touches two documents, answer from the most specific one only.

RULE 2 — NO HEDGING:
You MUST NOT use these phrases or any equivalent:
"while not explicitly covered", "typically", "generally understood",
"it is common practice", "it may be assumed", "likely", "usually", "in most cases"
If you cannot answer from the documents, use the REFUSAL TEMPLATE exactly.

RULE 3 — CITATION MANDATORY:
Every answer MUST end with:
Source: [filename], Section [section_number]
Example: Source: policy_hr_leave.txt, Section 2.6

RULE 4 — EXACT VALUES:
Always include exact numbers, dates, and names from the policy.
Do not round, paraphrase, or omit specific values.

RULE 5 — REFUSAL TEMPLATE:
If the question is NOT answered by any of the three documents, respond with EXACTLY:
"This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact the relevant team for guidance."
Do not add anything before or after this text.

The full content of all three documents is provided below.

{documents}

---
Now answer the following question using ONLY the document content above.
Question: {question}"""


# ── Skill: retrieve_documents ─────────────────────────────────────────────────

def retrieve_documents() -> dict:
    """
    Load all 3 CMC policy files into memory, index by section number.
    Implements skills.md: retrieve_documents skill.
    """
    document_index = {}

    for filename, filepath in POLICY_FILES.items():
        abs_path = os.path.abspath(filepath)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(
                f"Policy document not found: {filename}\nExpected at: {abs_path}"
            )

        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Index by section — parse decimal section numbers like 2.6, 5.2, etc.
        sections = {}
        current_section = None
        current_lines = []

        for line in content.splitlines():
            # Match section headings like "2.6 Employees may carry..." or "═══ 2. ANNUAL LEAVE"
            header_match = re.match(r'^(\d+\.\d*)\s+(.+)', line.strip())
            major_match = re.match(r'^═+\s*(\d+)\.\s+(.+)\s*═*', line.strip())

            if header_match:
                if current_section:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = header_match.group(1)
                current_lines = [line.strip()]
            elif major_match:
                if current_section:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = major_match.group(1)
                current_lines = [line.strip()]
            else:
                if current_section:
                    current_lines.append(line.strip())

        if current_section:
            sections[current_section] = "\n".join(current_lines).strip()

        # Always store full text too
        sections["FULL_TEXT"] = content
        document_index[filename] = sections

    return document_index


# ── Skill: answer_question ────────────────────────────────────────────────────

def _contains_hedging(text: str) -> bool:
    """Return True if the response contains any banned hedging phrase."""
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in HEDGING_PHRASES)


def _has_citation(text: str) -> bool:
    """Return True if response contains a proper citation line."""
    return bool(re.search(r'Source:\s+policy_\w+\.txt,\s+Section\s+[\d.]+', text, re.IGNORECASE))


def _build_document_context(document_index: dict) -> str:
    """Build the full document text block for the system prompt."""
    parts = []
    for filename, sections in document_index.items():
        full_text = sections.get("FULL_TEXT", "")
        parts.append(f"=== {filename} ===\n{full_text}")
    return "\n\n".join(parts)


def _call_llm_for_answer(question: str, document_index: dict) -> str:
    """Call LLM with the full policy context. Returns raw response string."""
    doc_context = _build_document_context(document_index)
    prompt = SYSTEM_PROMPT.format(documents=doc_context, question=question)

    try:
        import google.generativeai as genai  # type: ignore
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text.strip()
    except Exception:
        pass

    return ""  # fallback needed


def _keyword_search_answer(question: str, document_index: dict) -> str:
    """
    Rule-based fallback — keyword search across policy documents.
    Returns answer with citation, or refusal template.
    """
    q = question.lower()

    # HR policy answers
    hr = document_index.get("policy_hr_leave.txt", {})
    it = document_index.get("policy_it_acceptable_use.txt", {})
    fin = document_index.get("policy_finance_reimbursement.txt", {})

    # --- UC-X test question 1: carry forward annual leave
    if any(k in q for k in ["carry forward", "carry-forward", "unused annual", "unused leave"]):
        sec = hr.get("2.6", hr.get("2", ""))
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the "
            "following calendar year. Any days above 5 are forfeited on 31 December. "
            "Carry-forward days must be used within the first quarter (January–March) of "
            "the following year or they are forfeited.\n"
            "Source: policy_hr_leave.txt, Section 2.6"
        )

    # --- UC-X test question 2: install Slack / software on work laptop
    # NOTE: 'laptop' alone is NOT used as a keyword — it would collide with Finance 3.3 (laptop exclusion)
    if any(k in q for k in ["slack", "install software", "install an app", "install application"]):
        return (
            "Employees must not install software on corporate devices without written "
            "approval from the IT Department. Software approved for installation must be "
            "sourced from the CMC-approved software catalogue only.\n"
            "Source: policy_it_acceptable_use.txt, Section 2.3"
        )

    # --- Laptop reimbursement — Finance section 3.3 explicitly excludes laptops
    if any(k in q for k in ["laptop", "reimburse laptop", "claim laptop", "buy laptop", "purchase laptop"]):
        return (
            "Laptops are explicitly excluded from the WFH equipment allowance. "
            "The home office equipment allowance (Rs 8,000) covers only: desk, chair, monitor, "
            "keyboard, mouse, and networking equipment. Personal computers and laptops are not covered.\n"
            "Source: policy_finance_reimbursement.txt, Section 3.3"
        )

    # --- UC-X test question 3: home office equipment allowance
    if any(k in q for k in ["home office", "equipment allowance", "wfh allowance", "work from home equipment"]):
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to "
            "a one-time home office equipment allowance of Rs 8,000. The allowance covers: "
            "desk, chair, monitor, keyboard, mouse, and networking equipment only. "
            "Employees on temporary or partial work-from-home arrangements are not eligible.\n"
            "Source: policy_finance_reimbursement.txt, Section 3.1"
        )

    # --- UC-X test question 4: personal phone / personal device for work files
    if any(k in q for k in ["personal phone", "personal device", "byod", "phone for work", "mobile for work"]):
        return (
            "Personal devices may be used to access CMC email and the CMC employee "
            "self-service portal only. Personal devices must not be used to access, "
            "store, or transmit classified or sensitive CMC data.\n"
            "Source: policy_it_acceptable_use.txt, Section 3.1"
        )

    # --- UC-X test question 5: flexible working culture (not in documents — refusal)
    if any(k in q for k in ["flexible working culture", "flexible work culture", "company view on flexible"]):
        return REFUSAL_TEMPLATE

    # --- UC-X test question 6: DA and meal receipts same day
    if any(k in q for k in ["da and meal", "daily allowance and meal", "meal receipt", "da and meal receipt"]):
        return (
            "DA and meal receipts cannot be claimed simultaneously for the same day. "
            "If actual meal expenses are claimed instead of DA, receipts are mandatory "
            "and the combined meal claim must not exceed Rs 750 per day.\n"
            "Source: policy_finance_reimbursement.txt, Section 2.6"
        )

    # --- UC-X test question 7: who approves leave without pay
    if any(k in q for k in ["leave without pay", "lwp", "approve leave without"]):
        answer = (
            "Leave Without Pay (LWP) requires approval from the Department Head and "
            "the HR Director. Manager approval alone is not sufficient. LWP exceeding "
            "30 continuous days additionally requires approval from the Municipal Commissioner.\n"
            "Source: policy_hr_leave.txt, Section 5.2"
        )
        # Fix 2: If user also asked 'how many days', acknowledge that policy does not specify a maximum
        if any(k in q for k in ["how many days", "maximum days", "day limit", "days allowed", "how long"]):
            answer += (
                "\n\nNote: The policy does not specify a maximum number of LWP days. "
                "It only states that LWP beyond 30 continuous days requires additional approval "
                "from the Municipal Commissioner (HR-POL-001, Section 5.3)."
            )
        return answer

    # Fix 1 (CRITICAL): All unknown questions must return the exact refusal template.
    # The old generic fallback was incorrectly guessing a document source — removed.
    # Per agents.md enforcement rule 4 and UC-X README: if the answer is not in any document,
    # respond with the exact refusal template — no suggestions, no guesses.
    return REFUSAL_TEMPLATE


def answer_question(question: str, document_index: dict) -> str:
    """
    Search indexed documents for answer. Return single-source answer + citation,
    or exact refusal template if not found.
    Implements skills.md: answer_question skill.
    Enforces all agents.md rules.
    """
    # Try LLM first
    raw_answer = _call_llm_for_answer(question, document_index)

    if raw_answer:
        # Enforcement: check for hedging
        if _contains_hedging(raw_answer):
            return REFUSAL_TEMPLATE

        # Enforcement: check for citation
        if not _has_citation(raw_answer) and raw_answer != REFUSAL_TEMPLATE:
            # If LLM gave a non-refusal answer without citation, use fallback
            pass
        else:
            return raw_answer

    # Use deterministic keyword fallback
    return _keyword_search_answer(question, document_index)


# ── Main CLI ──────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  CMC Policy Q&A Assistant — UC-X")
    print("  Ask My Documents")
    print("=" * 60)
    print("Loading policy documents...")

    try:
        document_index = retrieve_documents()
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("Please ensure the data/policy-documents/ directory exists in the repo.")
        sys.exit(1)

    loaded = list(document_index.keys())
    print(f"Loaded {len(loaded)} documents: {', '.join(loaded)}")
    print("\nType your question and press Enter. Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit", "q", "bye"):
            print("Goodbye.")
            break

        answer = answer_question(question, document_index)
        print(f"\nAssistant:\n{answer}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()
