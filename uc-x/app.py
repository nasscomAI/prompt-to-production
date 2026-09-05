"""
UC-X app.py — Ask My Documents.
Answers questions about CMC policy from exactly three source documents.
Single-source answers with citations, or a verbatim refusal template.
Built from uc-x/agents.md and uc-x/skills.md (RICE).
"""
import argparse
import os
import re
import sys

POLICY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "data", "policy-documents")
DOCUMENTS = [
    os.path.join(POLICY_DIR, "policy_hr_leave.txt"),
    os.path.join(POLICY_DIR, "policy_it_acceptable_use.txt"),
    os.path.join(POLICY_DIR, "policy_finance_reimbursement.txt"),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGE_PHRASES = ["while not explicitly covered", "typically",
                 "generally understood", "it is common practice"]

STOPWORDS = {
    "i", "me", "my", "we", "our", "you", "your", "he", "she", "it",
    "its", "they", "them", "am", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "can", "could", "should", "may", "might", "must",
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "of",
    "at", "by", "for", "with", "about", "on", "to", "in", "from",
    "up", "down", "out", "off", "over", "under", "as", "what", "when",
    "where", "which", "who", "whom", "this", "that", "these", "those",
    "how", "so", "too", "there", "please", "any", "get", "use",
}

# Curated ground-truth topics -> single source (doc, section).
# 'required' tokens must all be present; 'any_of' groups need at least one.
TOPICS = [
    {"name": "carry forward leave",
     "required": {"carry", "forward"},
     "any_of": [], "doc": "policy_hr_leave.txt", "section": "2.6"},
    {"name": "install software on corporate device",
     "required": {"install"},
     "any_of": [{"slack"}, {"software"}, {"laptop"}, {"application"}],
     "doc": "policy_it_acceptable_use.txt", "section": "2.3"},
    {"name": "home office equipment allowance",
     "required": {"allowance", "home"},
     "any_of": [{"equipment"}, {"desk"}, {"office"}],
     "doc": "policy_finance_reimbursement.txt", "section": "3.1"},
    {"name": "personal device access from home",
     "required": {"personal"},
     "any_of": [{"phone"}, {"device"}, {"mobile"}],
     "extra": [{"home"}, {"remote"}],
     "doc": "policy_it_acceptable_use.txt", "section": "3.1"},
    {"name": "DA and meal receipts same day",
     "required": {"da", "meal", "receipt"},
     "any_of": [], "doc": "policy_finance_reimbursement.txt",
     "section": "2.6"},
    {"name": "LWP approval",
     "required": {"leave", "without", "pay"},
     "any_of": [{"approve"}, {"approver"}],
     "doc": "policy_hr_leave.txt", "section": "5.2"},
]


def _tokens(text: str):
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if t]


def _prefix_hit(tokens, word):
    return any(t == word or t.startswith(word) for t in tokens)


def retrieve_documents(paths):
    """Load the policy files into {doc_name: [(section, text), ...]}."""
    index = {}
    for path in paths:
        name = os.path.basename(path)
        if not os.path.exists(path):
            raise SystemExit(f"Missing policy document: {path}")
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()

        sections = []
        current = None
        for line in lines:
            stripped = line.strip()
            if not stripped or set(stripped) <= {"=", "\u2550"}:
                continue
            clause_match = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
            if clause_match:
                current = clause_match.group(1)
                sections.append([current, [clause_match.group(2)]])
                continue
            if sections and re.match(r"^\d+\.\s+[A-Z]", stripped):
                current = None
                continue
            if sections and current is not None:
                sections[-1][1].append(stripped)

        index[name] = [(num, " ".join(parts)) for num, parts in sections]
    return index


def _find_curated(question_tokens, index):
    for topic in TOPICS:
        matching = {word: _prefix_hit(question_tokens, word)
                    for word in topic["required"]}
        required_hit = all(matching.values())
        if not required_hit:
            continue
        any_hit = not topic["any_of"] or any(
            all(_prefix_hit(question_tokens, w) for w in group)
            for group in topic["any_of"])
        extra_hit = not topic.get("extra") or any(
            all(_prefix_hit(question_tokens, w) for w in group)
            for group in topic["extra"])
        if any_hit and extra_hit:
            for doc_name, sections in index.items():
                if doc_name == topic["doc"]:
                    for num, text in sections:
                        if num == topic["section"]:
                            return doc_name, num, text
    return None


def _score_sections(question_tokens, index):
    content = [t for t in question_tokens if t not in STOPWORDS]
    best_score = 0
    best = []  # (doc_name, section, text, score)
    for doc_name, sections in index.items():
        for num, text in sections:
            sec_tokens = {t for t in _tokens(text) if len(t) >= 3}
            score = 0
            for q in content:
                if any(t == q or t.startswith(q) or q.startswith(t)
                       for t in sec_tokens):
                    score += 1
            if score > best_score:
                best_score = score
                best = [(doc_name, num, text)]
            elif score == best_score and score > 0:
                best.append((doc_name, num, text))
    return best_score, best


def answer_question(question, index):
    """Return a single-source answer with citation, or the refusal template."""
    question_tokens = _tokens(question)
    if not question_tokens:
        return REFUSAL_TEMPLATE

    cur = _find_curated(question_tokens, index)
    if cur:
        doc_name, num, text = cur
        return f"Answer (Source: {doc_name} §{num}): {text}"

    score, best = _score_sections(question_tokens, index)
    if score < 2 or not best:
        return REFUSAL_TEMPLATE

    docs = {d for d, _, _ in best}
    if len(docs) > 1:
        return REFUSAL_TEMPLATE

    doc_name, num, text = best[0]
    return f"Answer (Source: {doc_name} §{num}): {text}"


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--question", help="Answer one question and exit "
                                           "(default: interactive REPL)")
    args = parser.parse_args()

    index = retrieve_documents(DOCUMENTS)
    loaded = ", ".join(sorted(index))
    print(f"Loaded documents: {loaded}\n")

    if args.question:
        print(answer_question(args.question, index))
        return

    print("Ask a question about the policy documents. "
          "Type 'exit' to quit.\n")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in ("exit", "quit", "q"):
            break
        if not question:
            continue
        print(answer_question(question, index))
        print()


if __name__ == "__main__":
    main()