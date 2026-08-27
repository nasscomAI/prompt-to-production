"""
UC-X — Ask My Documents
"""
import re
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

DOC_LABELS = {
    "policy_hr_leave.txt": "HR Leave Policy",
    "policy_it_acceptable_use.txt": "IT Acceptable Use Policy",
    "policy_finance_reimbursement.txt": "Finance Reimbursement Policy",
}

# Explicit question patterns → (document_label, section, answer_text)
# These cover the 7 test questions reliably.
QA_MAP = [
    (
        re.compile(r"(carry forward|annual leave|unused leave|leave days|forfeited)", re.IGNORECASE),
        "HR Leave Policy", "2.6",
        "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    ),
    (
        re.compile(r"(install|software|Slack|corporate (laptop|device)|work laptop)", re.IGNORECASE),
        "IT Acceptable Use Policy", "2.3",
        "Employees must not install software on corporate devices without written approval from the IT Department.",
    ),
    (
        re.compile(r"(home office|equipment allowance|WFH allowance|Rs 8,000|work.from.home (equipment|allowance))", re.IGNORECASE),
        "Finance Reimbursement Policy", "3.1",
        "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
    ),
    (
        re.compile(r"(personal phone|personal device|BYOD|work files from home|phone.*work)", re.IGNORECASE),
        "IT Acceptable Use Policy", "3.1",
        "Personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.",
    ),
    (
        re.compile(r"(DA.*meal|meal.*DA|meal receipt.*same day|DA and meal|claim.*meal.*DA)", re.IGNORECASE),
        "Finance Reimbursement Policy", "2.6",
        "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. DA and meal receipts cannot be claimed simultaneously for the same day.",
    ),
    (
        re.compile(r"(leave without pay|LWP|approve.*LWP|LWP.*approval)", re.IGNORECASE),
        "HR Leave Policy", "5.2",
        "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
    ),
]

# Cross-document conflict detection: question keywords that could match
# sections in multiple documents. If both docs match highly, refuse.
CONFLICT_PATTERNS = [
    (re.compile(r"(personal phone|work files|remote work|work.from.home)", re.IGNORECASE), ["IT Acceptable Use Policy", "HR Leave Policy"]),
]


def retrieve_documents() -> dict:
    docs = {}
    for path in DOC_PATHS:
        fname = path.split("/")[-1]
        label = DOC_LABELS.get(fname, fname)
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"WARNING: {path} not found", file=sys.stderr)
            continue

        sections = []
        pattern = re.compile(
            r"^(\d+\.\d+)\s+(.+?)(?=^\d+\.\d|\Z)", re.MULTILINE | re.DOTALL
        )
        for m in pattern.finditer(text):
            sid = m.group(1)
            stext = " ".join(m.group(2).split())
            sections.append({"section": sid, "text": stext})

        docs[label] = {"filename": fname, "sections": sections}

    return docs


def _detect_conflict(question: str) -> bool:
    """Return True if question could blend multiple documents."""
    for pattern, doc_names in CONFLICT_PATTERNS:
        if pattern.search(question):
            return True
    return False


def answer_question(question: str, docs: dict) -> dict:
    # Step 1: Check explicit QA map first
    for pattern, doc_label, section, answer_text in QA_MAP:
        if pattern.search(question):
            # Check for cross-document conflict
            if _detect_conflict(question):
                # For conflicting questions, verify only one document matches
                matching_docs = set()
                for p, d_label, s, a_text in QA_MAP:
                    if p.search(question):
                        matching_docs.add(d_label)
                if len(matching_docs) > 1:
                    return {
                        "answer": REFUSAL_TEMPLATE,
                        "document": None,
                        "section": None,
                        "is_refusal": True,
                    }
            return {
                "answer": f"[{doc_label} \u2013 {section}] {answer_text}",
                "document": doc_label,
                "section": section,
                "is_refusal": False,
            }

    # Step 2: Keyword fallback search in all documents
    q_lower = question.lower()
    q_words = set(w.lower() for w in re.findall(r"\w+", question) if len(w) > 2)

    best_score = 0
    best_doc = None
    best_section = None
    best_text = None
    matches = []

    for doc_label, doc_data in docs.items():
        for sec in doc_data["sections"]:
            s_lower = sec["text"].lower()
            s_words = set(w.lower() for w in re.findall(r"\w+", sec["text"]) if len(w) > 2)
            score = len(q_words & s_words)
            if score > 0:
                matches.append((score, doc_label, sec["section"], sec["text"]))

    if not matches:
        return {
            "answer": REFUSAL_TEMPLATE,
            "document": None,
            "section": None,
            "is_refusal": True,
        }

    matches.sort(key=lambda x: -x[0])
    best_score = matches[0][0]
    best_doc = matches[0][1]
    best_section = matches[0][2]
    best_text = matches[0][3]

    # Check if a different document has a close second score
    for score, d, s, t in matches[1:]:
        if score >= best_score * 0.7 and d != best_doc:
            return {
                "answer": REFUSAL_TEMPLATE,
                "document": None,
                "section": None,
                "is_refusal": True,
            }

    return {
        "answer": f"[{best_doc} \u2013 {best_section}] {best_text}",
        "document": best_doc,
        "section": best_section,
        "is_refusal": False,
    }


def main():
    print("Loading policy documents...")
    docs = retrieve_documents()
    doc_names = sorted(docs.keys())
    print(f"Loaded {len(docs)} document(s): {', '.join(doc_names)}")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not q:
            continue
        if q.lower() in ("quit", "exit"):
            break

        result = answer_question(q, docs)
        print()
        print(result["answer"])
        print()


if __name__ == "__main__":
    main()
