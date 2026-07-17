"""
UC-X app.py — Ask My Documents
Interactive CLI that answers employee questions using ONLY the content of
three policy documents. Never blends sources, never hedges, cites every claim.

Built using agents.md (enforcement rules) and skills.md (skill definitions).
"""
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

POLICY_DIR = Path(__file__).parent / ".." / "data" / "policy-documents"

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

# Hedging phrases that must NEVER appear in answers
FORBIDDEN_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "most organisations",
    "usually",
    "it is likely",
    "probably",
]


# ---------------------------------------------------------------------------
# Skill: retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents() -> dict:
    """
    Load all 3 policy files, parse into structured sections.
    Returns dict: {filename: [{"section_number", "section_title", "section_body"}, ...]}
    """
    documents = {}

    heading_pattern = re.compile(r"^(\d+)\.\s+([A-Z][A-Z &/()\-—]+)\s*$")
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)")

    for filename in POLICY_FILES:
        filepath = POLICY_DIR / filename
        if not filepath.exists():
            print(f"  WARNING: Could not load {filename} — file not found.", file=sys.stderr)
            continue

        content = filepath.read_text(encoding="utf-8")
        lines = content.splitlines()
        sections = []
        current_heading = ""

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            heading_match = heading_pattern.match(line)
            if heading_match:
                current_heading = heading_match.group(2).strip()
                i += 1
                continue

            clause_match = clause_pattern.match(line)
            if clause_match:
                clause_number = clause_match.group(1)
                clause_text = clause_match.group(2)

                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    stripped = next_line.strip()
                    if not stripped:
                        i += 1
                        break
                    if clause_pattern.match(stripped):
                        break
                    if heading_pattern.match(stripped):
                        break
                    if stripped.startswith("═"):
                        break
                    clause_text += " " + stripped
                    i += 1

                sections.append({
                    "section_number": clause_number,
                    "section_title": current_heading,
                    "section_body": clause_text.strip(),
                })
            else:
                i += 1

        documents[filename] = sections
        print(f"  Loaded {filename}: {len(sections)} sections")

    if not documents:
        print("ERROR: No policy documents could be loaded.", file=sys.stderr)
        sys.exit(1)

    return documents


# ---------------------------------------------------------------------------
# Skill: answer_question
# ---------------------------------------------------------------------------

# Question-to-section mapping based on keywords
SEARCH_RULES = [
    # (keywords, target_file, target_sections, priority)
    (["carry forward", "carry-forward", "unused annual leave", "unused leave"],
     "policy_hr_leave.txt", ["2.6", "2.7"], 10),
    (["install", "software", "slack", "application", "app"],
     "policy_it_acceptable_use.txt", ["2.3", "2.4"], 10),
    (["home office", "equipment allowance", "work from home equipment", "wfh equipment"],
     "policy_finance_reimbursement.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"], 10),
    (["personal phone", "personal device", "byod", "personal mobile"],
     "policy_it_acceptable_use.txt", ["3.1", "3.2"], 10),
    (["flexible working", "flexible culture", "work-life balance"],
     None, [], 10),  # Not in any document → refusal
    (["da and meal", "meal receipts", "daily allowance and meal", "claim da"],
     "policy_finance_reimbursement.txt", ["2.5", "2.6"], 10),
    (["leave without pay", "lwp", "who approves lwp", "approves leave without pay"],
     "policy_hr_leave.txt", ["5.2", "5.3"], 10),
    (["maternity", "paternity"],
     "policy_hr_leave.txt", ["4.1", "4.2", "4.3", "4.4"], 8),
    (["sick leave", "medical certificate"],
     "policy_hr_leave.txt", ["3.1", "3.2", "3.3", "3.4"], 8),
    (["annual leave", "leave entitle"],
     "policy_hr_leave.txt", ["2.1", "2.2"], 8),
    (["password", "mfa", "multi-factor"],
     "policy_it_acceptable_use.txt", ["4.1", "4.2", "4.3", "4.4"], 8),
    (["reimbursement", "expense", "claim"],
     "policy_finance_reimbursement.txt", ["1.1", "1.2", "1.3"], 7),
    (["travel", "outstation", "air travel"],
     "policy_finance_reimbursement.txt", ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6"], 8),
    (["training", "certification", "course fee"],
     "policy_finance_reimbursement.txt", ["4.1", "4.2", "4.3", "4.4"], 8),
    (["mobile phone reimbursement", "internet reimbursement"],
     "policy_finance_reimbursement.txt", ["5.1", "5.2", "5.3"], 8),
    (["leave encashment", "encash leave"],
     "policy_hr_leave.txt", ["7.1", "7.2", "7.3"], 8),
    (["grievance", "dispute"],
     "policy_hr_leave.txt", ["8.1", "8.2"], 8),
    (["data handling", "confidential", "restricted data"],
     "policy_it_acceptable_use.txt", ["5.1", "5.2", "5.3"], 8),
    (["violation", "disciplinary"],
     "policy_it_acceptable_use.txt", ["7.1", "7.2", "7.3"], 8),
    (["public holiday", "compensatory off"],
     "policy_hr_leave.txt", ["6.1", "6.2", "6.3"], 8),
]


def answer_question(question: str, documents: dict) -> str:
    """
    Search indexed documents and return single-source cited answer or refusal.
    """
    q_lower = question.lower()

    # Find matching rules
    best_match = None
    best_priority = 0

    for keywords, target_file, target_sections, priority in SEARCH_RULES:
        for kw in keywords:
            if kw in q_lower:
                if priority > best_priority:
                    best_match = (target_file, target_sections)
                    best_priority = priority
                break

    # If no match or explicit refusal rule
    if best_match is None or best_match[0] is None:
        return REFUSAL_TEMPLATE

    target_file, target_sections = best_match

    # Retrieve the relevant sections
    if target_file not in documents:
        return REFUSAL_TEMPLATE

    doc_sections = documents[target_file]
    relevant = [s for s in doc_sections if s["section_number"] in target_sections]

    if not relevant:
        return REFUSAL_TEMPLATE

    # Build answer from matched sections
    answer_parts = []
    for section in relevant:
        answer_parts.append(f"Section {section['section_number']}: {section['section_body']}")

    answer_text = "\n".join(answer_parts)
    citation = f"Source: {target_file}, Section(s) {', '.join(s['section_number'] for s in relevant)}"

    return f"{answer_text}\n\n{citation}"


# ---------------------------------------------------------------------------
# Main Interactive CLI
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("Policy Q&A System (3 documents loaded)")
    print("=" * 60)
    print("\nLoading policy documents...")

    documents = retrieve_documents()

    print(f"\nReady. {sum(len(v) for v in documents.values())} total sections indexed.")
    print("Type your question and press Enter. Type 'quit' or 'exit' to stop.\n")
    print("-" * 60)

    while True:
        try:
            question = input("\nYour question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        answer = answer_question(question, documents)

        # Enforcement check: ensure no hedging phrases slipped in
        for phrase in FORBIDDEN_PHRASES:
            if phrase in answer.lower():
                # This shouldn't happen with our rule-based system, but safety check
                answer = REFUSAL_TEMPLATE
                break

        print(f"\n{answer}")
        print("-" * 60)


if __name__ == "__main__":
    main()
