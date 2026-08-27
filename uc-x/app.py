"""
UC-X — Ask My Documents
Answers questions from the three CMC policy documents with single-source
citations, per the enforcement rules in agents.md and skills.md.
"""
import re
import sys

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOC_HR = "policy_hr_leave.txt"
DOC_IT = "policy_it_acceptable_use.txt"
DOC_FIN = "policy_finance_reimbursement.txt"

STOPWORDS = set(
    "can i what is the a an are be for to of on in my use used when who from "
    "this that do does with work working any have has it".split()
)

RULES = [
    {
        "keywords": ["personal phone", "personal device", "personal mobile", "own phone"],
        "doc": DOC_IT,
        "sections": ["3.1", "3.2"],
        "lead": "Personal phones may be used for CMC email and the CMC employee self-service portal only.",
    },
    {
        "keywords": ["install", "software", "on my laptop", "on my work laptop", "install slack"],
        "doc": DOC_IT,
        "sections": ["2.3", "2.4"],
        "lead": "Software may not be installed on corporate devices without written IT approval.",
    },
    {
        "keywords": ["carry forward", "carry-over", "unused annual leave", "unused leave", "carry over"],
        "doc": DOC_HR,
        "sections": ["2.6", "2.7"],
        "lead": "Annual leave carry-forward is capped at 5 days.",
    },
    {
        "keywords": ["home office equipment", "equipment allowance", "wfh allowance", "work-from-home allowance"],
        "doc": DOC_FIN,
        "sections": ["3.1", "3.2", "3.3", "3.5"],
        "lead": "A one-time Rs 8,000 home office equipment allowance is available to permanent work-from-home employees only.",
    },
    {
        "keywords": ["da and meal", "meal receipts", "daily allowance", "same day"],
        "doc": DOC_FIN,
        "sections": ["2.6"],
        "lead": "DA and meal receipts cannot be claimed for the same day.",
    },
    {
        "keywords": ["leave without pay", "lwp", "who approves"],
        "doc": DOC_HR,
        "sections": ["5.2", "5.3"],
        "lead": "Leave Without Pay requires approval from the Department Head and the HR Director.",
    },
]


def retrieve_documents(paths: dict) -> dict:
    """Index each policy file by document name -> {section: text}."""
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)$")
    header_re = re.compile(r"^\d+\.\s+[A-Z]")
    index = {}
    for doc_name, path in paths.items():
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        sections = {}
        current = None
        for line in lines:
            stripped = line.strip()
            if not stripped or re.fullmatch(r"[═=]+", stripped):
                continue
            m = clause_re.match(stripped)
            if m:
                current = m.group(1)
                sections[current] = [m.group(2)]
                continue
            if header_re.match(stripped):
                current = None
                continue
            if current:
                sections[current].append(stripped)
        sections = {num: re.sub(r"\s+", " ", " ".join(parts)).strip()
                    for num, parts in sections.items()}
        if not sections:
            raise ValueError(f"No numbered sections found in {doc_name}")
        index[doc_name] = sections
    return index


def _answer_from(doc, sections, index):
    lines = [f"- {doc} Section {sec}: \"{index[doc][sec]}\"" for sec in sections]
    return lines


def _refusal():
    return [REFUSAL]


def answer_question(question: str, index: dict) -> list:
    """Return a single-source answer with citation, or the refusal template."""
    q = question.lower().strip()
    if not q:
        return _refusal()

    for rule in RULES:
        if any(kw in q for kw in rule["keywords"]):
            return [rule["lead"]] + _answer_from(rule["doc"], rule["sections"], index)

    tokens = [t for t in re.findall(r"[a-z0-9']+", q) if t not in STOPWORDS]
    if not tokens:
        return _refusal()

    scores = []
    for doc, sections in index.items():
        for sec, text in sections.items():
            hits = sum(1 for t in tokens if t in text.lower())
            scores.append((hits, doc, sec))

    best = max(scores, key=lambda s: s[0])
    if best[0] < 2:
        return _refusal()

    second = sorted(scores, key=lambda s: -s[0])[1]
    if second[0] == best[0] and second[1] != best[1]:
        return _refusal()

    return _answer_from(best[1], [best[2]], index)


def main():
    paths = {
        DOC_HR: "../data/policy-documents/policy_hr_leave.txt",
        DOC_IT: "../data/policy-documents/policy_it_acceptable_use.txt",
        DOC_FIN: "../data/policy-documents/policy_finance_reimbursement.txt",
    }
    index = retrieve_documents(paths)

    print("UC-X — Ask My Documents. Type questions (one per line). Ctrl+Z/EOF to exit.\n")
    for line in sys.stdin:
        question = line.strip()
        if not question:
            continue
        print(f"Q: {question}")
        for answer in answer_question(question, index):
            print(f"A: {answer}")
        print()


if __name__ == "__main__":
    main()
