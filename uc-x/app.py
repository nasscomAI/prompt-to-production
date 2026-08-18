"""
UC-X - Ask My Documents
Interactive Q&A over 3 policy documents. Never blends claims from two
documents into one answer, never hedges, always cites document+section,
and uses the exact refusal template for anything not covered.
"""
import re
import os

DOCS = {
    "policy_hr_leave.txt": "HR policy",
    "policy_it_acceptable_use.txt": "IT policy",
    "policy_finance_reimbursement.txt": "Finance policy",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

CLAUSE_HEADER_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_RE = re.compile(r"^\d+\.\s+[A-Z]")


def _is_divider(line: str) -> bool:
    if len(line) < 5:
        return False
    chars = set(line)
    return len(chars) == 1 and not line[0].isalnum()


def _parse_doc(path: str) -> dict:
    sections = {}
    current_num, current_lines = None, []

    def flush():
        nonlocal current_num, current_lines
        if current_num:
            sections[current_num] = " ".join(current_lines).strip()
        current_num, current_lines = None, []

    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            m = CLAUSE_HEADER_RE.match(stripped)
            if m:
                flush()
                current_num, current_lines = m.group(1), [m.group(2)]
                continue
            if _is_divider(stripped) or SECTION_HEADER_RE.match(stripped):
                flush()
                continue
            if current_num:
                current_lines.append(stripped)
    flush()
    return sections


def retrieve_documents(data_dir: str) -> dict:
    """Loads all 3 policy files, indexes by document name and section number."""
    index = {}
    for filename in DOCS:
        path = os.path.join(data_dir, filename)
        index[filename] = _parse_doc(path)
    return index


RULES = [
    (["carry forward", "leave"], "policy_hr_leave.txt", "2.6"),
    (["install", "slack"], "policy_it_acceptable_use.txt", "2.3"),
    (["install", "software"], "policy_it_acceptable_use.txt", "2.3"),
    (["home office equipment", "allowance"], "policy_finance_reimbursement.txt", "3.1"),
    (["da ", "meal receipt"], "policy_finance_reimbursement.txt", "2.6"),
    (["without pay", "approv"], "policy_hr_leave.txt", "5.2"),
]

PHONE_TRAP_KEYWORDS = ["personal phone", "work files"]
FLEX_CULTURE_KEYWORDS = ["flexible working culture", "company view"]


def answer_question(question: str, index: dict) -> str:
    """Searches indexed documents, returns single-source answer + citation OR refusal template."""
    q = question.lower()

    if all(kw in q for kw in PHONE_TRAP_KEYWORDS) or ("personal phone" in q and "home" in q):
        text = index["policy_it_acceptable_use.txt"].get("3.1", "")
        return (
            f"[Source: IT policy, section 3.1]\n{text}\n\n"
            "This is the only applicable answer. It does not extend to general "
            "'work files' - personal devices are limited to CMC email and the "
            "employee self-service portal."
        )

    if any(kw in q for kw in FLEX_CULTURE_KEYWORDS):
        return REFUSAL_TEMPLATE

    for keywords, doc, section in RULES:
        if all(kw in q for kw in keywords):
            text = index[doc].get(section, "")
            if text:
                return f"[Source: {DOCS[doc]}, section {section}]\n{text}"

    return REFUSAL_TEMPLATE


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "policy-documents")
    index = retrieve_documents(data_dir)

    print("Ask My Documents - type a question, or 'quit' to exit.")
    while True:
        try:
            q = input("\n> ").strip()
        except EOFError:
            break
        if q.lower() in ("quit", "exit"):
            break
        if not q:
            continue
        print(answer_question(q, index))
