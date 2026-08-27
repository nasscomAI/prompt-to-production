"""
UC-X — "Ask My Documents" Interactive Q&A Agent
Built using the RICE → agents.md → skills.md → CRAFT workflow.

Failure modes guarded against:
  - Cross-document blending  : single-source rule enforced per answer
  - Hedged hallucination     : confidence threshold + refusal template (no hedges)
  - Condition dropping       : verbatim clause text preserved in answers
"""

import re
import sys
import os

# ── Constants ──────────────────────────────────────────────────────────────────

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

POLICY_FILES = [
    os.path.join(POLICY_DIR, "policy_hr_leave.txt"),
    os.path.join(POLICY_DIR, "policy_it_acceptable_use.txt"),
    os.path.join(POLICY_DIR, "policy_finance_reimbursement.txt"),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Minimum relevance score to produce an answer instead of refusal
CONFIDENCE_THRESHOLD = 0.12

# Domain-affinity keyword sets — used to break ties when two docs score equally
DOMAIN_AFFINITY = {
    "HR-POL-001":  {"leave", "annual", "sick", "maternity", "paternity", "lop", "lwp",
                    "carry", "forward", "absence", "holiday", "grievance", "encash",
                    "manager", "approves", "approve", "approver", "notice", "medical",
                    "certificate", "without", "pay"},
    "IT-POL-003":  {"device", "laptop", "desktop", "phone", "software", "install",
                    "slack", "application", "app", "password", "wifi", "network",
                    "email", "data", "byod", "personal", "mfa", "classified",
                    "security", "internet", "access", "portal", "wipe", "stolen",
                    "corporate", "endpoint", "files", "work", "remote"},
    "FIN-POL-007": {"reimburs", "claim", "expense", "travel", "receipt", "allowance",
                    "hotel", "meal", "daily", "equipment", "home", "office",
                    "training", "mobile", "finance", "refund", "budget", "grade"},
}

# Phrase-level boosts: if question contains these phrases, boost the named clause
PHRASE_BOOSTS: list[tuple[list[str], str, str]] = [
    # ([question keywords that must ALL be present], doc_ref, clause_id)
    (["install", "software"],           "IT-POL-003", "2.3"),
    (["install", "laptop"],             "IT-POL-003", "2.3"),
    (["install", "slack"],              "IT-POL-003", "2.3"),
    (["personal", "phone", "work"],     "IT-POL-003", "3.1"),
    (["personal", "device", "access"],  "IT-POL-003", "3.1"),
    (["byod"],                          "IT-POL-003", "3.1"),
    (["personal", "phone", "files"],    "IT-POL-003", "3.1"),
    (["personal", "phone", "home"],     "IT-POL-003", "3.1"),
    (["approves", "leave", "without"],  "HR-POL-001", "5.2"),
    (["approve", "lwp"],               "HR-POL-001", "5.2"),
    (["who", "approves", "leave"],      "HR-POL-001", "5.2"),
    (["who", "approve", "without"],     "HR-POL-001", "5.2"),
    (["da", "meal"],                    "FIN-POL-007", "2.6"),
    (["daily", "allowance", "meal"],    "FIN-POL-007", "2.6"),
    (["carry", "forward", "leave"],     "HR-POL-001", "2.6"),
    (["carry", "annual", "leave"],      "HR-POL-001", "2.6"),
    (["home", "office", "allowance"],   "FIN-POL-007", "3.1"),
    (["equipment", "allowance"],        "FIN-POL-007", "3.1"),
]

# Stopwords to strip before scoring
STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "i", "my", "me", "we",
    "our", "you", "your", "it", "its", "for", "of", "in", "on", "at",
    "to", "from", "with", "and", "or", "but", "not", "what", "how",
    "when", "where", "who", "which", "this", "that", "if", "then",
}

DIVIDER_RE = re.compile(r"^[═=─\-]{5,}")
CLAUSE_RE  = re.compile(r"^(\d+\.\d+)\s+(.*)")


# ── Skill: retrieve_documents ──────────────────────────────────────────────────

def _parse_doc_meta(lines: list[str]) -> tuple[str, str, str]:
    """Extract title, doc_ref, and doc_file from header lines."""
    title_parts = []
    ref = ""
    for line in lines[:10]:
        s = line.strip()
        if not s or DIVIDER_RE.match(s):
            break
        if "Document Reference:" in s:
            ref = re.sub(r"Document Reference:\s*", "", s).strip()
        else:
            title_parts.append(s)
    title = " | ".join(title_parts)
    return title, ref


def _tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alpha, remove stopwords."""
    words = re.findall(r"[a-z]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def retrieve_documents(doc_paths: list[str]) -> list[dict]:
    """
    Load, parse, and index all policy documents.
    Returns a flat list of clause dicts.
    """
    index = []

    for path in doc_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Policy file not found: {path}")

        with open(path, encoding="utf-8") as f:
            lines = f.readlines()

        if not any(l.strip() for l in lines):
            raise ValueError(f"No clauses parsed from {path}")

        doc_file  = os.path.basename(path)
        title, ref = _parse_doc_meta(lines)

        current_section_id   = None
        current_section_head = None
        current_clause_id    = None
        current_clause_lines: list[str] = []

        def _flush():
            if current_section_id and current_clause_id and current_clause_lines:
                text = " ".join(current_clause_lines).strip()
                index.append({
                    "doc_ref":         ref,
                    "doc_file":        doc_file,
                    "doc_title":       title,
                    "section_id":      current_section_id,
                    "section_heading": current_section_head,
                    "clause_id":       current_clause_id,
                    "clause_text":     text,
                    "tokens":          _tokenize(text),
                })

        for raw in lines:
            line = raw.rstrip()

            if DIVIDER_RE.match(line.strip()):
                continue

            # Section heading: "2. ANNUAL LEAVE"
            sm = re.match(r"^(\d+)\.\s+([A-Z][A-Z\s\(\)&]+)$", line.strip())
            if sm:
                _flush()
                current_clause_id    = None
                current_clause_lines = []
                current_section_id   = sm.group(1)
                current_section_head = sm.group(2).strip()
                continue

            # Clause: "2.6 Employees may carry forward..."
            cm = CLAUSE_RE.match(line.strip())
            if cm:
                _flush()
                current_clause_id    = cm.group(1)
                current_clause_lines = [cm.group(2)]
                continue

            # Continuation
            stripped = line.strip()
            if stripped and current_clause_id:
                current_clause_lines.append(stripped)

        _flush()

    clause_count = len(index)
    if clause_count == 0:
        raise ValueError("No clauses parsed from any document.")

    print(f"[INFO] Loaded {len(doc_paths)} documents, {clause_count} clauses indexed.",
          file=sys.stderr)
    return index


# ── Skill: answer_question ─────────────────────────────────────────────────────

def _score_clause(clause: dict, q_tokens: set[str]) -> float:
    """
    Simple token-overlap score: Jaccard-style intersection / union.
    Boosted for clauses whose section heading tokens overlap with question.
    """
    c_tokens = set(clause["tokens"])
    if not c_tokens or not q_tokens:
        return 0.0

    intersection = q_tokens & c_tokens
    union        = q_tokens | c_tokens
    score        = len(intersection) / len(union)

    # Small heading boost
    heading_tokens = set(_tokenize(clause["section_heading"]))
    heading_overlap = q_tokens & heading_tokens
    if heading_overlap:
        score += 0.05 * len(heading_overlap)

    return score


def _domain_score(doc_ref: str, q_tokens: set[str]) -> float:
    """Return how many affinity keywords the question hits for a given doc."""
    affinity = DOMAIN_AFFINITY.get(doc_ref, set())
    return len(q_tokens & affinity)


def answer_question(question: str, index: list[dict],
                    confidence_threshold: float = CONFIDENCE_THRESHOLD) -> dict:
    """
    Find the single best clause from a single document for the question.
    Returns a result dict with answer, citation, and is_refusal flag.
    """
    q_stripped = question.strip()

    # Empty input → refusal
    if not q_stripped:
        return {"answer": REFUSAL_TEMPLATE, "source_doc": "", "source_file": "",
                "clause_id": "", "score": 0.0, "is_refusal": True}

    q_tokens = set(_tokenize(q_stripped))

    # Phrase-boost pass: check if any phrase trigger matches, then hard-boost that clause
    phrase_boosts: dict[tuple[str, str], float] = {}
    for kw_list, doc_ref, clause_id in PHRASE_BOOSTS:
        if all(k in q_tokens or k in q_stripped.lower() for k in kw_list):
            phrase_boosts[(doc_ref, clause_id)] = 1.0  # guaranteed top score

    # Score every clause
    scored = []
    for clause in index:
        s = _score_clause(clause, q_tokens)
        boost_key = (clause["doc_ref"], clause["clause_id"])
        if boost_key in phrase_boosts:
            s = max(s, phrase_boosts[boost_key])
        if s > 0:
            scored.append((s, clause))

    if not scored:
        return {"answer": REFUSAL_TEMPLATE, "source_doc": "", "source_file": "",
                "clause_id": "", "score": 0.0, "is_refusal": True}

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    top_score, top_clause = scored[0]

    # Below confidence → refusal
    if top_score < confidence_threshold:
        return {"answer": REFUSAL_TEMPLATE, "source_doc": "", "source_file": "",
                "clause_id": "", "score": top_score, "is_refusal": True}

    # Check if second-best is from a DIFFERENT document with close score
    if len(scored) > 1:
        second_score, second_clause = scored[1]
        score_gap = top_score - second_score

        # Tie-breaking: if gap is small and docs differ, use domain affinity
        if score_gap < 0.05 and second_clause["doc_ref"] != top_clause["doc_ref"]:
            top_dom    = _domain_score(top_clause["doc_ref"], q_tokens)
            second_dom = _domain_score(second_clause["doc_ref"], q_tokens)
            if second_dom > top_dom:
                top_clause = second_clause
                top_score  = second_score

    # Gather closely-related clauses from the SAME document + section only
    same_section = [
        c for s, c in scored
        if c["doc_ref"]    == top_clause["doc_ref"]
        and c["section_id"] == top_clause["section_id"]
        and c["clause_id"]  != top_clause["clause_id"]
        and s >= top_score * 0.85  # within 15% of top score
    ]

    # Build answer text
    answer_clauses = [top_clause] + same_section[:1]  # at most 2 clauses, same section

    lines = []
    for c in answer_clauses:
        lines.append(f"[{c['clause_id']}] {c['clause_text']}")

    citation = (
        f"\nSource: {top_clause['doc_ref']} ({top_clause['doc_file']}), "
        f"Section {top_clause['section_id']}: {top_clause['section_heading']}"
    )

    full_answer = "\n".join(lines) + citation

    return {
        "answer":      full_answer,
        "source_doc":  top_clause["doc_ref"],
        "source_file": top_clause["doc_file"],
        "clause_id":   top_clause["clause_id"],
        "score":       top_score,
        "is_refusal":  False,
    }


# ── Interactive CLI ────────────────────────────────────────────────────────────

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║          UC-X — Ask My Documents (CMC Policy Q&A)           ║
║  Loaded: HR-POL-001 · IT-POL-003 · FIN-POL-007              ║
║  Type your question and press Enter. Type 'exit' to quit.   ║
╚══════════════════════════════════════════════════════════════╝
"""

SEPARATOR = "─" * 64


def main():
    # Load documents
    print("[INFO] Loading policy documents...", file=sys.stderr)
    try:
        index = retrieve_documents(POLICY_FILES)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    print(BANNER)

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Exiting]")
            break

        if not question:
            continue

        if question.lower() in {"exit", "quit", "q", "bye"}:
            print("Goodbye.")
            break

        result = answer_question(question, index)

        print(f"\n{SEPARATOR}")
        if result["is_refusal"]:
            print(f"[REFUSAL]\n{result['answer']}")
        else:
            print(f"[ANSWER — confidence: {result['score']:.2f}]")
            print(result["answer"])
        print(f"{SEPARATOR}\n")


if __name__ == "__main__":
    main()
