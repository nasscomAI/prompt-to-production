"""
UC-X — Ask My Documents
RICE-enforced policy Q&A. Rules from agents.md, structure from skills.md.
"""
import argparse
import math
import re

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "can", "could", "do", "does",
    "did", "i", "me", "my", "we", "our", "you", "your", "on", "in", "at", "to",
    "for", "of", "with", "and", "or", "but", "what", "who", "when", "where",
    "why", "how", "it", "its", "this", "that", "from", "by", "as", "be", "been",
    "being", "have", "has", "had", "not", "no", "may", "must", "will", "should",
    "would", "about", "any", "all", "their", "there", "here", "which", "please",
    "only", "within", "than", "up", "such", "each", "other", "per", "under",
}

WEAK_TOKENS = {"work", "working", "culture", "view", "company", "flexible"}

ALIASES = {
    "approval": "approve",
    "approved": "approve",
    "approves": "approve",
    "used": "use",
    "claimed": "claim",
    "claiming": "claim",
    "phone": "device",
}

SECTION_HEADER = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 .&()\-/]+)$")
CLAUSE_NUMBER = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def tokenize(text: str) -> list:
    text = text.lower()
    text = text.replace("leave without pay", " lwp ")
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    tokens = []
    for t in text.split():
        if t in STOPWORDS:
            continue
        t = ALIASES.get(t, t)
        if t.endswith("s") and t != "lwp":
            t = t[:-1]
        t = ALIASES.get(t, t)
        if t not in STOPWORDS and t not in WEAK_TOKENS:
            tokens.append(t)
    return tokens


def retrieve_documents(paths: list) -> dict:
    index = {}
    for path in paths:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()

        sections = []
        clauses = []
        current_section = None
        current_title = ""
        current_clause = None

        for raw in lines:
            line = raw.strip()
            if not line or set(line) <= {"\u2550"}:
                continue
            if line.startswith("Version:") or line.startswith("Document Reference:"):
                continue

            header = SECTION_HEADER.match(line)
            if header:
                sections.append({"number": header.group(1), "title": header.group(2)})
                current_section = header.group(1)
                current_title = header.group(2)
                current_clause = None
                continue

            clause = CLAUSE_NUMBER.match(line)
            if clause and not clause.group(2).startswith("|"):
                current_clause = {
                    "number": clause.group(1),
                    "section": current_section,
                    "title": current_title,
                    "text": clause.group(2),
                }
                clauses.append(current_clause)
                continue

            if current_clause is not None:
                current_clause["text"] += " " + line

        if not clauses:
            raise ValueError(f"No clauses found in {path}")
        index[path] = {"sections": sections, "clauses": clauses}
    return index


def build_idf(index: dict) -> dict:
    doc_names = list(index.keys())
    df = {}
    for path in index:
        doc_tokens = set()
        for clause in index[path]["clauses"]:
            doc_tokens.update(clause["tokens"])
        for token in doc_tokens:
            df[token] = df.get(token, 0) + 1
    return {
        token: math.log((len(doc_names) + 1) / (count + 1))
        for token, count in df.items()
    }


def answer_question(question: str, index: dict, idf: dict) -> str:
    qtokens = set(tokenize(question))
    if not qtokens:
        return REFUSAL_TEMPLATE

    best_score = (-1, 0.0, -1)
    best = []
    for path in index:
        for clause in index[path]["clauses"]:
            matched = set(clause["tokens"]) & qtokens
            title_matched = set(clause["title_tokens"]) & qtokens
            key = (len(matched),
                   sum(idf.get(t, 0.0) for t in matched),
                   len(title_matched))
            if key > best_score:
                best_score = key
                best = [(path, clause)]
            elif key == best_score and key[0] > 0:
                best.append((path, clause))

    if best_score[0] == 0:
        return REFUSAL_TEMPLATE

    best_docs = {path for path, _ in best}
    if len(best_docs) > 1:
        return REFUSAL_TEMPLATE

    path, clause = min(best, key=lambda x: x[1]["number"])
    doc_name = re.split(r"[\\/]", path)[-1]
    return f"[{doc_name} | Section {clause['number']}] {clause['text']}"


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument(
        "--docs", nargs="*", default=DOC_PATHS,
        help="Policy files to index (default: the three in ../data/policy-documents)",
    )
    args = parser.parse_args()

    index = retrieve_documents(args.docs)
    for clause in [c for p in index for c in index[p]["clauses"]]:
        clause["tokens"] = tokenize(clause["text"]) + tokenize(clause["title"])
        clause["title_tokens"] = tokenize(clause["title"])
    idf = build_idf(index)

    print("CMC Policy Q&A — sources:")
    for path in args.docs:
        print(f"  - {path.rsplit('/', 1)[-1]}")
    print("Type a question, or 'exit' to quit.")

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        print(answer_question(question, index, idf))


if __name__ == "__main__":
    main()
