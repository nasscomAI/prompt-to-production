"""
UC-X -- Ask My Documents
Implements retrieve_documents and answer_question using RICE enforcement rules
defined in agents.md and skills.md.

Core failure modes guarded against:
  - Cross-document blending   (single-source rule strictly enforced)
  - Hedged hallucination      (banned phrases list checked; refusal template used)
  - Condition dropping        (citations include section numbers)
"""
import sys
import os
import re

# Reconfigure stdout to UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

POLICY_FILES = {
    "policy_hr_leave.txt":             "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt":    "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt":"../data/policy-documents/policy_finance_reimbursement.txt",
}

# Phrases BANNED from any answer (trigger refusal template)
BANNED_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "employees are generally expected",
    "in most organisations",
    "as is standard",
]

# Which team to contact per document
DOC_TEAM = {
    "policy_hr_leave.txt":              "HR",
    "policy_it_acceptable_use.txt":     "IT",
    "policy_finance_reimbursement.txt": "Finance",
}


def _refusal_template(question: str, relevant_team: str = "[relevant team]") -> str:
    docs = ", ".join(POLICY_FILES.keys())
    return (
        f"This question is not covered in the available policy documents\n"
        f"({docs}).\n"
        f"Please contact {relevant_team} for guidance."
    )


# ──────────────────────────────────────────────────────────────────────────────
# SKILL: retrieve_documents
# ──────────────────────────────────────────────────────────────────────────────

def retrieve_documents(file_paths: dict) -> dict:
    """
    Load all policy .txt files and return a unified section index:
      { "policy_hr_leave.txt": [ {"section": "2.3", "text": "..."}, ... ], ... }

    Enforcement: All three documents must load or exit with code 1.
    """
    index = {}

    for doc_name, path in file_paths.items():
        if not os.path.exists(path):
            print(f"ERROR: Cannot find document '{doc_name}' at path: {path}",
                  file=sys.stderr)
            print("All three policy documents are required. Cannot proceed with partial index.",
                  file=sys.stderr)
            sys.exit(1)

        with open(path, encoding="utf-8") as f:
            content = f.read()

        # Parse parent headings to inject as context (e.g. "3. PERSONAL DEVICES (BYOD)")
        parent_headings = {}
        heading_pattern = re.compile(r"(?m)^[ \t]*(\d+)\.[ \t]+([A-Z][A-Z &\-()]+)[ \t]*$")
        for m in heading_pattern.finditer(content):
            num = m.group(1).strip()
            title = m.group(2).strip()
            parent_headings[num] = title

        # Parse sections: match "X.Y text..." blocks
        section_pattern = re.compile(
            r"(?m)^[ \t]*(\d+\.\d+)[ \t]+(.*?)(?=\n[ \t]*\d+\.\d+[ \t]|\Z)",
            re.DOTALL
        )

        sections = []
        for m in section_pattern.finditer(content):
            sec_num  = m.group(1).strip()
            sec_body = (m.group(1) + " " + m.group(2)).strip()
            # Normalise internal whitespace
            sec_body = re.sub(r"\n[ \t]+", " ", sec_body).strip()
            # Strip embedded section headings (e.g. "═══...═══" and "N. SECTION TITLE" lines)
            # that the regex captures when they appear right after the last sub-clause
            sec_body = re.sub(r"[\r\n]+\u2550+[\r\n]*", " ", sec_body)
            sec_body = re.sub(r"[\r\n]+\d+\.[ \t]+[A-Z][A-Z &\-()]+[\r\n]*", " ", sec_body)
            sec_body = re.sub(r"\s{2,}", " ", sec_body).strip()
            # Strip any trailing section heading (e.g. "5. LEAVE WITHOUT PAY (LWP)")
            # that was captured as trailing content of the prior section
            sec_body = re.sub(r"\s+\d+\.\s+[A-Z][A-Z ()&/\-]+$", "", sec_body).strip()

            # Inject parent title for block context
            parent_num = sec_num.split(".")[0]
            parent_title = parent_headings.get(parent_num, "")
            if parent_title:
                sec_body = parent_title + " -- " + sec_body

            sections.append({"section": sec_num, "text": sec_body})

        if not sections:
            print(f"WARNING: No numbered sections found in '{doc_name}'. "
                  f"Storing as UNPARSED.", file=sys.stderr)
            sections = [{"section": "UNPARSED", "text": content.strip()}]

        index[doc_name] = sections

    return index


# ──────────────────────────────────────────────────────────────────────────────
# SKILL: answer_question
# ──────────────────────────────────────────────────────────────────────────────

# Synonym/acronym expansions: query word → extra words to also search for
SYNONYMS = {
    "da":         ["daily allowance", "da"],
    "lwp":        ["leave without pay", "lwp", "without pay"],
    "leave":      ["lwp", "leave"],
    "pay":        ["lwp", "without pay", "loss of pay"],
    "slack":      ["software", "application", "program", "app"],
    "laptop":     ["device", "devices", "computer", "laptop"],
    "phone":      ["device", "devices", "mobile", "phone", "personal device", "personal devices"],
    "personal":   ["personal device", "personal devices", "byod"],
    "files":      ["data", "files", "document", "documents"],
    "home":       ["remote", "wfh", "work-from-home"],
    "approves":   ["approval", "approved", "approves", "approve"],
    "approve":    ["approval", "approved", "approves", "approve"],
    "manager":    ["director", "head", "commissioner"],
    "culture":    ["flexible", "culture", "environment"],
}

STOP_WORDS = {
    "can", "for", "my", "from", "the", "and", "or", "to", "of", "in", "is", "it", "on", "at",
    "by", "an", "be", "with", "this", "that", "your", "who", "what", "how", "why", "which",
    "he", "she", "they", "we", "you", "me", "our", "him", "her", "us", "them", "are", "was",
    "were", "been", "have", "has", "had", "do", "does", "did", "but", "so", "if", "not", "no",
    "yes", "about", "would", "should", "could", "will", "without", "work"
}

def _expand_query_phrases(q: str) -> str:
    """Helper to detect key multi-word phrases and append their abbreviations."""
    q = q.lower()
    if "leave without pay" in q:
        q += " lwp"
    if "work from home" in q or "working from home" in q:
        q += " wfh"
    if "daily allowance" in q:
        q += " da"
    return q

def _score_section(section_text: str, query_tokens: list) -> int:
    """
    Keyword relevance score with synonym expansion and exact match boost.
    Matches exact token as +2, synonym as +1 (only if exact not found).
    """
    text_lower = section_text.lower()
    score = 0
    for t in query_tokens:
        if t in STOP_WORDS:
            continue
        if t in text_lower:
            score += 2
        else:
            for expanded in SYNONYMS.get(t, []):
                if expanded in text_lower:
                    score += 1
                    break
    return score


def answer_question(question: str, index: dict) -> str:
    """
    Search index for an answer. Returns:
      (a) Single-source answer with citation  -- if exactly one document answers
      (b) Exact refusal template              -- if no doc answers OR if blending required

    Enforcement:
    1. Never blend claims from two documents.
    2. Never use banned/hedging phrases.
    3. If question empty or index incomplete -- return refusal.
    4. Cite source doc + section for every claim.
    """
    # ── Guard: empty question ──────────────────────────────────────────────
    if not question or not question.strip():
        return _refusal_template(question)

    # ── Guard: incomplete index ────────────────────────────────────────────
    missing_docs = [d for d in POLICY_FILES if d not in index]
    if missing_docs:
        print(f"  WARNING: Missing documents in index: {missing_docs}", file=sys.stderr)
        return _refusal_template(question)

    # ── Expand and Tokenise question ───────────────────────────────────────
    expanded_q = _expand_query_phrases(question)
    query_tokens = re.findall(r"[a-z]{2,}", expanded_q)

    # ── Score each section across all documents ────────────────────────────
    hits = []   # list of (score, doc_name, section)
    for doc_name, sections in index.items():
        for sec in sections:
            score = _score_section(sec["text"], query_tokens)
            if score > 0:
                hits.append((score, doc_name, sec))

    # ── Tie-breaking: prefer approval-specific sections when question is about approvals ──
    # If "who" and an approval verb are in query tokens, boost sections containing "approval"
    if "who" in query_tokens and any(t in query_tokens for t in ("approve", "approves", "approval")):
        def _approval_boost(hit):
            score, doc, sec = hit
            boost = 5 if "approval" in sec["text"].lower() else 0
            return -(score + boost)
        hits.sort(key=_approval_boost)
    else:
        hits.sort(key=lambda x: -x[0])

    if not hits:
        # No sections matched → refusal
        team = _guess_team(question)
        return _refusal_template(question, team)

    # ── Calculate best hit and best score ──────────────────────────────────
    best_hit = hits[0]
    best_score = best_hit[0]
    if "who" in query_tokens and any(t in query_tokens for t in ("approve", "approves", "approval")):
        boost = 5 if "approval" in best_hit[2]["text"].lower() else 0
        best_score += boost

    top_doc = best_hit[1]

    # ── Enforcement: Single-source rule ────────────────────────────────────
    # Find matching hits in OTHER documents to check for ambiguity/blending
    other_docs = []
    for h in hits:
        if h[1] != top_doc:
            h_score = h[0]
            if "who" in query_tokens and any(t in query_tokens for t in ("approve", "approves", "approval")):
                h_boost = 5 if "approval" in h[2]["text"].lower() else 0
                h_score += h_boost
            if h_score >= max(1, best_score - 1):
                other_docs.append((h_score, h[1], h[2]))

    if other_docs:
        other_best = other_docs[0][0]
        if other_best >= best_score - 1 and other_best >= 2:
            # Multi-doc ambiguity/overlap → refusal
            team = _guess_team(question)
            return _refusal_template(question, team)

    # ── Build answer from top_doc sections ────────────────────────────────
    # Use ONLY the single best-matching section to prevent noise / partial blending
    answer_sections = [best_hit]
    citations = []
    answer_parts = []

    for _, doc_name, sec in answer_sections:
        sec_text = sec["text"].strip()
        # Enforce: check no banned phrase slipped in from source
        for banned in BANNED_PHRASES:
            if banned.lower() in sec_text.lower():
                team = _guess_team(question)
                return _refusal_template(question, team)

        citations.append(f"Section {sec['section']}")
        answer_parts.append(sec_text)

    answer_body = "\n".join(answer_parts)
    citation_str = ", ".join(citations)

    answer = (
        f"{answer_body}\n\n"
        f"(Source: {top_doc}, {citation_str})"
    )

    # ── Final check: no banned phrases in assembled answer ────────────────
    for banned in BANNED_PHRASES:
        if banned.lower() in answer.lower():
            team = _guess_team(question)
            return _refusal_template(question, team)

    return answer


def _guess_team(question: str) -> str:
    """Heuristic: guess which team to contact based on question topic."""
    q = question.lower()
    if any(w in q for w in ["leave", "annual", "sick", "holiday", "maternity",
                              "paternity", "lwp", "carry forward", "encash"]):
        return "HR"
    if any(w in q for w in ["laptop", "software", "device", "install", "phone",
                              "byod", "wifi", "network", "it", "email"]):
        return "IT"
    if any(w in q for w in ["claim", "reimburs", "travel", "allowance", "receipt",
                              "expense", "da ", "meal", "finance"]):
        return "Finance"
    return "[relevant team]"


# ──────────────────────────────────────────────────────────────────────────────
# CLI ENTRY POINT — Interactive loop
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("\nUC-X -- Ask My Documents")
    print("Loading policy documents...")

    index = retrieve_documents(POLICY_FILES)

    total_sections = sum(len(s) for s in index.values())
    print(f"  Loaded {len(index)} documents, {total_sections} sections indexed.")
    print(f"  Documents: {', '.join(index.keys())}")
    print(f"\n{'='*60}")
    print("  Type your question and press Enter.")
    print("  Type 'quit' or 'exit' to stop.")
    print(f"{'='*60}\n")

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        if not question:
            continue

        print()
        answer = answer_question(question, index)
        print("-" * 60)
        print(answer)
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()
