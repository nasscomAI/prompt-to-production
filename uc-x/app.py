"""
UC-X - Policy Q&A That Hallucinates
Vibe-coded from agents.md + skills.md (RICE -> CRAFT workflow).

Enforcement rules from agents.md are implemented here:
  1. Every answer cites exactly one source document and its clause.
  2. Answers never blend two policy documents into one reply.
  3. No clause match -> fixed refusal template (never general knowledge).
  4. Refusal template is emitted verbatim.
  5. BYOD questions are answered from IT policy section 3 only.
"""
import argparse
import re
import sys

DOC_PATHS = {
    "policy_hr_leave.txt": "data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
)

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.+?)\s*$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 &'()\-]*)$")
DIVIDER_RE = re.compile(r"^[\s═\-\=\_]+$")
STOPWORDS = {"the", "a", "an", "can", "i", "my", "me", "to", "for", "of",
             "is", "am", "in", "on", "at", "do", "does", "how", "much",
             "what", "about", "and", "or", "if", "with", "it", "do i"}
# Generic scope words: matching ONLY these is not enough to ground an answer.
GENERIC_TOKENS = {"policy", "employee", "staff", "cmc", "department"}
# Jargon/compound words mapped to the vocabulary used inside the documents.
COMPOUND_EXPANSIONS = {"airfare": ("air",)}


def load_policies():
    """Parse every numbered clause from the three policy documents."""
    index = {}
    for filename, path in DOC_PATHS.items():
        clauses = []
        current = None
        try:
            with open(path, "r", encoding="utf-8-sig") as filehandle:
                lines = filehandle.read().splitlines()
        except OSError as error:
            raise RuntimeError(f"Policy file '{path}' could not be read: {error}")

        for line in lines:
            line = line.strip()
            if not line or DIVIDER_RE.match(line):
                continue
            clause_match = CLAUSE_RE.match(line)
            if clause_match:
                current = (clause_match.group(1), clause_match.group(2).strip())
                clauses.append(current)
                continue
            if current is not None and not SECTION_RE.match(line):
                # Join continuation lines against the latest stored clause so
                # wrapped lines are fully preserved.
                number, text = clauses[-1]
                clauses[-1] = (number, f"{text} {line}")
        index[filename] = clauses
    return index


def _stem(token):
    if token.endswith("ies") and len(token) > 4:
        token = token[:-3] + "y"
    elif token.endswith("s") and len(token) > 3:
        token = token[:-1]
    if token.endswith("ed") and len(token) > 4:
        token = token[:-2]
    if token.endswith("ing") and len(token) > 5:
        token = token[:-3]
    return token


def _tokens(text, stem=True):
    words = re.findall(r"[a-z0-9]+", text.lower())
    result = []
    for word in words:
        if word in STOPWORDS or len(word) < 3:
            continue
        value = _stem(word) if stem else word
        result.append(value)
    return result


def _vocabulary(text):
    """Raw and stemmed forms so inflections ('access') never mis-match."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    vocab = []
    for word in words:
        if word in STOPWORDS or len(word) < 3:
            continue
        vocab.append(word)
        vocab.append(_stem(word))
    return vocab


def _bigrams(question):
    words = re.findall(r"[a-z0-9]+", question.lower())
    return [" ".join(words[i:i + 2]) for i in range(len(words) - 1)]


def _occurrences(index):
    occ = {}
    for filename, clauses in index.items():
        for _, text in clauses:
            seen = set(_vocabulary(text))
            for token in seen:
                occ[token] = occ.get(token, 0) + 1
    return occ


def answer_question(question, index, occ):
    """Return (answer, source); source is None and answer is the refusal."""
    if not question.strip():
        return "Please ask a policy question supported by the documents.", None

    question_tokens = list(dict.fromkeys(_vocabulary(question)))
    question_bigrams = _bigrams(question)
    byod_context = bool(
        set(question_tokens) & {"personal", "phone", "device", "smartphone"}
        and set(question_tokens) & {"email", "portal", "mail", "access"})

    best = None  # (weight, bigram_score, doc_rank, min_number_key) + result
    for doc_rank, filename in enumerate(DOC_PATHS):
        for number, text in index[filename]:
            clause_set = set(_vocabulary(text))

            exact = []
            for qtok in question_tokens:
                expanded = (qtok,) + COMPOUND_EXPANSIONS.get(qtok, ())
                if any(word in clause_set for word in expanded):
                    exact.append(qtok)
            exact = list(dict.fromkeys(exact))
            if not exact:
                continue
            if all(token in GENERIC_TOKENS for token in exact):
                continue  # only boilerplate scope language -> refuse later

            weight = (sum(min(0.5, 1.0 / occ.get(token, 1)) for token in exact)
                      + 0.1 * len(exact))
            byod_bonus = weight + (3 if byod_context
                                   and number.startswith("3.")
                                   and filename == "policy_it_acceptable_use.txt"
                                   else 0)
            bigram_score = sum(1 for bigram in question_bigrams if bigram in text.lower())
            key = (byod_bonus, bigram_score, doc_rank, -float(number.replace(".", "")))
            if best is None or key > best[0]:
                best = (key, filename, number, text)

    if best is None:
        return REFUSAL_TEMPLATE, None

    _, filename, number, text = best
    return text, f"{filename}, clause {number}"


def run_session(index, occ, questions=None):
    """Interactive loop, or a fixed question list when provided."""
    if questions is None:
        questions = []
        while True:
            question = input("Ask a policy question ('exit' to quit): ").strip()
            if question.lower() in ("exit", "quit"):
                break
            questions.append(question)
    for question in questions:
        answer, source = answer_question(question, index, occ)
        print(f"Q: {question}")
        print(f"A: {answer}")
        if source:
            print(f"Source: {source}")
        print()


def main():
    parser = argparse.ArgumentParser(description="UC-X policy Q&A assistant")
    parser.add_argument("--question", default=None,
                        help="Answer a single question and exit")
    args = parser.parse_args()

    index = load_policies()
    occ = _occurrences(index)
    if args.question:
        answer, source = answer_question(args.question, index, occ)
        print(answer)
        if source:
            print(f"Source: {source}")
        return
    run_session(index, occ)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)