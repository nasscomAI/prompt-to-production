"""
UC-X — Ask My Documents
Implements agents.md + skills.md: retrieve_documents and answer_question.
Single-source policy Q&A with strict citation and exact refusal template.
"""
import os
import re
import sys

# ── Constants ────────────────────────────────────────────────────────────────

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Forbidden hedging phrases (enforcement rule)
FORBIDDEN_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it could be inferred",
    "employees are generally expected to",
]


# ── Skill 1: retrieve_documents ──────────────────────────────────────────────

def retrieve_documents(file_paths: list[str]) -> dict:
    """
    Load all policy .txt files and index by {filename: {section: text}}.

    Raises FileNotFoundError or ValueError on any missing/unparseable file.
    Never returns a partial index.
    """
    index = {}
    for path in file_paths:
        filename = os.path.basename(path)
        try:
            with open(path, encoding="utf-8") as f:
                raw = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Policy file not found: {path}")

        # Parse numbered sections e.g. "3.1 ..."
        section_pattern = re.compile(
            r"(?m)^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+\s|\Z)", re.DOTALL
        )
        matches = section_pattern.findall(raw)
        if not matches:
            raise ValueError(f"{filename}: no numbered sections found.")

        sections = {}
        for sec_num, body in matches:
            text = " ".join(line.strip() for line in body.strip().splitlines() if line.strip())
            sections[sec_num] = text

        index[filename] = sections

    return index


# ── Skill 2: answer_question ─────────────────────────────────────────────────

# Keyword → (document hint, section hint) for known high-priority lookups
KNOWN_LOOKUPS = {
    # personal device / byod
    ("personal device", "personal phone", "byod", "own phone", "own device"):
        ("policy_it_acceptable_use.txt", "3.1"),
    # carry forward leave
    ("carry forward", "carry-forward", "unused leave", "annual leave"):
        ("policy_hr_leave.txt", "2.6"),
    # leave without pay approver
    ("leave without pay", "lwp", "who approves"):
        ("policy_hr_leave.txt", "5.2"),
    # slack / software install
    ("install", "slack", "software", "app"):
        ("policy_it_acceptable_use.txt", "2.3"),
    # home office equipment
    ("home office", "equipment allowance", "wfh equipment", "work from home equipment"):
        ("policy_finance_reimbursement.txt", "3.1"),
    # da and meal receipts
    ("da and meal", "daily allowance and meal", "meal receipt", "da and meal receipt"):
        ("policy_finance_reimbursement.txt", "2.6"),
    # leave encashment
    ("encash", "encashment"):
        ("policy_hr_leave.txt", "7.2"),
}


def _keyword_lookup(question: str, index: dict) -> dict | None:
    """Try to find an answer using known keyword→section mappings."""
    q = question.lower()
    for keywords, (doc, sec) in KNOWN_LOOKUPS.items():
        if any(kw in q for kw in keywords):
            if doc in index and sec in index[doc]:
                return {
                    "answer":  index[doc][sec],
                    "source":  f"{doc}, section {sec}",
                    "refused": False,
                }
    return None


def _full_text_search(question: str, index: dict) -> dict | None:
    """
    Search all sections for keyword overlap. Returns best single-source match
    only — never combines across documents.
    """
    q_words = set(re.findall(r"\w+", question.lower()))
    best_score = 0
    best_doc   = None
    best_sec   = None
    best_text  = None

    for doc, sections in index.items():
        for sec, text in sections.items():
            sec_words = set(re.findall(r"\w+", text.lower()))
            score = len(q_words & sec_words)
            if score > best_score:
                best_score = best_doc = None  # reset
                best_score = score
                best_doc   = doc
                best_sec   = sec
                best_text  = text

    if best_score >= 3:  # minimum overlap threshold
        return {
            "answer":  best_text,
            "source":  f"{best_doc}, section {best_sec}",
            "refused": False,
        }
    return None


def answer_question(index: dict, question: str) -> dict:
    """
    Answer a policy question from the indexed documents.

    Returns dict with keys: answer (str), source (str), refused (bool).
    Never combines text from two different documents.
    Never uses hedging phrases.
    Falls back to exact refusal template if no answer found.
    """
    if not index:
        raise ValueError("Document index is empty. Check retrieve_documents output.")

    if not question or not question.strip():
        return {"answer": REFUSAL_TEMPLATE, "source": "NONE", "refused": True}

    # Try known keyword lookup first (highest precision)
    result = _keyword_lookup(question, index)
    if result:
        return result

    # Try full-text search (single-source only)
    result = _full_text_search(question, index)
    if result:
        return result

    # No match — use exact refusal template
    return {"answer": REFUSAL_TEMPLATE, "source": "NONE", "refused": True}


# ── Entry point (interactive CLI) ────────────────────────────────────────────

def main():
    # Resolve policy file paths relative to this script or from data/
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    data_dir    = os.path.join(script_dir, "..", "data", "policy-documents")
    file_paths  = [os.path.join(data_dir, f) for f in POLICY_FILES]

    print("UC-X — Ask My Documents")
    print("Loading policy documents...", end=" ")
    try:
        index = retrieve_documents(file_paths)
    except (FileNotFoundError, ValueError) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"OK ({len(index)} documents indexed)\n")

    print("Type your question and press Enter. Type 'quit' to exit.\n")
    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue

        result = answer_question(index, question)

        print()
        if result["refused"]:
            print(f"[REFUSED]  {result['answer']}")
        else:
            print(f"[ANSWER]  {result['answer']}")
            print(f"   [SOURCE]  {result['source']}")
        print()


if __name__ == "__main__":
    main()
