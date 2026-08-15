"""
UC-X — Ask My Documents.

Deterministic document-answer agent implementing agents.md and skills.md:
answers employee policy questions from three documents only, returns verbatim
single-source section text with a document + section citation, or the exact
refusal template when the question is not covered. Never blends documents.
"""
import argparse
import math
import os
import re
import sys

DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

MIN_SCORE = 3.0
CROSS_DOC_TOLERANCE = 1.0
SYNONYM_SCALE = 0.8
PHRASE_SCALE = 1.2
ACRONYM_PHRASE_SCALE = 0.8
CONSUMED_TOKEN_SCALE = 0.5
ACTION_BONUS = 0.6
BYOD_BONUS = 1.5

STOPWORDS = frozenset(
    [
        "a", "an", "the", "and", "or", "but", "if", "of", "to", "in", "on",
        "at", "for", "with", "by", "from", "up", "over", "under", "again",
        "further", "then", "once", "here", "there", "when", "where", "why",
        "how", "all", "any", "both", "each", "few", "more", "most", "other",
        "some", "such", "no", "nor", "not", "only", "own", "who", "what",
        "which", "can", "could", "would", "should", "will", "may", "might",
        "must", "do", "does", "did", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "i", "me", "my", "mine", "we", "our",
        "ours", "you", "your", "yours", "they", "them", "their", "it", "its",
        "this", "that", "these", "those", "please", "about", "also", "into",
        "during", "within", "per", "used", "use",
    ]
)

SYNONYMS = {
    "slack": ("software",),
    "phone": ("device",),
    "approve": ("approval",),
    "approves": ("approval",),
    "approved": ("approval",),
}

ACTION_VERBS = {
    "install": ("install", "installs", "installing", "installed"),
    "claim": ("claim", "claims", "claimed", "claiming"),
    "carry": ("carry", "carries", "carried", "carrying"),
}

APPROVAL_WORDS = frozenset(
    [
        "approve", "approved", "approves", "approval",
        "authorise", "authorised", "authorize", "authorized",
        "permission", "permit", "permits", "allowed",
    ]
)

PERSONAL_DEVICE_PHRASES = (
    "personal phone",
    "personal device",
    "personal laptop",
    "personal tablet",
)

DEVICE_TERMS = {
    "phone", "device", "mobile", "laptop", "desktop", "computer", "smartphone",
}

ACRONYM_RE = re.compile(r"([a-zA-Z][a-zA-Z\- ]{1,40}?)\s*\(([A-Z]{2,6})\)")
SECTION_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
HEADER_RE = re.compile(r"^\d+\.\s+")
SEPARATOR_RE = re.compile(r"^[═=\-_]+$")


def tokenize(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]


def parse_sections(text):
    sections = {}
    current = None
    buffer = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or SEPARATOR_RE.match(line) or HEADER_RE.match(line):
            continue
        match = SECTION_RE.match(line)
        if match:
            if current is not None:
                sections[current] = " ".join(buffer)
            current = match.group(1)
            buffer = [match.group(2)]
        elif current is not None:
            buffer.append(line)
    if current is not None:
        sections[current] = " ".join(buffer)
    return sections


def extract_acronyms(texts):
    acronyms = {}
    for text in texts:
        for phrase, acro in ACRONYM_RE.findall(text):
            key = " ".join(re.findall(r"[a-z]+", phrase.lower()))
            if 2 <= len(key.split()) <= 5:
                acronyms[key] = acro.lower()
    return acronyms


def retrieve_documents(policy_dir):
    index = {}
    raw_texts = []
    for name in DOCUMENTS:
        path = os.path.join(policy_dir, name)
        try:
            with open(path, encoding="utf-8") as file:
                text = file.read()
        except OSError as exc:
            raise FileNotFoundError(
                f"Policy file unavailable ({name}): {exc}"
            ) from exc
        sections = parse_sections(text)
        if not sections:
            raise ValueError(f"No sections could be parsed from {name}")
        index[name] = sections
        raw_texts.append(text)
    return index, extract_acronyms(raw_texts)


def build_model(index, acronyms):
    wordsets = {
        doc: {sec: set(re.findall(r"[a-z]+", text.lower())) for sec, text in sections.items()}
        for doc, sections in index.items()
    }
    plain_texts = {
        doc: {sec: re.sub(r"\s+", " ", text.lower()) for sec, text in sections.items()}
        for doc, sections in index.items()
    }
    section_keys = [(doc, sec) for doc, sections in index.items() for sec in sections]
    total = len(section_keys)

    df_cache = {}

    def document_frequency(term):
        if term not in df_cache:
            df_cache[term] = sum(
                1 for doc, sec in section_keys if term in wordsets[doc][sec]
            )
        return df_cache[term]

    def idf(term):
        return math.log(1.0 + total / (1.0 + document_frequency(term)))

    approval_counts = {
        (doc, sec): sum(1 for word in wordsets[doc][sec] if word in APPROVAL_WORDS)
        for doc, sec in section_keys
    }
    acronym_phrases = {}
    for phrase, acro in acronyms.items():
        acronym_phrases[acro] = phrase

    return {
        "index": index,
        "wordsets": wordsets,
        "plain_texts": plain_texts,
        "idf": idf,
        "approval_counts": approval_counts,
        "acronyms": acronyms,
        "acronym_phrases": acronym_phrases,
    }


def _matches_token(token, wordset):
    if token in wordset:
        return True
    if token.endswith("ies") and token[:-3] + "y" in wordset:
        return True
    if token.endswith("s") and len(token) > 3 and token[:-1] in wordset:
        return True
    if not token.endswith("s") and token + "s" in wordset:
        return True
    return False


def _query_terms(tokens, acronyms, acronym_phrases):
    terms = {tok: 1.0 for tok in tokens}
    consumed = set()
    for length in range(min(5, len(tokens)), 1, -1):
        for i in range(len(tokens) - length + 1):
            phrase = " ".join(tokens[i:i + length])
            if phrase in acronyms:
                terms[acronyms[phrase]] = max(terms.get(acronyms[phrase], 0.0), PHRASE_SCALE)
                consumed.update(range(i, i + length))
    for i in consumed:
        terms[tokens[i]] = CONSUMED_TOKEN_SCALE
    for tok in tokens:
        for synonym in SYNONYMS.get(tok, ()):
            terms[synonym] = max(terms.get(synonym, 0.0), SYNONYM_SCALE)
    for tok in tokens:
        phrase = acronym_phrases.get(tok)
        if phrase:
            for word in phrase.split():
                terms[word] = max(terms.get(word, 0.0), ACRONYM_PHRASE_SCALE)
    return list(terms.items())


def _action_roots(tokens):
    inverse = {}
    for root, forms in ACTION_VERBS.items():
        for form in forms:
            inverse[form] = root
    return [inverse[tok] for tok in tokens if tok in inverse]


def answer_question(model, question):
    tokens = tokenize(question)
    if not tokens:
        return REFUSAL_TEMPLATE

    terms = _query_terms(tokens, model["acronyms"], model["acronym_phrases"])
    action_roots = _action_roots(tokens)
    query_has_approval = any(term in APPROVAL_WORDS for term, _ in terms)
    has_personal_device = any(
        phrase in question.lower() for phrase in PERSONAL_DEVICE_PHRASES
    )
    question_is_personal = "personal" in tokens

    scored = []
    for doc, sections in model["index"].items():
        for sec, text in sections.items():
            wordset = model["wordsets"][doc][sec]
            is_corporate = "corporate device" in model["plain_texts"][doc][sec]
            score = 0.0
            for term, scale in terms:
                if (
                    question_is_personal
                    and is_corporate
                    and term in DEVICE_TERMS
                ):
                    continue
                if _matches_token(term, wordset):
                    score += scale * model["idf"](term)
            if action_roots:
                hits = sum(
                    1
                    for root in action_roots
                    if any(form in wordset for form in ACTION_VERBS[root])
                )
                score += ACTION_BONUS * min(hits, 2)
            if query_has_approval:
                score += 0.5 * model["approval_counts"][(doc, sec)]
            if has_personal_device and "personal device" in model["plain_texts"][doc][sec]:
                score += BYOD_BONUS
            scored.append((score, doc, sec, text))

    scored.sort(key=lambda item: item[0], reverse=True)
    top_score = scored[0][0]

    if top_score < MIN_SCORE:
        return REFUSAL_TEMPLATE

    best_docs = {
        doc
        for score, doc, _sec, _text in scored
        if score >= top_score - CROSS_DOC_TOLERANCE
    }
    if len(best_docs) > 1:
        return REFUSAL_TEMPLATE

    _score, doc, sec, text = scored[0]
    return f"{text}\n\nSource: {doc}, section {sec}"


def _default_policy_dir():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data", "policy-documents"
    )


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="UC-X — Ask My Documents")
    parser.add_argument("question", nargs="?", help="Ask a single question and exit")
    parser.add_argument(
        "--policy-dir", default=None, help="Directory containing the policy files"
    )
    args = parser.parse_args()

    policy_dir = args.policy_dir or _default_policy_dir()
    try:
        index, acronyms = retrieve_documents(policy_dir)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    model = build_model(index, acronyms)

    if args.question:
        print(answer_question(model, args.question))
        return

    print("UC-X — Ask My Documents")
    print("Type a question, or 'quit' to exit.")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"quit", "exit", "q"}:
            break
        if not question:
            continue
        print(answer_question(model, question))


if __name__ == "__main__":
    main()
