"""
UC-X app.py — Ask My Documents
Interactive single-source policy Q&A implementing the RICE enforcement in
agents.md and the skill contracts in skills.md.
"""
import math
import re
import sys
from pathlib import Path

POLICY_DIR = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
DEFAULT_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

TEAM_HINTS = [
    ({"device", "devices", "software", "network", "password", "wifi", "email",
      "system", "systems", "laptop", "computer", "install", "access", "phone",
      "internet", "data"}, "IT Department"),
    ({"claim", "claims", "reimburse", "reimbursement", "allowance", "expense",
      "expenses", "travel", "hotel", "receipt", "receipts", "da", "refund",
      "payment", "finance"}, "Finance Department"),
    ({"leave", "lwp", "holiday", "holidays", "absence", "maternity",
      "paternity", "sick", "hr", "carry", "encashment"}, "HR Department"),
]

DOC_TEAMS = {
    "policy_hr_leave.txt": "HR Department",
    "policy_it_acceptable_use.txt": "IT Department",
    "policy_finance_reimbursement.txt": "Finance Department",
}

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

STOPWORDS = {
    "can", "could", "should", "would", "may", "might", "will", "shall",
    "i", "my", "me", "we", "our", "you", "your",
    "is", "are", "am", "was", "were", "be", "been", "being", "do", "does",
    "did", "has", "have", "had",
    "the", "a", "an", "to", "of", "in", "on", "at", "for", "and", "or",
    "with", "from", "by", "as", "if", "into", "about", "there", "that",
    "this", "these", "those", "it", "its", "when", "while", "what", "which",
    "who", "whom", "whose", "how", "why", "where", "any", "some", "same",
    "per", "get", "use", "used", "using",
}

STRONG_SCORE = 4
MIN_TERMS = 2
EXCLUSIVE_WEIGHT = 3
EXCLUSIVE_BYPASS_SCORE = 3
BLEND_MARGIN = 0.8


def parse_document(path: Path) -> dict:
    """Parse one policy .txt into {title, sections:{no:{heading, clauses}}} preserving wording."""
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    title_parts = []
    sections = {}
    current_section = None
    current_heading = ""
    current_clause_id = None
    current_parts = []

    def flush_clause():
        nonlocal current_clause_id, current_parts
        if current_clause_id is not None and current_parts:
            sections[current_section]["clauses"][current_clause_id] = " ".join(
                " ".join(current_parts).split()
            )
        current_clause_id = None
        current_parts = []

    for line in lines:
        stripped = line.strip()
        if not stripped or re.fullmatch(r"═+", stripped):
            continue
        clause_match = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
        section_match = None if clause_match else re.match(r"^(\d+)\.\s+(\S.*)$", stripped)

        if clause_match:
            flush_clause()
            current_section = clause_match.group(1).split(".")[0]
            current_clause_id = clause_match.group(1)
            current_parts = [clause_match.group(2)]
        elif section_match:
            flush_clause()
            current_section = section_match.group(1)
            current_heading = section_match.group(2).strip()
            sections[current_section] = {"heading": current_heading, "clauses": {}}
        elif current_clause_id is not None:
            current_parts.append(stripped)
        else:
            title_parts.append(stripped)

    flush_clause()
    return {"title": " | ".join(title_parts[:4]), "sections": sections}


def retrieve_documents(paths=None) -> dict:
    """
    Load all three policy files and index them by document name and section
    number (skills.md contract). Exits the session on unreadable files.
    """
    file_names = paths if paths else DEFAULT_FILES
    index = {}
    for name in file_names:
        path = Path(name)
        if not path.is_absolute() and not path.exists():
            path = POLICY_DIR / name
        try:
            index[Path(name).name] = parse_document(path)
        except OSError as exc:
            print(f"Error: cannot read policy file '{name}': {exc}")
            sys.exit(1)
        if not index[Path(name).name]["sections"]:
            print(f"Warning: no parsable sections found in '{name}'.")
    return index


def _question_terms(question: str) -> list:
    raw = [w for w in re.findall(r"[a-z0-9]+", question.lower()) if w not in STOPWORDS and len(w) >= 2]
    raw = sorted(set(raw))
    terms = []
    for w in raw:  # keep the shortest root: drop any term containing another term
        if not any(other != w and other in w for other in raw):
            terms.append(w)
    return terms


def _term_roots(term: str) -> list:
    """Cheap normalisation: term plus crude singular/stem variants."""
    roots = [term]
    for suffix in ("ies", "ing", "ied", "es", "ed", "s"):
        if term.endswith(suffix) and len(term) - len(suffix) >= 4:
            stem = term[: -len(suffix)]
            roots.append(stem)
            if stem.endswith("e") and len(stem) > 4:
                roots.append(stem[:-1])
            break
    return roots


def _term_in(term: str, blob: str) -> bool:
    for root in _term_roots(term):
        if len(root) <= 3:  # tiny terms need word boundaries ("da" must not hit "daily")
            if re.search(rf"\b{re.escape(root)}\b", blob):
                return True
        elif re.search(rf"\b{re.escape(root)}", blob):
            # Word-PREFIX match: token must start with the root. Genuine
            # inflections pass ("approval" ~ "approv"); compound-word traps
            # fail ("networks" must not match "work").
            return True
    return False


def _resolve_team(question: str) -> str:
    lowered = question.lower()
    for hints, team in TEAM_HINTS:
        if any(h in lowered for h in hints):
            return team
    return "the relevant department"


def _detect_department(question: str) -> str | None:
    """Department whose document should be searched — only when UNAMBIGUOUS."""
    lowered = question.lower()
    matched = [team for hints, team in TEAM_HINTS if any(h in lowered for h in hints)]
    return matched[0] if len(matched) == 1 else None


def _build_refusal(question: str) -> dict:
    return {
        "answer": REFUSAL_TEMPLATE.replace("[relevant team]", _resolve_team(question)),
        "source": None,
        "refused": True,
    }


def _corpus(index: dict) -> list:
    corpus = []
    for doc_name, doc in index.items():
        for section_no, section in doc["sections"].items():
            for clause_id, clause_text in section["clauses"].items():
                blob = f"{section['heading']} {clause_text}".lower()
                corpus.append({
                    "document": doc_name,
                    "section": clause_id,
                    "blob": blob,
                    "tokens": set(re.findall(r"[a-z0-9]+", blob)),
                    "text": clause_text,
                })
    return corpus


def answer_question(question: str, index: dict) -> dict:
    """
    Search the indexed documents and return a single-source cited answer,
    or the refusal template (skills.md contract). Never blends documents.
    """
    if not question.strip():
        return _build_refusal(question)

    corpus = _corpus(index)
    terms = _question_terms(question)

    # Document-rarity weighting computed on the FULL corpus: a term found in
    # only one document is a much stronger signal than one that appears
    # everywhere. This must happen BEFORE topic routing narrows the corpus.
    weights = {}
    for term in terms:
        docs_with = {c["document"] for c in corpus if _term_in(term, c["blob"])}
        weights[term] = EXCLUSIVE_WEIGHT if len(docs_with) == 1 else 1

    # Topic routing: when the question unambiguously belongs to one department,
    # search only that department's document. This prevents answering a devices
    # question from the finance document (anti-blending, agents.md).
    department = _detect_department(question)
    if department:
        allowed_docs = {d for d, t in DOC_TEAMS.items() if t == department}
        routed = [c for c in corpus if c["document"] in allowed_docs]
        if not routed:
            return _build_refusal(question)
        candidates_pool = routed
    else:
        candidates_pool = corpus

    candidates = []
    for entry in candidates_pool:
        hits = []
        score = 0
        exact_count = 0
        for t in terms:
            if not _term_in(t, entry["blob"]):
                continue
            exact = any(r in entry["tokens"] for r in _term_roots(t))
            # A stem match ("installed" for "install") is weaker evidence than
            # the question's own word — and much weaker when it is really a
            # different compound word ("networks" containing "work").
            value = weights[t] if exact else max(1, math.ceil(weights[t] / 2))
            hits.append(t)
            score += value
            exact_count += 1 if exact else 0
        if hits:
            candidates.append({
                **entry,
                "hits": hits,
                "score": score,
                "n_terms": len(hits),
                "exact_hits": exact_count,
                "exact_ratio": round(exact_count / len(hits), 3),
            })

    # A lone generic word must never surface an answer (anti-hallucination gate).
    # Exception: one document-EXCLUSIVE term (weight 3) is strong enough evidence
    # to route on its own.
    # Evidence-strength gate: either several corroborating terms (strong score)
    # or one document-exclusive term. A couple of generic word overlaps must
    # never produce a confident answer.
    eligible = [
        c for c in candidates
        if (c["score"] >= STRONG_SCORE and c["n_terms"] >= MIN_TERMS)
        or (c["score"] >= EXCLUSIVE_BYPASS_SCORE and any(weights[t] >= EXCLUSIVE_WEIGHT for t in c["hits"]))
    ]
    if not eligible:
        return _build_refusal(question)

    top_score = max(c["score"] for c in eligible)
    # Near-top evidence in ANOTHER document counts as a blend risk.
    cutoff = math.ceil(top_score * BLEND_MARGIN)
    leaders = [c for c in eligible if c["score"] >= cutoff]

    if len({c["document"] for c in leaders}) > 1:
        # Conflicting evidence across documents: refusing beats blending.
        return _build_refusal(question)

    best = sorted(
        leaders,
        key=lambda c: (
            -c["score"],  # strongest evidence first
            -c["exact_ratio"],  # then precision: the question's own words
            -c["n_terms"],
            tuple(int(p) for p in c["section"].split(".")),
        ),
    )[0]
    answer = f'{best["document"]} §{best["section"]}: "{best["text"]}"'

    lowered_answer = answer.lower()
    if any(h in lowered_answer for h in HEDGING_PHRASES):
        return _build_refusal(question)

    return {
        "answer": answer,
        "source": {"document": best["document"], "section": best["section"]},
        "refused": False,
    }


def main():
    print("=" * 64)
    print("UC-X — Ask My Documents")
    print("Sources: policy_hr_leave.txt, policy_it_acceptable_use.txt,")
    print("         policy_finance_reimbursement.txt")
    print("Type a question, or 'quit' to exit.")
    print("=" * 64)

    index = retrieve_documents()
    loaded = sum(len(d["sections"]) for d in index.values())
    print(f"Indexed {len(index)} documents, {loaded} sections.\n")

    while True:
        try:
            question = input("Ask> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            print("Goodbye.")
            break

        result = answer_question(question, index)
        if result["refused"]:
            print(f"[REFUSAL]\n{result['answer']}\n")
        else:
            src = result["source"]
            print(f"[{src['document']} §{src['section']}]\n{result['answer']}\n")


if __name__ == "__main__":
    main()
