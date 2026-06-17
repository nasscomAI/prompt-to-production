"""
UC-X — Ask My Documents
Interactive CLI that answers questions from 3 CMC policy documents only.
Never blends documents. Uses exact refusal template when unanswerable.
"""
import re
import sys
from pathlib import Path

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

STOPWORDS = {
    "this", "that", "with", "from", "have", "been", "will", "must",
    "not", "are", "the", "for", "and", "can", "all", "any", "per",
    "may", "each", "their", "than", "into", "about", "shall", "also",
    "its", "has", "had", "but", "was", "were", "is", "be", "to", "of",
    "in", "on", "at", "by", "or", "an", "as", "do", "if", "use", "used",
    "using", "work", "working", "employee", "employees", "policy",
    "policies", "department", "company", "cmc", "including", "above",
    "within", "who", "what", "when", "where", "how", "why",
    "which", "does", "could", "would", "should", "after", "before",
    "during", "between", "under", "over", "through", "than", "then",
    "other", "such", "more", "very", "just", "also", "well",
}

DOMAIN_KEYWORDS = {
    "policy_hr_leave.txt": {
        "leave", "annual", "sick", "maternity", "paternity", "holiday",
        "encash", "grievance", "lwp",
    },
    "policy_it_acceptable_use.txt": {
        "access", "install", "software", "device", "password", "email",
        "internet", "data", "network", "portal", "byod", "corporate",
        "acceptable",
    },
    "policy_finance_reimbursement.txt": {
        "reimburse", "allowance", "travel", "receipt", "expense",
        "claim", "equip", "submission",
    },
}

RAW_STEMMER = {
    "approves": "approve", "approved": "approve", "approving": "approve",
    "carries": "carry", "carried": "carry", "carrying": "carry",
    "entitled": "entitle", "entitlement": "entitle",
    "reimbursement": "reimburse", "reimbursed": "reimburse", "reimbursable": "reimburse",
    "equipment": "equip",
    "receipts": "receipt",
    "expenses": "expense",
    "days": "day",
    "files": "file",
    "phones": "phone", "smartphone": "phone",
    "laptops": "laptop",
    "devices": "device",
    "documents": "document",
    "categories": "category",
    "benefits": "benefit",
    "exhausting": "exhaust",
    "permitted": "permit",
    "forfeited": "forfeit",
    "continuous": "continue",
    "compensatory": "compensate",
    "grievances": "grievance",
    "gazetted": "gazette",
    "written": "write",
    "approval": "approve",
    "monthly": "month",
    "annual": "year",
    "yearly": "year",
    "classroom": "class",
    "learning": "learn",
}

SECTION_TITLE_MAP = {
    "policy_hr_leave.txt": {
        "1": "purpose and scope",
        "2": "annual leave",
        "3": "sick leave",
        "4": "maternity and paternity leave",
        "5": "leave without pay lwp",
        "6": "public holidays",
        "7": "leave encashment",
        "8": "grievances",
    },
    "policy_it_acceptable_use.txt": {
        "1": "purpose and scope",
        "2": "corporate devices",
        "3": "personal devices byod",
        "4": "passwords and access control",
        "5": "data handling",
        "6": "internet and email use",
        "7": "violations and consequences",
    },
    "policy_finance_reimbursement.txt": {
        "1": "purpose and scope",
        "2": "travel reimbursement",
        "3": "work from home equipment",
        "4": "training and professional development",
        "5": "mobile phone and internet",
        "6": "submission process",
    },
}


def _stem(word: str):
    return RAW_STEMMER.get(word, word)


def parse_document(path: str):
    doc_name = Path(path).name
    text = Path(path).read_text()

    sections = []
    current_main = None
    current_sub = None
    current_lines = []
    main_titles = SECTION_TITLE_MAP.get(doc_name, {})

    def flush():
        nonlocal current_lines
        if current_sub is not None and current_lines:
            body = " ".join(current_lines).strip()
            sec_num = current_sub.split(".")[0]
            title = main_titles.get(sec_num, "")
            sections.append({
                "doc": doc_name,
                "section": current_sub,
                "section_title": title,
                "body": body,
            })
        current_lines = []

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        if re.match(r"^[═\-]{10,}", line):
            continue

        main_match = re.match(r"^(\d+)\.\s+([A-Z].*)", line)
        if main_match:
            flush()
            current_main = main_match.group(1)
            current_sub = None
            continue

        sub_match = re.match(r"^(\d+\.\d+)\s+(.*)", line)
        if sub_match:
            flush()
            current_sub = sub_match.group(1)
            rest = sub_match.group(2)
            if rest:
                current_lines.append(rest)
            continue

        if current_sub is not None:
            current_lines.append(line)

    flush()
    return sections


def extract_terms(text: str):
    terms = set()
    for w in re.findall(r"[a-zA-Z]\w+", text.lower()):
        w = w.rstrip(".,;:!?()").strip()
        w = _stem(w)
        if len(w) >= 3 and w not in STOPWORDS:
            terms.add(w)
    return terms


def extract_question_terms(text: str):
    terms = set()
    for w in re.findall(r"[a-zA-Z]\w+", text.lower()):
        w = w.rstrip(".,;:!?()").strip()
        w = _stem(w)
        if len(w) >= 3 and w not in STOPWORDS:
            terms.add(w)
    return terms


def build_index(sections):
    df = {}
    for sec in sections:
        body_terms = extract_terms(sec["body"])
        title_terms = extract_terms(sec["section_title"])
        all_terms = body_terms | title_terms
        sec["terms"] = all_terms
        for t in all_terms:
            df[t] = df.get(t, 0) + 1

    total = len(sections)
    idf = {}
    for t, doc_count in df.items():
        idf[t] = 1.0 / (1 + doc_count)

    return sections, idf


def compute_domain_boost(q_terms: set, doc_name: str) -> float:
    keywords = DOMAIN_KEYWORDS.get(doc_name, set())
    if not keywords:
        return 1.0
    matches = len(q_terms & keywords)
    if matches == 0:
        return 0.5
    return 1.0 + 0.3 * matches


def compute_title_boost(q_terms: set, section_title: str) -> float:
    title_terms = extract_terms(section_title)
    matches = len(q_terms & title_terms)
    return 1.0 + 0.5 * matches


def answer_question(question: str, sections, idf):
    q_terms = extract_question_terms(question)
    if not q_terms:
        return REFUSAL_TEMPLATE

    scored = []
    for sec in sections:
        overlap = q_terms & sec["terms"]
        content_score = sum(idf.get(t, 0) for t in overlap)
        boost = compute_domain_boost(q_terms, sec["doc"])
        title_boost = compute_title_boost(q_terms, sec["section_title"])
        scored.append((content_score * boost * title_boost, content_score, sec))

    scored.sort(key=lambda x: -x[0])
    top = [(fin_score, sec) for fin_score, content_score, sec in scored if fin_score > 0]

    if not top:
        return REFUSAL_TEMPLATE

    best_fin_score, best_sec = top[0]

    if best_fin_score < 0.01:
        return REFUSAL_TEMPLATE

    best_doc = best_sec["doc"]
    same_doc_count = sum(1 for fs, sec in top[:5] if sec["doc"] == best_doc and fs > 0)
    other_doc_count = sum(1 for fs, sec in top[:5] if sec["doc"] != best_doc and fs > 0)

    if other_doc_count > same_doc_count:
        return REFUSAL_TEMPLATE

    if len(top) > 1 and top[1][0] > 0 and best_sec["doc"] != top[1][1]["doc"]:
        if top[1][0] / best_fin_score > 0.6:
            return REFUSAL_TEMPLATE

    body = best_sec["body"]
    doc_name = best_sec["doc"]
    section = best_sec["section"]

    return f"Per {doc_name}, Section {section}: {body}"


def main():
    print("Loading policy documents...", file=sys.stderr)
    all_sections = []
    for p in DOC_PATHS:
        try:
            all_sections.extend(parse_document(p))
        except FileNotFoundError:
            print(f"Error: File not found at {p}", file=sys.stderr)
            sys.exit(1)

    sections, idf = build_index(all_sections)
    print(
        f"Loaded {len(sections)} sections across {len(DOC_PATHS)} documents.",
        file=sys.stderr,
    )
    print("Type your questions below (or 'exit' to quit).\n")

    while True:
        try:
            q = input("> ").strip()
        except EOFError:
            break
        if not q:
            continue
        if q.lower() in ("exit", "quit"):
            break
        print(answer_question(q, sections, idf))
        print()


if __name__ == "__main__":
    main()
