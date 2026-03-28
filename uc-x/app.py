"""
UC-X — Ask My Documents
Policy Document Q&A Agent: answers employee questions strictly from three
policy documents with single-source citation and refusal template.
Built using agents.md (RICE enforcement) + skills.md (retrieve_documents, answer_question).
"""
import argparse
import re
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ── Refusal template (verbatim from agents.md) ────────────────────────────
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# ── Banned hedging phrases (enforcement rule #2) ──────────────────────────
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "as is standard practice",
    "generally",
    "usually",
]

# ── Document metadata for team referral in refusal ────────────────────────
DOC_TEAMS = {
    "policy_hr_leave.txt": "HR Department",
    "policy_it_acceptable_use.txt": "IT Department",
    "policy_finance_reimbursement.txt": "Finance Department",
}

# ── Default policy file paths ─────────────────────────────────────────────
DEFAULT_POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
DEFAULT_POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


# ═══════════════════════════════════════════════════════════════════════════
# Skill: retrieve_documents
# ═══════════════════════════════════════════════════════════════════════════

def retrieve_documents(file_paths: list[str]) -> dict[str, dict[str, str]]:
    """
    Loads all 3 policy files and indexes their content by document name
    and section number.

    Returns:
        {
            "policy_hr_leave.txt": {
                "1.1": "clause text...",
                "2.3": "clause text...",
                ...
            },
            ...
        }

    Error handling:
        - Raises error naming the missing file if any file cannot be read.
        - Does NOT proceed with partial data.
    """
    index: dict[str, dict[str, str]] = {}

    for fpath in file_paths:
        doc_name = os.path.basename(fpath)

        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            logger.error(f"FATAL: Policy file not found: {fpath}")
            raise FileNotFoundError(f"Missing policy file: {fpath}. Cannot proceed with partial data.")
        except Exception as exc:
            logger.error(f"FATAL: Cannot read policy file {fpath}: {exc}")
            raise

        # Parse sections
        clauses: dict[str, str] = {}
        section_title: dict[str, str] = {}  # section_num -> section title
        clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)$")
        section_pattern = re.compile(r"^(\d+)\.\s+(.+)$")

        current_clause = None
        current_section_num = None

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("═") or not stripped:
                continue

            # Top-level section header
            sec_match = section_pattern.match(stripped)
            if sec_match and not clause_pattern.match(stripped):
                current_section_num = sec_match.group(1)
                section_title[current_section_num] = sec_match.group(2)
                current_clause = None
                continue

            # Sub-clause
            clause_match = clause_pattern.match(stripped)
            if clause_match:
                current_clause = clause_match.group(1)
                clauses[current_clause] = clause_match.group(2)
                continue

            # Continuation line
            if current_clause and current_clause in clauses:
                clauses[current_clause] += " " + stripped

        # Store section titles as well for richer context
        # using format "SECTION_N" as key
        for sec_num, title in section_title.items():
            clauses[f"SECTION_{sec_num}"] = title

        index[doc_name] = clauses
        logger.info(f"Indexed {doc_name}: {len([k for k in clauses if not k.startswith('SECTION_')])} clauses")

    return index


# ═══════════════════════════════════════════════════════════════════════════
# Skill: answer_question
# ═══════════════════════════════════════════════════════════════════════════

# ── Keyword-to-document routing rules ──────────────────────────────────
# Each rule: (list of keywords/phrases, document name, relevant sections)
ROUTING_RULES: list[tuple[list[str], str, list[str]]] = [
    # HR Leave Policy
    (["annual leave", "carry forward", "leave days", "paid leave", "casual leave"],
     "policy_hr_leave.txt", ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"]),
    (["sick leave", "medical certificate", "sick"],
     "policy_hr_leave.txt", ["3.1", "3.2", "3.3", "3.4"]),
    (["maternity", "paternity", "child birth", "childbirth"],
     "policy_hr_leave.txt", ["4.1", "4.2", "4.3", "4.4"]),
    (["leave without pay", "lwp", "unpaid leave"],
     "policy_hr_leave.txt", ["5.1", "5.2", "5.3", "5.4"]),
    (["public holiday", "compensatory off", "gazetted"],
     "policy_hr_leave.txt", ["6.1", "6.2", "6.3"]),
    (["leave encashment", "encash leave"],
     "policy_hr_leave.txt", ["7.1", "7.2", "7.3"]),
    (["leave grievance", "leave dispute"],
     "policy_hr_leave.txt", ["8.1", "8.2"]),

    # IT Acceptable Use Policy
    (["install software", "install slack", "install app", "software install", "approved software"],
     "policy_it_acceptable_use.txt", ["2.3", "2.4"]),
    (["corporate device", "work laptop", "work phone", "work computer", "company device"],
     "policy_it_acceptable_use.txt", ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6"]),
    (["personal device", "personal phone", "byod", "own device", "own phone", "personal laptop"],
     "policy_it_acceptable_use.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"]),
    (["password", "mfa", "multi-factor", "authentication", "access control"],
     "policy_it_acceptable_use.txt", ["4.1", "4.2", "4.3", "4.4"]),
    (["data handling", "confidential data", "sensitive data", "data classif"],
     "policy_it_acceptable_use.txt", ["5.1", "5.2", "5.3"]),
    (["internet use", "email use", "mass email", "personal email"],
     "policy_it_acceptable_use.txt", ["6.1", "6.2", "6.3"]),
    (["it violation", "disciplinary", "unauthorised access"],
     "policy_it_acceptable_use.txt", ["7.1", "7.2", "7.3"]),

    # Finance Reimbursement Policy
    (["travel reimburs", "local travel", "outstation", "air travel", "hotel", "daily allowance",
      "da ", "meal receipt", "meal claim", "meal expense"],
     "policy_finance_reimbursement.txt", ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6"]),
    (["da and meal", "da or meal", "claim da", "claim meal"],
     "policy_finance_reimbursement.txt", ["2.5", "2.6"]),
    (["home office", "wfh equipment", "work from home equipment", "home equipment allowance",
      "office equipment allowance", "wfh allowance", "work from home allowance"],
     "policy_finance_reimbursement.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"]),
    (["training", "professional development", "course fee", "certification", "exam fee"],
     "policy_finance_reimbursement.txt", ["4.1", "4.2", "4.3", "4.4"]),
    (["mobile phone reimburs", "internet reimburs", "phone bill", "internet bill"],
     "policy_finance_reimbursement.txt", ["5.1", "5.2", "5.3"]),
    (["reimbursement claim", "submit claim", "claim process", "receipt", "fin-exp"],
     "policy_finance_reimbursement.txt", ["6.1", "6.2", "6.3", "6.4"]),
    (["reimburse", "reimbursement", "expense claim"],
     "policy_finance_reimbursement.txt", ["1.1", "1.2", "1.3"]),
]


def _find_matching_documents(question: str) -> list[tuple[str, list[str]]]:
    """
    Find which documents and sections are relevant to a question.
    Returns list of (doc_name, relevant_section_numbers).
    """
    q_lower = question.lower()
    matches: dict[str, list[str]] = {}

    for keywords, doc_name, sections in ROUTING_RULES:
        for kw in keywords:
            if kw in q_lower:
                if doc_name not in matches:
                    matches[doc_name] = []
                for sec in sections:
                    if sec not in matches[doc_name]:
                        matches[doc_name].append(sec)
                break  # found a keyword match for this rule

    return list(matches.items())


def _format_answer(doc_name: str, sections: list[str], doc_index: dict[str, str]) -> str:
    """
    Format a single-source answer citing the document and section numbers.
    """
    lines = [f"Source: {doc_name}\n"]

    for sec_num in sorted(sections, key=lambda x: float(x)):
        if sec_num in doc_index:
            lines.append(f"  [{doc_name}, Section {sec_num}] {doc_index[sec_num]}")

    return "\n".join(lines)


def answer_question(question: str, doc_index: dict[str, dict[str, str]]) -> str:
    """
    Searches the indexed documents for a single-source answer to the user's
    question, returning the answer with citation or the refusal template.

    Enforcement:
    - Never combines claims from two different documents (single-source only)
    - Never uses hedging phrases
    - Cites document name + section number for every claim
    - Uses exact refusal template if question is not covered
    """
    # ── Find matching documents ────────────────────────────────────────
    matches = _find_matching_documents(question)

    # ── No match → refusal ─────────────────────────────────────────────
    if not matches:
        return REFUSAL_TEMPLATE

    # ── Single document match → answer from that document ──────────────
    if len(matches) == 1:
        doc_name, sections = matches[0]
        return _format_answer(doc_name, sections, doc_index[doc_name])

    # ── Multiple document match → SINGLE-SOURCE ONLY ───────────────────
    # Enforcement: never blend. Pick the most relevant document based on
    # number of matching sections (stronger signal). If tie, use first match.
    # But if question touches genuinely different topics across docs,
    # answer from the primary document only.

    # Check if the question is specifically about a cross-document topic
    q_lower = question.lower()

    # Special handling: "personal phone" + "work files" → IT policy only (section 3.1)
    # This prevents the critical cross-document blend trap
    if "personal" in q_lower and ("phone" in q_lower or "device" in q_lower):
        if "policy_it_acceptable_use.txt" in [m[0] for m in matches]:
            doc_name = "policy_it_acceptable_use.txt"
            sections = [m[1] for m in matches if m[0] == doc_name][0]
            answer = _format_answer(doc_name, sections, doc_index[doc_name])
            answer += (
                "\n\n⚠ NOTE: This answer is sourced exclusively from "
                f"{doc_name}. Other policy documents were not consulted "
                "to avoid cross-document blending."
            )
            return answer

    # Default: answer from the document with the most section matches
    best_doc = max(matches, key=lambda m: len(m[1]))
    doc_name, sections = best_doc
    answer = _format_answer(doc_name, sections, doc_index[doc_name])
    answer += (
        "\n\n⚠ NOTE: This answer is sourced exclusively from "
        f"{doc_name}. Other policy documents were not consulted "
        "to avoid cross-document blending."
    )
    return answer


# ═══════════════════════════════════════════════════════════════════════════
# Interactive CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="UC-X — Ask My Documents: Policy Q&A Agent"
    )
    parser.add_argument(
        "--policy-dir", default=DEFAULT_POLICY_DIR,
        help="Directory containing the 3 policy .txt files"
    )
    parser.add_argument(
        "--question", default=None,
        help="Single question (non-interactive mode). If omitted, starts interactive CLI."
    )
    args = parser.parse_args()

    # ── Skill 1: retrieve_documents ────────────────────────────────────
    file_paths = [os.path.join(args.policy_dir, f) for f in DEFAULT_POLICY_FILES]
    logger.info("Loading and indexing policy documents...")

    try:
        doc_index = retrieve_documents(file_paths)
    except FileNotFoundError:
        sys.exit(1)

    total_clauses = sum(
        len([k for k in v if not k.startswith("SECTION_")])
        for v in doc_index.values()
    )
    logger.info(f"Ready. {len(doc_index)} documents, {total_clauses} clauses indexed.\n")

    # ── Single-question mode ───────────────────────────────────────────
    if args.question:
        answer = answer_question(args.question, doc_index)
        print(f"\nQ: {args.question}\n")
        print(f"A: {answer}\n")
        return

    # ── Interactive CLI ────────────────────────────────────────────────
    print("=" * 60)
    print("  UC-X — Ask My Documents")
    print("  Policy Q&A Agent (3 documents loaded)")
    print("  Type your question or 'quit' to exit.")
    print("=" * 60)
    print()

    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        # ── Skill 2: answer_question ───────────────────────────────────
        answer = answer_question(question, doc_index)
        print(f"\nA: {answer}\n")


if __name__ == "__main__":
    main()
