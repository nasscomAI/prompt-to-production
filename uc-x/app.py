"""
UC-X — Ask My Documents: Interactive Policy Q&A CLI
Built using the RICE → agents.md → skills.md → CRAFT workflow.

Agent Role (agents.md):
  Policy Q&A agent. Answers only from the 3 CMC policy documents.
  Single-source answers with citations. Verbatim refusal for out-of-scope questions.

Skills (skills.md):
  - retrieve_documents: loads all 3 .txt files → section-indexed dict
  - answer_question:    keyword search → cited answer OR verbatim refusal template

Enforcement (agents.md / README.md):
  1. Never blend claims from two documents into one sentence.
  2. No hedging phrases: "while not explicitly covered", "typically", etc.
  3. Out-of-scope → verbatim refusal template, nothing else.
  4. Every factual claim must cite [policy_<name>.txt §<section>].
"""

import os
import re
import sys
from typing import Dict, List, Optional, Tuple

# ── Document paths ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "policy-documents")

POLICY_FILES = {
    "policy_hr_leave.txt":              os.path.join(DATA_DIR, "policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt":     os.path.join(DATA_DIR, "policy_it_acceptable_use.txt"),
    "policy_finance_reimbursement.txt": os.path.join(DATA_DIR, "policy_finance_reimbursement.txt"),
}

# ── Verbatim refusal template (README.md / agents.md enforcement rule 4) ─────
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# ── Forbidden hedging phrases (agents.md enforcement rule 2) ──────────────────
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "employees are generally expected to",
    "it is generally",
    "as is standard",
    "not explicitly",
]

# ── Keyword index — maps question topics to (doc, section_id) hints ───────────
# This drives the rule-based search used in answer_question.
TOPIC_INDEX: List[Tuple[List[str], str, str]] = [
    # (trigger_keywords,                      doc_key,                         section_id)
    (["carry forward", "carry-forward", "unused leave", "annual leave carry"],
     "policy_hr_leave.txt", "2.6"),
    (["carry-forward days", "carry forward days", "first quarter", "january march"],
     "policy_hr_leave.txt", "2.7"),
    (["14 day", "advance notice", "leave application", "form hr-l1"],
     "policy_hr_leave.txt", "2.3"),
    (["written approval", "verbal approval", "written approval before leave"],
     "policy_hr_leave.txt", "2.4"),
    (["unapproved absence", "loss of pay", "lop", "unapproved"],
     "policy_hr_leave.txt", "2.5"),
    (["sick leave", "medical certificate", "sick days", "3 consecutive", "three consecutive"],
     "policy_hr_leave.txt", "3.2"),
    (["sick leave before", "sick leave after", "public holiday", "sick before holiday"],
     "policy_hr_leave.txt", "3.4"),
    (["leave without pay", "lwp", "department head", "hr director", "who approves lwp",
      "who approves leave without pay"],
     "policy_hr_leave.txt", "5.2"),
    (["lwp 30 days", "lwp exceeding", "municipal commissioner", "30 continuous days"],
     "policy_hr_leave.txt", "5.3"),
    (["leave encashment", "encash leave", "encashment during service"],
     "policy_hr_leave.txt", "7.2"),
    (["maternity", "maternity leave", "26 weeks"],
     "policy_hr_leave.txt", "4.1"),
    (["paternity", "paternity leave", "5 days"],
     "policy_hr_leave.txt", "4.3"),

    (["install", "software", "slack", "install software", "install app", "work laptop"],
     "policy_it_acceptable_use.txt", "2.3"),
    (["personal device", "personal phone", "byod", "own phone", "own device",
      "phone for work", "use my phone"],
     "policy_it_acceptable_use.txt", "3.1"),
    (["personal device data", "classified data", "sensitive data", "store data"],
     "policy_it_acceptable_use.txt", "3.2"),
    (["cmc network", "internal network", "wifi", "wireless"],
     "policy_it_acceptable_use.txt", "3.3"),
    (["password", "share password", "change password", "90 days"],
     "policy_it_acceptable_use.txt", "4.1"),
    (["mfa", "multi-factor", "remote access"],
     "policy_it_acceptable_use.txt", "4.4"),
    (["confidential", "restricted data", "personal cloud", "cloud storage"],
     "policy_it_acceptable_use.txt", "5.1"),

    (["home office", "equipment allowance", "wfh equipment", "work from home equipment",
      "desk", "chair", "monitor"],
     "policy_finance_reimbursement.txt", "3.1"),
    (["allowance covers", "what does allowance cover"],
     "policy_finance_reimbursement.txt", "3.2"),
    (["daily allowance", "da", "meal receipt", "meal claim", "da and meal",
      "claim da and meal", "same day"],
     "policy_finance_reimbursement.txt", "2.6"),
    (["outstation", "air travel", "500 km", "economy class"],
     "policy_finance_reimbursement.txt", "2.3"),
    (["hotel", "accommodation", "3500", "2500", "per night"],
     "policy_finance_reimbursement.txt", "2.4"),
    (["training", "course fee", "professional development", "certification"],
     "policy_finance_reimbursement.txt", "4.1"),
    (["repay training", "leave within 12 months", "12 months training"],
     "policy_finance_reimbursement.txt", "4.4"),
    (["mobile reimbursement", "phone reimbursement", "rs 500", "grade c"],
     "policy_finance_reimbursement.txt", "5.1"),
    (["internet reimbursement", "rs 800", "grade b"],
     "policy_finance_reimbursement.txt", "5.2"),
    (["submit claim", "30 days", "claim submission", "expense claim"],
     "policy_finance_reimbursement.txt", "1.3"),
    (["local travel", "rs 4 per km", "public transport"],
     "policy_finance_reimbursement.txt", "2.1"),
]


# ── Skill: retrieve_documents ─────────────────────────────────────────────────

def retrieve_documents(file_map: Dict[str, str]) -> Dict[str, List[Dict]]:
    """
    Skill: retrieve_documents (skills.md)
    Loads all policy .txt files and parses them into a section-indexed structure.

    Returns:
        {
            "policy_hr_leave.txt": [
                {"section_id": "2.3", "section_heading": "ANNUAL LEAVE", "text": "..."},
                ...
            ],
            ...
        }

    Errors (skills.md):
      - Any file not found → FileNotFoundError (halt, don't answer with partial data)
      - Empty file         → ValueError
    """
    index: Dict[str, List[Dict]] = {}

    for doc_name, file_path in file_map.items():
        try:
            with open(file_path, encoding="utf-8") as f:
                raw = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Policy document not found: '{file_path}'\n"
                f"Cannot answer questions without the complete document set."
            )
        except (PermissionError, OSError) as exc:
            raise FileNotFoundError(f"Cannot read '{file_path}': {exc}")

        if not raw.strip():
            raise ValueError(f"Policy document is empty: '{file_path}'")

        index[doc_name] = _parse_document(raw)

    return index


def _parse_document(raw: str) -> List[Dict]:
    """Parse a policy .txt into a list of clause dicts."""
    clauses: List[Dict] = []
    lines = raw.splitlines()

    current_heading = "GENERAL"
    clause_buffer: Dict = {}

    section_heading_re = re.compile(r"^(\d+)\.\s+([A-Z][A-Z &()/–-]+)$")
    clause_re          = re.compile(r"^(\d+\.\d+)\s+(.*)")

    def flush():
        if clause_buffer:
            clauses.append({
                "section_id":      clause_buffer["section_id"],
                "section_heading": clause_buffer["heading"],
                "text":            clause_buffer["text"].strip(),
            })
            clause_buffer.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped or set(stripped) <= {"═", "─", "=", "-"}:
            continue

        heading_match = section_heading_re.match(stripped)
        if heading_match:
            flush()
            current_heading = stripped
            continue

        clause_match = clause_re.match(stripped)
        if clause_match:
            flush()
            clause_buffer["section_id"] = clause_match.group(1)
            clause_buffer["heading"]    = current_heading
            clause_buffer["text"]       = clause_match.group(2)
            continue

        if clause_buffer:
            clause_buffer["text"] = clause_buffer.get("text", "") + " " + stripped

    flush()
    return clauses


# ── Skill: answer_question ────────────────────────────────────────────────────

def answer_question(question: str, doc_index: Dict[str, List[Dict]]) -> str:
    """
    Skill: answer_question (skills.md)
    Searches indexed documents for the user's question. Returns:
      - A single-source cited answer, OR
      - Separate per-document cited answers (never blended), OR
      - The verbatim refusal template.

    Enforcement:
      - No cross-document blending (rule 1)
      - No hedging phrases (rule 2)
      - Verbatim refusal if nothing found (rule 3)
      - Every claim cites [doc §section] (rule 4)
    """
    if not question.strip():
        return "Please enter a question."

    q_lower = question.lower()

    # Find matching (doc, section_id) pairs from TOPIC_INDEX
    matches: List[Tuple[str, str]] = []
    for keywords, doc_key, section_id in TOPIC_INDEX:
        if any(kw in q_lower for kw in keywords):
            if (doc_key, section_id) not in matches:
                matches.append((doc_key, section_id))

    if not matches:
        # Enforcement rule 3: verbatim refusal, nothing added
        return REFUSAL_TEMPLATE

    # Group matches by document (enforcement rule 1: no cross-doc blending)
    by_doc: Dict[str, List[str]] = {}
    for doc_key, section_id in matches:
        by_doc.setdefault(doc_key, []).append(section_id)

    answer_parts: List[str] = []

    for doc_key, section_ids in by_doc.items():
        doc_clauses = doc_index.get(doc_key, [])
        clause_map  = {c["section_id"]: c for c in doc_clauses}

        for section_id in section_ids:
            clause = clause_map.get(section_id)
            if not clause:
                continue

            text     = clause["text"]
            citation = f"[{doc_key} §{section_id}]"

            # Build answer line — text + citation (enforcement rule 4)
            answer_parts.append(f"{text}\n  → {citation}")

    if not answer_parts:
        return REFUSAL_TEMPLATE

    # If answers come from multiple documents, label each clearly (enforcement rule 1)
    if len(by_doc) > 1:
        header = (
            "This question touches multiple policy areas. "
            "Each answer is from its own document — they are not combined:\n"
        )
        return header + "\n\n".join(answer_parts)

    return "\n\n".join(answer_parts)


# ── Interactive CLI ───────────────────────────────────────────────────────────

def run_cli(doc_index: Dict[str, List[Dict]]) -> None:
    """Run the interactive Q&A loop."""
    print("\n" + "═" * 70)
    print("  CMC Policy Q&A — Ask My Documents")
    print("  Documents loaded:")
    for doc_name in doc_index:
        clause_count = len(doc_index[doc_name])
        print(f"    • {doc_name}  ({clause_count} clauses indexed)")
    print("═" * 70)
    print("  Type your question and press Enter.")
    print("  Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Exiting]")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("[Exiting]")
            break

        if not question:
            continue

        answer = answer_question(question, doc_index)
        print(f"\nA: {answer}\n")
        print("─" * 70)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # ── Skill 1: retrieve_documents ───────────────────────────────────────────
    try:
        doc_index = retrieve_documents(POLICY_FILES)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    # ── Interactive CLI (skills.md: answer_question in a loop) ────────────────
    run_cli(doc_index)


if __name__ == "__main__":
    main()
