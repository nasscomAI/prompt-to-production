"""UC-X — Ask My Documents."""

import argparse
import re
from pathlib import Path

DOCUMENTS = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)
REFUSAL = "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance."
CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.+)$")


def retrieve_documents(paths: dict[str, Path]) -> dict[str, list[tuple[str, str]]]:
    """Load each policy independently and preserve source/section boundaries."""
    index = {}
    for name in DOCUMENTS:
        path = paths[name]
        if not path.exists():
            raise FileNotFoundError(f"Required policy document not found: {path}")
        clauses = []
        current = None
        text_parts = []
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            match = CLAUSE_PATTERN.match(line)
            if match:
                if current is not None:
                    clauses.append((current, " ".join(text_parts)))
                current = match.group(1)
                text_parts = [match.group(2)]
            elif current is not None and line:
                text_parts.append(line)
        if current is not None:
            clauses.append((current, " ".join(text_parts)))
        index[name] = clauses
    return index


def _score(question: str, clause: str) -> int:
    stop = {"can", "i", "the", "what", "is", "my", "for", "from", "to", "and", "of", "on", "in", "a", "an"}
    q_words = {word for word in re.findall(r"[a-z0-9]+", question.lower()) if word not in stop and len(word) > 2}
    c_words = set(re.findall(r"[a-z0-9]+", clause.lower()))
    return len(q_words & c_words)


def answer_question(question: str, index: dict[str, list[tuple[str, str]]]) -> str:
    """Return a single-source answer with citation, or the exact refusal."""
    candidates = []
    for document, clauses in index.items():
        for section, text in clauses:
            score = _score(question, text)
            if score:
                candidates.append((score, document, section, text))
    if not candidates:
        return REFUSAL
    candidates.sort(reverse=True)
    best_score = candidates[0][0]
    best = [candidate for candidate in candidates if candidate[0] == best_score]
    if len({candidate[1] for candidate in best}) > 1:
        return REFUSAL
    _, document, section, text = best[0]
    return f"{text}\nSource: {document}, section {section}."


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-X policy document question answering")
    parser.add_argument("--data-dir", default="../data/policy-documents", help="Directory containing the three policy files")
    args = parser.parse_args()
    base = Path(args.data_dir)
    paths = {name: base / name for name in DOCUMENTS}
    index = retrieve_documents(paths)
    print("UC-X — Ask My Documents")
    print("Type a policy question. Type 'exit' to quit.")
    while True:
        try:
            question = input("Question: ").strip()
        except EOFError:
            break
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            print("Please enter a question.")
            continue
        print(answer_question(question, index))
        print()


if __name__ == "__main__":
    main()
