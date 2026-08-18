"""
UC-X — Ask My Documents
Interactive Q&A over 3 policy documents.
Single-source answers only — refuses cross-document blends and
out-of-scope questions.

Usage:
  python app.py
"""
import math
import re
import sys
from pathlib import Path


DOC_PATHS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "out", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "when",
    "where", "why", "how", "all", "each", "every", "both", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "so", "than", "too", "very", "just", "because", "but", "and",
    "or", "if", "what", "which", "who", "whom", "this", "that", "these",
    "those", "about", "up", "it", "its", "my", "your", "our", "their",
    "his", "her", "my", "your", "his", "her", "our", "their",
    "i", "me", "we", "us", "you", "he", "she", "they", "them",
    "myself", "yourself", "himself", "herself", "itself", "ourselves",
    "themselves", "any", "some", "anything", "something", "nothing",
    "everything", "everyone", "anyone", "someone", "please", "thanks",
    "thank", "get", "tell", "ask", "like", "want", "need", "know",
    "also", "well", "back", "still", "even", "much", "many", "also",
    "whether", "within", "must", "regarding", "regards",
    "via", "per", "than", "into",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

CROSS_DOC_REFUSAL = (
    "This question spans topics from multiple policy documents. "
    "To avoid combining information from different sources, "
    "I cannot provide a combined answer. "
    "Please ask about a specific policy document or consult "
    "the relevant department."
)


IRREGULAR_ROOTS = {
    "approval": "approv", "approve": "approv", "approves": "approv",
    "approved": "approv", "approving": "approv",
    "entitlement": "entitle", "entitlements": "entitle",
    "entitled": "entitle",
    "encashed": "encash",
    "chang": "change",
    "instal": "install",
}


def stem(word: str) -> str:
    w = word.lower()
    if len(w) <= 3:
        return w

    # ies → y
    if w.endswith("ies") and len(w) > 4:
        w = w[:-3] + "y"
    # regular s removal (handles most plurals + verb third-person)
    elif w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        w = w[:-1]

    # ing
    if w.endswith("ing") and len(w) > 4:
        base = w[:-3]
        if len(base) > 2 and base[-1] == base[-2]:
            base = base[:-1]  # running → run, installing → install
        w = base
    # ed
    if w.endswith("ed") and len(w) > 3:
        base = w[:-2]
        if len(base) > 2 and base[-1] == base[-2]:
            base = base[:-1]  # stopped → stop, submitted → submit
        w = base

    if w in IRREGULAR_ROOTS:
        w = IRREGULAR_ROOTS[w]

    return w


def tokenize(text: str, apply_stem: bool = True) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    words = [w for w in words if w not in STOPWORDS]
    if apply_stem:
        words = [stem(w) for w in words]
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_document(text: str, doc_name: str) -> list[dict]:
    lines = text.splitlines()
    sections = []
    current_section = None
    clause_pat = re.compile(r"^(\d+\.\d+)\s+(.+)")
    sec_pat = re.compile(r"^(\d+)\.\s+(.+)")
    sep_pat = re.compile(r"^═+$")

    for line in lines:
        s = line.strip()
        if not s or sep_pat.match(s):
            continue
        cm = clause_pat.match(s)
        sm = sec_pat.match(s)
        if cm and current_section is not None:
            current_section["clauses"].append({
                "num": cm.group(1),
                "text": cm.group(2).strip(),
            })
        elif sm and not cm:
            current_section = {
                "num": sm.group(1),
                "title": sm.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
        elif current_section and current_section["clauses"] and s:
            current_section["clauses"][-1]["text"] += " " + s

    index = []
    for sec in sections:
        sec_text_combined = " ".join(c["text"] for c in sec["clauses"])
        sec_tokens = tokenize(sec_text_combined)
        for cl in sec["clauses"]:
            combined = sec["title"] + " " + cl["text"]
            index.append({
                "doc": doc_name,
                "clause_num": cl["num"],
                "section_num": sec["num"],
                "section_title": sec["title"],
                "text": cl["text"],
                "doc_tokens": None,
                "sec_tokens": sec_tokens,
                "clause_tokens": tokenize(combined),
                "full_ref": f"{doc_name} section {cl['num']}",
            })
    return index


def retrieve_documents() -> list[dict]:
    all_idx = []
    base = Path(__file__).parent
    for doc_name, rel in DOC_PATHS.items():
        p = (base / rel).resolve()
        if not p.exists():
            sys.exit(f"Error: Document not found: {p}")
        text = read_file(str(p))
        docs = parse_document(text, doc_name)
        all_idx.extend(docs)

    doc_names = list(DOC_PATHS.keys())
    doc_texts = {d: "" for d in doc_names}
    for e in all_idx:
        doc_texts[e["doc"]] += e["text"] + " "

    for d in doc_names:
        doc_tokens = tokenize(doc_texts[d])
        for e in all_idx:
            if e["doc"] == d:
                e["doc_tokens"] = doc_tokens

    return all_idx


def compute_idf(index: list[dict]) -> dict[str, float]:
    n_docs = len(DOC_PATHS)
    token_doc_count: dict[str, int] = {}
    seen_in_doc: dict[str, set[str]] = {}
    for e in index:
        if e["doc"] not in seen_in_doc:
            seen_in_doc[e["doc"]] = set()
        for t in e["doc_tokens"]:
            if t not in seen_in_doc[e["doc"]]:
                seen_in_doc[e["doc"]].add(t)
                token_doc_count[t] = token_doc_count.get(t, 0) + 1
    idf = {}
    for token, count in token_doc_count.items():
        idf[token] = math.log((n_docs - count + 0.5) / (count + 0.5) + 1.0)
    return idf


def score_document(q_tokens: set[str], doc_tokens: set[str], idf: dict[str, float]) -> float:
    score = 0.0
    for qt in q_tokens:
        if qt in doc_tokens:
            score += idf.get(qt, 1.0)
    return score


def answer_question(question: str, index: list[dict], idf: dict[str, float]) -> str:
    q_tokens = tokenize(question)
    if not q_tokens:
        return REFUSAL_TEMPLATE

    MIN_SCORE = 0.5
    CROSS_RATIO = 0.6

    doc_names = list(DOC_PATHS.keys())
    doc_tokens_map = {}
    doc_scores = {}
    for d in doc_names:
        dt = next(e["doc_tokens"] for e in index if e["doc"] == d)
        doc_tokens_map[d] = dt
        doc_scores[d] = score_document(q_tokens, dt, idf)

    best_doc = max(doc_scores, key=doc_scores.get)
    best_score = doc_scores[best_doc]

    if best_score < MIN_SCORE:
        return REFUSAL_TEMPLATE

    close_docs = [d for d, s in doc_scores.items()
                  if s >= best_score * CROSS_RATIO
                  and len(q_tokens & doc_tokens_map[d]) >= 3]
    if len(close_docs) > 1:
        return CROSS_DOC_REFUSAL

    doc_entries = [e for e in index if e["doc"] == best_doc]
    scored = []
    for e in doc_entries:
        clause_idf = sum(idf.get(t, 0.0) for t in (q_tokens & e["clause_tokens"]))
        sec_idf = sum(idf.get(t, 0.0) for t in (q_tokens & e["sec_tokens"]))
        score = clause_idf * 5 + sec_idf
        scored.append((score, e))

    best_clause_score = max(s for s, _ in scored)
    best = [e for s, e in scored if s == best_clause_score][0]
    return f"[{best['full_ref']}] {best['text']}"


def main():
    print("Loading policy documents...", flush=True)
    index = retrieve_documents()
    idf = compute_idf(index)
    print(f"Indexed {len(index)} clauses across {len(DOC_PATHS)} policy documents.\n")
    print("Ask me anything about the policies (or type 'quit' to exit).\n")

    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q:
            continue
        if q.lower() in ("quit", "exit", "q"):
            break
        ans = answer_question(q, index, idf)
        print(ans)
        print()


if __name__ == "__main__":
    main()
