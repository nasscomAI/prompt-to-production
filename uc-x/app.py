"""
UC-X — Ask My Documents

Interactive CLI that answers policy questions from three CMC policy documents.
Implements retrieve_documents and answer_question per skills.md.
"""
import re
import sys
from pathlib import Path

POLICY_DIR = (
    Path(__file__).resolve().parent.parent / "data" / "policy-documents"
)
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

OUTPUT_FILE = Path(__file__).resolve().parent / "answer.txt"

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "can",
    "could", "shall", "should", "may", "might", "i", "you", "he", "she",
    "it", "we", "they", "me", "him", "us", "them", "my", "your", "his",
    "her", "its", "our", "their", "this", "that", "these", "those",
    "what", "which", "who", "whom", "when", "where", "why", "how",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
    "into", "about", "like", "through", "after", "over", "between",
    "out", "if", "than", "then", "also", "just", "or", "but", "and",
    "not", "no", "nor", "so", "yet", "up", "down", "off", "per",
    "any", "all", "each", "every", "both", "own", "same", "too",
    "very", "please", "work", "use", "day", "new",
}


# ---------------------------------------------------------------------------
# Skill 1: retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents():
    """Load all three policy files, indexed by document name and section number."""
    docs = {}
    for fname in POLICY_FILES:
        path = POLICY_DIR / fname
        if not path.exists():
            print(f"Error: {path} not found.", file=sys.stderr)
            sys.exit(1)
        docs[fname] = _parse_sections(path.read_text(encoding="utf-8"))
    return docs


def _parse_sections(text):
    """Return dict mapping 'X.Y' section numbers to their content text."""
    sections = {}
    current_num = None
    current_lines = []
    subsec_pat = re.compile(r"^(\d+\.\d+)\s+(.*)")
    major_sec_pat = re.compile(r"^\d+\.\s")
    sep_pat = re.compile(r"^[═=]{10,}$")

    for line in text.splitlines():
        s = line.strip()
        if not s or sep_pat.match(s):
            continue
        m = subsec_pat.match(s)
        if m:
            if current_num is not None and current_lines:
                sections[current_num] = " ".join(current_lines)
            current_num = m.group(1)
            current_lines = [m.group(2)]
        elif major_sec_pat.match(s):
            if current_num is not None and current_lines:
                sections[current_num] = " ".join(current_lines)
            current_num = None
            current_lines = []
        elif current_num is not None:
            current_lines.append(s)

    if current_num is not None and current_lines:
        sections[current_num] = " ".join(current_lines)

    return sections


# ---------------------------------------------------------------------------
# Skill 2: answer_question
# ---------------------------------------------------------------------------

def answer_question(question, documents):
    """Return a single-source answer with citation, or the refusal template."""
    q_tokens = _tokenize(question)
    if not q_tokens:
        return REFUSAL

    # Determine question type for bonus scoring
    q_lower = question.lower().strip()
    q_type = None
    if q_lower.startswith("who"):
        q_type = "who"
    elif q_lower.startswith("can"):
        q_type = "can"

    role_pattern = re.compile(
        r"\b(Head|Director|Manager|Commissioner|Officer|Department|"
        r"HR|IT|Finance|Municipal)\b", re.IGNORECASE
    )

    # Score each document independently — best matching section per doc
    best_per_doc = {}
    for doc_name, sections in documents.items():
        best_score = 0
        best_sections = []
        for sec_num, sec_text in sections.items():
            sec_tokens = _tokenize(sec_text)
            score = 0
            for qt in q_tokens:
                for st in sec_tokens:
                    if _stem_match(qt, st):
                        if qt == st:
                            score += 2
                        else:
                            score += 1
                        break
            if q_type == "who":
                roles = role_pattern.findall(sec_text)
                score += len(roles) * 2
            elif q_type == "can":
                if "must not" in sec_text.lower() or "not" in sec_text.lower():
                    score += 1
                if "only" in sec_text.lower():
                    score += 1
            if score > best_score:
                best_score = score
                best_sections = [(sec_num, sec_text)]
            elif score == best_score and score > 0:
                best_sections.append((sec_num, sec_text))
        if best_sections:
            best_per_doc[doc_name] = (best_score, best_sections)

    if not best_per_doc:
        return REFUSAL

    max_score = max(s for s, _ in best_per_doc.values())
    top_docs = {d: v for d, v in best_per_doc.items() if v[0] == max_score}

    # If two different documents tie at the top, refuse (no blending)
    if len(top_docs) > 1 and max_score > 0:
        return REFUSAL

    doc_name = next(iter(top_docs))
    _, best_sections = top_docs[doc_name]
    sec_num, sec_text = best_sections[0]

    return f"{doc_name} section {sec_num}: {sec_text}"


def _tokenize(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {w for w in words if w not in STOP_WORDS and len(w) > 1}


def _stem_match(q_token, sec_token):
    """True if one token is a prefix of the other (handles plurals, verb forms)."""
    shorter, longer = (q_token, sec_token) if len(q_token) <= len(sec_token) else (sec_token, q_token)
    return shorter == longer[:len(shorter)]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    print("UC-X \u2014 Ask My Documents")
    print("Type a question (or 'exit' to quit)\n")
    documents = retrieve_documents()

    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q:
            continue
        if q.lower() in ("exit", "quit"):
            break
        result = answer_question(q, documents)
        print(result)
        OUTPUT_FILE.write_text(result + "\n", encoding="utf-8")
        print()


if __name__ == "__main__":
    main()
