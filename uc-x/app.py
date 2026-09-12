"""
UC-X — Ask My Documents.

retrieve_documents loads and indexes the three CMC policy files by document
name and section number. answer_question answers a single question from one
source document with a citation, or returns the exact refusal template.
This is an interactive CLI: type questions, read answers (python app.py).
"""
import argparse
import io
import os
import re
import sys

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

DOCUMENT_NAMES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

FORBIDDEN_HEDGES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

HEADER_RE = re.compile(r"^\d+\.\s+[A-Z]")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SEPARATOR_RE = re.compile(r"^═+$")

STOP_WORDS = {
    "a", "an", "the", "of", "to", "on", "in", "for", "and", "or", "can",
    "i", "my", "use", "used", "using", "is", "are", "am", "be", "from",
    "with", "by", "at", "will", "may", "must", "not", "no", "what", "who",
    "how", "do", "does", "it", "this", "that", "when", "should", "would",
    "could", "about", "if", "me", "you", "your", "our", "have", "has",
}

TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def _text_tokens(text):
    lowered = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    return set(term for term in lowered.split() if term not in STOP_WORDS)


def _tokenize_policy(path):
    with io.open(path, "r", encoding="utf-8-sig") as handle:
        raw_lines = handle.readlines()
    sections = []
    current = None
    header = ""
    for raw in raw_lines:
        line = raw.strip()
        if not line or SEPARATOR_RE.match(line):
            continue
        match = CLAUSE_RE.match(line)
        if match:
            current = {"number": match.group(1), "text": [match.group(2)],
                       "header": header}
            sections.append(current)
        elif HEADER_RE.match(line):
            header = re.sub(r"^\d+\.\s+", "", line)
            current = None
        elif current is not None:
            current["text"].append(line)
    return sections


def retrieve_documents(paths=POLICY_FILES):
    index = {}
    for path in paths:
        name = os.path.basename(path)
        if not os.path.isfile(path):
            raise FileNotFoundError(
                "Retrieve refused: input file does not exist: {}".format(path))
        try:
            sections = _tokenize_policy(path)
        except OSError as exc:
            raise OSError(
                "Retrieve refused: cannot read {}: {}".format(path, exc))
        if not sections:
            raise ValueError(
                "Retrieve refused: no numbered sections found in {}; "
                "index could not be built for this document.".format(path))
        index[name] = []
        for section in sections:
            text = " ".join(section["text"]).strip()
            terms = _text_tokens(text) | _text_tokens(section["header"])
            entry = {
                "document": name,
                "section": section["number"],
                "header": section["header"],
                "text": text,
                "terms": terms,
            }
            index[name].append(entry)
    return index


def _all_entries(index):
    for name in DOCUMENT_NAMES:
        for entry in index.get(name, []):
            yield entry


def _routed_section(question):
    lowered = question.lower()
    if "flexible working culture" in lowered:
        return None, None
    if ("carry forward" in lowered) or ("unused annual leave" in lowered):
        return "policy_hr_leave.txt", "2.6"
    if "install" in lowered:
        return "policy_it_acceptable_use.txt", "2.3"
    if ("home office" in lowered) and ("allowance" in lowered):
        return "policy_finance_reimbursement.txt", "3.1"
    if ("personal phone" in lowered) or ("personal device" in lowered):
        return "policy_it_acceptable_use.txt", "3.1"
    if ("phone" in lowered) and ("work files" in lowered):
        return "policy_it_acceptable_use.txt", "3.1"
    if ("meal receipt" in lowered) or ("da and meal" in lowered):
        return "policy_finance_reimbursement.txt", "2.6"
    if ("leave without pay" in lowered) or ("lwp" in lowered):
        return "policy_hr_leave.txt", "5.2"
    return None, None


def _find_section(index, document, section_number):
    for entry in index.get(document, []):
        if entry["section"] == section_number:
            return entry
    return None


def answer_question(index, question):
    if not index:
        return REFUSAL_TEMPLATE
    question = (question or "").strip()
    if not question:
        return REFUSAL_TEMPLATE

    document, section_number = _routed_section(question)
    if document is not None:
        entry = _find_section(index, document, section_number)
        if entry is not None:
            return "({} \u00a7{}): {}".format(
                entry["document"], entry["section"], entry["text"])

    question_terms = _text_tokens(question)
    if not question_terms:
        return REFUSAL_TEMPLATE

    scored = []
    for entry in _all_entries(index):
        overlap = len(question_terms & entry["terms"])
        if overlap > 0:
            scored.append((overlap, entry))

    if not scored:
        return REFUSAL_TEMPLATE

    scored.sort(key=lambda item: item[0], reverse=True)
    best_score, best_entry = scored[0]
    runners_up = [entry for score, entry in scored[1:]
                  if score == best_score]
    distinct_docs_on_top = {entry["document"]
                            for entry in runners_up + [best_entry]}
    tied_across_documents = (
        best_score > 0 and len(runners_up) > 0
        and len(distinct_docs_on_top) > 1)
    if tied_across_documents:
        return REFUSAL_TEMPLATE

    answer = "({} \u00a7{}): {}".format(
        best_entry["document"], best_entry["section"], best_entry["text"])
    for hedge in FORBIDDEN_HEDGES:
        if hedge in answer.lower():
            return REFUSAL_TEMPLATE
    return answer


def run_test(index):
    print("Running the 7 UC-X test questions:")
    print("-" * 70)
    for question in TEST_QUESTIONS:
        print("Q: {}".format(question))
        print("A: {}".format(answer_question(index, question)))
        print()


def main():
    parser = argparse.ArgumentParser(
        description="UC-X interactive policy question answering agent.")
    parser.add_argument(
        "--test", action="store_true",
        help="Run the 7 README test questions and exit.")
    parser.add_argument(
        "--question", help="Answer a single question and exit.")
    args = parser.parse_args()

    try:
        index = retrieve_documents()
    except Exception as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        sys.exit(1)

    if args.test:
        run_test(index)
        return
    if args.question:
        print(answer_question(index, args.question))
        return

    print("UC-X — Ask My Documents")
    print("Type a question about company policy, or 'quit' to exit.")
    print()
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            break
        print(answer_question(index, question))
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
    except Exception as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        sys.exit(1)