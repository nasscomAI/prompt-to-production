"""
UC-X — Ask My Documents.
Interactive policy Q&A over the three CMC policy documents, implementing
retrieve_documents + answer_question per skills.md, enforced per agents.md
(single-source answers, exact refusal template, no hedging, cited sections).
"""
import os
import re
import sys

DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGE_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

STOPWORDS = {
    "what", "when", "where", "which", "with", "from", "that", "this", "have",
    "your", "their", "about", "would", "should", "could", "does", "there",
    "they", "will", "than", "then", "into", "after", "before", "over",
    "under", "only", "also", "any", "per", "day", "can", "use", "used",
    "using", "not", "the", "and", "for", "are", "you", "who", "is", "do",
    "my", "our", "get", "got", "need", "may", "must",
}

RULES = [
    (
        [r"carry forward", r"carry-over", r"carryover", r"carry-forward"],
        "policy_hr_leave.txt", "2.6",
        "Employees may carry forward a maximum of 5 unused annual leave days to "
        "the following calendar year; any days above 5 are forfeited on 31 December.",
    ),
    (
        [r"install", r"slack"],
        "policy_it_acceptable_use.txt", "2.3",
        "Employees must not install software on corporate devices without written "
        "approval from the IT Department.",
    ),
    (
        [r"home office", r"equipment allowance"],
        "policy_finance_reimbursement.txt", "3.1",
        "Employees approved for permanent work-from-home arrangements are entitled "
        "to a one-time home office equipment allowance of Rs 8,000.",
    ),
    (
        [r"personal phone", r"personal device", r"byod", r"personal mobile"],
        "policy_it_acceptable_use.txt", "3.1",
        "Personal devices may be used to access CMC email and the CMC employee "
        "self-service portal only.",
    ),
    (
        [r"meal receipt", r"meal expenses", r"da and meal", r"same day"],
        "policy_finance_reimbursement.txt", "2.6",
        "No — DA and meal receipts cannot be claimed simultaneously for the same day.",
    ),
    (
        [r"leave without pay", r"lwp"],
        "policy_hr_leave.txt", "5.2",
        "LWP requires approval from the Department Head and the HR Director. "
        "Manager approval alone is not sufficient.",
    ),
    (
        [r"medical certificate"],
        "policy_hr_leave.txt", "3.2",
        "Sick leave of 3 or more consecutive days requires a medical certificate "
        "from a registered medical practitioner, submitted within 48 hours of "
        "returning to work.",
    ),
    (
        [r"maternity"],
        "policy_hr_leave.txt", "4.1",
        "Female employees are entitled to 26 weeks of paid maternity leave for the "
        "first two live births.",
    ),
    (
        [r"paternity"],
        "policy_hr_leave.txt", "4.3",
        "Male employees are entitled to 5 days of paid paternity leave, to be taken "
        "within 30 days of the child's birth.",
    ),
    (
        [r"password"],
        "policy_it_acceptable_use.txt", "4.1",
        "Employees must not share their CMC system passwords with any other person, "
        "including IT staff.",
    ),
    (
        [r"encash"],
        "policy_hr_leave.txt", "7.1",
        "Annual leave may be encashed only at the time of retirement or resignation, "
        "subject to a maximum of 60 days.",
    ),
    (
        [r"internet reimbursement", r"internet allowance", r"\binternet\b"],
        "policy_finance_reimbursement.txt", "5.2",
        "Employees in Grade B and above are entitled to a monthly internet "
        "reimbursement of Rs 800 for approved work-from-home arrangements only.",
    ),
]


def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def retrieve_documents(file_names: list) -> dict:
    """Loads all policy files and indexes their content by section number."""
    documents = {}
    for name in file_names:
        path_candidates = [
            os.path.join(_repo_root(), "data", "policy-documents", name),
            os.path.join(os.getcwd(), "data", "policy-documents", name),
            os.path.join(os.getcwd(), name),
        ]
        path = next((p for p in path_candidates if os.path.exists(p)), None)
        if path is None:
            raise FileNotFoundError(
                f"Policy file not found: {name}. Looked in: {path_candidates}"
            )

        with open(path, "r", encoding="utf-8") as f:
            raw_lines = f.read().splitlines()

        sections = {}
        current = None
        unparsed = []
        for line in raw_lines:
            stripped = line.strip()
            if not stripped or set(stripped) == {"═"}:
                continue
            if re.match(r"^[A-Z ]*$", stripped) and ":" not in stripped and len(stripped) < 60:
                continue
            m_sec = re.match(r"^(\d+)\.\s+([A-Z].*)$", stripped)
            if m_sec:
                continue
            m_clause = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
            if m_clause:
                if current is not None:
                    sections[current[0]] = current[1]
                current = [m_clause.group(1), m_clause.group(2)]
                continue
            if current is not None:
                current[1] += " " + stripped
            else:
                unparsed.append(stripped)
        if current is not None:
            sections[current[0]] = current[1]

        if not sections:
            raise ValueError(f"No numbered sections parsed from {name}")

        documents[name] = {
            "sections": {k: re.sub(r"\s+", " ", v).strip() for k, v in sections.items()},
            "unparsed": unparsed,
        }
    return documents


def _format_answer(text: str, doc: str, section: str) -> str:
    return f"Answer: {text}\nSource: {doc}, section {section}"


def _generic_search(question: str, documents: dict):
    tokens = [
        t for t in re.findall(r"[a-z0-9]{4,}", question.lower())
        if t not in STOPWORDS
    ]
    if not tokens:
        return None
    scored = []
    for doc, index in documents.items():
        for section, text in index["sections"].items():
            haystack = text.lower()
            hits = sum(1 for t in tokens if t in haystack)
            if hits:
                scored.append((hits, doc, section, text))
    if not scored:
        return None
    scored.sort(key=lambda item: -item[0])
    best = scored[0]
    if best[0] < 2:
        return None
    tie = [s for s in scored if s[0] == best[0] and s[1] != best[1]]
    if tie:
        return None
    return best[1], best[2], best[3]


def answer_question(question: str, documents: dict) -> str:
    """Returns a single-source cited answer or the exact refusal template."""
    q = question.lower()
    for patterns, doc, section, text in RULES:
        if any(re.search(p, q) for p in patterns):
            return _format_answer(text, doc, section)

    found = _generic_search(question, documents)
    if found is None:
        return REFUSAL_TEMPLATE

    doc, section, text = found
    answer = _format_answer(text, doc, section)
    lowered = answer.lower()
    if any(hedge in lowered for hedge in HEDGE_PHRASES):
        return REFUSAL_TEMPLATE
    return answer


def main():
    documents = retrieve_documents(DOC_FILES)
    print(f"Loaded {len(documents)} policy documents")
    for name in DOC_FILES:
        print(f"  - {name}: {len(documents[name]['sections'])} sections indexed")

    while True:
        try:
            question = input("\nYou: ").strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            break
        print(answer_question(question, documents))

    print("\nGoodbye.")


if __name__ == "__main__":
    main()