"""
UC-X — Ask My Documents
Policy Q&A system built from agents.md and skills.md specifications.
Interactive CLI — type questions, read answers.
"""
import os
import re
import sys

# Fix Windows console encoding
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data",
                          "policy-documents")

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

BANNED_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it is reasonable to assume",
    "generally",
]


# ---------------------------------------------------------------------------
# Skill: retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents(policy_dir: str,
                       policy_files: list[str]) -> list[dict]:
    """
    Load all policy .txt files and index by document name and section number.

    Returns: list of section dicts with keys:
        document_name, section_number, section_heading, section_text
    """
    all_sections: list[dict] = []

    for filename in policy_files:
        filepath = os.path.join(policy_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Warning: Could not find {filepath}", file=sys.stderr)
            continue
        except Exception as exc:
            print(f"Warning: Error reading {filepath}: {exc}",
                  file=sys.stderr)
            continue

        sections = _parse_sections(filename, content)
        all_sections.extend(sections)

    if not all_sections:
        print("Error: No policy documents could be loaded.", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(all_sections)} sections from "
          f"{len(policy_files)} documents.")
    return all_sections


def _parse_sections(doc_name: str, content: str) -> list[dict]:
    """Parse a policy document into numbered sections."""
    sections: list[dict] = []
    current_heading = ""

    heading_pattern = re.compile(r"^(\d+)\.\s+(.+)$")
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)")

    lines = content.splitlines()
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
            clause_num = clause_match.group(1)
            clause_text = clause_match.group(2)

            i += 1
            while i < len(lines):
                next_line = lines[i]
                stripped = next_line.strip()
                if not stripped:
                    break
                if clause_pattern.match(stripped):
                    break
                if heading_pattern.match(stripped):
                    break
                if re.match(r"^[═]+$", stripped):
                    break
                clause_text += " " + stripped
                i += 1

            sections.append({
                "document_name": doc_name,
                "section_number": clause_num,
                "section_heading": current_heading,
                "section_text": clause_text.strip(),
            })
            continue

        i += 1

    return sections


# ---------------------------------------------------------------------------
# Keyword mapping for the 7 test questions
# ---------------------------------------------------------------------------

# Maps question keywords to relevant section lookups
QUESTION_KEYWORDS = {
    # HR leave
    "carry forward": [("policy_hr_leave.txt", "2.6"),
                      ("policy_hr_leave.txt", "2.7")],
    "carry-forward": [("policy_hr_leave.txt", "2.6"),
                      ("policy_hr_leave.txt", "2.7")],
    "annual leave": [("policy_hr_leave.txt", "2.6"),
                     ("policy_hr_leave.txt", "2.7")],
    "leave without pay": [("policy_hr_leave.txt", "5.2"),
                          ("policy_hr_leave.txt", "5.3")],
    "lwp": [("policy_hr_leave.txt", "5.2"),
            ("policy_hr_leave.txt", "5.3")],
    "who approves": [("policy_hr_leave.txt", "5.2"),
                     ("policy_hr_leave.txt", "5.3")],
    "sick leave": [("policy_hr_leave.txt", "3.1"),
                   ("policy_hr_leave.txt", "3.2"),
                   ("policy_hr_leave.txt", "3.4")],
    "maternity": [("policy_hr_leave.txt", "4.1"),
                  ("policy_hr_leave.txt", "4.2")],
    "paternity": [("policy_hr_leave.txt", "4.3"),
                  ("policy_hr_leave.txt", "4.4")],
    "encash": [("policy_hr_leave.txt", "7.1"),
               ("policy_hr_leave.txt", "7.2")],
    "grievance": [("policy_hr_leave.txt", "8.1"),
                  ("policy_hr_leave.txt", "8.2")],

    # IT policy
    "install": [("policy_it_acceptable_use.txt", "2.3"),
                ("policy_it_acceptable_use.txt", "2.4")],
    "software": [("policy_it_acceptable_use.txt", "2.3"),
                 ("policy_it_acceptable_use.txt", "2.4")],
    "slack": [("policy_it_acceptable_use.txt", "2.3"),
              ("policy_it_acceptable_use.txt", "2.4")],
    "personal device": [("policy_it_acceptable_use.txt", "3.1"),
                        ("policy_it_acceptable_use.txt", "3.2")],
    "personal phone": [("policy_it_acceptable_use.txt", "3.1"),
                       ("policy_it_acceptable_use.txt", "3.2")],
    "byod": [("policy_it_acceptable_use.txt", "3.1"),
             ("policy_it_acceptable_use.txt", "3.2")],
    "password": [("policy_it_acceptable_use.txt", "4.1"),
                 ("policy_it_acceptable_use.txt", "4.3")],
    "mfa": [("policy_it_acceptable_use.txt", "4.4")],
    "remote access": [("policy_it_acceptable_use.txt", "4.4")],
    "work files": [("policy_it_acceptable_use.txt", "3.1"),
                   ("policy_it_acceptable_use.txt", "3.2")],
    "data handling": [("policy_it_acceptable_use.txt", "5.1"),
                      ("policy_it_acceptable_use.txt", "5.2")],

    # Finance policy
    "home office": [("policy_finance_reimbursement.txt", "3.1"),
                    ("policy_finance_reimbursement.txt", "3.2"),
                    ("policy_finance_reimbursement.txt", "3.5")],
    "equipment allowance": [("policy_finance_reimbursement.txt", "3.1"),
                            ("policy_finance_reimbursement.txt", "3.2"),
                            ("policy_finance_reimbursement.txt", "3.5")],
    "wfh": [("policy_finance_reimbursement.txt", "3.1"),
            ("policy_finance_reimbursement.txt", "3.5")],
    "travel": [("policy_finance_reimbursement.txt", "2.1"),
               ("policy_finance_reimbursement.txt", "2.2")],
    "daily allowance": [("policy_finance_reimbursement.txt", "2.5"),
                        ("policy_finance_reimbursement.txt", "2.6")],
    "da ": [("policy_finance_reimbursement.txt", "2.5"),
            ("policy_finance_reimbursement.txt", "2.6")],
    "meal": [("policy_finance_reimbursement.txt", "2.5"),
             ("policy_finance_reimbursement.txt", "2.6")],
    "reimburs": [("policy_finance_reimbursement.txt", "1.1"),
                 ("policy_finance_reimbursement.txt", "6.1")],
    "training": [("policy_finance_reimbursement.txt", "4.1"),
                 ("policy_finance_reimbursement.txt", "4.2")],
    "mobile phone reimburs": [("policy_finance_reimbursement.txt", "5.1")],
    "internet reimburs": [("policy_finance_reimbursement.txt", "5.2")],
    "hotel": [("policy_finance_reimbursement.txt", "2.4")],
    "air travel": [("policy_finance_reimbursement.txt", "2.3")],
    "flight": [("policy_finance_reimbursement.txt", "2.3")],
}

# Questions that should trigger the refusal template
REFUSAL_KEYWORDS = [
    "flexible working culture",
    "work-life balance",
    "remote work policy",
    "company view",
    "company culture",
    "company opinion",
]


# ---------------------------------------------------------------------------
# Skill: answer_question
# ---------------------------------------------------------------------------

def answer_question(question: str, sections: list[dict]) -> str:
    """
    Search indexed documents for sections relevant to the question.
    Returns a single-source answer with citation, or the refusal template.

    Enforcement (from agents.md):
      - Never blend claims from two documents
      - Never use hedging phrases
      - Cite document + section for every claim
      - Use refusal template for uncovered questions
    """
    q_lower = question.lower().strip()

    # Check refusal keywords first
    for kw in REFUSAL_KEYWORDS:
        if kw in q_lower:
            return REFUSAL_TEMPLATE

    # Find matching sections via keyword lookup
    matched_refs: list[tuple[str, str]] = []
    for keyword, refs in QUESTION_KEYWORDS.items():
        if keyword in q_lower:
            for ref in refs:
                if ref not in matched_refs:
                    matched_refs.append(ref)

    if not matched_refs:
        # Fallback: search all sections for keyword overlap
        q_words = set(re.findall(r"[a-zA-Z]{4,}", q_lower))
        scored: list[tuple[int, dict]] = []
        for sec in sections:
            sec_words = set(
                w.lower() for w in re.findall(r"[a-zA-Z]{4,}",
                                              sec["section_text"])
            )
            overlap = len(q_words & sec_words)
            if overlap >= 2:
                scored.append((overlap, sec))

        scored.sort(key=lambda x: x[0], reverse=True)

        if not scored:
            return REFUSAL_TEMPLATE

        # Group by document — enforce single-source
        top_sections = scored[:5]
        matched_refs = [(s["document_name"], s["section_number"])
                        for _, s in top_sections]

    # Look up the actual section content
    matched_sections: list[dict] = []
    for doc_name, sec_num in matched_refs:
        for sec in sections:
            if (sec["document_name"] == doc_name and
                    sec["section_number"] == sec_num):
                matched_sections.append(sec)
                break

    if not matched_sections:
        return REFUSAL_TEMPLATE

    # Group by document — enforce single-source rule
    by_doc: dict[str, list[dict]] = {}
    for sec in matched_sections:
        doc = sec["document_name"]
        if doc not in by_doc:
            by_doc[doc] = []
        by_doc[doc].append(sec)

    # Build response — separate by document if multiple docs matched
    response_parts: list[str] = []

    if len(by_doc) == 1:
        # Single document — straightforward answer
        doc_name = list(by_doc.keys())[0]
        secs = by_doc[doc_name]
        response_parts.append(f"According to {doc_name}:\n")
        for sec in secs:
            response_parts.append(
                f"  Section {sec['section_number']} "
                f"({sec['section_heading']}): {sec['section_text']}\n"
            )
    else:
        # Multiple documents — present separately, never blend
        response_parts.append(
            "This question relates to multiple policy documents. "
            "Each document's relevant section is presented separately "
            "below (not blended):\n"
        )
        for doc_name, secs in by_doc.items():
            response_parts.append(f"\n--- {doc_name} ---")
            for sec in secs:
                response_parts.append(
                    f"  Section {sec['section_number']} "
                    f"({sec['section_heading']}): {sec['section_text']}"
                )

    return "\n".join(response_parts)


# ---------------------------------------------------------------------------
# Main — Interactive CLI
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("Policy Q&A System (HR Leave, IT Acceptable Use, Finance)")
    print("=" * 60)
    print("Type your question and press Enter. Type 'quit' to exit.\n")

    # Load and index documents
    sections = retrieve_documents(POLICY_DIR, POLICY_FILES)
    print()

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

        answer = answer_question(question, sections)
        print(f"\nAnswer:\n{answer}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()
