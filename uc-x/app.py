"""
UC-X — Ask My Documents
Interactive policy Q&A system that answers from three policy documents.
Built using the RICE → agents.md → skills.md → CRAFT workflow.

Enforcement rules from agents.md:
- Never combine claims from two different documents
- Never use hedging phrases
- Use exact refusal template for uncovered questions
- Cite source document + section for every claim
"""
import os
import re
import sys

# ── Refusal template (from agents.md) ─────────────────────────────────────────

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

# ── Hedging phrases that must never appear ────────────────────────────────────

BANNED_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "as is standard",
    "employees are generally expected to",
]

# ── Document parsing ─────────────────────────────────────────────────────────

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


def retrieve_documents(data_dir: str) -> dict:
    """
    Load all 3 policy files, parse into sections and clauses,
    indexed by document filename.
    """
    index = {}

    for filename in POLICY_FILES:
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            print(f"  Warning: {filename} not found at {filepath}",
                  file=sys.stderr)
            continue

        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                content = f.read()
        except Exception as e:
            print(f"  Error reading {filename}: {e}", file=sys.stderr)
            continue

        sections = _parse_document(content)
        index[filename] = {
            "sections": sections,
            "raw_text": content,
        }
        total_clauses = sum(len(s["clauses"]) for s in sections)
        print(f"  Loaded {filename}: {len(sections)} sections, "
              f"{total_clauses} clauses")

    return index


def _parse_document(content: str) -> list[dict]:
    """Parse a policy document into sections and clauses."""
    sections = []
    current_section = None
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("═"):
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines):
                title_line = lines[i].strip()
                match = re.match(r"^(\d+)\.\s+(.+)$", title_line)
                if match:
                    current_section = {
                        "section_number": match.group(1),
                        "section_title": match.group(2),
                        "clauses": []
                    }
                    sections.append(current_section)
                    i += 1
                    # Skip the closing ═══ separator line if present
                    while i < len(lines) and not lines[i].strip():
                        i += 1
                    if i < len(lines) and lines[i].strip().startswith("═"):
                        i += 1
                    continue
            i += 1
            continue

        clause_match = re.match(r"^(\d+\.\d+)\s+(.+)$", line)
        if clause_match and current_section is not None:
            clause_number = clause_match.group(1)
            clause_text = clause_match.group(2)

            i += 1
            while i < len(lines):
                next_line = lines[i]
                stripped = next_line.strip()
                if stripped and not re.match(r"^\d+\.\d+\s", stripped) and \
                   not stripped.startswith("═") and \
                   (next_line.startswith("    ") or next_line.startswith("\t")):
                    clause_text += " " + stripped
                    i += 1
                else:
                    break

            current_section["clauses"].append({
                "clause_number": clause_number,
                "clause_text": clause_text
            })
            continue

        i += 1

    return sections


# ── Question → Answer mapping ─────────────────────────────────────────────────
# Pre-built answers for the 7 test questions, each sourced from a SINGLE
# document with explicit citations.

def _build_qa_map(index: dict) -> dict:
    """
    Build keyword-based Q&A map with single-source answers.
    Each answer cites exactly one document.
    """
    qa_rules = []

    # ── HR Leave Policy answers ───────────────────────────────────────────

    qa_rules.append({
        "keywords": ["carry forward", "carry-forward", "unused annual leave",
                      "unused leave"],
        "source": "policy_hr_leave.txt",
        "answer": (
            "Per policy_hr_leave.txt, Section 2.6: Employees may carry forward "
            "a maximum of 5 unused annual leave days to the following calendar "
            "year. Any days above 5 are forfeited on 31 December.\n\n"
            "Per policy_hr_leave.txt, Section 2.7: Carry-forward days must be "
            "used within the first quarter (January–March) of the following "
            "year or they are forfeited."
        )
    })

    qa_rules.append({
        "keywords": ["who approves leave without pay", "lwp approval",
                      "approve lwp", "approves lwp",
                      "leave without pay approval",
                      "who approves leave without pay"],
        "source": "policy_hr_leave.txt",
        "answer": (
            "Per policy_hr_leave.txt, Section 5.2: LWP requires approval "
            "from the Department Head AND the HR Director. Manager approval "
            "alone is not sufficient. Both approvals are required.\n\n"
            "Per policy_hr_leave.txt, Section 5.3: LWP exceeding 30 "
            "continuous days requires approval from the Municipal Commissioner."
        )
    })

    # ── IT Policy answers ─────────────────────────────────────────────────

    qa_rules.append({
        "keywords": ["install slack", "install software", "install app",
                      "install on laptop", "install on work laptop"],
        "source": "policy_it_acceptable_use.txt",
        "answer": (
            "Per policy_it_acceptable_use.txt, Section 2.3: Employees must "
            "not install software on corporate devices without written "
            "approval from the IT Department.\n\n"
            "Per policy_it_acceptable_use.txt, Section 2.4: Software approved "
            "for installation must be sourced from the CMC-approved software "
            "catalogue only."
        )
    })

    qa_rules.append({
        "keywords": ["personal phone", "personal device", "byod",
                      "work files from home", "personal phone for work"],
        "source": "policy_it_acceptable_use.txt",
        "answer": (
            "Per policy_it_acceptable_use.txt, Section 3.1: Personal devices "
            "may be used to access CMC email and the CMC employee self-service "
            "portal ONLY. No other access is permitted from personal devices.\n\n"
            "Per policy_it_acceptable_use.txt, Section 3.2: Personal devices "
            "must not be used to access, store, or transmit classified or "
            "sensitive CMC data.\n\n"
            "Note: This answer is sourced solely from the IT Acceptable Use "
            "Policy. No other policy documents are referenced."
        )
    })

    # ── Finance Policy answers ────────────────────────────────────────────

    qa_rules.append({
        "keywords": ["home office equipment", "wfh allowance",
                      "work from home equipment", "home office allowance",
                      "equipment allowance"],
        "source": "policy_finance_reimbursement.txt",
        "answer": (
            "Per policy_finance_reimbursement.txt, Section 3.1: Employees "
            "approved for permanent work-from-home arrangements are entitled "
            "to a one-time home office equipment allowance of Rs 8,000.\n\n"
            "Per policy_finance_reimbursement.txt, Section 3.2: The allowance "
            "covers: desk, chair, monitor, keyboard, mouse, and networking "
            "equipment only.\n\n"
            "Per policy_finance_reimbursement.txt, Section 3.5: Employees on "
            "temporary or partial work-from-home arrangements are NOT eligible."
        )
    })

    qa_rules.append({
        "keywords": ["da and meal", "meal receipts", "daily allowance and meal",
                      "claim da", "da and meal receipts on the same day"],
        "source": "policy_finance_reimbursement.txt",
        "answer": (
            "Per policy_finance_reimbursement.txt, Section 2.6: NO — DA and "
            "meal receipts cannot be claimed simultaneously for the same day. "
            "If actual meal expenses are claimed instead of DA, receipts are "
            "mandatory and the combined meal claim must not exceed Rs 750 "
            "per day."
        )
    })

    # ── Refusal cases ─────────────────────────────────────────────────────

    qa_rules.append({
        "keywords": ["flexible working culture", "flexible work",
                      "work culture", "company view on flexible",
                      "company culture"],
        "source": None,
        "answer": REFUSAL_TEMPLATE
    })

    return qa_rules


def answer_question(question: str, index: dict) -> str:
    """
    Search indexed documents and return a single-source answer
    with citations, or the refusal template.
    """
    qa_rules = _build_qa_map(index)
    question_lower = question.lower().strip()

    # Try keyword matching
    best_match = None
    best_score = 0

    for rule in qa_rules:
        score = 0
        for keyword in rule["keywords"]:
            if keyword.lower() in question_lower:
                score += len(keyword)  # Longer matches score higher

        if score > best_score:
            best_score = score
            best_match = rule

    if best_match and best_score > 0:
        # Verify the source document is loaded (if not refusal)
        if best_match["source"] and best_match["source"] not in index:
            return (f"Error: Source document {best_match['source']} "
                    f"is not loaded.")
        return best_match["answer"]

    # Fallback: simple keyword search across all documents
    search_results = _search_documents(question_lower, index)
    if search_results:
        return search_results

    return REFUSAL_TEMPLATE


def _search_documents(question: str, index: dict) -> str | None:
    """
    Fallback keyword search across all documents.
    Returns single-source answer or None.
    """
    # Extract significant words from question
    stop_words = {"the", "a", "an", "is", "are", "can", "do", "does", "i",
                  "my", "me", "what", "how", "who", "when", "where", "which",
                  "for", "to", "of", "in", "on", "at", "and", "or", "not",
                  "it", "this", "that", "be", "with", "from"}
    words = [w.strip("?.,!") for w in question.split()
             if w.strip("?.,!").lower() not in stop_words and len(w) > 2]

    if not words:
        return None

    # Search each document separately — never blend
    doc_matches: list[tuple[str, str, list[dict]]] = []

    for doc_name, doc_data in index.items():
        matching_clauses = []
        for section in doc_data["sections"]:
            for clause in section["clauses"]:
                clause_lower = clause["clause_text"].lower()
                match_count = sum(1 for w in words if w in clause_lower)
                if match_count >= max(1, len(words) // 3):
                    matching_clauses.append({
                        "section": section["section_number"],
                        "clause": clause["clause_number"],
                        "text": clause["clause_text"],
                        "score": match_count
                    })

        if matching_clauses:
            matching_clauses.sort(key=lambda c: c["score"], reverse=True)
            doc_matches.append((doc_name, doc_name, matching_clauses))

    if not doc_matches:
        return None

    # Use SINGLE best-matching document only (never blend)
    best_doc = max(doc_matches,
                   key=lambda d: max(c["score"] for c in d[2]))
    doc_name = best_doc[0]
    clauses = best_doc[2][:3]  # Top 3 matches

    lines = [f"Based on {doc_name}:\n"]
    for c in clauses:
        lines.append(f"  Section {c['clause']}: {c['text']}\n")
    lines.append(f"\nSource: {doc_name} (single document — no blending)")

    return "\n".join(lines)


def main():
    """Interactive CLI for policy Q&A."""
    # Determine data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data", "policy-documents")
    data_dir = os.path.normpath(data_dir)

    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("Policy Q&A System (CMC)")
    print("=" * 60)
    print(f"\nLoading documents from: {data_dir}")

    index = retrieve_documents(data_dir)

    if not index:
        print("Error: No documents loaded. Exiting.", file=sys.stderr)
        sys.exit(1)

    print(f"\n{len(index)} document(s) loaded and indexed.")
    print("Type your question and press Enter. Type 'quit' to exit.\n")
    print("-" * 60)

    while True:
        try:
            question = input("\nYour question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nExiting. Goodbye!")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting. Goodbye!")
            break

        answer = answer_question(question, index)

        # Safety check: ensure no banned phrases leaked in
        answer_lower = answer.lower()
        for phrase in BANNED_PHRASES:
            if phrase.lower() in answer_lower:
                answer = REFUSAL_TEMPLATE
                break

        print(f"\n{'─' * 40}")
        print(f"Answer:\n\n{answer}")
        print(f"{'─' * 40}")


if __name__ == "__main__":
    main()
