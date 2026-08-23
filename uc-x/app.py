"""
UC-X — Ask My Documents
Single-source policy QA over three CMC policy files.
Implements agents.md enforcement and skills.md contracts.
"""
import argparse
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
DOC_NAMES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.+?)\s*$")
HEADING_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z \-&(),]+)\s*$")

STOPWORDS = {
    "a", "an", "and", "are", "at", "can", "do", "does", "for", "from", "i",
    "in", "is", "it", "me", "my", "of", "on", "or", "our", "the", "their",
    "to", "what", "when", "who", "with", "you", "your",
}

SYNONYMS = {
    "phone": {"phone", "device", "mobile"},
    "laptop": {"laptop", "computer", "device"},
    "file": {"file", "document", "data"},
    "wfh": {"home"},
}

DOMAIN_TERMS = {
    "policy_it_acceptable_use.txt": {
        "device", "devices", "laptop", "desktop", "phone", "email", "portal",
        "password", "network", "wifi", "software", "internet", "mfa",
        "security", "data", "access", "print", "install",
    },
    "policy_finance_reimbursement.txt": {
        "reimbursement", "claim", "claims", "receipt", "receipts",
        "allowance", "expense", "expenses", "travel", "hotel", "meal",
        "meals", "training", "course", "exam", "money", "rs", "8000",
        "3500", "2500", "750", "500", "15000", "5000", "800",
    },
    "policy_hr_leave.txt": {
        "leave", "holiday", "holidays", "sick", "maternity", "paternity",
        "encash", "encashment", "grievance", "grievances", "lwp", "lop",
        "carry", "forward", "accrual", "entitled",
    },
}

TEAM_BY_DOC = {
    "policy_hr_leave.txt": "the HR Department",
    "policy_it_acceptable_use.txt": "the IT Department or IT helpdesk",
    "policy_finance_reimbursement.txt": "the Finance Department",
}
DEFAULT_TEAM = "the relevant department"

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact {team} for guidance."
)

MIN_SCORE = 2
AMBIGUITY_RATIO = 0.75


def stem(word):
    word = word.lower()
    for suffix in ("ation", "ing", "ies"):
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            word = word[: -len(suffix)]
            break
    if word.endswith("ies") and len(word) > 3:
        word = word[:-3] + "y"
    elif word.endswith("s") and not word.endswith(("ss", "us", "is")) and len(word) > 3:
        word = word[:-1]
    return word


def question_terms(question):
    raw_tokens = re.findall(r"[a-zA-Z0-9,\.]+", question)
    terms = set()
    numbers = {t.replace(",", "") for t in raw_tokens if any(ch.isdigit() for ch in t)}
    for token in raw_tokens:
        token = token.strip(",.")
        if not token or any(ch.isdigit() for ch in token):
            continue
        low = token.lower()
        if low in STOPWORDS or len(low) <= 2:
            continue
        stemmed = stem(low)
        expanded = {stemmed}
        for mapping in SYNONYMS.values():
            if stemmed in mapping or low in mapping:
                expanded |= mapping
        terms |= expanded
    return terms, numbers


def retrieve_documents(base_dir=BASE_DIR):
    index = []
    warnings = []
    for doc_name in DOC_NAMES:
        path = Path(base_dir) / doc_name
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"Cannot read policy document {path}: {exc}", file=sys.stderr)
            sys.exit(1)
        text = re.sub(r"\uFFFD+|[\u2013\u2014]", "-", text)

        heading = ""
        current_id = None
        parsed = 0
        for line in text.splitlines():
            stripped = line.strip()
            heading_match = HEADING_RE.match(line)
            clause_match = CLAUSE_RE.match(line)
            if heading_match:
                heading = f"{heading_match.group(1)}. {heading_match.group(2).title()}"
                current_id = None
            elif clause_match:
                current_id = clause_match.group(1)
                index.append(
                    {
                        "doc": doc_name,
                        "section": current_id,
                        "heading": heading,
                        "text": clause_match.group(2),
                    }
                )
                parsed += 1
            elif current_id and stripped and set(stripped) - set("-= "):
                for entry in reversed(index):
                    if entry["doc"] == doc_name:
                        entry["text"] += " " + stripped
                        break
            else:
                current_id = None
        if parsed == 0:
            warnings.append(doc_name)
    if warnings:
        print(f"WARNING: no clauses parsed from: {warnings}", file=sys.stderr)
    return index


def _entry_terms(entry):
    words = set()
    for word in re.findall(r"[A-Za-z0-9]+", entry["heading"] + " " + entry["text"]):
        lowered = word.lower().replace(",", "")
        if len(lowered) > 2:
            words.add(stem(lowered))
            if any(ch.isdigit() for ch in lowered):
                words.add(lowered)
    return words


def _terms_match(entry_word, term):
    if entry_word == term:
        return True
    return len(term) >= 4 and len(entry_word) >= 4 and (
        entry_word.startswith(term) or term.startswith(entry_word)
    )


def score_entry(entry, terms, numbers, domain_set):
    entry_words = _entry_terms(entry)
    score = 0.0
    matched = []
    for term in terms:
        if any(_terms_match(word, term) for word in entry_words):
            weight = 3.0 if term in domain_set else 1.0
            score += weight
            matched.append(term)
    for number in numbers:
        if number in entry_words:
            score += 4.0
            matched.append(number)
    return score, matched


def answer_question(question, index):
    terms, numbers = question_terms(question)
    if not terms and not numbers:
        team = DEFAULT_TEAM
        return REFUSAL_TEMPLATE.format(team=team), []

    doc_scores = {}
    scored_entries = []
    for entry in index:
        score, matched = score_entry(entry, terms, numbers, DOMAIN_TERMS.get(entry["doc"], set()))
        if score > 0:
            scored_entries.append((score, matched, entry))
            doc_scores[entry["doc"]] = doc_scores.get(entry["doc"], 0.0) + score

    ranked_docs = sorted(doc_scores.items(), key=lambda kv: kv[1], reverse=True)
    best_entry_score = max((s for s, _, _ in scored_entries), default=0.0)
    if not ranked_docs or best_entry_score < MIN_SCORE:
        return REFUSAL_TEMPLATE.format(team=DEFAULT_TEAM), []

    best_doc = ranked_docs[0][0]
    second_score = ranked_docs[1][1] if len(ranked_docs) > 1 else 0.0
    if second_score >= AMBIGUITY_RATIO * doc_scores[best_doc]:
        return REFUSAL_TEMPLATE.format(team=DEFAULT_TEAM), []

    doc_entries = [(s, m, e) for s, m, e in scored_entries if e["doc"] == best_doc]
    doc_entries.sort(key=lambda item: item[0], reverse=True)
    top_entry = doc_entries[0]
    siblings = [
        item
        for item in doc_entries[1:]
        if item[2]["heading"] == top_entry[2]["heading"] and item[2]["section"] != top_entry[2]["section"]
    ]
    rest = [item for item in doc_entries[1:] if item not in siblings]
    top = [top_entry] + siblings[:2] if siblings else [top_entry] + rest[:2]

    lines = [f"Answer (single source: {best_doc}):"]
    citations = []
    for _, _, entry in top:
        citation = f"[{best_doc} Section {entry['section']}{(' ' + entry['heading']) if entry['heading'] else ''}]"
        citations.append(citation)
        lines.append(f"{citation}\n\"{entry['text']}\"")
    return "\n".join(lines), citations


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--question", help="Ask one question non-interactively")
    parser.add_argument("--data-dir", default=str(BASE_DIR), help="Directory containing the three policy files")
    args = parser.parse_args()

    print("Loading policy documents...")
    index = retrieve_documents(args.data_dir)
    print(f"Indexed {len(index)} clauses from {len(DOC_NAMES)} documents.")
    print("Type your policy question (or 'quit' to exit).")

    questions = [args.question] if args.question else iter(lambda: input("\nQ> ").strip(), "")
    for question in questions:
        if question.lower() in {"quit", "exit"}:
            break
        if not question:
            continue
        answer, _ = answer_question(question, index)
        print(answer)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nBye.")
