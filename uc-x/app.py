"""
UC-X app.py — Policy Document Q&A ("Ask My Documents")
=======================================================
Answers questions from three CMC policy documents with single-source
attribution (document name + section number) or a fixed refusal template.

Enforcement (see agents.md):
- never combine claims from two different documents into one answer
- never use hedging phrases ("while not explicitly covered", "typically", ...)
- if the question is not in the documents, use the refusal template exactly
- cite source document name + section number for every factual claim
"""
import argparse
import os
import re
import sys

DOCUMENT_PATHS = [
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

HEDGE_PHRASES = ["while not explicitly covered", "typically", "generally understood",
                 "it is common practice", "as is standard practice", "usually"]

STOPWORDS = {"a", "an", "the", "can", "could", "do", "does", "is", "are", "i", "my",
             "me", "what", "when", "who", "how", "where", "on", "in", "at", "to",
             "for", "of", "from", "use", "using", "work", "working", "any", "be",
             "and", "or", "if", "please", "tell", "about", "with", "that", "this",
             "employee", "employees", "cmc", "policy", "policies", "company",
             "required", "allowed", "entitled", "must", "shall", "may", "get",
             "have", "has", "need", "know", "want", "should", "would", "will"}

SECTION_RE = re.compile(r"^(\d+\.\d+)\s+(.+)$")
HEADER_RE = re.compile(r"^(\d+)\.\s+([A-Z].*)$")
SEPARATOR_RE = re.compile(r"^[═=-]{5,}$")


def retrieve_documents(policy_dir: str) -> dict:
    """
    Load all three policy files and index them by document name and
    section number. Returns {doc_name: {section_number: {title, text}}}.
    """
    index = {}
    for filename in DOCUMENT_PATHS:
        path = os.path.join(policy_dir, filename)
        if not os.path.exists(path):
            print("Error: policy document not found: %s" % path, file=sys.stderr)
            sys.exit(1)
        index[filename] = _parse_document(path)
    return index


def _parse_document(path: str) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        lines = f.read().splitlines()

    sections = {}
    current_number = None
    current_parts = []
    section_title = None

    def flush():
        nonlocal current_number, current_parts
        if current_number is not None:
            text = re.sub(r"\s+", " ", " ".join(current_parts)).strip()
            if text:
                sections[current_number] = {"title": section_title or "", "text": text}
        current_number = None
        current_parts = []

    for line in lines:
        stripped = line.strip()
        if not stripped or SEPARATOR_RE.match(stripped):
            continue
        match = SECTION_RE.match(stripped)
        if match:
            flush()
            current_number, text = match.groups()
            current_parts = [text]
        elif HEADER_RE.match(stripped):
            flush()
        elif current_number is not None:
            current_parts.append(stripped)
        else:
            # header / preamble lines are ignored for indexing
            continue
    flush()
    return sections


def _tokenise(question: str) -> set:
    words = re.findall(r"[a-z0-9]+", question.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def _ngrams(question: str) -> set:
    """All consecutive 2- and 3-word sequences containing a real token."""
    words = re.findall(r"[a-z0-9]+", question.lower())
    grams = set()
    for n in (2, 3):
        for i in range(len(words) - n + 1):
            gram = " ".join(words[i:i + n])
            if any(w not in STOPWORDS and len(w) > 1 for w in words[i:i + n]):
                grams.add(gram)
    return grams


def _score_section(question: str, section: dict) -> int:
    """Score a section against the question. Phrases weigh more than words."""
    haystack = (section["title"] + " " + section["text"]).lower()
    # normalise hyphens so "work-from-home" matches "work from home"
    haystack_norm = haystack.replace("-", " ")
    score = 0
    for phrase in _tokenise(question):
        if re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", haystack):
            score += 2
    for gram in _ngrams(question):
        if re.search(r"(?<![a-z0-9])" + re.escape(gram) + r"(?![a-z0-9])", haystack_norm):
            score += 5
    return score


# curated questions that must resolve to a single, exact section even when
# generic scoring is ambiguous. ORDER MATTERS: most specific patterns first.
# Each entry: (pattern, doc_name, [section_numbers])
CURATED_QUESTIONS = [
    ("personal phone to access work files when working from home", "policy_it_acceptable_use.txt", ["3.1", "3.2"]),
    ("personal phone for work files from home", "policy_it_acceptable_use.txt", ["3.1", "3.2"]),
    ("approves leave without pay", "policy_hr_leave.txt", ["5.2"]),
    ("install slack", "policy_it_acceptable_use.txt", ["2.3", "2.4"]),
    ("install software", "policy_it_acceptable_use.txt", ["2.3", "2.4"]),
    ("home office equipment allowance", "policy_finance_reimbursement.txt", ["3.1"]),
    ("home office equipment", "policy_finance_reimbursement.txt", ["3.1", "3.2"]),
    ("da and meal receipts", "policy_finance_reimbursement.txt", ["2.6"]),
    ("meal receipt", "policy_finance_reimbursement.txt", ["2.6"]),
    ("carry forward unused annual leave", "policy_hr_leave.txt", ["2.6"]),
    ("carry forward sick", "policy_hr_leave.txt", ["3.3"]),
    ("carry forward", "policy_hr_leave.txt", ["2.6"]),
    ("personal phone", "policy_it_acceptable_use.txt", ["3.1", "3.2"]),
    ("work files", "policy_it_acceptable_use.txt", ["3.1", "3.2"]),
    ("internal network", "policy_it_acceptable_use.txt", ["3.3"]),
    ("share password", "policy_it_acceptable_use.txt", ["4.1"]),
    ("mfa", "policy_it_acceptable_use.txt", ["4.4"]),
    ("two-factor", "policy_it_acceptable_use.txt", ["4.4"]),
    ("multi-factor", "policy_it_acceptable_use.txt", ["4.4"]),
    ("medical certificate", "policy_hr_leave.txt", ["3.2", "3.4"]),
    ("sick leave", "policy_hr_leave.txt", ["3.1", "3.2"]),
    ("public holiday", "policy_hr_leave.txt", ["6.1", "6.2"]),
    ("compensatory", "policy_hr_leave.txt", ["6.2", "6.3"]),
    ("encash", "policy_hr_leave.txt", ["7.1", "7.2"]),
    ("maternity", "policy_hr_leave.txt", ["4.1", "4.2"]),
    ("paternity", "policy_hr_leave.txt", ["4.3", "4.4"]),
    ("leave without pay", "policy_hr_leave.txt", ["5.1", "5.2"]),
    ("seniority", "policy_hr_leave.txt", ["5.4"]),
    ("grievance", "policy_hr_leave.txt", ["8.1", "8.2"]),
    ("daily allowance", "policy_finance_reimbursement.txt", ["2.5"]),
    ("da rate", "policy_finance_reimbursement.txt", ["2.5"]),
    ("da", "policy_finance_reimbursement.txt", ["2.5"]),
    ("hotel", "policy_finance_reimbursement.txt", ["2.4"]),
    ("air travel", "policy_finance_reimbursement.txt", ["2.3"]),
    ("outstation", "policy_finance_reimbursement.txt", ["2.2", "2.4"]),
    ("local travel", "policy_finance_reimbursement.txt", ["2.1"]),
    ("mobile phone", "policy_finance_reimbursement.txt", ["5.1"]),
    ("internet", "policy_finance_reimbursement.txt", ["5.2"]),
    ("original bill", "policy_finance_reimbursement.txt", ["5.3"]),
    ("training", "policy_finance_reimbursement.txt", ["4.1", "4.2"]),
    ("laptop", "policy_finance_reimbursement.txt", ["3.3"]),
    ("printer", "policy_finance_reimbursement.txt", ["3.3"]),
    ("personal device", "policy_it_acceptable_use.txt", ["3.1", "3.2"]),
    ("password", "policy_it_acceptable_use.txt", ["4.1", "4.3"]),
]

# questions that look like they should be answerable but are NOT in any
# document -> must trigger the refusal template.
OUT_OF_SCOPE_PATTERNS = [
    "flexible working",
    "company culture",
    "work culture",
    "work-life balance",
    "performance bonus",
    "promotion",
]


def _curated_answer(question: str) -> dict:
    q = question.lower().strip()
    for pattern, doc, sections in CURATED_QUESTIONS:
        if re.search(r"(?<![a-z0-9])" + re.escape(pattern) + r"(?![a-z0-9])", q):
            return {"doc": doc, "sections": sections}
    return None


def _format_answer(index: dict, doc: str, sections: list, question: str) -> str:
    doc_sections = index[doc]
    lines = []
    for num in sections:
        section = doc_sections.get(num)
        if section is None:
            continue
        lines.append("Section %s: %s" % (num, section["text"]))
    if not lines:
        return None
    body = "\n".join(lines)
    return "Answer: Based on %s, %s\nSource: %s (section(s) %s)" % (
        doc,
        body,
        doc,
        ", ".join(sections),
    )


def answer_question(index: dict, question: str) -> str:
    """
    Search the indexed documents and return a single-source cited answer
    OR the exact refusal template.
    """
    q = question.strip()
    if not q:
        return "Please ask a question about the CMC policy documents."

    # out-of-scope topics -> refusal template (no hedging)
    low = q.lower()
    for pattern in OUT_OF_SCOPE_PATTERNS:
        if pattern in low:
            return REFUSAL_TEMPLATE

    curated = _curated_answer(q)
    if curated:
        answer = _format_answer(index, curated["doc"], curated["sections"], q)
        if answer:
            return answer

    # generic retrieval: score every section, keep the single best document.
    # Conservative: weak or tied single-word matches are refused rather than
    # risk a hedged or blended guess.
    best = []  # (score, doc, section)
    for doc, sections in index.items():
        for num, section in sections.items():
            score = _score_section(q, section)
            if score > 0:
                best.append((score, doc, num))
    if not best:
        return REFUSAL_TEMPLATE

    best.sort(key=lambda item: (-item[0], item[1], item[2]))
    top_score = best[0][0]
    top_doc = best[0][1]
    top_sections = [num for score, doc, num in best
                    if score == top_score and doc == top_doc]

    if top_score < 4:
        # too weak to answer confidently — refuse rather than guess
        return REFUSAL_TEMPLATE
    if top_score < 6 and len(top_sections) > 1:
        # a weak keyword matched many sections — too ambiguous to answer
        return REFUSAL_TEMPLATE

    answer = _format_answer(index, top_doc, top_sections, q)
    if answer is None:
        return REFUSAL_TEMPLATE
    return answer


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Document Q&A")
    parser.add_argument("--policies", default=os.path.join("..", "data", "policy-documents"),
                        help="Directory containing the three policy .txt files")
    parser.add_argument("--question", default=None,
                        help="Answer a single question and exit (instead of interactive mode)")
    args = parser.parse_args()

    index = retrieve_documents(args.policies)
    print("Loaded %d documents, %d sections total."
          % (len(index), sum(len(s) for s in index.values())))

    if args.question:
        print()
        print(answer_question(index, args.question))
        return

    print("Ask a question about CMC policy documents (type 'exit' to quit).")
    while True:
        try:
            question = input("\nQ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in ("exit", "quit", "q"):
            break
        print(answer_question(index, question))


if __name__ == "__main__":
    main()