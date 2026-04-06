"""
UC-X app.py — Ask My Documents
Interactive CLI for answering employee questions from CMC policy documents.
Uses retrieval-and-cite approach per agents.md RICE framework.
See README.md for run command and expected behaviour.
"""

import os
import re
import sys


# ---------------------------------------------------------------------------
# Skill 1: retrieve_documents
# ---------------------------------------------------------------------------
POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

# Hedging phrases that must never appear in answers (enforcement rule).
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it is likely",
    "it is reasonable to assume",
]


def retrieve_documents() -> dict[str, dict[str, str]]:
    """Load all three policy files and index by document name → section → text.

    Returns
    -------
    dict
        {filename: {section_number: section_text, ...}, ...}

    Raises
    ------
    FileNotFoundError
        If any policy file is missing. All three must be present.
    """
    index: dict[str, dict[str, str]] = {}

    for filename in POLICY_FILES:
        filepath = os.path.join(POLICY_DIR, filename)
        if not os.path.isfile(filepath):
            raise FileNotFoundError(
                f"Required policy document not found: {filepath}"
            )
        with open(filepath, "r", encoding="utf-8") as fh:
            raw = fh.read()
        index[filename] = _parse_sections(raw)

    return index


def _parse_sections(text: str) -> dict[str, str]:
    """Parse a policy document into {section_number: section_text}.

    Handles both major headings (e.g. "2. ANNUAL LEAVE") and sub-sections
    (e.g. "2.1 Each permanent employee …").
    """
    sections: dict[str, str] = {}
    current_major = ""
    current_sub = ""
    current_lines: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()

        # Detect major section heading: "2. ANNUAL LEAVE"
        major_match = re.match(r"^(\d+)\.\s+[A-Z]", stripped)
        if major_match:
            # Save previous sub-section
            if current_sub:
                sections[current_sub] = "\n".join(current_lines).strip()
            current_major = major_match.group(1)
            current_sub = ""
            current_lines = []
            continue

        # Detect sub-section: "2.6 Employees may carry forward …"
        sub_match = re.match(r"^(\d+\.\d+)\s+", stripped)
        if sub_match:
            # Save previous sub-section
            if current_sub:
                sections[current_sub] = "\n".join(current_lines).strip()
            current_sub = sub_match.group(1)
            current_lines = [stripped]
            continue

        # Separator lines — skip
        if stripped.startswith("═") or stripped == "":
            continue

        # Continuation of current sub-section
        if current_sub:
            current_lines.append(stripped)

    # Save last sub-section
    if current_sub:
        sections[current_sub] = "\n".join(current_lines).strip()

    return sections


# ---------------------------------------------------------------------------
# Skill 2: answer_question
# ---------------------------------------------------------------------------

# Keywords mapped to likely document + section for precise retrieval.
# Each entry: (keywords, filename, primary_sections, description)
TOPIC_MAP = [
    # HR Leave Policy
    (["carry forward", "carry-forward", "carryforward", "unused annual leave"],
     "policy_hr_leave.txt", ["2.6", "2.7"],
     "annual leave carry-forward"),
    (["annual leave", "paid leave", "leave entitlement", "days of leave"],
     "policy_hr_leave.txt", ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"],
     "annual leave"),
    (["sick leave", "medical certificate", "medical leave"],
     "policy_hr_leave.txt", ["3.1", "3.2", "3.3", "3.4"],
     "sick leave"),
    (["maternity", "paternity"],
     "policy_hr_leave.txt", ["4.1", "4.2", "4.3", "4.4"],
     "maternity/paternity leave"),
    (["leave without pay", "lwp", "unpaid leave"],
     "policy_hr_leave.txt", ["5.1", "5.2", "5.3", "5.4"],
     "leave without pay"),
    (["approve", "approves", "approval"] ,
     "policy_hr_leave.txt", ["5.2", "5.3", "2.4"],
     "leave approval"),
    (["public holiday", "compensatory off", "compensatory leave"],
     "policy_hr_leave.txt", ["6.1", "6.2", "6.3"],
     "public holidays"),
    (["leave encashment", "encash leave"],
     "policy_hr_leave.txt", ["7.1", "7.2", "7.3"],
     "leave encashment"),
    (["leave grievance"],
     "policy_hr_leave.txt", ["8.1", "8.2"],
     "leave grievances"),

    # IT Acceptable Use Policy
    (["install", "software", "slack", "application on", "app on"],
     "policy_it_acceptable_use.txt", ["2.3", "2.4"],
     "software installation"),
    (["personal device", "personal phone", "byod", "personal mobile"],
     "policy_it_acceptable_use.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"],
     "personal device / BYOD"),
    (["corporate device", "work laptop", "work device"],
     "policy_it_acceptable_use.txt", ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6"],
     "corporate devices"),
    (["password", "mfa", "multi-factor", "access control"],
     "policy_it_acceptable_use.txt", ["4.1", "4.2", "4.3", "4.4"],
     "passwords and access control"),
    (["data handling", "confidential data", "restricted data"],
     "policy_it_acceptable_use.txt", ["5.1", "5.2", "5.3"],
     "data handling"),
    (["internet use", "email use", "mass email"],
     "policy_it_acceptable_use.txt", ["6.1", "6.2", "6.3"],
     "internet and email use"),

    # Finance Reimbursement Policy
    (["da ", "daily allowance", "meal receipt", "meal claim", "meal expense"],
     "policy_finance_reimbursement.txt", ["2.5", "2.6"],
     "daily allowance and meals"),
    (["home office", "wfh equipment", "equipment allowance",
      "work from home equipment", "work-from-home equipment"],
     "policy_finance_reimbursement.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"],
     "home office equipment allowance"),
    (["travel", "outstation", "air travel", "hotel", "accommodation"],
     "policy_finance_reimbursement.txt", ["2.1", "2.2", "2.3", "2.4"],
     "travel reimbursement"),
    (["training", "professional development", "course fee", "certification"],
     "policy_finance_reimbursement.txt", ["4.1", "4.2", "4.3", "4.4"],
     "training reimbursement"),
    (["mobile phone reimbursement", "internet reimbursement", "mobile reimbursement"],
     "policy_finance_reimbursement.txt", ["5.1", "5.2", "5.3"],
     "mobile/internet reimbursement"),
    (["reimbursement claim", "submit claim", "expense claim", "form fin"],
     "policy_finance_reimbursement.txt", ["6.1", "6.2", "6.3", "6.4"],
     "reimbursement submission"),
    (["reimbursement", "expense"],
     "policy_finance_reimbursement.txt", ["1.1", "1.2", "1.3"],
     "reimbursement general"),
]


def _find_relevant_topics(question: str) -> list[tuple[str, list[str], str]]:
    """Return list of (filename, sections, description) matching the question.

    Matches are based on keyword overlap. Returns all matching topics so we
    can enforce the single-source rule.
    """
    q_lower = question.lower()
    matches: list[tuple[str, list[str], str]] = []
    seen_descs: set[str] = set()

    for keywords, filename, sections, desc in TOPIC_MAP:
        for kw in keywords:
            if kw in q_lower and desc not in seen_descs:
                matches.append((filename, sections, desc))
                seen_descs.add(desc)
                break

    return matches


def _spans_multiple_documents(
    matches: list[tuple[str, list[str], str]],
) -> bool:
    """Check if matches span more than one source document."""
    filenames = {m[0] for m in matches}
    return len(filenames) > 1


def answer_question(
    question: str, index: dict[str, dict[str, str]]
) -> str:
    """Search indexed documents and return a single-source answer or refusal.

    Enforcement rules applied:
    - Single-source: answers from exactly one document.
    - Cross-document blending: refuse if question genuinely spans two docs.
    - Mandatory citation: every claim cites filename + section number.
    - Condition completeness: full section text reproduced.
    - Refusal template: used verbatim when question is not in documents.
    """
    matches = _find_relevant_topics(question)

    # --- No match → refusal ---
    if not matches:
        return REFUSAL_TEMPLATE

    # --- Cross-document blending check ---
    if _spans_multiple_documents(matches):
        # Pick the single most relevant document (first match priority),
        # unless the question explicitly asks to combine — in which case refuse.
        q_lower = question.lower()
        # Detect combination/blending intent
        blending_signals = ["and also", "both", "combine", "together with"]
        if any(sig in q_lower for sig in blending_signals):
            return REFUSAL_TEMPLATE

        # Otherwise, answer from the first (most specific) match only.
        matches = [matches[0]]

    # At this point, all matches should be from the same document.
    filename = matches[0][0]
    doc_sections = index.get(filename, {})

    # Gather relevant section texts.
    relevant_section_nums: list[str] = []
    for _, section_list, _ in matches:
        relevant_section_nums.extend(section_list)
    # De-duplicate while preserving order.
    seen: set[str] = set()
    unique_sections: list[str] = []
    for s in relevant_section_nums:
        if s not in seen:
            seen.add(s)
            unique_sections.append(s)

    # Build answer from matching sections.
    answer_parts: list[str] = []
    for sec_num in unique_sections:
        sec_text = doc_sections.get(sec_num)
        if sec_text:
            answer_parts.append(
                f"[{filename}, Section {sec_num}]\n{sec_text}"
            )

    if not answer_parts:
        return REFUSAL_TEMPLATE

    answer = "\n\n".join(answer_parts)

    # Final enforcement: ensure no hedging phrases leaked in.
    for phrase in HEDGING_PHRASES:
        if phrase in answer.lower():
            # This should not happen with raw document text, but guard anyway.
            answer = answer.replace(phrase, "[REDACTED — hedging removed]")

    return answer


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the interactive Ask My Documents CLI."""
    print("=" * 60)
    print("  UC-X: Ask My Documents — CMC Policy Q&A")
    print("=" * 60)
    print()
    print("Loading policy documents...")

    try:
        index = retrieve_documents()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    doc_count = sum(len(secs) for secs in index.values())
    print(f"Loaded {len(index)} documents with {doc_count} sections total.")
    print()
    print("Type your question and press Enter.")
    print("Type 'quit' or 'exit' to stop.")
    print("-" * 60)

    while True:
        try:
            question = input("\nYour question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        answer = answer_question(question, index)
        print(f"\n{answer}")
        print("-" * 60)


if __name__ == "__main__":
    main()
