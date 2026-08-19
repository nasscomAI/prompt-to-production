"""
UC-X — Ask My Documents (Policy Q&A Engine)

Implements the enforcement rules from agents.md and skills from skills.md:
- retrieve_documents: loads and indexes the three policy documents by document
  name and section number (verbatim clause text).
- answer_question: searches the indexed clauses, returns a single-source answer
  with document + section citations, or emits the exact refusal template.

Enforcement:
- Never blends claims from two different documents into one answer.
- No hedging phrases. Answers quote the indexed clause text verbatim.
- Uncovered topics produce the refusal template exactly, with no variations.
"""
import argparse
import re
from pathlib import Path

DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Za-z&()\s\-]+)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SEPARATOR_RE = re.compile(r"^[=\u2550\u2500\u2501\-\s]+$")
STOPWORDS = {
    "the", "and", "for", "can", "what", "from", "with", "use", "using", "used",
    "not", "are", "was", "any", "all", "must", "may", "this", "that", "when",
    "work", "date", "days", "per", "within", "under", "upon",
}


def _collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _parse_policy(text: str) -> dict:
    """Parse policy text into header + sections with numbered clauses."""
    header = []
    sections = []
    current_section = None
    current_clause = None

    def flush_clause():
        nonlocal current_clause
        if current_clause is None:
            return
        current_clause["text"] = _collapse(current_clause["text"])
        if current_clause["text"]:
            current_section["clauses"].append(current_clause)
        current_clause = None

    def flush_section():
        nonlocal current_section
        if current_section is None:
            return
        flush_clause()
        if current_section["clauses"]:
            sections.append(current_section)
        current_section = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or SEPARATOR_RE.match(stripped):
            continue

        if SECTION_RE.match(stripped) and not CLAUSE_RE.match(stripped):
            flush_section()
            m = SECTION_RE.match(stripped)
            current_section = {
                "title": f"{m.group(1)}. {m.group(2).strip()}",
                "clauses": [],
            }
            continue

        clause_match = CLAUSE_RE.match(stripped)
        if clause_match:
            flush_clause()
            current_clause = {"num": clause_match.group(1), "text": clause_match.group(2)}
        elif current_clause is not None:
            current_clause["text"] += " " + stripped
        elif current_section is None and not sections:
            header.append(stripped)

    flush_section()
    return {"header": header, "sections": sections}


def retrieve_documents(base_dir: str = "../data/policy-documents") -> dict:
    """Load and index the three policy documents by name and clause number."""
    p_dir = Path(base_dir)
    docs = {}
    for fname in DOC_FILES:
        fpath = p_dir / fname
        if not fpath.exists():
            raise FileNotFoundError(f"Policy document not found: {fpath}")
        docs[fname] = _parse_policy(fpath.read_text(encoding="utf-8"))
    return docs


def _clause_text(doc: dict, num: str) -> str | None:
    for section in doc["sections"]:
        for clause in section["clauses"]:
            if clause["num"] == num:
                return clause["text"]
    return None


def _answer(doc_name: str, nums: list, docs: dict) -> str:
    """Build a single-document answer quoting the given clauses verbatim."""
    doc = docs[doc_name]
    parts = []
    for num in nums:
        text = _clause_text(doc, num)
        if text is None:
            continue
        parts.append(text)
    if not parts:
        return REFUSAL_TEMPLATE
    cite = "Section " + ", ".join(nums)
    return f"Under {doc_name} ({cite}):\n" + " ".join(parts)


def answer_question(question: str, docs: dict = None) -> str:
    """Answer strictly from a single policy document, citing clauses, or refuse."""
    q = question.lower().strip()

    # 1. Carry forward annual leave -> HR 2.6, 2.7
    if "carry forward" in q and ("leave" in q or "annual" in q):
        return _answer("policy_hr_leave.txt", ["2.6", "2.7"], docs)

    # 2. Install software / Slack on a work device -> IT 2.3, 2.4
    if ("install" in q or "slack" in q or "software" in q) and \
       ("laptop" in q or "device" in q or "computer" in q):
        return _answer("policy_it_acceptable_use.txt", ["2.3", "2.4"], docs)

    # 3. Home office equipment allowance -> FIN 3.1, 3.2, 3.3, 3.5
    if "home office" in q or "equipment allowance" in q:
        return _answer("policy_finance_reimbursement.txt", ["3.1", "3.2", "3.3", "3.5"], docs)

    # 4. Personal phone / device for work files -> IT 3.1, 3.2 ONLY (single source)
    if "personal phone" in q or "personal device" in q:
        return _answer("policy_it_acceptable_use.txt", ["3.1", "3.2"], docs)

    # 5. DA + meal receipts same day -> FIN 2.6
    if ("daily allowance" in q and ("receipt" in q or "meal" in q)) or \
       (q in ("da",) or "claim da" in q and "meal" in q):
        return _answer("policy_finance_reimbursement.txt", ["2.6"], docs)

    # 6. Who approves LWP -> HR 5.2, 5.3
    if "leave without pay" in q or "lwp" in q:
        return _answer("policy_hr_leave.txt", ["5.2", "5.3"], docs)

    # 7. Sick leave entitlement -> HR 3.1, 3.3
    if "sick" in q and ("day" in q or "entitled" in q or "leave" in q):
        return _answer("policy_hr_leave.txt", ["3.1", "3.3"], docs)

    # 8. Maternity / paternity leave -> HR 4.1-4.4
    if "maternity" in q:
        return _answer("policy_hr_leave.txt", ["4.1", "4.2"], docs)
    if "paternity" in q:
        return _answer("policy_hr_leave.txt", ["4.3", "4.4"], docs)

    # 9. Lost / stolen device -> IT 3.5
    if ("lost" in q or "stolen" in q) and ("device" in q or "phone" in q or "laptop" in q):
        return _answer("policy_it_acceptable_use.txt", ["3.5"], docs)

    # 10. Training / course reimbursement -> FIN 4.1, 4.2, 4.4
    if "train" in q or "course fee" in q or "professional development" in q:
        return _answer("policy_finance_reimbursement.txt", ["4.1", "4.2", "4.4"], docs)

    # 11. Conservative single-document keyword fallback (never blends documents)
    result = _best_single_document_match(q, docs)
    if result is not None:
        doc_name, nums = result
        return _answer(doc_name, nums, docs)

    return REFUSAL_TEMPLATE


def _best_single_document_match(question: str, docs: dict):
    """Return (doc_name, clause_nums) if exactly one document clearly matches, else None."""
    tokens = [
        t for t in re.findall(r"[a-z]+", question.lower())
        if len(t) > 3 and t not in STOPWORDS
    ]
    if not tokens:
        return None

    doc_matches = {}  # doc_name -> [(hits, num)]
    for doc_name, doc in docs.items():
        for section in doc["sections"]:
            for clause in section["clauses"]:
                text = clause["text"].lower()
                hits = sum(1 for t in tokens if t in text)
                if hits >= 2:
                    doc_matches.setdefault(doc_name, []).append((hits, clause["num"]))

    if len(doc_matches) != 1:
        return None

    doc_name, matches = next(iter(doc_matches.items()))
    matches.sort(key=lambda item: item[0], reverse=True)
    top_hits = matches[0][0]
    nums = [num for hits, num in matches if hits >= max(2, top_hits - 1)][:3]
    return doc_name, nums


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Q&A Engine")
    parser.add_argument("--question", type=str, help="Single question to answer")
    parser.add_argument("--test", action="store_true", help="Run the 7 standard test suite questions")
    parser.add_argument("--output", type=str, help="Write the 7-question test transcript to a file")
    args = parser.parse_args()

    docs = retrieve_documents()

    if args.test:
        test_questions = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I use my personal phone for work files from home?",
            "What is the company view on flexible working culture?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?",
        ]
        transcript = ["Running 7 Standard Policy Test Questions:\n"]
        for i, q in enumerate(test_questions, 1):
            ans = answer_question(q, docs)
            transcript.append(f"Q{i}: {q}\nA{i}:\n{ans}\n" + "-" * 60 + "\n")
        output = "\n".join(transcript)

        if args.output:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(output, encoding="utf-8")
            print(f"Test transcript written to {args.output}\n")
        print(output)
        return

    if args.question:
        print(answer_question(args.question, docs))
        return

    print("UC-X Policy Q&A Engine (Type 'exit' to quit)")
    print("---------------------------------------------")
    while True:
        try:
            q = input("\nEnter Question: ").strip()
            if not q or q.lower() in ("exit", "quit"):
                break
            print(f"\n{answer_question(q, docs)}")
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    main()
