"""
UC-X — Ask My Documents
Built using the RICE → agents.md → skills.md → CRAFT workflow.

Role: Policy QA Agent — answers from 3 docs only, no blending, no hedging.
Intent: Single-source answers with citation, or exact refusal template.
Context: HR leave, IT acceptable use, Finance reimbursement policies only.
Enforcement: No cross-doc blending; no hedging; refusal template; cite source+section.
"""
import re
import sys
import os


# ── Constants ─────────────────────────────────────────────────────────────────

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it is reasonable to assume",
    "as is standard practice",
    "employees are generally expected",
]

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]


# ── Skill: retrieve_documents ────────────────────────────────────────────────

def retrieve_documents(file_paths: list[str]) -> dict:
    """
    Load all 3 policy files and index by document name and section number.
    """
    doc_index = {}

    for path in file_paths:
        filename = os.path.basename(path)

        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"ERROR: Policy file not found: {path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Could not read {path}: {e}", file=sys.stderr)
            sys.exit(1)

        # Parse document reference and title from first lines
        lines = content.split("\n")
        doc_ref = ""
        title = ""
        for line in lines[:10]:
            line = line.strip()
            if line.startswith("Document Reference:"):
                doc_ref = line.split(":", 1)[1].strip()
            if "POLICY" in line.upper() and not line.startswith("Document") and not line.startswith("Version"):
                title = line

        # Parse sections
        sections = {}
        current_section_num = None
        current_section_text = ""

        for line in lines:
            stripped = line.strip()

            # Match clause lines like "3.1 Personal devices may..."
            clause_match = re.match(r'^(\d+\.\d+)\s+(.+)$', stripped)
            if clause_match:
                # Save previous section
                if current_section_num:
                    sections[current_section_num] = current_section_text.strip()

                current_section_num = clause_match.group(1)
                current_section_text = clause_match.group(2)
                continue

            # Continuation lines
            if current_section_num and stripped and not stripped.startswith("═") and not re.match(r'^\d+\.\s+[A-Z]', stripped):
                current_section_text += " " + stripped

        # Save last section
        if current_section_num:
            sections[current_section_num] = current_section_text.strip()

        # Clean up whitespace in all sections
        for key in sections:
            sections[key] = re.sub(r'\s+', ' ', sections[key]).strip()

        doc_index[filename] = {
            "doc_ref": doc_ref,
            "title": title,
            "sections": sections,
            "path": path,
        }

    print(f"Loaded {len(doc_index)} policy documents:")
    for fname, doc in doc_index.items():
        print(f"  • {fname} ({doc['doc_ref']}) — {len(doc['sections'])} sections")

    return doc_index


# ── Skill: answer_question ────────────────────────────────────────────────────

# Question → keyword → relevant sections mapping
QUESTION_KEYWORDS = {
    # HR Leave topics
    "annual leave": [("policy_hr_leave.txt", ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"])],
    "carry forward": [("policy_hr_leave.txt", ["2.6", "2.7"])],
    "carry-forward": [("policy_hr_leave.txt", ["2.6", "2.7"])],
    "sick leave": [("policy_hr_leave.txt", ["3.1", "3.2", "3.3", "3.4"])],
    "medical certificate": [("policy_hr_leave.txt", ["3.2", "3.4"])],
    "maternity": [("policy_hr_leave.txt", ["4.1", "4.2"])],
    "paternity": [("policy_hr_leave.txt", ["4.3", "4.4"])],
    "leave without pay": [("policy_hr_leave.txt", ["5.1", "5.2", "5.3", "5.4"])],
    "lwp": [("policy_hr_leave.txt", ["5.1", "5.2", "5.3", "5.4"])],
    "leave encashment": [("policy_hr_leave.txt", ["7.1", "7.2", "7.3"])],
    "grievance": [("policy_hr_leave.txt", ["8.1", "8.2"])],
    "approve leave without pay": [("policy_hr_leave.txt", ["5.2", "5.3"])],
    "approves leave without pay": [("policy_hr_leave.txt", ["5.2", "5.3"])],

    # IT topics
    "install": [("policy_it_acceptable_use.txt", ["2.3", "2.4"])],
    "software": [("policy_it_acceptable_use.txt", ["2.3", "2.4"])],
    "slack": [("policy_it_acceptable_use.txt", ["2.3", "2.4"])],
    "personal device": [("policy_it_acceptable_use.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"])],
    "personal phone": [("policy_it_acceptable_use.txt", ["3.1", "3.2"])],
    "byod": [("policy_it_acceptable_use.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"])],
    "password": [("policy_it_acceptable_use.txt", ["4.1", "4.2", "4.3", "4.4"])],
    "mfa": [("policy_it_acceptable_use.txt", ["4.4"])],
    "remote access": [("policy_it_acceptable_use.txt", ["4.4"])],
    "data handling": [("policy_it_acceptable_use.txt", ["5.1", "5.2", "5.3"])],
    "confidential": [("policy_it_acceptable_use.txt", ["5.1", "5.2", "5.3"])],
    "work laptop": [("policy_it_acceptable_use.txt", ["2.3", "2.4", "2.5", "2.6"])],

    # Finance topics
    "reimbursement": [("policy_finance_reimbursement.txt", ["1.1", "1.2", "1.3"])],
    "travel": [("policy_finance_reimbursement.txt", ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6"])],
    "daily allowance": [("policy_finance_reimbursement.txt", ["2.5", "2.6"])],
    "da ": [("policy_finance_reimbursement.txt", ["2.5", "2.6"])],
    "meal": [("policy_finance_reimbursement.txt", ["2.5", "2.6"])],
    "home office": [("policy_finance_reimbursement.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"])],
    "equipment allowance": [("policy_finance_reimbursement.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"])],
    "wfh": [("policy_finance_reimbursement.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"])],
    "training": [("policy_finance_reimbursement.txt", ["4.1", "4.2", "4.3", "4.4"])],
    "certification": [("policy_finance_reimbursement.txt", ["4.3", "4.4"])],
    "mobile phone reimbursement": [("policy_finance_reimbursement.txt", ["5.1", "5.2", "5.3"])],
    "internet reimbursement": [("policy_finance_reimbursement.txt", ["5.2", "5.3"])],
}


def answer_question(question: str, doc_index: dict) -> str:
    """
    Search indexed documents for relevant sections.
    Return single-source answer with citation OR refusal template.
    Never blend across documents.
    """
    question_lower = question.lower().strip()

    # Find matching documents and sections
    matches = {}  # doc_filename -> set of section numbers

    for keyword, doc_sections_list in QUESTION_KEYWORDS.items():
        if keyword in question_lower:
            for doc_filename, section_nums in doc_sections_list:
                if doc_filename not in matches:
                    matches[doc_filename] = set()
                matches[doc_filename].update(section_nums)

    # No matches → refusal
    if not matches:
        return REFUSAL_TEMPLATE

    # Build answer — each document separately (no blending)
    answer_parts = []

    for doc_filename, section_nums in matches.items():
        if doc_filename not in doc_index:
            continue

        doc = doc_index[doc_filename]
        doc_ref = doc["doc_ref"]

        relevant_sections = []
        for snum in sorted(section_nums):
            if snum in doc["sections"]:
                relevant_sections.append((snum, doc["sections"][snum]))

        if not relevant_sections:
            continue

        part = f"Source: {doc_filename} ({doc_ref})\n"
        for snum, text in relevant_sections:
            part += f"  §{snum}: {text}\n"

        answer_parts.append(part)

    if not answer_parts:
        return REFUSAL_TEMPLATE

    # If multiple documents matched, add a warning
    if len(answer_parts) > 1:
        header = ("NOTE: This question touches multiple policy documents. "
                  "Each document's provisions are shown separately below. "
                  "These should NOT be combined into a single interpretation.\n\n")
        return header + "\n".join(answer_parts)

    return "\n".join(answer_parts)


# ── Interactive CLI ───────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("Policy QA System (3 documents loaded)")
    print("=" * 60)
    print()

    # Load documents
    doc_index = retrieve_documents(POLICY_FILES)
    print()
    print("Type your question and press Enter. Type 'quit' to exit.")
    print("-" * 60)

    while True:
        try:
            question = input("\n❓ Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        if not question:
            continue

        print()
        answer = answer_question(question, doc_index)
        print(f"📄 Answer:\n{answer}")
        print("-" * 60)


if __name__ == "__main__":
    main()
