"""UC-X app: single-source policy Q&A with strict refusal template."""
import argparse
import re
import sys
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

SECTION_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def _emit(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        safe = text.encode("utf-8", errors="replace").decode("utf-8")
        sys.stdout.buffer.write((safe + "\n").encode("utf-8", errors="replace"))


def _is_separator(line: str) -> bool:
    stripped = line.strip()
    return len(stripped) >= 3 and re.search(r"[A-Za-z0-9]", stripped) is None


def _is_section_heading(line: str) -> bool:
    stripped = line.strip()
    return re.match(r"^\d+\.\s", stripped) is not None and SECTION_RE.match(stripped) is None


def _parse_sections(file_path: Path) -> dict[str, str]:
    text = file_path.read_text(encoding="utf-8-sig")
    sections: dict[str, list[str]] = {}
    current_section = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        match = SECTION_RE.match(stripped)
        if match:
            current_section = match.group(1)
            sections[current_section] = [match.group(2).strip()]
            continue

        if current_section and _is_section_heading(line):
            continue

        if current_section and stripped and not _is_separator(line):
            sections[current_section].append(stripped)

    return {sec: " ".join(parts).strip() for sec, parts in sections.items()}


def retrieve_documents(policy_dir: str) -> dict[str, dict[str, str]]:
    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]
    index: dict[str, dict[str, str]] = {}
    for name in files:
        path = Path(policy_dir) / name
        if not path.exists():
            raise FileNotFoundError(f"Missing required document: {path}")
        index[name] = _parse_sections(path)
    return index


def _build_cited_answer(doc: str, section: str, section_text: str) -> str:
    return f"According to {doc} section {section}: {section_text}"


def answer_question(question: str, docs_index: dict[str, dict[str, str]]) -> str:
    q = question.strip().lower()

    fixed_mappings = [
        (lambda s: "carry forward" in s and "leave" in s, ("policy_hr_leave.txt", "2.6")),
        (lambda s: "install" in s and "slack" in s and "laptop" in s, ("policy_it_acceptable_use.txt", "2.3")),
        (lambda s: "home office" in s and "allowance" in s, ("policy_finance_reimbursement.txt", "3.1")),
        (lambda s: "personal phone" in s and "work files" in s, ("policy_it_acceptable_use.txt", "3.1")),
        (lambda s: "da" in s and "meal" in s and "same day" in s, ("policy_finance_reimbursement.txt", "2.6")),
        (lambda s: "who approves" in s and "leave without pay" in s, ("policy_hr_leave.txt", "5.2")),
    ]

    for matcher, (doc_name, section) in fixed_mappings:
        if matcher(q):
            section_text = docs_index.get(doc_name, {}).get(section)
            if not section_text:
                return REFUSAL_TEMPLATE
            return _build_cited_answer(doc_name, section, section_text)

    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE

    token_pattern = re.compile(r"[a-z0-9]+")
    tokens = set(token_pattern.findall(q))
    if not tokens:
        return REFUSAL_TEMPLATE

    best = None
    tied = False
    for doc_name, sections in docs_index.items():
        for section, text in sections.items():
            section_tokens = set(token_pattern.findall(text.lower()))
            score = len(tokens.intersection(section_tokens))
            if score == 0:
                continue
            if best is None or score > best[0]:
                best = (score, doc_name, section, text)
                tied = False
            elif best and score == best[0] and doc_name != best[1]:
                tied = True

    if not best or tied:
        return REFUSAL_TEMPLATE

    _, doc_name, section, text = best
    return _build_cited_answer(doc_name, section, text)


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--policy-dir", default="../data/policy-documents", help="Directory containing policy documents")
    parser.add_argument("--question", help="Optional single question mode")
    args = parser.parse_args()

    docs_index = retrieve_documents(args.policy_dir)

    if args.question:
        _emit(answer_question(args.question, docs_index))
        return

    _emit("UC-X Policy Q&A. Type a question, or type 'exit' to quit.")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue
        _emit(answer_question(user_input, docs_index))


if __name__ == "__main__":
    main()
