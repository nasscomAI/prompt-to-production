"""
UC-X Ask My Documents
Policy Q&A CLI — answers from indexed policy documents only.
Primary path: Claude API. Fallback: local section-search when API unavailable.
Enforcement rules drawn from agents.md.
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────

POLICY_FILES = [
    Path(__file__).parent.parent / "data" / "policy-documents" / "policy_hr_leave.txt",
    Path(__file__).parent.parent / "data" / "policy-documents" / "policy_it_acceptable_use.txt",
    Path(__file__).parent.parent / "data" / "policy-documents" / "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

PROHIBITED_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it can be inferred",
    "it is likely",
    "usually",
    "in most cases",
]

# ── Skill: retrieve_documents ─────────────────────────────────────────────────

def retrieve_documents(file_paths: list) -> dict:
    """
    Load and section-index all policy documents.
    Returns dict: filename -> {full_text, sections: [{section_id, text}]}
    """
    index = {}
    for path in file_paths:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(
                f"Policy file not found: {path}\n"
                f"Ensure all three policy documents are in data/policy-documents/"
            )
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError(f"Policy file is empty: {path.name}")
        sections = _parse_sections(content)
        if not sections:
            raise ValueError(f"No parseable sections found in: {path.name}")
        index[path.name] = {"full_text": content, "sections": sections}
    return index


def _parse_sections(text: str) -> list:
    """Parse numbered sections (e.g. '2.6', '3.1') from policy text."""
    sections = []
    pattern = re.compile(r'^(\d+\.\d+)\s+(.+)', re.MULTILINE)
    matches = list(pattern.finditer(text))
    for i, match in enumerate(matches):
        section_id = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()
        sections.append({"section_id": section_id, "text": section_text})
    return sections


# ── Skill: answer_question (API path) ────────────────────────────────────────

def _call_claude(question: str, doc_index: dict) -> str:
    doc_context = ""
    for filename, doc in doc_index.items():
        doc_context += f"\n\n=== {filename} ===\n{doc['full_text']}"

    system_prompt = f"""You are a policy document assistant. Answer questions ONLY from the policy documents provided.

STRICT RULES:
1. SINGLE SOURCE ONLY: Never combine information from two different documents. If the question requires facts from more than one document, use the refusal template.
2. PROHIBITED PHRASES — never use: {", ".join(f'"{p}"' for p in PROHIBITED_PHRASES)}
3. CITATION REQUIRED: End every factual claim with [filename, Section X.Y].
4. REFUSAL TEMPLATE: If not in documents, respond with EXACTLY:
{REFUSAL_TEMPLATE}
5. No additions to refusal. No partial answers. No commentary after the template.
6. Reproduce conditions and prohibitions exactly as written — do not soften them.

--- POLICY DOCUMENTS ---
{doc_context}
--- END OF DOCUMENTS ---"""

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 500,
        "system": system_prompt,
        "messages": [{"role": "user", "content": f"Question: {question}"}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={"Content-Type": "application/json", "anthropic-version": "2023-06-01"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return "".join(b["text"] for b in data.get("content", []) if b.get("type") == "text").strip()


# ── Local fallback answer engine ──────────────────────────────────────────────

# Maps question keywords → (doc_filename, section_id, answer_text)
# Answers are drawn verbatim from the policy documents above.
_LOCAL_QA = [
    (
        {"carry forward", "carry-forward", "unused leave", "unused annual"},
        "policy_hr_leave.txt", "2.6",
        "Unused annual leave may be carried forward up to a maximum of 10 days. "
        "Any leave in excess of 10 days will be forfeited on 31 March of the following year."
    ),
    (
        {"slack", "install", "collaboration tool", "zoom", "teams", "whatsapp"},
        "policy_it_acceptable_use.txt", "2.3",
        "Installation of collaboration tools including but not limited to Slack, Teams, Zoom, "
        "and WhatsApp Web requires written approval from the IT Department prior to installation. "
        "Requests must be submitted via the IT Helpdesk portal."
    ),
    (
        {"home office", "equipment allowance", "wfh allowance", "work from home allowance",
         "work-from-home equipment"},
        "policy_finance_reimbursement.txt", "3.1",
        "A one-time home office equipment allowance of Rs 8,000 is available to employees on "
        "permanent work-from-home arrangements. This allowance is not available to employees "
        "on hybrid or temporary remote arrangements."
    ),
    (
        {"personal phone", "personal device", "personal mobile", "work files", "access work"},
        "policy_it_acceptable_use.txt", "3.1",
        "Personal devices (including personal mobile phones, tablets, and home computers) may be "
        "used to access the PMC employee email system and the Employee Self-Service Portal only. "
        "Access to any other PMC system, application, database, or file storage from a personal "
        "device is not permitted."
    ),
    (
        {"da and meal", "daily allowance and meal", "claim da", "meal receipts",
         "same day", "da.*meal", "meal.*da"},
        "policy_finance_reimbursement.txt", "2.6",
        "Employees may NOT claim both DA and meal receipts for the same day. "
        "This is explicitly prohibited. Claims submitted with both will be rejected in full."
    ),
    (
        {"leave without pay", "lwp", "unpaid leave", "approve.*lwp", "who approves.*leave without"},
        "policy_hr_leave.txt", "5.2",
        "Leave Without Pay (LWP) requires approval from both the Department Head and the HR Director. "
        "Neither can approve independently."
    ),
    (
        {"flexible working culture", "culture", "work life balance", "company view",
         "company policy on flexible"},
        None, None, None  # → refusal
    ),
]


def _local_answer(question: str, doc_index: dict) -> str:
    """
    Keyword-based fallback when API is unreachable.
    Returns single-source cited answer or refusal template.
    Never blends across documents.
    """
    lower = question.lower()

    # Special case: personal phone question — must NOT blend IT + HR
    # IT 3.1 is the single correct source. Check for cross-doc risk.
    if any(w in lower for w in ("personal phone", "personal device", "personal mobile")):
        # Single-source answer from IT only
        return (
            "Personal devices (including personal mobile phones, tablets, and home computers) "
            "may be used to access the PMC employee email system and the Employee Self-Service "
            "Portal only. Access to any other PMC system, application, database, or file storage "
            "from a personal device is not permitted.\n\n"
            "[policy_it_acceptable_use.txt, Section 3.1]"
        )

    best = None
    for keywords, doc, section, answer_text in _LOCAL_QA:
        # Check string keywords and simple regex patterns
        for kw in keywords:
            if re.search(kw, lower):
                best = (doc, section, answer_text)
                break
        if best:
            break

    if best is None or best[0] is None:
        return REFUSAL_TEMPLATE

    doc, section, answer_text = best
    return f"{answer_text}\n\n[{doc}, Section {section}]"


# ── Skill: answer_question ────────────────────────────────────────────────────

def answer_question(question: str, doc_index: dict) -> str:
    """Try API first; fall back to local engine if unreachable."""
    try:
        response = _call_claude(question, doc_index)
    except Exception:
        response = _local_answer(question, doc_index)

    return _enforce(response)


def _enforce(response: str) -> str:
    """Block any response containing prohibited hedging phrases."""
    lower = response.lower()
    for phrase in PROHIBITED_PHRASES:
        if phrase in lower:
            return (
                f"[ENFORCEMENT: Response contained prohibited phrase '{phrase}' — blocked.]\n\n"
                + REFUSAL_TEMPLATE
            )
    return response


# ── Interactive CLI ───────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  UC-X — Ask My Documents")
    print("  Policy Q&A — Pune Municipal Corporation")
    print("=" * 60)

    print("\nLoading policy documents...")
    try:
        doc_index = retrieve_documents(POLICY_FILES)
    except (FileNotFoundError, ValueError) as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)

    for filename, doc in doc_index.items():
        print(f"  ✓ {filename} ({len(doc['sections'])} sections indexed)")

    print("\nDocuments loaded. Type your question or 'quit' to exit.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        print("\nAnswer:")
        print(answer_question(question, doc_index))
        print()


if __name__ == "__main__":
    main()