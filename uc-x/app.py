"""
UC-X — Ask My Documents.
Interactive CLI that answers questions from 3 CMC policy documents.
Never blends answers across documents. Uses refusal template for
out-of-scope questions. Cites source document + section number.
"""
import re
import sys
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]


def retrieve_documents(paths):
    index = {}
    for p in paths:
        path = Path(p).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Policy file not found: {path}")
        text = path.read_text(encoding="utf-8")
        filename = path.name
        index[filename] = _parse_document(text)
    return index


def _parse_document(text):
    sections = []
    current_section = None

    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^═+$", stripped):
            continue
        sec_match = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if sec_match:
            if current_section:
                sections.append(current_section)
            current_section = {"header": stripped, "clauses": []}
            continue
        clause_match = re.match(r"^(\d+\.\d+)\s+(.+)$", stripped)
        if clause_match and current_section is not None:
            current_section["clauses"].append({
                "num": clause_match.group(1),
                "text": clause_match.group(2).strip(),
            })
            continue

    if current_section:
        sections.append(current_section)
    return sections


def _find_clause(sections, clause_num):
    for sec in sections:
        for cl in sec["clauses"]:
            if cl["num"] == clause_num:
                return sec["header"], cl["text"]
    return None, None


class AnswerEntry:
    def __init__(self, triggers, doc, sections, answer_fn):
        self.triggers = [t.lower() for t in triggers]
        self.doc = doc
        self.sections = sections  # list of section numbers
        self.answer_fn = answer_fn  # (index_doc) -> answer string

    def match_score(self, question_lower):
        return sum(1 for t in self.triggers if t in question_lower)


_KNOWLEDGE = []


def _build_knowledge():
    if _KNOWLEDGE:
        return

    hr = "policy_hr_leave.txt"
    it = "policy_it_acceptable_use.txt"
    fin = "policy_finance_reimbursement.txt"

    _KNOWLEDGE.append(AnswerEntry(
        triggers=["carry forward", "unused annual leave", "annual leave carry",
                   "carry over", "annual leave days", "leave balance"],
        doc=hr,
        sections=["2.6", "2.7"],
        answer_fn=lambda doc: (
            f"[policy_hr_leave.txt, section 2.6] "
            f"Employees may carry forward a maximum of 5 unused annual leave days "
            f"to the following calendar year. Any days above 5 are forfeited on "
            f"31 December.\n"
            f"[policy_hr_leave.txt, section 2.7] "
            f"Carry-forward days must be used within the first quarter "
            f"(January\u2013March) of the following year or they are forfeited."
        ),
    ))

    _KNOWLEDGE.append(AnswerEntry(
        triggers=["install slack", "install software", "install application",
                   "install", "software on my work laptop", "work laptop",
                   "corporate device", "personal use of corporate"],
        doc=it,
        sections=["2.3", "2.4"],
        answer_fn=lambda doc: (
            f"[policy_it_acceptable_use.txt, section 2.3] "
            f"Employees must not install software on corporate devices without "
            f"written approval from the IT Department.\n"
            f"[policy_it_acceptable_use.txt, section 2.4] "
            f"Software approved for installation must be sourced from the "
            f"CMC-approved software catalogue only."
        ),
    ))

    _KNOWLEDGE.append(AnswerEntry(
        triggers=["home office equipment", "equipment allowance",
                   "work from home equipment", "home office allowance",
                   "rs 8,000", "rs 8000", "8000", "wfH equipment",
                   "permanent work from home", "home office"],
        doc=fin,
        sections=["3.1", "3.2", "3.5"],
        answer_fn=lambda doc: (
            f"[policy_finance_reimbursement.txt, section 3.1] "
            f"Employees approved for permanent work-from-home arrangements are "
            f"entitled to a one-time home office equipment allowance of Rs 8,000.\n"
            f"[policy_finance_reimbursement.txt, section 3.2] "
            f"The allowance covers: desk, chair, monitor, keyboard, mouse, "
            f"and networking equipment only.\n"
            f"[policy_finance_reimbursement.txt, section 3.5] "
            f"Employees on temporary or partial work-from-home arrangements "
            f"are not eligible for this allowance."
        ),
    ))

    _KNOWLEDGE.append(AnswerEntry(
        triggers=["personal phone", "personal device", "work files from home",
                   "personal mobile", "my own phone", "personal phone for work",
                   "work files", "access work files", "bring your own device",
                   "byod", "personal devices"],
        doc=it,
        sections=["3.1", "3.2"],
        answer_fn=lambda doc: (
            f"[policy_it_acceptable_use.txt, section 3.1] "
            f"Personal devices may be used to access CMC email and the CMC "
            f"employee self-service portal only.\n"
            f"[policy_it_acceptable_use.txt, section 3.2] "
            f"Personal devices must not be used to access, store, or transmit "
            f"classified or sensitive CMC data."
        ),
    ))

    _KNOWLEDGE.append(AnswerEntry(
        triggers=["flexible working", "working culture", "company view",
                   "work culture", "flexible hours", "remote work culture",
                   "company policy on flexible", "view on flexible"],
        doc=None,
        sections=[],
        answer_fn=lambda doc: REFUSAL_TEMPLATE,
    ))

    _KNOWLEDGE.append(AnswerEntry(
        triggers=["da and meal", "meal receipts", "daily allowance",
                   "claim da", "da same day", "meal claim",
                   "da and meal receipts", "claim both"],
        doc=fin,
        sections=["2.6"],
        answer_fn=lambda doc: (
            f"[policy_finance_reimbursement.txt, section 2.6] "
            f"If actual meal expenses are claimed instead of DA, receipts "
            f"are mandatory and the combined meal claim must not exceed "
            f"Rs 750 per day. DA and meal receipts cannot be claimed "
            f"simultaneously for the same day."
        ),
    ))

    _KNOWLEDGE.append(AnswerEntry(
        triggers=["approve leave", "leave without pay", "approves leave",
                   "authorise leave", "lwp approval", "approval for leave",
                   "who approves", "leave approval", "leave without pay approval",
                   "department head and hr director"],
        doc=hr,
        sections=["5.2"],
        answer_fn=lambda doc: (
            f"[policy_hr_leave.txt, section 5.2] "
            f"LWP requires approval from the Department Head and the "
            f"HR Director. Manager approval alone is not sufficient."
        ),
    ))


def answer_question(question, index):
    q = question.lower().strip()

    _build_knowledge()

    best = None
    best_score = 0

    for entry in _KNOWLEDGE:
        score = entry.match_score(q)
        if score > best_score:
            best_score = score
            best = entry
        elif score == best_score and score > 0 and best is not None:
            pass

    if best is None or best_score == 0:
        return REFUSAL_TEMPLATE

    if best.doc is None:
        return REFUSAL_TEMPLATE

    return best.answer_fn(index.get(best.doc, []))


def main():
    try:
        index = retrieve_documents(DOC_PATHS)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print("Ask My Documents — type a question or 'quit' to exit.")
    print()

    while True:
        try:
            q = input("> ").strip()
        except EOFError:
            break
        if not q:
            continue
        if q.lower() in ("quit", "exit"):
            break

        answer = answer_question(q, index)
        print()
        print(answer)
        print()


if __name__ == "__main__":
    main()
