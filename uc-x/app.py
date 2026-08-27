import argparse
import os
import re
import sys


POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def retrieve_policy(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()
    content = "".join(lines).strip()
    if not content:
        return []
    clause_pat = re.compile(r'^(\d+\.\d+)\s')
    section_pat = re.compile(r'^\d+\.\s+[A-Z]')
    sep_pat = re.compile(r'^═+$')
    clauses = []
    cur_id = None
    cur_lines = []
    def flush():
        nonlocal cur_id, cur_lines
        if cur_id is not None:
            text = "\n".join(cur_lines).strip()
            clauses.append({"clause_id": cur_id, "text": text})
            cur_id = None
            cur_lines = []
    for raw_line in lines:
        line = raw_line.rstrip("\n")
        m = clause_pat.match(line)
        if m:
            flush()
            cur_id = m.group(1)
            cur_lines = [line]
        elif cur_id is not None:
            if sep_pat.match(line) or section_pat.match(line) or line.strip() == "":
                flush()
            else:
                cur_lines.append(line)
    flush()
    if not clauses:
        clauses.append({"clause_id": "raw", "text": content})
    return clauses


def summarize_policy(clauses):
    if not clauses:
        return "The document contains no clauses to summarise."
    parts = []
    for clause in clauses:
        if clause["clause_id"] == "raw":
            parts.append(f"FLAGGED — No numbered clauses found.\n{clause['text']}")
        else:
            parts.append(f"Clause {clause['clause_id']}: {clause['text']}")
    return "\n\n".join(parts)


def retrieve_documents():
    index = {}
    for fname in POLICY_FILES:
        fpath = os.path.join(POLICY_DIR, fname)
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Policy file not found: {fpath}")
        with open(fpath, encoding="utf-8") as f:
            content = f.read()
        clauses = retrieve_policy(fpath)
        index[fname] = {c["clause_id"]: c["text"] for c in clauses}
    return index


def answer_question(question, index):
    q_lower = question.lower().strip()
    best_match = None
    best_score = 0
    for doc_name, clauses in index.items():
        for clause_id, clause_text in clauses.items():
            if clause_id == "raw":
                continue
            score = _match_score(q_lower, clause_text.lower())
            if score > best_score:
                best_score = score
                best_match = (doc_name, clause_id, clause_text)
    if best_match and best_score > 0:
        doc_name, clause_id, clause_text = best_match
        return f"According to {doc_name} (section {clause_id}): {clause_text}"
    return REFUSAL_TEMPLATE


_STOP_WORDS = frozenset({
    "a", "about", "after", "also", "an", "and", "are", "as", "at", "be",
    "been", "being", "but", "by", "can", "could", "did", "do", "does",
    "for", "from", "had", "has", "have", "how", "i", "if", "in", "into",
    "is", "it", "its", "just", "my", "no", "not", "of", "on", "or",
    "out", "over", "should", "so", "than", "that", "the", "them", "then",
    "this", "to", "up", "very", "was", "were", "what", "when", "where",
    "who", "will", "with", "would", "use", "used", "using", "work",
    "working",
})


def _match_score(question, text):
    q_words = {w for w in re.findall(r'\b[a-z]+\b', question.lower()) if w not in _STOP_WORDS}
    if not q_words:
        return 0
    t_words = {w for w in re.findall(r'\b[a-z]+\b', text.lower()) if w not in _STOP_WORDS}
    if not t_words:
        return 0
    matches = 0
    for qw in q_words:
        if qw in t_words:
            matches += 1
        else:
            for tw in t_words:
                if len(qw) >= 5 and len(tw) >= 5 and qw[:5] == tw[:5]:
                    matches += 0.5
                    break
    return matches / len(q_words)


def main():
    parser = argparse.ArgumentParser(description="UC-X — Ask My Documents")
    parser.add_argument("--input", help="Input policy file path")
    parser.add_argument("--output", help="Output summary file path")
    args = parser.parse_args()
    if args.input and args.output:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
        return
    try:
        index = retrieve_documents()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    print("UC-X — Ask My Documents (type 'exit' to quit)")
    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in ("exit", "quit"):
            break
        if not q:
            continue
        print(answer_question(q, index))


if __name__ == "__main__":
    main()
