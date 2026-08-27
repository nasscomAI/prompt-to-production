"""
UC-X — Ask My Documents.
Deterministic single-source Q&A over the CMC policy documents.
Run `python app.py` for the interactive CLI, or
`python app.py "question"` for a single answer.
"""
import argparse
import os
import re
from collections import namedtuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, os.pardir, "data", "policy-documents")

DOCUMENTS = ["policy_hr_leave.txt", "policy_it_acceptable_use.txt",
             "policy_finance_reimbursement.txt"]
DEFAULT_DOCS = tuple(DOCUMENTS)

TEAMS = {"policy_hr_leave.txt": "HR Department",
         "policy_it_acceptable_use.txt": "IT Department",
         "policy_finance_reimbursement.txt": "Finance Department"}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGE_PHRASES = ["while not explicitly covered", "typically",
                 "generally understood", "it is common practice"]

CLAUSE_START_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
HEADING_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z &()\-]+)$")
SECTION_HEADER_RE = re.compile(r"^\d+\.\s+[A-Z].*$")
DIVIDER_RE = re.compile(r"^═+$")

STOPWORDS = set("""a an and are as at be by can for from how i in is it me may
my not of on or should the to do does did what when where which who whom why
will with would you your if there their they them we us our about into over
under please tell give show""".split())

SYNONYMS = {
    "phone": ["device", "devices", "personal"],
    "mobile": ["device", "devices"],
    "smartphone": ["device", "devices"],
    "laptop": ["corporate", "device", "devices", "computer"],
    "computer": ["corporate", "device", "devices"],
    "slack": ["software", "install", "installing"],
    "zoom": ["software", "install"],
    "app": ["software", "application"],
    "install": ["software", "installation"],
    "wfh": ["work", "home", "remote"],
    "encash": ["encashment"],
    "cash": ["encashment"],
    "payout": ["encashment"],
    "carryforward": ["carry", "forward"],
    "cert": ["certificate", "medical"],
    "sick": ["medical", "certificate"],
    "approve": ["approval", "approved"],
    "approver": ["approval", "approved"],
    "allowance": ["equipment", "reimbursable", "entitled"],
    "claim": ["claims", "claimed", "reimbursable", "reimbursement"],
    "receipt": ["receipts"],
    "meal": ["meals", "da", "daily", "allowance"],
    "da": ["daily", "allowance", "meals"],
    "perdiem": ["daily", "allowance", "da"],
    "wifi": ["network", "guest"],
    "password": ["passwords"],
    "gadgets": ["device", "devices"],
    "lop": ["loss", "pay"],
    "compoff": ["compensatory"],
    "portal": ["self", "service"],
}

REFUSAL_THRESHOLD = 0.34
MIN_MATCHED_TERMS = 2
MAX_CLAUSES = 3
PROXIMITY_BONUS = 0.15
CANDIDATE_FLOOR_RATIO = 0.75

ClauseHit = namedtuple("ClauseHit",
                       ["score", "document_name", "section_number",
                        "clause_id", "clause_text"])


def _normalize_token(token):
    if len(token) > 4 and token.endswith("ing"):
        stem = token[:-3]
        if len(stem) >= 4:
            return stem
    if len(token) > 4 and token.endswith("ed"):
        stem = token[:-2]
        if len(stem) >= 4:
            return stem
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def retrieve_documents():
    document_index = {}
    for document_name in DOCUMENTS:
        file_path = os.path.abspath(os.path.join(DATA_DIR, document_name))
        with open(file_path, encoding="utf-8") as file_handle:
            file_lines = file_handle.read().splitlines()
        indexed_sections = {}
        current_section_number = None
        for line in file_lines:
            clean_line = line.strip()
            if not clean_line or DIVIDER_RE.match(clean_line):
                continue
            heading_match = HEADING_RE.match(clean_line)
            if heading_match:
                current_section_number = heading_match.group(1)
                indexed_sections[current_section_number] = {
                    "title": heading_match.group(2).strip(),
                    "clauses": {},
                }
                continue
            clause_match = CLAUSE_START_RE.match(clean_line)
            if clause_match and current_section_number is not None:
                indexed_sections[current_section_number]["clauses"][
                    clause_match.group(1)] = clause_match.group(2).strip()
                continue
            if (current_section_number is not None
                    and indexed_sections[current_section_number]["clauses"]):
                last_clause_id = list(
                    indexed_sections[current_section_number]["clauses"])[-1]
                indexed_sections[current_section_number]["clauses"][
                    last_clause_id] += " " + clean_line
        document_index[document_name] = indexed_sections
    return document_index


def _query_terms(question):
    raw_tokens = re.findall(r"[a-z0-9]+", question.lower())
    collected_terms = []
    for token in raw_tokens:
        if token in STOPWORDS:
            continue
        collected_terms.append(token)
        collected_terms.extend(SYNONYMS.get(token, []))
    return {_normalize_token(term) for term in collected_terms}


def _query_pairs(question):
    positioned_tokens = [
        (token_ordinal, matcher.group(0))
        for token_ordinal, matcher
        in enumerate(re.finditer(r"[a-z0-9]+", question.lower()))
    ]
    kept_tokens = []
    for token_ordinal, token in positioned_tokens:
        if token in STOPWORDS:
            continue
        term_alternatives = {_normalize_token(token)}
        for synonym in SYNONYMS.get(token, []):
            term_alternatives.add(_normalize_token(synonym))
        kept_tokens.append((token_ordinal, term_alternatives))
    adjacent_term_pairs = set()
    for i in range(len(kept_tokens)):
        for j in range(i + 1, len(kept_tokens)):
            if kept_tokens[j][0] - kept_tokens[i][0] > 2:
                break
            for first_term in kept_tokens[i][1]:
                for second_term in kept_tokens[j][1]:
                    if first_term != second_term:
                        adjacent_term_pairs.add((first_term, second_term))
    return adjacent_term_pairs


def _score_clauses(document_index, query_terms, query_pairs):
    scored_clauses = []
    best_score_per_document = {}
    weak_score_per_document = {}
    for document_name in DOCUMENTS:
        best_score = 0.0
        weak_score = 0.0
        for section_number, section_data in \
                document_index[document_name].items():
            for clause_id, clause_text in section_data["clauses"].items():
                searchable_text = section_data["title"] + " " + clause_text
                tokens = [_normalize_token(token) for token
                          in re.findall(r"[a-z0-9]+",
                                        searchable_text.lower())]
                matched_terms = query_terms & set(tokens)
                if not matched_terms:
                    continue
                token_positions = {}
                for position, token in enumerate(tokens):
                    token_positions.setdefault(token, []).append(position)
                pair_hits = 0
                for first_term, second_term in query_pairs:
                    first_positions = token_positions.get(first_term)
                    second_positions = token_positions.get(second_term)
                    if first_positions and second_positions and any(
                            0 < later_position - earlier_position <= 3
                            for earlier_position in first_positions
                            for later_position in second_positions):
                        pair_hits += 1
                relevance_score = (
                    len(matched_terms) / len(query_terms)
                    + PROXIMITY_BONUS * (pair_hits ** 0.5))
                if relevance_score > weak_score:
                    weak_score = relevance_score
                if len(matched_terms) < MIN_MATCHED_TERMS:
                    continue
                scored_clauses.append(
                    ClauseHit(relevance_score, document_name,
                              section_number, clause_id, clause_text))
                if relevance_score > best_score:
                    best_score = relevance_score
        best_score_per_document[document_name] = best_score
        weak_score_per_document[document_name] = weak_score
    return scored_clauses, best_score_per_document, weak_score_per_document


def _build_refusal(signal_document):
    team = TEAMS.get(signal_document) if signal_document else None
    if team:
        return REFUSAL_TEMPLATE.replace("[relevant team]", team)
    return REFUSAL_TEMPLATE


def _enforce_output_guards(candidate_answer, cited_documents):
    answer_lowered = candidate_answer.lower()
    for hedge_phrase in HEDGE_PHRASES:
        if hedge_phrase in answer_lowered:
            return None
    if len(cited_documents) > 1:
        return None
    return candidate_answer


def answer_question(question, document_index):
    query_terms = _query_terms(question)
    if not query_terms:
        return _build_refusal(None)
    query_pairs = _query_pairs(question)
    scored_clauses, best_score_per_document, weak_score_per_document = \
        _score_clauses(document_index, query_terms, query_pairs)
    best_document = None
    best_document_score = 0.0
    for document_name in DOCUMENTS:
        if best_score_per_document[document_name] > best_document_score:
            best_document_score = best_score_per_document[document_name]
            best_document = document_name
    if best_document is None or best_document_score < REFUSAL_THRESHOLD:
        signal_document = best_document
        if signal_document is None:
            weak_document = None
            weak_document_score = 0.0
            for document_name in DOCUMENTS:
                if (weak_score_per_document[document_name]
                        > weak_document_score):
                    weak_document_score = \
                        weak_score_per_document[document_name]
                    weak_document = document_name
            signal_document = weak_document
        return _build_refusal(signal_document)
    score_floor = best_document_score * CANDIDATE_FLOOR_RATIO
    candidate_pool = [hit for hit in scored_clauses
                      if hit.document_name == best_document
                      and hit.score > score_floor]
    candidate_pool.sort(key=lambda hit: (-hit.score,
                                         float(hit.section_number),
                                         float(hit.clause_id)))
    selected_clauses = candidate_pool[:MAX_CLAUSES]
    selected_clauses.sort(key=lambda hit: (float(hit.section_number),
                                           float(hit.clause_id)))
    citation_lines = ["[%s §%s] %s" % (hit.document_name, hit.clause_id,
                                       hit.clause_text)
                      for hit in selected_clauses]
    composed_answer = "\n".join(citation_lines)
    enforced_answer = _enforce_output_guards(
        composed_answer, {hit.document_name for hit in selected_clauses})
    if enforced_answer is None or not selected_clauses:
        return _build_refusal(best_document)
    return enforced_answer


def main():
    argument_parser = argparse.ArgumentParser(
        description="Ask My Documents — CMC policy Q&A")
    argument_parser.add_argument("question", nargs="*",
                                 help="optional single question; "
                                      "omit for REPL")
    arguments = argument_parser.parse_args()
    document_index = retrieve_documents()
    if arguments.question:
        print(answer_question(" ".join(arguments.question),
                              document_index))
        return
    print("UC-X — Ask My Documents (type 'quit' to exit)")
    while True:
        try:
            user_question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_question:
            continue
        if user_question.lower() in {"quit", "exit"}:
            break
        print(answer_question(user_question, document_index))
        print()


if __name__ == "__main__":
    main()
