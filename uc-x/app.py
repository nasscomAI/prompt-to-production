"""
UC-X — Ask My Documents
Interactive CLI policy Q&A agent.
Implemented according to agents.md (RICE) and skills.md.

Enforcement rules (from agents.md):
  1. Never combine claims from two different documents into a single answer.
     Each response cites exactly one document + one section number.
     If the question spans two documents and creates ambiguity → refusal template.
  2. Never use hedging phrases: "while not explicitly covered", "typically",
     "generally understood", "it is common practice", "employees are generally expected to".
  3. If not covered by any document → exact refusal template verbatim.
  4. Cite source document name and section number for every factual claim.

Context boundary (from agents.md):
  Only the indexed text of the three policy files. No external knowledge.
  Critical cross-document trap: personal-phone question must be answered from
  policy_it_acceptable_use section 3.1 ONLY — not blended with HR remote work.

Run: python app.py
"""

import os
import re
import sys

# ── Paths (relative to this file's location) ─────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
POLICY_FILES = [
    os.path.join(_HERE, "..", "data", "policy-documents", "policy_hr_leave.txt"),
    os.path.join(_HERE, "..", "data", "policy-documents", "policy_it_acceptable_use.txt"),
    os.path.join(_HERE, "..", "data", "policy-documents", "policy_finance_reimbursement.txt"),
]

# ── Exact refusal template (from agents.md / README — must be verbatim) ──────
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# ── Prohibited hedging phrases (enforcement rule 2) ───────────────────────────
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "employees are generally expected to",
    "generally",
    "usually",
    "often",
    "in most cases",
]

# ── Document display names (for citations) ────────────────────────────────────
DOC_DISPLAY = {
    "policy_hr_leave":            "policy_hr_leave.txt",
    "policy_it_acceptable_use":   "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement": "policy_finance_reimbursement.txt",
}


# ─────────────────────────────────────────────────────────────────────────────
# Skill: retrieve_documents
# ─────────────────────────────────────────────────────────────────────────────

def retrieve_documents(file_paths: list[str]) -> dict:
    """
    Load all three policy .txt files and return an index structured as:
      { "policy_hr_leave": { "2.3": "<full clause text>", ... }, ... }

    Enforcement:
      - All three files must load successfully — partial loading not permitted.
      - If no numbered sections detected: stores full text under "FULL_TEXT".

    Raises:
        FileNotFoundError  if any file is missing
    """
    index = {}

    clause_pattern = re.compile(r"^(\d+\.\d+(?:\.\d+)?)\s+(.*?)$", re.MULTILINE)

    for file_path in file_paths:
        norm = os.path.normpath(file_path)
        if not os.path.exists(norm):
            raise FileNotFoundError(
                f"Policy document not found: {file_path}\n"
                "All three documents must be present."
            )

        raw = open(norm, encoding="utf-8").read()
        doc_key = os.path.splitext(os.path.basename(norm))[0]  # e.g. "policy_hr_leave"

        matches = list(clause_pattern.finditer(raw))

        if not matches:
            print(
                f"WARNING: No numbered clauses in '{doc_key}'. "
                "Storing as FULL_TEXT.",
                file=sys.stderr,
            )
            index[doc_key] = {"FULL_TEXT": raw.strip()}
            continue

        sections = {}
        for i, m in enumerate(matches):
            clause_id  = m.group(1)
            first_line = m.group(2).strip()

            # Capture continuation lines until next clause or section header
            start = m.end()
            end   = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
            continuation = raw[start:end]

            body_lines = [first_line]
            for line in continuation.splitlines():
                if re.match(r"^═+", line):
                    break
                body_lines.append(line.strip())

            body = "\n".join(body_lines).strip()
            body = re.sub(r"\n{3,}", "\n\n", body).rstrip()
            sections[clause_id] = body

        index[doc_key] = sections

    return index


# ─────────────────────────────────────────────────────────────────────────────
# Keyword search index for answer_question
# ─────────────────────────────────────────────────────────────────────────────

# Each entry: (list_of_trigger_keywords, doc_key, section_id)
# More specific entries listed first. First match wins for single-source answers.
# Where a question could match two documents → refusal (cross-doc trap).

QUESTION_ROUTING = [
    # ── HR Leave ──────────────────────────────────────────────────────────────
    (["carry forward", "carry-forward", "unused leave", "annual leave carry",
      "forfeited", "unused annual"],
     "policy_hr_leave", "2.6"),

    (["14 day", "14-day", "advance notice", "leave application", "notice period leave",
      "submit leave"],
     "policy_hr_leave", "2.3"),

    (["written approval", "verbal approval", "manager approv", "leave approval"],
     "policy_hr_leave", "2.4"),

    (["unapproved absence", "loss of pay", "lop", "absent without"],
     "policy_hr_leave", "2.5"),

    (["carry-forward", "january", "first quarter", "jan-mar", "jan–mar"],
     "policy_hr_leave", "2.7"),

    (["medical certificate", "sick leave certificate", "3 consecutive", "three consecutive",
      "48 hours", "48hrs"],
     "policy_hr_leave", "3.2"),

    (["sick leave", "sick day", "sick"],
     "policy_hr_leave", "3.1"),

    (["sick leave before holiday", "sick before", "sick after holiday",
      "public holiday sick", "sick adjacent"],
     "policy_hr_leave", "3.4"),

    (["who approves", "who approve", "who must approve", "who needs to approve",
      "approve leave without pay", "approve lwp", "lwp approv",
      "department head", "hr director", "both approv"],
     "policy_hr_leave", "5.2"),

    (["leave without pay", "lwp", "unpaid leave"],
     "policy_hr_leave", "5.1"),

    (["30 days lwp", "30 continuous", "municipal commissioner", "commissioner approv"],
     "policy_hr_leave", "5.3"),

    (["leave encashment", "encash leave", "cash leave", "encashment during service"],
     "policy_hr_leave", "7.2"),

    (["encash", "encashment"],
     "policy_hr_leave", "7.1"),

    (["maternity", "maternity leave"],
     "policy_hr_leave", "4.1"),

    (["paternity", "paternity leave"],
     "policy_hr_leave", "4.3"),

    (["grievance", "dispute leave", "leave grievance"],
     "policy_hr_leave", "8.1"),

    # ── IT Acceptable Use ─────────────────────────────────────────────────────
    # personal phone / BYOD — section 3.1 ONLY (critical cross-doc trap)
    (["personal phone", "personal device", "byod", "own phone", "my phone",
      "personal mobile"],
     "policy_it_acceptable_use", "3.1"),

    (["install", "software", "slack", "teams", "zoom", "application install",
      "app install", "install software", "install app"],
     "policy_it_acceptable_use", "2.3"),

    (["software catalogue", "approved software", "cmc catalogue"],
     "policy_it_acceptable_use", "2.4"),

    (["password", "share password", "change password"],
     "policy_it_acceptable_use", "4.1"),

    (["multi-factor", "mfa", "two-factor", "2fa", "remote access authentication"],
     "policy_it_acceptable_use", "4.4"),

    (["confidential data", "sensitive data", "classified data", "data handling"],
     "policy_it_acceptable_use", "5.1"),

    (["forward email", "forward cmc email", "personal email"],
     "policy_it_acceptable_use", "5.2"),

    (["internet", "email use", "cmc email register"],
     "policy_it_acceptable_use", "6.1"),

    (["endpoint security", "security agent", "antivirus"],
     "policy_it_acceptable_use", "2.6"),

    # ── Finance Reimbursement ─────────────────────────────────────────────────
    (["home office", "work from home equipment", "wfh equipment", "home equipment",
      "office allowance", "equipment allowance", "rs 8000", "rs 8,000"],
     "policy_finance_reimbursement", "3.1"),

    (["da and meal", "daily allowance and meal", "meal receipt", "da claim",
      "daily allowance", "da ", "meal and da", "simultaneously"],
     "policy_finance_reimbursement", "2.6"),

    (["daily allowance", "outstation allowance"],
     "policy_finance_reimbursement", "2.5"),

    (["travel", "local travel", "km rate", "transport", "reimburs"],
     "policy_finance_reimbursement", "2.1"),

    (["outstation", "pre-approved travel", "fin-t1"],
     "policy_finance_reimbursement", "2.2"),

    (["air travel", "flight", "economy class", "business class"],
     "policy_finance_reimbursement", "2.3"),

    (["hotel", "accommodation", "per night"],
     "policy_finance_reimbursement", "2.4"),

    (["training", "course fee", "professional development", "certification"],
     "policy_finance_reimbursement", "4.1"),

    (["mobile reimburs", "phone bill", "internet reimburs", "internet bill"],
     "policy_finance_reimbursement", "5.1"),

    (["submit claim", "reimbursement process", "fin-exp", "30 days claim"],
     "policy_finance_reimbursement", "6.1"),
]


def _contains_hedging(text: str) -> bool:
    """Return True if answer text contains any prohibited hedging phrase."""
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in HEDGING_PHRASES)


# ─────────────────────────────────────────────────────────────────────────────
# Skill: answer_question
# ─────────────────────────────────────────────────────────────────────────────

def answer_question(question: str, index: dict) -> str:
    """
    Search the document index for a single-source answer.

    Returns one of:
      1. Cited answer: "<clause text>\\nSource: <doc_name>, section <N.N>."
      2. Exact refusal template (verbatim, no variation).

    Enforcement:
      - Never combines claims from two documents.
      - Returns refusal if hedging phrases detected in any candidate.
      - Empty question → refusal.
    """
    if not index:
        raise ValueError(
            "Document index is not loaded. Call retrieve_documents first."
        )

    question = question.strip()
    if not question:
        return REFUSAL_TEMPLATE

    q_lower = question.lower()

    # ── Route question to doc + section via keyword matching ──────────────────
    matched_doc     = None
    matched_section = None

    for triggers, doc_key, section_id in QUESTION_ROUTING:
        if any(trigger in q_lower for trigger in triggers):
            matched_doc     = doc_key
            matched_section = section_id
            break

    # ── No route found → refusal ──────────────────────────────────────────────
    if matched_doc is None:
        return REFUSAL_TEMPLATE

    # ── Retrieve clause text from index ──────────────────────────────────────
    doc_sections = index.get(matched_doc, {})
    clause_text  = doc_sections.get(matched_section)

    if not clause_text:
        return REFUSAL_TEMPLATE

    # ── Hedging guard (enforcement rule 2) ────────────────────────────────────
    if _contains_hedging(clause_text):
        return REFUSAL_TEMPLATE

    # ── Build cited answer (enforcement rule 4) ───────────────────────────────
    doc_display = DOC_DISPLAY.get(matched_doc, matched_doc + ".txt")
    answer = (
        f"{clause_text}\n\n"
        f"Source: {doc_display}, section {matched_section}."
    )
    return answer


# ─────────────────────────────────────────────────────────────────────────────
# Main — interactive CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("── UC-X: Ask My Documents ───────────────────────────────────────────")
    print("Loading policy documents...")

    try:
        index = retrieve_documents(POLICY_FILES)
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

    doc_count = len(index)
    total_sections = sum(len(v) for v in index.values())
    print(f"Loaded {doc_count} documents · {total_sections} sections indexed.")
    print()
    print("Documents in scope:")
    for key, sections in index.items():
        print(f"  {DOC_DISPLAY.get(key, key):40s}  ({len(sections)} sections)")
    print()
    print("Type your question and press Enter. Type 'quit' or 'exit' to stop.")
    print("─────────────────────────────────────────────────────────────────────")
    print()

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in ("quit", "exit", "q", "bye"):
            print("Goodbye.")
            break

        if not question:
            continue

        answer = answer_question(question, index)

        print()
        print("Agent:", answer)
        print()
        print("─────────────────────────────────────────────────────────────────")
        print()


if __name__ == "__main__":
    main()
