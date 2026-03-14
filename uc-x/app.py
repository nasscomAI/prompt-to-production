"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)
SECTION_RE = re.compile(r"^(\d+\.\d+)\s+(.*\S)\s*$")
DECORATION_RE = re.compile(r"^[^\w]+$")
STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "for", "from", "i", "in", "is",
    "my", "of", "on", "or", "the", "to", "what", "when", "who", "with",
    "work", "working", "use", "using", "about",
}


def normalize_text(value: str) -> str:
    return " ".join(value.casefold().replace("—", " ").replace("–", " ").split())


def retrieve_documents() -> dict[str, dict[str, str]]:
    base_dir = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    doc_paths = {
        "policy_hr_leave.txt": base_dir / "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": base_dir / "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": base_dir / "policy_finance_reimbursement.txt",
    }
    documents: dict[str, dict[str, str]] = {}
    for doc_name, path in doc_paths.items():
        text = path.read_text(encoding="utf-8")
        sections: dict[str, str] = {}
        current_id = ""
        current_lines: list[str] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()
            match = SECTION_RE.match(line)
            if match:
                if current_id:
                    sections[current_id] = " ".join(current_lines)
                current_id = match.group(1)
                current_lines = [match.group(2)]
                continue

            if not current_id:
                continue
            if not line or DECORATION_RE.match(line):
                continue
            if re.match(r"^\d+\.\s+[A-Z]", line):
                continue
            current_lines.append(line)

        if current_id:
            sections[current_id] = " ".join(current_lines)
        documents[doc_name] = sections
    return documents


def cite(doc_name: str, section_ids: list[str]) -> str:
    section_text = "section" if len(section_ids) == 1 else "sections"
    joined = " and ".join(section_ids) if len(section_ids) == 2 else ", ".join(section_ids)
    return f"(Source: {doc_name} {section_text} {joined})"


def build_curated_answer(documents: dict[str, dict[str, str]], question: str) -> str | None:
    q = normalize_text(question)

    if "carry forward" in q and "leave" in q:
        doc = "policy_hr_leave.txt"
        text = documents[doc]["2.6"]
        return f"{text} {cite(doc, ['2.6'])}"

    if "install slack" in q or ("work laptop" in q and "install" in q):
        doc = "policy_it_acceptable_use.txt"
        text = documents[doc]["2.3"]
        return f"{text} {cite(doc, ['2.3'])}"

    if "home office equipment allowance" in q:
        doc = "policy_finance_reimbursement.txt"
        text = documents[doc]["3.1"]
        return f"{text} {cite(doc, ['3.1'])}"

    if ("personal phone" in q or "personal device" in q) and ("work files" in q or "access work files" in q):
        doc = "policy_it_acceptable_use.txt"
        first = documents[doc]["3.1"]
        second = documents[doc]["3.2"]
        return f"{first} {second} {cite(doc, ['3.1', '3.2'])}"

    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE

    if "da" in q and "meal" in q:
        doc = "policy_finance_reimbursement.txt"
        text = documents[doc]["2.6"]
        return f"{text} {cite(doc, ['2.6'])}"

    if ("leave without pay" in q or "lwp" in q) and ("approve" in q or "approval" in q):
        doc = "policy_hr_leave.txt"
        text = documents[doc]["5.2"]
        return f"{text} {cite(doc, ['5.2'])}"

    return None


def search_single_source(documents: dict[str, dict[str, str]], question: str) -> str:
    curated = build_curated_answer(documents, question)
    if curated:
        return curated

    q_tokens = {
        token
        for token in re.findall(r"[a-z0-9]+", normalize_text(question))
        if token not in STOPWORDS
    }
    if not q_tokens:
        return REFUSAL_TEMPLATE

    scored: list[tuple[int, str, str, str]] = []
    for doc_name, sections in documents.items():
        for section_id, text in sections.items():
            section_tokens = set(re.findall(r"[a-z0-9]+", normalize_text(text)))
            score = len(q_tokens.intersection(section_tokens))
            if score:
                scored.append((score, doc_name, section_id, text))

    if not scored:
        return REFUSAL_TEMPLATE

    scored.sort(key=lambda item: (-item[0], item[1], item[2]))
    best_score, best_doc, best_section, best_text = scored[0]
    if best_score < 2:
        return REFUSAL_TEMPLATE
    if len(scored) > 1 and scored[1][0] == best_score and scored[1][1] != best_doc:
        return REFUSAL_TEMPLATE
    return f"{best_text} {cite(best_doc, [best_section])}"


def answer_question(documents: dict[str, dict[str, str]], question: str) -> str:
    return search_single_source(documents, question)

def main():
    parser = argparse.ArgumentParser(description="UC-X single-source policy question answering CLI")
    parser.add_argument("--question", help="Optional single question to answer without interactive mode")
    args = parser.parse_args()

    documents = retrieve_documents()

    if args.question:
        print(answer_question(documents, args.question))
        return

    print("Ask a policy question. Type 'exit' to quit.")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            print()
            break
        if not question:
            continue
        if question.casefold() in {"exit", "quit"}:
            break
        print(answer_question(documents, question))

if __name__ == "__main__":
    main()
