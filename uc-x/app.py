"""
UC-X app.py — Ask My Documents
Built with the RICE → agents.md → skills.md → CRAFT workflow.
Enforcement mirrors uc-x/agents.md: single-source answers with citation,
no cross-document blending, no hedging, exact refusal template.

Run: python app.py   (interactive; also accepts questions piped on stdin)
"""
import os
import re
import sys

POLICY_DIR = os.path.join("..", "data", "policy-documents")
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department (HR, IT, or Finance) for guidance."
)

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z].*)$")

STOPWORDS = {
    "a", "an", "the", "is", "are", "can", "i", "my", "to", "for", "of", "on",
    "in", "at", "and", "or", "do", "does", "what", "who", "when", "how", "may",
    "use", "used", "using", "be", "with", "from", "this", "that", "it", "if",
    "am", "will", "would", "should", "could", "have", "has", "you", "your",
    "me", "we", "our", "as", "by", "into", "same", "day", "get", "there",
}

# Light synonym map so question wording matches document wording.
SYNONYMS = {
    "phone": {"phone", "device", "mobile"},
    "laptop": {"laptop", "device", "computer", "corporate"},
    "install": {"install", "installation", "software"},
    "slack": {"software"},
    "lwp": {"lwp", "leave", "pay"},
    "approves": {"approval", "approve", "approved"},
    "approve": {"approval", "approved"},
    "allowance": {"allowance"},
    "carry": {"carry", "carry-forward", "forward"},
    "da": {"da", "allowance"},
}


def tokenize(text):
    words = re.findall(r"[a-z0-9\-]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def expand(tokens):
    out = set()
    for t in tokens:
        out.add(t)
        out |= SYNONYMS.get(t, set())
    return out


def retrieve_documents(paths):
    """Load policy files, index by document name + section id."""
    index = []
    for path in paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Policy file not found: {path}")
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        if not any(l.strip() for l in lines):
            raise ValueError(f"Policy file is empty: {path}")

        doc_name = os.path.basename(path)
        section_title = ""
        current = None
        for line in lines:
            if not line.strip() or set(line.strip()) <= set("═ "):
                continue
            clause = CLAUSE_RE.match(line)
            section = SECTION_RE.match(line)
            if clause:
                current = {
                    "document_name": doc_name,
                    "section_id": clause.group(1),
                    "section_title": section_title,
                    "clause_text": clause.group(2).strip(),
                }
                index.append(current)
            elif section:
                section_title = section.group(2).strip()
                current = None
            elif current is not None:
                current["clause_text"] += " " + line.strip()
    return index


def score_entry(q_terms, entry):
    """Overlap score between question terms and a clause (+ its section title)."""
    hay = expand(tokenize(entry["clause_text"] + " " + entry["section_title"]))
    return sum(1 for t in q_terms if t in hay)


def answer_question(question, index, threshold=2, margin=1):
    """Return a single-source cited answer or the exact refusal template."""
    q_terms = expand(tokenize(question))
    scored = sorted(
        ((score_entry(q_terms, e), e) for e in index),
        key=lambda x: x[0], reverse=True,
    )
    if not scored or scored[0][0] < threshold:
        return REFUSAL_TEMPLATE

    top_score, top_entry = scored[0]

    # Cross-document ambiguity: a near-tied top match from a different document.
    for s, e in scored[1:]:
        if top_score - s > margin:
            break
        if e["document_name"] != top_entry["document_name"] and s >= threshold:
            return REFUSAL_TEMPLATE

    return (
        f"{top_entry['clause_text']}\n"
        f"Source: {top_entry['document_name']}, section {top_entry['section_id']}"
    )


def main():
    paths = [os.path.join(POLICY_DIR, name) for name in POLICY_FILES]
    index = retrieve_documents(paths)
    print(f"Loaded {len(index)} clauses from {len(paths)} policy documents.")
    print("Ask a policy question (Ctrl-D or 'quit' to exit).\n")

    while True:
        try:
            question = input("Q: ").strip()
        except EOFError:
            break
        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            break
        print("\n" + answer_question(question, index) + "\n")


if __name__ == "__main__":
    main()
