"""
UC-X ("Ask My Documents") — policy question answerer.

Answers strictly from the three policy documents (HR leave, IT acceptable
use, finance reimbursement). Every answer cites exactly one source document
and section number, or returns the refusal template verbatim. See README.md,
agents.md, and skills.md.
"""
import argparse
import os
import re
import sys

DOC_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
)

MIN_SCORE = 2

PHRASE_COLLAPSES = [
    ("leave without pay", "lwp"),
    ("loss of pay", "lop"),
    ("daily allowance", "da"),
    ("work from home", "wfh"),
    ("working from home", "wfh"),
    ("work-from-home", "wfh"),
    ("carry forward", "carryforward"),
    ("carried forward", "carryforward"),
    ("carry-forward", "carryforward"),
    ("same day", "sameday"),
    ("personal phone", "personalphone"),
    ("personal devices", "personaldevices"),
    ("personal device", "personaldevices"),
]

CONCEPTS = {
    "carry_forward": ({"carryforward", "carry", "carriedforward"}, {"carryforward", "carry", "carriedforward"}, 3),
    "annual": ({"annual"}, {"annual"}, 1),
    "leave": ({"leave", "leaves"}, {"leave", "leaves"}, 1),
    "unused": ({"unused"}, {"unused"}, 1),
    "forfeit": ({"forfeit", "forfeited", "forfeiture"}, {"forfeit", "forfeited", "forfeiture"}, 1),
    "lwp": ({"lwp", "unpaid"}, {"lwp"}, 3),
    "lop": ({"lop"}, {"lop"}, 1),
    "approval": (
        {"approve", "approves", "approved", "approving", "approval"},
        {"approve", "approved", "approving", "approval"},
        1,
    ),
    "install_software": (
        {"install", "installing", "installed", "slack", "software", "app", "apps", "application", "applications"},
        {"install", "installing", "installed", "installation", "software"},
        4,
    ),
    "laptop": ({"laptop", "laptops"}, {"laptop", "laptops"}, 1),
    "phone": ({"phone", "phones", "smartphone", "smartphones", "mobile"}, {"phone", "phones", "smartphone", "smartphones", "mobile"}, 1),
    "personal_device": ({"personalphone", "personaldevices", "byod"}, {"personaldevices", "personalphone", "byod"}, 3),
    "access": ({"access", "accessing"}, {"access", "accessing", "accessed"}, 1),
    "work": ({"work", "working", "works", "duties", "duty", "official"}, {"work", "working", "works", "official", "duties", "duty"}, 1),
    "files": ({"files", "file"}, {"files", "file"}, 1),
    "home": ({"home", "remote", "wfh"}, {"home", "wfh"}, 1),
    "office": ({"office"}, {"office"}, 1),
    "equipment": ({"equipment", "gear", "furniture"}, {"equipment"}, 1),
    "allowance": ({"allowance", "allowances"}, {"allowance", "allowances"}, 2),
    "da": ({"da", "daily"}, {"da"}, 3),
    "meal": ({"meal", "meals"}, {"meal", "meals"}, 2),
    "receipts": ({"receipt", "receipts"}, {"receipt", "receipts"}, 1),
    "claim": (
        {"claim", "claims", "claimed", "claiming", "reimburse", "reimbursement", "reimbursements", "reimbursable"},
        {"claim", "claims", "claimed", "claiming", "reimbursable", "reimbursement"},
        1,
    ),
    "sameday": ({"sameday", "simultaneously", "together"}, {"sameday", "simultaneously", "together"}, 2),
    "company": ({"company", "corporation", "cmc"}, {"company", "corporation", "cmc"}, 1),
    "flexible": ({"flexible", "flexibility"}, {"flexible", "flexibility"}, 1),
    "culture": ({"culture", "cultural"}, {"culture", "cultural"}, 1),
    "view": ({"view", "views", "stance", "opinion", "position"}, {"view", "views", "stance", "opinion", "position"}, 1),
    "sick": ({"sick", "illness", "ill", "medical"}, {"sick", "medical", "certificate", "illness"}, 1),
    "maternity": ({"maternity", "maternal"}, {"maternity"}, 1),
    "paternity": ({"paternity", "paternal"}, {"paternity"}, 1),
    "holiday": ({"holiday", "holidays"}, {"holiday", "holidays"}, 1),
    "encash": ({"encash", "encashed", "encashment", "redeem"}, {"encash", "encashed", "encashment"}, 1),
    "travel": ({"travel", "travelling", "traveling", "outstation", "commute"}, {"travel", "travelling", "outstation", "local"}, 1),
    "hotel": ({"hotel", "accommodation", "lodging", "stay"}, {"hotel", "accommodation", "night"}, 1),
    "training": (
        {"training", "course", "courses", "seminar", "workshop"},
        {"training", "course", "courses", "professional", "development"},
        1,
    ),
    "internet": ({"internet", "broadband", "wifi", "data"}, {"internet", "broadband", "wifi", "data"}, 1),
}


def retrieve_documents():
    base = os.path.dirname(os.path.abspath(__file__))
    index = {}
    for order, rel in enumerate(DOC_FILES):
        path = os.path.join(base, rel)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing policy document: {path}")
        doc_name = os.path.basename(rel)
        index[doc_name] = _parse_document(path, doc_name, order)
    return index


def _normalize(text):
    t = text.lower()
    for phrase, repl in PHRASE_COLLAPSES:
        t = t.replace(phrase, repl)
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return " ".join(t.split())


def _clean_clause(text):
    return " ".join(text.split())


def _parse_document(path, doc_name, file_order):
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()
    sections = []
    title = ""
    current = None
    for raw in lines:
        raw = raw.rstrip("\n")
        if re.match(r"^[═\s]+$", raw):
            continue
        m_clause = re.match(r"^\s*(\d+)\.(\d+)\s+(.+)$", raw)
        if m_clause:
            if current is not None:
                sections.append(current)
            current = {
                "doc": doc_name,
                "num": f"{int(m_clause.group(1))}.{int(m_clause.group(2))}",
                "num_tuple": (int(m_clause.group(1)), int(m_clause.group(2))),
                "title": title,
                "text": m_clause.group(3).strip(),
                "file_order": file_order,
            }
            continue
        m_heading = re.match(r"^\s*(\d+)\.\s+([A-Z][A-Z0-9 \-/()]+)\s*$", raw)
        if m_heading:
            if current is not None:
                sections.append(current)
                current = None
            title = _clean_clause(m_heading.group(2))
            continue
        if current is not None:
            current["text"] += " " + raw.strip()
    if current is not None:
        sections.append(current)
    for sec in sections:
        searchable = _normalize(sec["text"])
        sec["tokens"] = set(searchable.split())
        sec["text"] = _clean_clause(sec["text"])
    return sections


def _extract_concepts(question):
    tokens = set(_normalize(question).split())
    return [(name, weight) for name, (triggers, terms, weight) in CONCEPTS.items() if tokens & triggers]


def _tiebreak_key(item):
    sec, score = item
    return (score, -sec["num_tuple"][0], -sec["num_tuple"][1])


def _score_sections(active, sections):
    scored = []
    for sec in sections:
        score = sum(weight for name, weight in active if sec["tokens"] & CONCEPTS[name][1])
        scored.append((sec, score))
    return scored


def answer_question(question, index):
    active = _extract_concepts(question)
    if not active:
        return REFUSAL_TEMPLATE
    doc_scores = []
    for doc_name, sections in index.items():
        scored = _score_sections(active, sections)
        if not scored:
            continue
        best = max(scored, key=_tiebreak_key)
        doc_scores.append((doc_name, best[1]))
    if not doc_scores:
        return REFUSAL_TEMPLATE
    doc_scores.sort(key=lambda r: -r[1])
    top_doc, top_score = doc_scores[0]
    if top_score < MIN_SCORE:
        return REFUSAL_TEMPLATE
    if len(doc_scores) > 1 and doc_scores[1][1] >= top_score:
        return REFUSAL_TEMPLATE
    scored = _score_sections(active, index[top_doc])
    sec, _ = max(scored, key=_tiebreak_key)
    return f"Source: {sec['doc']}, section {sec['num']}\n\n{sec['text']}"


def main():
    parser = argparse.ArgumentParser(description="UC-X — Ask My Documents")
    parser.add_argument("--question", help="Ask a single question and exit.")
    args = parser.parse_args()
    try:
        index = retrieve_documents()
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    if args.question:
        print(answer_question(args.question, index))
        return
    print("UC-X — Ask My Documents")
    print("Type a question, or 'exit' to quit.")
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit", "q", "bye"}:
            break
        print()
        print(answer_question(question, index))


if __name__ == "__main__":
    main()
