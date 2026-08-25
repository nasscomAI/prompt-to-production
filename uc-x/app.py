"""
UC-X — Ask My Documents
Built per agents.md (RICE enforcement rules) and skills.md.
"""
import argparse
import re

DOC_PATHS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")

# Synonym map so a question written in everyday language ("phone", "laptop", "files",
# "approves") still matches policy wording ("device", "data", "approval") — pure literal-
# word overlap would otherwise miss both the cross-document trap question (README's
# Section 3.1 trap) and plain morphological variants (approves/approval, devices/device).
SYNONYMS = {
    "phone": "device", "phones": "device", "mobile": "device", "smartphone": "device",
    "laptop": "device", "computer": "device", "device": "device",
    "files": "data", "file": "data",
    "wfh": "home",
    "slack": "software", "app": "software",
    "approves": "approve", "approved": "approve", "approval": "approve", "approving": "approve",
    "carry": "carry", "forward": "forward",
}

STOPWORDS = {
    "the", "a", "an", "is", "are", "can", "i", "my", "to", "for", "on", "in", "of", "and",
    "what", "who", "when", "do", "does", "if", "or", "be", "used", "use", "this", "that",
    "same", "day",
    # Domain-specific over-common words: "leave"/"without"/"pay" appear in nearly every
    # clause of the HR leave policy, so they carry almost no discriminating signal for
    # THIS corpus even though they'd matter in a general-purpose retriever. The "lwp"
    # synthetic token (added below) already captures the "Leave Without Pay" concept.
    "leave", "without", "pay",
}


def _stem(word: str) -> str:
    """Crude plural-stripping so 'devices'/'device' and 'laptops'/'laptop' align —
    intentionally not a full Porter stemmer, just enough for this tiny corpus."""
    if len(word) > 4 and word.endswith("es"):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _normalize(text: str) -> set:
    words = re.findall(r"[a-z]+", text.lower())
    out = set()
    for w in words:
        if w in STOPWORDS:
            continue
        w = SYNONYMS.get(w, _stem(w))
        out.add(SYNONYMS.get(w, w))
    # LWP is an abbreviation used ONLY in some clauses (5.2, 5.3) — the phrase "Leave
    # Without Pay" used elsewhere (5.1, 5.4) does NOT literally contain "lwp". Bag-of-
    # words alone would score the spelled-out clauses higher just from word count, even
    # when the abbreviated clause is the semantically correct one — add "lwp" as a
    # shared token for both forms so TF-IDF weighting (not raw word count) decides.
    lowered = text.lower()
    if "lwp" in lowered or "leave without pay" in lowered:
        out.add("lwp")
    return out


def retrieve_documents(paths: dict) -> dict:
    """
    Load all 3 policy files, index by document name and section number.
    Returns: dict {doc_name: {section_number: text}}
    """
    index = {}
    for doc_name, path in paths.items():
        sections = {}
        current_num = None
        with open(path, encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                # Same fix as UC-0B: unicode "═" divider or ALL-CAPS header is a
                # hard stop, never a continuation of the previous clause.
                if set(line) <= {"═"} or (line.isupper() and current_num is not None):
                    current_num = None
                    continue
                m = CLAUSE_RE.match(line)
                if m:
                    current_num = m.group(1)
                    sections[current_num] = m.group(2)
                elif current_num is not None:
                    sections[current_num] += " " + line
        index[doc_name] = sections
    return index


def _build_doc_frequency(index: dict) -> dict:
    """
    df[token] = number of (doc, section) pairs across the WHOLE corpus containing that
    token. Used as a simple TF-IDF-style rarity weight: a word shared by nearly every
    clause in a section (e.g. "leave", "pay" inside the leave policy) shouldn't out-
    score a rare, discriminating word (e.g. "approve") just by raw count.
    """
    df = {}
    for sections in index.values():
        for text in sections.values():
            for tok in _normalize(text):
                df[tok] = df.get(tok, 0) + 1
    return df


def answer_question(question: str, index: dict, df: dict) -> str:
    """
    Score every section across all 3 documents against the question using TF-IDF-style
    weighting. Return a single-source cited answer, or the exact refusal template.
    """
    q_tokens = _normalize(question)

    def weighted_score(tokens: set) -> float:
        shared = q_tokens & tokens
        return sum(1.0 / df.get(tok, 1) for tok in shared)

    # best score per document (doc -> (score, section_num))
    best_per_doc = {}
    for doc_name, sections in index.items():
        best_score, best_sec = 0.0, None
        for sec_num, text in sections.items():
            score = weighted_score(_normalize(text))
            if score > best_score:
                best_score, best_sec = score, sec_num
        best_per_doc[doc_name] = (best_score, best_sec)

    ranked = sorted(best_per_doc.items(), key=lambda kv: kv[1][0], reverse=True)
    top_doc, (top_score, top_sec) = ranked[0]
    second_doc, (second_score, _second_sec) = ranked[1]

    if top_score <= 0.0:
        return REFUSAL_TEMPLATE

    # Genuine cross-document ambiguity: a different document's best section scores
    # almost as well as the winner — refuse rather than silently pick one (or blend).
    if second_score > 0 and (top_score - second_score) < 0.3 * top_score:
        return REFUSAL_TEMPLATE

    clause_text = index[top_doc][top_sec]
    return f'[Source: {top_doc}, Section {top_sec}] "{clause_text}"'


TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--test", action="store_true", help="Run the 7 fixed test questions non-interactively")
    args = parser.parse_args()

    idx = retrieve_documents(DOC_PATHS)
    doc_freq = _build_doc_frequency(idx)

    if args.test:
        for q in TEST_QUESTIONS:
            print(f"\nQ: {q}")
            print(f"A: {answer_question(q, idx, doc_freq)}")
    else:
        print("Ask My Documents — type a question, or 'quit' to exit.")
        while True:
            try:
                q = input("\n> ").strip()
            except EOFError:
                break
            if q.lower() in ("quit", "exit"):
                break
            if not q:
                continue
            print(answer_question(q, idx, doc_freq))
