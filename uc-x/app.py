"""
UC-X app.py — Ask My Documents
Interactive CLI Q&A over three CMC policy documents.

Enforcement rules:
  1. Never combine claims from two different documents into a single answer.
  2. Never use hedging phrases.
  3. If question is not in the documents — use the refusal template exactly.
  4. Cite source document name + section number for every factual claim.
"""

import os
import re
import sys
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent / "data" / "policy-documents"
POLICY_FILES = {
    "policy_hr_leave.txt":            "HR-POL-001 (Employee Leave Policy)",
    "policy_it_acceptable_use.txt":   "IT-POL-003 (Acceptable Use Policy)",
    "policy_finance_reimbursement.txt": "FIN-POL-007 (Expense Reimbursement Policy)",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant team for guidance."
)

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "to", "of", "in", "on",
    "at", "by", "for", "with", "about", "from", "that", "this", "it",
    "its", "i", "me", "my", "we", "our", "you", "your", "he", "she",
    "they", "their", "what", "who", "how", "when", "where", "which",
    "and", "or", "not", "no", "any", "all", "if", "up", "as", "so",
    "there", "use", "used",
}

# Synonym expansion: maps a stem to additional stems to search for.
SYNONYMS = {
    "phone":   ["devic", "byod", "person"],
    "laptop":  ["devic", "corpor", "byod"],
    "slack":   ["softwar", "instal"],
    "instal":  ["softwar", "slack"],
    "file":    ["data", "document"],
    "remot":   ["home", "wfh"],
    "home":    ["remot", "wfh"],
    "claim":   ["reimburse", "submit"],
    "reimburse": ["claim", "submit"],
    "approv":  ["approval", "approv"],
    "pay":     ["lwp", "paid", "salari"],
    "da":      ["allowance", "meal", "dai"],
    "meal":    ["da", "allowance", "receipt"],
    "leav":    ["lwp", "annual", "entitl"],
}

MIN_SCORE = 3   # minimum keyword hits required to attempt an answer


def stem(word):
    """Minimal suffix stemmer for consistent matching."""
    for suffix in ["tion", "ment", "ing", "ness", "ful", "less",
                   "er", "ed", "al", "ly", "es", "s"]:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[:-len(suffix)]
    return word


def expand_tokens(tokens):
    """Expand query tokens with synonyms (stemmed)."""
    expanded = list(tokens)
    for t in tokens:
        s = stem(t)
        for syn in SYNONYMS.get(t, []) + SYNONYMS.get(s, []):
            if syn not in expanded:
                expanded.append(syn)
    return expanded


# ─── Document loading and indexing ────────────────────────────────────────────

def load_documents():
    """Load all policy files and parse them into labelled sections."""
    documents = {}
    for filename, label in POLICY_FILES.items():
        path = BASE_DIR / filename
        if not path.exists():
            print(f"WARNING: {path} not found — skipping.", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8")
        sections = parse_sections(text, filename, label)
        documents[filename] = {
            "label": label,
            "filename": filename,
            "sections": sections,
        }
    return documents


def parse_sections(text, filename, label):
    """
    Split document into sections.
    Returns list of dicts: {section_header, section_num, clauses: [{num, text}]}
    """
    lines = text.splitlines()
    sections = []
    current_header = "PREAMBLE"
    current_num = "0"
    current_clauses = []

    # Section header lines are all-caps words after ═══ dividers
    divider_re = re.compile(r"^═+$")
    header_re  = re.compile(r"^(\d+)\.\s+([A-Z].*)")
    clause_re  = re.compile(r"^\s*(\d+\.\d+)\s+(.*)")

    i = 0
    while i < len(lines):
        line = lines[i]
        if divider_re.match(line.strip()):
            # Next non-empty line is section header
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines):
                hline = lines[i].strip()
                m = header_re.match(hline)
                if m:
                    if current_clauses:
                        sections.append({
                            "header": current_header,
                            "num": current_num,
                            "clauses": current_clauses,
                        })
                    current_num = m.group(1)
                    current_header = hline
                    current_clauses = []
            i += 1
            continue

        m = clause_re.match(line)
        if m:
            clause_num = m.group(1)
            clause_text = m.group(2).strip()
            # Accumulate continuation lines (indented, not a new clause)
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if next_line.strip() == "":
                    break
                if clause_re.match(next_line):
                    break
                if divider_re.match(next_line.strip()):
                    break
                clause_text += " " + next_line.strip()
                i += 1
            current_clauses.append({"num": clause_num, "text": clause_text})
            continue

        i += 1

    if current_clauses:
        sections.append({
            "header": current_header,
            "num": current_num,
            "clauses": current_clauses,
        })

    return sections


# ─── Retrieval ────────────────────────────────────────────────────────────────

def tokenise(text):
    words = re.findall(r"[a-z]+", text.lower())
    raw = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return [stem(w) for w in raw]


def tokenise_raw(text):
    """Tokenise without stemming (for display / logging only)."""
    words = re.findall(r"[a-z]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def score_document(query_tokens, doc):
    """Return (total_score, best_section, best_clauses) for a document."""
    best_section = None
    best_clauses = []
    best_score = 0

    for section in doc["sections"]:
        # Score section header too
        header_tokens = tokenise(section["header"])
        header_hit = sum(1 for qt in query_tokens if qt in header_tokens)

        section_score = header_hit * 0.5   # half-weight for header
        matching_clauses = []
        for clause in section["clauses"]:
            ctokens = tokenise(clause["text"])
            hits = sum(1 for qt in query_tokens if qt in ctokens)
            clause_score = float(hits)
            if clause_score > 0:
                matching_clauses.append((clause_score, clause))
                section_score += clause_score

        if section_score > best_score:
            best_score = section_score
            best_section = section
            best_clauses = [c for _, c in sorted(matching_clauses, key=lambda x: x[0], reverse=True)]

    return best_score, best_section, best_clauses


def retrieve_documents(query, documents):
    """
    Search all documents. Return the single best-matching document with its
    top section and clauses, or None if confidence is too low.
    Enforces single-source rule — never blends across documents.
    """
    query_tokens = expand_tokens(tokenise(query))
    if not query_tokens:
        return None, None, None

    results = []
    for filename, doc in documents.items():
        score, section, clauses = score_document(query_tokens, doc)
        results.append((score, filename, doc, section, clauses))

    results.sort(reverse=True, key=lambda x: x[0])

    top_score, top_file, top_doc, top_section, top_clauses = results[0]

    if top_score < MIN_SCORE:
        return None, None, None

    # Single-source enforcement: if runner-up is close, still pick top only
    # (never blend — just pick the winner)
    return top_doc, top_section, top_clauses[:5]   # cap at 5 most relevant clauses


# ─── Answer generation ────────────────────────────────────────────────────────

def format_answer(doc, section, clauses):
    """Format a single-source answer with citation."""
    source = f"{doc['label']} (file: {doc['filename']})"
    sec_ref = f"Section {section['num']} — {section['header']}"

    lines = [
        f"Source: {source}",
        f"Section: {sec_ref}",
        "",
    ]
    for clause in clauses:
        lines.append(f"  [{clause['num']}] {clause['text']}")

    return "\n".join(lines)


def answer_question(query, documents):
    """Return formatted answer string."""
    doc, section, clauses = retrieve_documents(query, documents)

    if doc is None or section is None or not clauses:
        return REFUSAL_TEMPLATE

    return format_answer(doc, section, clauses)


# ─── Interactive CLI ──────────────────────────────────────────────────────────

def main():
    print("=== CMC Policy Q&A — Ask My Documents ===")
    print("Loading policy documents …")

    documents = load_documents()
    if not documents:
        print("ERROR: No policy documents loaded. Check the data/policy-documents/ directory.")
        sys.exit(1)

    loaded = ", ".join(doc["label"] for doc in documents.values())
    print(f"Loaded: {loaded}")
    print(f"\nType your question and press Enter. Type 'quit' or 'exit' to stop.\n")
    print("-" * 60)

    while True:
        try:
            query = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not query:
            continue
        if query.lower() in {"quit", "exit", "q"}:
            print("Exiting.")
            break

        print()
        answer = answer_question(query, documents)
        print(answer)
        print("-" * 60)


if __name__ == "__main__":
    main()

