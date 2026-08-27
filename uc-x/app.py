"""
UC-X — Ask My Documents

Single-source policy Q&A over three CMC policy files that enforces the
contracts in agents.md:
  - Every answer cites exactly one document and one clause number
  - No cross-document blending (top-1 vs top-2 tie-margin guard)
  - No hedging phrases (post-hoc string check)
  - Below-confidence queries → verbatim refusal template
"""
import argparse
import os
import re
import sys
from collections import Counter
from typing import Dict, List, Optional, Tuple

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact the relevant "
    "department for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered", "typically", "generally understood",
    "it is common practice", "as a rule", "in most cases", "usually",
    "based on general knowledge",
]

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "am", "be", "been",
    "being", "and", "or", "of", "to", "for", "in", "on", "at", "by",
    "from", "with", "as", "can", "i", "my", "we", "our", "you", "your",
    "if", "when", "what", "who", "how", "does", "do", "did", "will",
    "would", "should", "may", "might", "have", "has", "had", "this",
    "that", "these", "those", "not", "no", "yes", "there", "it", "its",
    "any", "some", "all", "same", "day", "days", "one",
}

EQUIVALENCE_CLASSES = [
    ["approve", "approves", "approved", "approving", "approval", "approvals"],
    ["phone", "phones", "device", "devices", "laptop", "laptops",
     "tablet", "mobile"],
    ["install", "installs", "installed", "installing", "installation",
     "software", "app", "apps", "application", "applications",
     "slack", "zoom", "teams", "whatsapp"],
    ["work", "works", "working", "worked", "workplace"],
    ["leave", "leaves", "vacation", "pto"],
    ["pay", "pays", "paid", "payment", "salary"],
    ["carry", "carries", "carrying", "carried"],
    ["home", "homes", "wfh"],
    ["file", "files", "data"],
    ["claim", "claims", "claimed", "claiming"],
    ["receipt", "receipts"],
    ["meal", "meals"],
    ["access", "accesses", "accessed", "accessing"],
    ["allowance", "allowances", "reimbursement", "reimbursements"],
]

TOKEN_TO_CANONICAL: Dict[str, str] = {
    tok: cls[0] for cls in EQUIVALENCE_CLASSES for tok in cls
}

SECTION_HEADER_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s()/&\-]+)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
WORD_RE = re.compile(r"[a-z0-9]+")


def _parse_policy(path: str, filename: str) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    clauses: List[dict] = []
    section_num = ""
    section_title = ""
    current_clause: Optional[dict] = None

    for raw in source.splitlines():
        line = raw.rstrip()
        if not line or set(line.strip()) <= {"═", "=", "-"}:
            continue

        stripped = line.strip()
        sec_match = SECTION_HEADER_RE.match(stripped)
        cls_match = CLAUSE_RE.match(stripped)

        if sec_match and not cls_match:
            if current_clause:
                clauses.append(current_clause)
                current_clause = None
            section_num = sec_match.group(1)
            section_title = sec_match.group(2).strip()
        elif cls_match:
            if current_clause:
                clauses.append(current_clause)
            current_clause = {
                "filename": filename,
                "section_num": section_num,
                "section_title": section_title,
                "clause_num": cls_match.group(1),
                "text": cls_match.group(2).strip(),
            }
        else:
            if current_clause:
                current_clause["text"] = (
                    current_clause["text"] + " " + stripped
                ).strip()

    if current_clause:
        clauses.append(current_clause)

    return clauses


def retrieve_documents(dir_path: str) -> List[dict]:
    all_clauses: List[dict] = []
    for name in POLICY_FILES:
        full = os.path.join(dir_path, name)
        if not os.path.exists(full):
            raise FileNotFoundError(full)
        all_clauses.extend(_parse_policy(full, name))
    return all_clauses


def _tokens(text: str) -> List[str]:
    return [
        TOKEN_TO_CANONICAL.get(w, w)
        for w in WORD_RE.findall(text.lower())
        if w not in STOPWORDS
    ]


def _contains_hedging(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in HEDGING_PHRASES)


def _score_clause(question_tokens: set, clause: dict) -> Tuple[int, int]:
    """Returns (unique_match_count, ranking_score).
    ranking_score = 3 * (title matches) + text TF for question tokens NOT in title.
    Rationale: title selects the section, so among siblings (which share a title)
    the discriminator is text matches on tokens the title doesn't already cover.
    """
    title_tokens = set(_tokens(clause["section_title"]))
    text_token_list = _tokens(clause["text"])
    text_tokens = set(text_token_list)
    text_counter = Counter(text_token_list)

    title_hits = question_tokens & title_tokens
    text_hits = question_tokens & text_tokens
    unique_matches = title_hits | text_hits

    residual_tokens = question_tokens - title_hits
    residual_tf = sum(text_counter[t] for t in (residual_tokens & text_tokens))

    ranking_score = len(title_hits) * 3 + residual_tf
    return len(unique_matches), ranking_score


def answer_question(question: str, clauses: List[dict],
                    confidence_threshold: int = 2,
                    tie_margin: int = 1) -> str:
    if not clauses:
        raise RuntimeError("No clauses indexed — call retrieve_documents first.")

    q_tokens = set(_tokens(question))
    if not q_tokens:
        return REFUSAL_TEMPLATE

    scored: List[Tuple[int, int, dict]] = [
        (*_score_clause(q_tokens, c), c) for c in clauses
    ]
    scored.sort(key=lambda t: (t[1], t[0]), reverse=True)

    top_match_count, top_weighted, top_clause = scored[0]
    if top_match_count < confidence_threshold:
        return REFUSAL_TEMPLATE

    if len(scored) >= 2:
        second_match_count, second_weighted, second_clause = scored[1]
        different_docs = second_clause["filename"] != top_clause["filename"]
        close_call = (top_weighted - second_weighted) <= tie_margin
        if different_docs and close_call and second_match_count >= confidence_threshold:
            return REFUSAL_TEMPLATE

    answer = (
        f"{top_clause['text']}\n"
        f"(source: {top_clause['filename']} · section {top_clause['clause_num']})"
    )

    if _contains_hedging(answer):
        return REFUSAL_TEMPLATE

    return answer


TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def _run_test_questions(clauses: List[dict]) -> None:
    for i, q in enumerate(TEST_QUESTIONS, start=1):
        print(f"\nQ{i}: {q}")
        print(answer_question(q, clauses))
        print("-" * 60)


def _repl(clauses: List[dict]) -> None:
    print("Ask My Documents — CMC policy Q&A")
    print(f"Indexed {len(clauses)} clauses across {len(POLICY_FILES)} documents.")
    print("Type your question, or 'quit' to exit.\n")
    while True:
        try:
            q = input("? ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q:
            continue
        if q.lower() in ("quit", "exit", "q"):
            break
        print()
        print(answer_question(q, clauses))
        print()


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs", default="../data/policy-documents",
                        help="Path to policy documents directory")
    parser.add_argument("--questions", action="store_true",
                        help="Run the 7 canonical test questions instead of REPL")
    args = parser.parse_args()

    clauses = retrieve_documents(args.docs)

    if args.questions:
        _run_test_questions(clauses)
    else:
        _repl(clauses)


if __name__ == "__main__":
    main()
