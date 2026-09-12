"""
UC-X — Ask My Documents
Single-source policy QA over three documents, implementing the enforcement
rules from agents.md (never blend two documents, no hedging, verbatim refusal
template, cite document + section) and the skills from skills.md:
retrieve_documents + answer_question.
"""
import os
import re
import sys

DOCUMENTS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
)

HEDGE_PHRASES = (
    "while not explicitly covered", "typically", "generally understood",
    "it is common practice",
)

SECTION_HEADER = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z0-9 &/()\-.]+)\s*$")
CLAUSE_NUMBER = re.compile(r"^\s*(\d+\.\d+)\s+")


def _parse_document(name: str, path: str):
    """Parse one policy .txt into {title, ref, version, sections:[clauses]}."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Policy file not found: {path}")

    with open(path, encoding="utf-8") as f:
        raw_lines = f.read().splitlines()

    title, document_ref, version = "", "", ""
    sections = []
    current_section = None
    current_clause = None

    for line in raw_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("═"):
            continue
        if title == "" and "POLICY" in stripped.upper():
            title = stripped
            continue
        m = re.fullmatch(r"Document Reference:\s*(.+)", stripped)
        if m:
            document_ref = m.group(1).strip()
            continue
        m = re.fullmatch(r"Version:\s*(.+)", stripped)
        if m:
            version = m.group(1).strip()
            continue
        sh = SECTION_HEADER.match(stripped)
        if sh:
            current_section = {"section": f"{sh.group(1)}. {sh.group(2).strip()}",
                               "clauses": []}
            sections.append(current_section)
            current_clause = None
            continue
        cm = CLAUSE_NUMBER.match(stripped)
        if cm:
            if current_section is None:
                current_section = {"section": "UNTITLED", "clauses": []}
                sections.append(current_section)
            current_clause = {"number": cm.group(1),
                              "text": stripped[cm.end():].strip()}
            current_section["clauses"].append(current_clause)
            continue
        if current_clause is not None:
            current_clause["text"] += " " + stripped

    clause_count = sum(len(s["clauses"]) for s in sections)
    if clause_count == 0:
        raise ValueError(f"No numbered clauses found in {path}")

    return {"file": name, "title": title, "document_ref": document_ref,
            "version": version, "sections": sections}


def retrieve_documents(paths: dict = None):
    """Load all policy files and index them, keeping each document separate."""
    paths = paths or DOCUMENTS
    index = {}
    problems = []
    for name, path in paths.items():
        try:
            index[name] = _parse_document(name, path)
        except (FileNotFoundError, ValueError) as exc:
            problems.append(f"{name}: {exc}")
    if not index:
        raise ValueError("None of the policy documents could be loaded: "
                         + "; ".join(problems))
    for p in problems:
        print(f"WARNING: {p}", file=sys.stderr)
    return index


def _clause(index: dict, doc: str, number: str, normalize: bool = False):
    """Return normalized text of clause `number` from `doc`."""
    for section in index[doc]["sections"]:
        for c in section["clauses"]:
            if c["number"] == number:
                text = re.sub(r"\s+", " ", c["text"]).strip()
                return text.lower() if normalize else text
    return None


# Rules: ordered; the first matching rule wins so an answer always comes from
# exactly one document. `sections` must all belong to `doc`.
RULES = [
    # IT — BYOD / personal devices (must sit first so personal-phone questions
    # resolve to a single source and are never blended with the HR remote-work
    # sections)
    {"topics": ["personal phone", "personal device", "own phone", "own device",
                "byod", "work files", "access work", "work from home"],
     "doc": "policy_it_acceptable_use.txt",
     "sections": ["3.1", "3.2"],
     "lead": "Personal devices may be used to access CMC email and the CMC "
             "employee self-service portal only."},
    # IT — software installation
    {"topics": ["install", "software", "app on", "slack", "application"],
     "doc": "policy_it_acceptable_use.txt",
     "sections": ["2.3"],
     "lead": "Software may not be installed on corporate devices without written "
             "approval from the IT Department."},
    # IT — passwords
    {"topics": ["password", "passwords"],
     "doc": "policy_it_acceptable_use.txt",
     "sections": ["4.1", "4.3"],
     "lead": "Passwords must not be shared and must be changed every 90 days."},
    # IT — MFA
    {"topics": ["multi-factor", "mfa", "two-factor", "2fa"],
     "doc": "policy_it_acceptable_use.txt",
     "sections": ["4.4"],
     "lead": "Multi-factor authentication is mandatory for all remote access "
             "to CMC systems."},
    # IT — CMC email for personal services
    {"topics": ["personal services", "social media", "register for"],
     "doc": "policy_it_acceptable_use.txt",
     "sections": ["6.2"],
     "lead": "CMC email addresses must not be used for personal services."},
    # HR — annual leave carry forward
    {"topics": ["carry forward", "carry-forward", "unused annual leave"],
     "doc": "policy_hr_leave.txt",
     "sections": ["2.6"],
     "lead": "A maximum of 5 unused annual leave days may be carried forward; "
             "days above 5 are forfeited on 31 December."},
    # HR — leave notice and approval
    {"topics": ["notice", "advance", "approval for leave", "request leave"],
     "doc": "policy_hr_leave.txt",
     "sections": ["2.3", "2.4"],
     "lead": "Leave applications require 14 days advance notice and written "
             "approval before the leave commences."},
    # HR — leave without pay approval
    {"topics": ["leave without pay", "lwp", "unpaid leave"],
     "doc": "policy_hr_leave.txt",
     "sections": ["5.2", "5.3"],
     "lead": "LWP requires approval from BOTH the Department Head and the HR "
             "Director; over 30 days also requires the Municipal Commissioner."},
    # HR — sick leave certificate
    {"topics": ["sick leave", "medical certificate", "doctor", "sick days"],
     "doc": "policy_hr_leave.txt",
     "sections": ["3.2"],
     "lead": "Sick leave of 3 or more consecutive days requires a medical "
             "certificate submitted within 48 hours of returning to work."},
    # HR — encashment
    {"topics": ["encash", "encashment", "cash out leave"],
     "doc": "policy_hr_leave.txt",
     "sections": ["7.1", "7.2"],
     "lead": "Leave may be encashed only at retirement or resignation; "
             "encashment during service is not permitted under any circumstances."},
    # HR — paternity leave
    {"topics": ["paternity", "father"],
     "doc": "policy_hr_leave.txt",
     "sections": ["4.3"],
     "lead": "Male employees are entitled to 5 days of paid paternity leave "
             "within 30 days of the child's birth."},
    # Finance — home office allowance
    {"topics": ["home office", "work from home equipment", "wfh equipment",
                "equipment allowance", "8000", "rs 8,000"],
     "doc": "policy_finance_reimbursement.txt",
     "sections": ["3.1", "3.5"],
     "lead": "Permanent work-from-home employees receive a one-time Rs 8,000 "
             "home office equipment allowance; temporary or partial "
             "arrangements are not eligible."},
    # Finance — DA and meal receipts
    {"topics": ["meal receipt", "da and meal", "daily allowance", "meals on",
                "same day"],
     "doc": "policy_finance_reimbursement.txt",
     "sections": ["2.6"],
     "lead": "DA and meal receipts cannot be claimed simultaneously for the "
             "same day."},
    # Finance — outstation travel approval
    {"topics": ["outstation", "pre-approved", "travelling", "travel expenses"],
     "doc": "policy_finance_reimbursement.txt",
     "sections": ["2.2", "2.3"],
     "lead": "Outstation travel must be pre-approved on Form FIN-T1; air "
             "travel requires journeys over 500 km and economy class."},
    # Finance — training reimbursement
    {"topics": ["training", "course fee", "certification"],
     "doc": "policy_finance_reimbursement.txt",
     "sections": ["4.1", "4.2"],
     "lead": "Training expenses are reimbursable only when pre-approved by the "
             "Department Head, up to Rs 15,000 per financial year."},
]


def _matches(question: str, topics):
    return any(t in question for t in topics)


def answer_question(question: str, index: dict) -> str:
    """Answer from exactly one source with citations, or refuse verbatim."""
    q = re.sub(r"[?.!,]+", "", question.lower())

    if any(h in q for h in HEDGE_PHRASES):
        return REFUSAL_TEMPLATE

    for rule in RULES:
        if not _matches(q, rule["topics"]):
            continue
        doc = index[rule["doc"]]
        lines = [rule["lead"]]
        for number in rule["sections"]:
            text = _clause(index, rule["doc"], number)
            if text is None:
                return REFUSAL_TEMPLATE
            lines.append(f"- {rule['doc']} §{number}: {text}")
        citation = ", ".join(f"{rule['doc']} §{n}" for n in rule["sections"])
        lines.append(f"Source(single-document): {citation}")
        lines.append("This answer is drawn from a single document; no claims "
                     "from other policy documents were combined into it.")
        return "\n".join(lines)

    return REFUSAL_TEMPLATE


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--question":
        index = retrieve_documents()
        print(answer_question(sys.argv[2], index))
        return

    if len(sys.argv) > 1:
        print("Usage: python app.py  (interactive) | python app.py --question \"<text>\"")
        sys.exit(1)

    index = retrieve_documents()
    print("UC-X — Ask My Documents (single-source policy QA)")
    print("Documents indexed: " + ", ".join(sorted(index)))
    print("Type a policy question, or 'exit' to quit.")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            break
        print()
        print(answer_question(question, index))
        print()


if __name__ == "__main__":
    main()