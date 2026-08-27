"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

PROHIBITED_HEDGING = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]


def _normalize_space(text: str) -> str:
    return " ".join((text or "").split())


def _parse_sections(text: str):
    section_pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
    sections = []
    current_id = None
    current_lines = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        match = section_pattern.match(line)
        if match:
            if current_id is not None:
                sections.append({"section_id": current_id, "section_text": _normalize_space(" ".join(current_lines))})
            current_id = match.group(1)
            current_lines = [match.group(2).strip()]
            continue

        if current_id is None:
            continue

        stripped = line.strip()
        if not stripped:
            continue
        if set(stripped) == {"═"}:
            continue
        if re.match(r"^\d+\.\s+", stripped):
            continue
        if not re.search(r"[A-Za-z0-9]", stripped):
            continue
        current_lines.append(stripped)

    if current_id is not None:
        sections.append({"section_id": current_id, "section_text": _normalize_space(" ".join(current_lines))})

    return sections


def retrieve_documents(document_paths: list) -> dict:
    """
    Load policy documents and index sections by document + section id.
    """
    documents_by_name = {}
    all_sections = []
    diagnostics = {}

    for path in document_paths:
        name = os.path.basename(path)
        try:
            with open(path, mode="r", encoding="utf-8") as infile:
                content = infile.read()
        except OSError as exc:
            raise RuntimeError(f"Failed to read document '{path}': {exc}") from exc

        sections = _parse_sections(content)
        parse_warning = ""
        if not sections:
            parse_warning = "No numbered sections parsed."

        document_info = {
            "document_name": name,
            "path": path,
            "content": content,
            "sections": sections,
            "sections_by_id": {sec["section_id"]: sec["section_text"] for sec in sections},
        }
        documents_by_name[name] = document_info
        diagnostics[name] = {"parse_warning": parse_warning, "section_count": len(sections)}

        for sec in sections:
            all_sections.append(
                {
                    "document_name": name,
                    "section_id": sec["section_id"],
                    "section_text": sec["section_text"],
                }
            )

    return {
        "documents_by_name": documents_by_name,
        "sections": all_sections,
        "diagnostics": diagnostics,
    }


def _build_single_source_answer(document_name: str, section_id: str, section_text: str) -> str:
    return f"{section_text} Source: {document_name} section {section_id}."


def answer_question(question: str, indexed_documents: dict) -> str:
    """
    Return single-source answer with citation, or exact refusal template.
    """
    q = _normalize_space((question or "").lower())
    if not q:
        return REFUSAL_TEMPLATE

    docs = indexed_documents.get("documents_by_name", {})

    def sec(doc_name: str, section_id: str):
        doc = docs.get(doc_name, {})
        return doc.get("sections_by_id", {}).get(section_id, "")

    # Deterministic single-source routing for known policy intents.
    if "carry forward" in q and "leave" in q:
        text = sec("policy_hr_leave.txt", "2.6")
        return _build_single_source_answer("policy_hr_leave.txt", "2.6", text) if text else REFUSAL_TEMPLATE

    if "install" in q and ("laptop" in q or "work laptop" in q or "corporate" in q):
        text = sec("policy_it_acceptable_use.txt", "2.3")
        return _build_single_source_answer("policy_it_acceptable_use.txt", "2.3", text) if text else REFUSAL_TEMPLATE

    if "home office" in q and "allowance" in q:
        text = sec("policy_finance_reimbursement.txt", "3.1")
        return _build_single_source_answer("policy_finance_reimbursement.txt", "3.1", text) if text else REFUSAL_TEMPLATE

    if "personal phone" in q and ("work files" in q or "working from home" in q or "from home" in q):
        text = sec("policy_it_acceptable_use.txt", "3.1")
        return _build_single_source_answer("policy_it_acceptable_use.txt", "3.1", text) if text else REFUSAL_TEMPLATE

    if "da" in q and "meal" in q:
        text = sec("policy_finance_reimbursement.txt", "2.6")
        return _build_single_source_answer("policy_finance_reimbursement.txt", "2.6", text) if text else REFUSAL_TEMPLATE

    if "leave without pay" in q or "lwp" in q:
        if "approve" in q or "approval" in q or "who" in q:
            text = sec("policy_hr_leave.txt", "5.2")
            return _build_single_source_answer("policy_hr_leave.txt", "5.2", text) if text else REFUSAL_TEMPLATE

    # Fallback lexical search with strict single-source gating.
    tokens = re.findall(r"[a-z0-9]+", q)
    tokens = [t for t in tokens if len(t) > 2]
    if not tokens:
        return REFUSAL_TEMPLATE

    scored = []
    for sec_row in indexed_documents.get("sections", []):
        section_text_lower = sec_row["section_text"].lower()
        score = sum(1 for t in tokens if t in section_text_lower)
        if score > 0:
            scored.append((score, sec_row))

    if not scored:
        return REFUSAL_TEMPLATE

    scored.sort(key=lambda x: x[0], reverse=True)
    top_score = scored[0][0]
    top_rows = [row for score, row in scored if score == top_score]
    doc_set = {row["document_name"] for row in top_rows}

    # Ambiguity across documents is refused to prevent cross-document blending.
    if len(doc_set) != 1:
        return REFUSAL_TEMPLATE

    best = top_rows[0]
    answer = _build_single_source_answer(best["document_name"], best["section_id"], best["section_text"])

    answer_lower = answer.lower()
    for phrase in PROHIBITED_HEDGING:
        if phrase in answer_lower:
            return REFUSAL_TEMPLATE

    return answer

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents CLI")
    parser.add_argument("--question", required=False, help="Optional single question mode")
    args = parser.parse_args()

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"))
    doc_paths = [os.path.join(base_dir, name) for name in DOC_FILES]
    indexed_documents = retrieve_documents(doc_paths)

    if args.question:
        print(answer_question(args.question, indexed_documents))
        return

    print("UC-X Ask My Documents")
    print("Type your question and press Enter. Type 'exit' to quit.")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() in {"exit", "quit"}:
            break

        print(answer_question(question, indexed_documents))
        print()

if __name__ == "__main__":
    main()
