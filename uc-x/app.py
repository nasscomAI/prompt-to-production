"""
UC-X — Ask My Documents.

Single-source policy Q&A across three CMC documents. Every answer either
comes from ONE document (with citation) or is the exact refusal template.

Usage:
  Interactive:      python app.py
  Single question:  python app.py --question "Can I carry forward unused annual leave?"
  Test suite:       python app.py --test-suite [--output answers.txt]

See agents.md for the enforcement rules this implements.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Optional


# ── Source documents ────────────────────────────────────────────────────────
DOCS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

# Topic keywords per document — used to route a question to a single owner.
# If a question hits multiple topics with meaningful weight, we refuse.
DOC_TOPICS: dict[str, list[str]] = {
    "policy_hr_leave.txt": [
        "leave",
        "annual leave",
        "sick leave",
        "carry forward",
        "carry-forward",
        "maternity",
        "paternity",
        "lwp",
        "leave without pay",
        "public holiday",
        "compensatory off",
        "encashment",
        "grievance",
        "medical certificate",
        "loss of pay",
        "lop",
    ],
    "policy_it_acceptable_use.txt": [
        "install",
        "software",
        "corporate device",
        "personal device",
        "personal phone",
        "byod",
        "laptop",
        "password",
        "mfa",
        "multi-factor",
        "cmc email",
        "endpoint security",
        "cmc network",
        "guest wifi",
        "remote access",
        "work files",
        "cmc data",
        "self-service portal",
    ],
    "policy_finance_reimbursement.txt": [
        "reimburse",
        "reimbursement",
        "claim",
        "expense",
        "receipt",
        "receipts",
        "da",
        "daily allowance",
        "meal",
        "hotel",
        "travel",
        "outstation",
        "air travel",
        "home office",
        "equipment allowance",
        "training",
        "certification",
        "mobile phone reimbursement",
        "internet reimbursement",
    ],
}

# Forbidden hedging phrases — every emitted answer is checked before return.
FORBIDDEN_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "in most cases",
    "as is standard",
    "usually",
    "generally speaking",
    "commonly",
]

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.+)$")
SECTION_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z0-9 &()/-]+)\s*$")


# ── retrieve_documents ─────────────────────────────────────────────────────
def retrieve_documents(paths: dict[str, str], base_dir: str) -> dict:
    clauses: list[dict] = []
    for doc_name, rel_path in paths.items():
        abs_path = os.path.join(base_dir, rel_path) if not os.path.isabs(rel_path) else rel_path
        if not os.path.exists(abs_path):
            sys.exit(f"ERROR: policy file not found: {abs_path}")
        with open(abs_path, encoding="utf-8") as f:
            lines = f.readlines()

        current_section: Optional[str] = None
        current_clause: Optional[dict] = None
        for raw in lines:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if stripped and set(stripped) <= {"═", "─", "=", "-"}:
                continue
            m_section = SECTION_RE.match(line)
            if m_section:
                current_section = m_section.group(1)
                current_clause = None
                continue
            m_clause = CLAUSE_RE.match(line)
            if m_clause and current_section is not None:
                current_clause = {
                    "doc": doc_name,
                    "section": current_section,
                    "clause": m_clause.group(1),
                    "text": m_clause.group(2).strip(),
                }
                clauses.append(current_clause)
                continue
            if current_clause is not None and stripped:
                current_clause["text"] = (current_clause["text"] + " " + stripped).strip()

    if not clauses:
        sys.exit("ERROR: no clauses parsed from any document — refusing to run.")
    return {"clauses": clauses, "doc_topics": DOC_TOPICS}


# ── answer_question ────────────────────────────────────────────────────────
def _score_topic(question_lower: str, keywords: list[str]) -> tuple[int, list[str]]:
    hits = [kw for kw in keywords if kw in question_lower]
    return len(hits), hits


def _pick_owner_doc(question: str) -> tuple[Optional[str], dict]:
    """Route the question to a single owning document. Returns (doc_name, debug)."""
    q = question.lower()
    scores: dict[str, tuple[int, list[str]]] = {}
    for doc, kws in DOC_TOPICS.items():
        n, hits = _score_topic(q, kws)
        if n > 0:
            scores[doc] = (n, hits)

    if not scores:
        return None, {"reason": "no topic keyword matched any document"}

    ranked = sorted(scores.items(), key=lambda kv: kv[1][0], reverse=True)
    top_doc, (top_n, top_hits) = ranked[0]

    # If more than one document scores, and the second is within 1 of the top,
    # treat it as cross-document ambiguity and refuse.
    if len(ranked) > 1:
        second_n = ranked[1][1][0]
        if second_n >= top_n:  # a tie is definitionally cross-doc
            return None, {
                "reason": "cross-document ambiguity — refusing to blend",
                "scores": {d: s for d, (s, _) in ranked},
            }
    return top_doc, {"scores": {d: s for d, (s, _) in ranked}, "top_hits": top_hits}


# Multi-word phrases we care about — presence in a clause is a strong signal
# that the clause is on-topic, worth much more than a single loose token match.
KNOWN_PHRASES = [
    "personal phone", "personal device", "personal devices",
    "personal use",
    "work files", "work laptop", "work from home", "working from home",
    "home office", "equipment allowance",
    "leave without pay", "annual leave", "sick leave", "carry forward",
    "carry-forward", "medical certificate", "public holiday",
    "compensatory off",
    "daily allowance", "meal receipts", "meal receipt", "outstation travel",
    "air travel",
    "corporate device", "corporate devices", "cmc email",
    "self-service portal",
    "hr director", "department head", "municipal commissioner",
    "professional certification",
    "mobile phone reimbursement", "internet reimbursement",
]

# Acronym expansions — a question mentioning either side surfaces the other.
ACRONYMS = {
    "lwp": "leave without pay",
    "leave without pay": "lwp",
    "da": "daily allowance",
    "daily allowance": "da",
    "byod": "personal device",
    "mfa": "multi-factor authentication",
    "lop": "loss of pay",
    "loss of pay": "lop",
    "wfh": "work from home",
    "work from home": "wfh",
}


def _stem(token: str) -> str:
    """Very small suffix stripper so 'approves' matches 'approval' via prefix."""
    for suffix in ("ing", "ed", "es", "s"):
        if len(token) > len(suffix) + 3 and token.endswith(suffix):
            return token[: -len(suffix)]
    return token


def _extract_phrases(question_lower: str) -> list[str]:
    hits = [p for p in KNOWN_PHRASES if p in question_lower]
    # Also fold in acronym-equivalents.
    for k, v in ACRONYMS.items():
        if k in question_lower and v not in hits and v in KNOWN_PHRASES:
            hits.append(v)
        if v in question_lower and k not in hits and k in KNOWN_PHRASES:
            hits.append(k)
    return hits


def _intent_boost_terms(question_lower: str) -> list[str]:
    """Return substrings whose presence in a clause deserves an extra score bump."""
    boosts: list[str] = []
    if question_lower.lstrip().startswith("who "):
        # Entity-lookup intent — favour clauses that name an approver.
        boosts.extend(["approval from", "approved by", "must be approved"])
    if "approve" in question_lower or "approval" in question_lower or "approves" in question_lower:
        boosts.extend(["approval from", "approved by", "requires approval"])
    return boosts


def _rank_clauses(question: str, clauses: list[dict], owner_doc: str) -> list[dict]:
    """
    Rank owner_doc clauses by phrase hits + stemmed token hits + intent boosts.
    Then group by section, pick the section with the highest cumulative score,
    and return that section's clauses in descending clause score.
    """
    q_lower = question.lower()

    # Expand acronyms into the searchable question text so tokenisation catches them.
    expanded_q = q_lower
    for k, v in ACRONYMS.items():
        if k in q_lower and v not in expanded_q:
            expanded_q += " " + v

    tokens = _extract_tokens(expanded_q)
    stems = list({_stem(t) for t in tokens} | set(tokens))
    phrases = _extract_phrases(q_lower)
    boost_terms = _intent_boost_terms(q_lower)

    per_clause: list[tuple[int, dict]] = []
    for c in clauses:
        if c["doc"] != owner_doc:
            continue
        text_l = c["text"].lower()

        phrase_score = 3 * sum(1 for p in phrases if p in text_l)
        token_score = sum(1 for s in stems if len(s) >= 3 and s in text_l)
        boost_score = 5 * sum(1 for b in boost_terms if b in text_l)

        total = phrase_score + token_score + boost_score
        if total > 0:
            per_clause.append((total, c))

    if not per_clause:
        return []

    # Section-level winner-take-all.
    section_totals: dict[str, int] = {}
    for score, c in per_clause:
        sec = c["clause"].split(".")[0]
        section_totals[sec] = section_totals.get(sec, 0) + score
    top_section = max(section_totals.items(), key=lambda kv: kv[1])[0]

    in_section = [(s, c) for s, c in per_clause if c["clause"].startswith(f"{top_section}.")]
    in_section.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in in_section]


_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "can", "could", "may", "might", "should", "would", "will", "shall",
    "do", "does", "did", "have", "has", "had", "of", "and", "or", "but",
    "if", "then", "else", "in", "on", "at", "to", "for", "with", "from",
    "by", "as", "it", "this", "that", "these", "those", "my", "your",
    "our", "their", "his", "her", "its", "i", "we", "you", "they",
    "what", "which", "who", "whom", "whose", "how", "when", "where", "why",
    "not", "no", "yes", "same", "day", "days",
}


def _extract_tokens(text: str) -> list[str]:
    tokens = re.findall(r"[a-z][a-z\-]{2,}", text.lower())
    return [t for t in tokens if t not in _STOPWORDS]


def _assert_no_hedging(text: str) -> None:
    t = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in t:
            sys.exit(
                f"ERROR: refusing to emit answer containing hedging phrase "
                f"'{phrase}'. Enforcement rule 2 violated."
            )


def answer_question(question: str, index: dict) -> dict:
    q = (question or "").strip()
    if not q:
        return {
            "answer": REFUSAL_TEMPLATE,
            "source_doc": None,
            "sections": [],
            "refused": True,
        }

    owner_doc, debug = _pick_owner_doc(q)
    if owner_doc is None:
        _assert_no_hedging(REFUSAL_TEMPLATE)
        return {
            "answer": REFUSAL_TEMPLATE,
            "source_doc": None,
            "sections": [],
            "refused": True,
        }

    ranked = _rank_clauses(q, index["clauses"], owner_doc)
    if not ranked:
        return {
            "answer": REFUSAL_TEMPLATE,
            "source_doc": None,
            "sections": [],
            "refused": True,
        }

    # _rank_clauses already picked one winning section — cap the citation list.
    supporting = ranked[:4]

    citations = ", ".join(f"section {c['clause']}" for c in supporting)
    body_lines = [f"  - {c['text']}" for c in supporting]
    answer = (
        "Answer (single-source, verbatim from policy):\n"
        + "\n".join(body_lines)
        + f"\n(source: {owner_doc}, {citations})"
    )
    _assert_no_hedging(answer)
    return {
        "answer": answer,
        "source_doc": owner_doc,
        "sections": [c["clause"] for c in supporting],
        "refused": False,
    }


# ── Test suite (from README) ───────────────────────────────────────────────
TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def run_test_suite(index: dict, output_path: Optional[str] = None) -> str:
    blocks: list[str] = []
    for i, q in enumerate(TEST_QUESTIONS, start=1):
        result = answer_question(q, index)
        marker = "REFUSED" if result["refused"] else "ANSWERED"
        blocks.append(
            f"── Q{i} [{marker}] ─────────────────────────────────────────\n"
            f"Q: {q}\n\n"
            f"{result['answer']}\n"
        )
    output = "\n".join(blocks)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
    return output


# ── CLI ────────────────────────────────────────────────────────────────────
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="UC-X Ask My Documents")
    p.add_argument("--question", help="Ask one question and exit.")
    p.add_argument("--test-suite", action="store_true", help="Run the 7 README test questions.")
    p.add_argument("--output", help="Optional path to write test-suite results.")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    index = retrieve_documents(DOCS, base_dir)

    if args.test_suite:
        out = run_test_suite(index, args.output)
        print(out)
        return 0

    if args.question:
        result = answer_question(args.question, index)
        print(result["answer"])
        return 0

    # Interactive fallback.
    print("UC-X Ask My Documents — type a question, or 'quit' to exit.")
    while True:
        try:
            q = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if q.lower() in {"quit", "exit", "q"}:
            return 0
        if not q:
            continue
        result = answer_question(q, index)
        print()
        print(result["answer"])


if __name__ == "__main__":
    raise SystemExit(main())
