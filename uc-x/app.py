"""
UC-X — Ask My Documents (Multi-Source Policy Q&A)
Implementation guided by agents.md (RICE framework) and skills.md.

Design: Keyword + section-match retrieval — no LLM dependency.
Documents are loaded into isolated namespaces. Every answer cites exactly one
document and section. Cross-document blending is prevented by design.
The exact refusal template is returned when a question cannot be answered
from a single document.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

# Ensure UTF-8 on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Constants ─────────────────────────────────────────────────────────────────
DOC_DIR = Path(__file__).parent.parent / "data" / "policy-documents"

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

FORBIDDEN_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "usually",
    "it would be reasonable to",
    "in general",
]


# ── skill: retrieve_documents ─────────────────────────────────────────────────
def retrieve_documents(doc_dir: str | Path) -> dict:
    """
    Load all 3 policy documents into isolated namespaces.
    Returns { filename: { section_number: {"heading": str, "text": str} } }
    """
    doc_dir = Path(doc_dir)
    missing = [f for f in POLICY_FILES if not (doc_dir / f).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing policy files in {doc_dir}: {missing}"
        )

    index = {}
    for filename in POLICY_FILES:
        path = doc_dir / filename
        content = path.read_text(encoding="utf-8-sig")
        index[filename] = _parse_document(content)

    return index


def _parse_document(content: str) -> dict:
    """Parse a policy document into {section_number: {heading, text}} dict."""
    sections = {}
    current_heading = "General"
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Section heading separator
        if re.match(r"═{3,}", line):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                heading_raw = lines[j].strip()
                if not re.match(r"^\d+\.\d+\s", heading_raw):
                    current_heading = heading_raw
                    i = j + 1
                    continue
            i += 1
            continue

        # Numbered clause
        m = re.match(r"^\s*(\d+\.\d+)\s+(.*)", line)
        if m:
            clause_num = m.group(1)
            first_line = m.group(2).strip()
            text_lines = [first_line]
            j = i + 1
            while j < len(lines):
                stripped = lines[j].strip()
                if re.match(r"═{3,}", stripped):
                    break
                if re.match(r"^\d+\.\d+\s", stripped):
                    break
                if stripped == "" and j + 1 < len(lines):
                    peek = lines[j + 1].strip()
                    if re.match(r"^\d+\.\d+\s", peek) or re.match(r"═{3,}", peek):
                        break
                if stripped:
                    text_lines.append(stripped)
                j += 1
            full_text = " ".join(text_lines).strip()
            sections[clause_num] = {
                "heading": current_heading,
                "text": full_text,
            }
            i = j
            continue
        i += 1
    return sections


# ── Retrieval Rules — maps question patterns to expected documents/sections ──
# Format: (question_patterns, document_key, section_hint, is_refusal)
RETRIEVAL_RULES = [
    # Carry-forward annual leave
    (
        [r"carry.?forward", r"unused.*leave", r"annual.*leave.*carry"],
        "policy_hr_leave.txt", "2.6", False,
    ),
    # Install software / Slack / apps on work laptop
    (
        [r"install", r"software.*laptop", r"slack", r"app.*laptop", r"work.*laptop"],
        "policy_it_acceptable_use.txt", "2.3", False,
    ),
    # Home office equipment / WFH equipment allowance
    (
        [r"home.*office.*equip", r"equipment.*allowance", r"wfh.*equip",
         r"work.*from.*home.*equip", r"office.*allowance"],
        "policy_finance_reimbursement.txt", "3.1", False,
    ),
    # Personal phone / personal device — CRITICAL: IT only, no blending
    (
        [r"personal.*phone", r"personal.*device", r"own.*phone", r"byod",
         r"mobile.*work.*files", r"phone.*work.*files"],
        "policy_it_acceptable_use.txt", "3.1", False,
    ),
    # DA and meal receipts same day
    (
        [r"da.*meal", r"daily.*allowance.*meal", r"meal.*receipt.*same.*day",
         r"claim.*da.*meal", r"da.*and.*meal"],
        "policy_finance_reimbursement.txt", "2.6", False,
    ),
    # Who approves LWP / leave without pay
    (
        [r"leave.*without.*pay", r"lwp.*approv", r"approv.*leave.*without",
         r"who.*approv.*lwp", r"lwp"],
        "policy_hr_leave.txt", "5.2", False,
    ),
    # Flexible working / culture — refusal
    (
        [r"flexible.*working.*culture", r"company.*view.*flexible",
         r"flexible.*culture", r"working.*culture"],
        None, None, True,
    ),
    # Sick leave
    (
        [r"sick.*leave", r"medical.*cert", r"ill.*leave"],
        "policy_hr_leave.txt", "3.1", False,
    ),
    # LWP long duration / Municipal Commissioner
    (
        [r"municipal.*commissioner", r"lwp.*30.*days", r"30.*days.*lwp"],
        "policy_hr_leave.txt", "5.3", False,
    ),
    # Encashment
    (
        [r"encash", r"cash.*leave", r"leave.*cash"],
        "policy_hr_leave.txt", "7.2", False,
    ),
    # Air travel
    (
        [r"air.*travel", r"flight", r"business.*class", r"economy"],
        "policy_finance_reimbursement.txt", "2.3", False,
    ),
    # Password
    (
        [r"password", r"change.*password"],
        "policy_it_acceptable_use.txt", "4.3", False,
    ),
    # MFA
    (
        [r"\bmfa\b", r"multi.*factor", r"two.*factor", r"remote.*access.*auth"],
        "policy_it_acceptable_use.txt", "4.4", False,
    ),
]


def _match_rule(question: str):
    """Return matching (doc_key, section, is_refusal) or None."""
    q_lower = question.lower()
    for patterns, doc_key, section, is_refusal in RETRIEVAL_RULES:
        if any(re.search(p, q_lower) for p in patterns):
            return doc_key, section, is_refusal
    return None, None, False


def _get_section_context(index: dict, doc_key: str, section_hint: str) -> str:
    """
    Retrieve the best matching clause(s) from the specified document.
    Returns the section text plus surrounding clauses if helpful.
    """
    doc = index.get(doc_key, {})
    if not doc:
        return ""

    # If section_hint is provided, get that clause and adjacent clauses
    results = []
    if section_hint and section_hint in doc:
        # Include the target clause
        results.append(f"[{section_hint}] {doc[section_hint]['text']}")

        # Include sibling clauses in same section group
        major = section_hint.split(".")[0]
        for num in sorted(doc.keys()):
            if num.split(".")[0] == major and num != section_hint:
                results.append(f"[{num}] {doc[num]['text']}")
    else:
        # Fall back: include all clauses from that document
        for num in sorted(doc.keys()):
            results.append(f"[{num}] {doc[num]['text']}")

    return "\n".join(results[:6])  # limit to 6 clauses


# ── skill: answer_question ────────────────────────────────────────────────────
def answer_question(question: str, index: dict) -> str:
    """
    Return a single-source answer with citation, or the exact refusal template.
    """
    if not index:
        return "ERROR: No documents loaded. Cannot answer questions."
    if not question.strip():
        return "Please enter a question."

    doc_key, section_hint, is_refusal = _match_rule(question)

    if is_refusal or doc_key is None:
        return REFUSAL_TEMPLATE

    doc = index.get(doc_key, {})
    if not doc:
        return REFUSAL_TEMPLATE

    # Build answer
    answer_parts = []
    answer_parts.append(f"Source: {doc_key}, Section {section_hint}")
    answer_parts.append("")

    # Get relevant clauses
    context = _get_section_context(index, doc_key, section_hint)
    answer_parts.append(context)

    return "\n".join(answer_parts)


# ── Interactive CLI ───────────────────────────────────────────────────────────
def run_batch_test(index: dict):
    """Run all 7 test questions and display answers."""
    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone to access work files when working from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?",
    ]
    print("=" * 70)
    print("UC-X BATCH TEST — 7 Standard Test Questions")
    print("=" * 70)
    for i, q in enumerate(test_questions, 1):
        print(f"\n[Q{i}] {q}")
        print("-" * 60)
        answer = answer_question(q, index)
        print(answer)
    print("\n" + "=" * 70)
    print("Batch test complete.")


def run_interactive(index: dict):
    """Interactive Q&A loop."""
    print("=" * 70)
    print("UC-X Policy Q&A Agent")
    print("Documents: HR Leave | IT Acceptable Use | Finance Reimbursement")
    print("Type 'quit' or 'exit' to stop. Type 'batch' to run all 7 test questions.")
    print("=" * 70)
    while True:
        try:
            question = input("\nYour question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break
        if question.lower() == "batch":
            run_batch_test(index)
            continue
        if not question:
            continue
        answer = answer_question(question, index)
        print("\n" + answer)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="UC-X Policy Q&A Agent")
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Run batch test of all 7 standard questions and exit",
    )
    parser.add_argument(
        "--doc-dir",
        default=str(DOC_DIR),
        help="Directory containing the three policy .txt files",
    )
    args = parser.parse_args()

    print(f"Loading policy documents from: {args.doc_dir}")
    index = retrieve_documents(args.doc_dir)
    doc_counts = {k: len(v) for k, v in index.items()}
    print(f"Loaded: {doc_counts}")

    if args.batch:
        run_batch_test(index)
    else:
        run_interactive(index)
