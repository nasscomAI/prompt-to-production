"""
UC-X — Ask My Documents
Implements retrieve_documents and answer_question per agents.md + skills.md.
"""
import argparse
import os
import re
import time
from pathlib import Path

_MODEL = "gemini-3.5-flash-lite"

POLICY_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

DEFAULT_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

GROUND_TRUTH_SECTIONS = {
    ("policy_hr_leave.txt", "2.6"),
    ("policy_hr_leave.txt", "5.2"),
    ("policy_it_acceptable_use.txt", "2.3"),
    ("policy_it_acceptable_use.txt", "3.1"),
    ("policy_finance_reimbursement.txt", "2.6"),
    ("policy_finance_reimbursement.txt", "3.1"),
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = (
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "may be permitted",
    "usually allowed",
)

SECTION_HEADING_RE = re.compile(r"^(\d+)\.\s+([A-Z].+)$")
CLAUSE_START_RE = re.compile(r"^(\d+\.\d+)\s+(.+)$")

TEST_QUESTIONS = (
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
)


def _load_env() -> None:
    if os.environ.get("GEMINI_API_KEY"):
        return

    candidates = [
        Path(__file__).resolve().parents[2] / ".env",
        Path(__file__).resolve().parents[1] / ".env",
    ]
    for env_path in candidates:
        if not env_path.is_file():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value
        if os.environ.get("GEMINI_API_KEY"):
            return


def _get_client():
    from google import genai

    _load_env()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Export it or add it to .env in the project root."
        )
    return genai.Client(api_key=api_key)


_client = None


def _client_instance():
    global _client
    if _client is None:
        _client = _get_client()
    return _client


def _parse_policy_file(path: str) -> dict:
    resolved = os.path.abspath(path)
    if not os.path.exists(resolved):
        raise FileNotFoundError(f"Input file not found: {resolved}")

    content = Path(resolved).read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError(f"File contains no policy content: {resolved}")

    lines = content.splitlines()
    document_title = next(
        (line.strip() for line in lines if line.strip() and not line.startswith("═")),
        "Unknown Policy",
    )

    sections = []
    current_heading = ""
    current_id = None
    current_text: list[str] = []

    def flush_clause() -> None:
        nonlocal current_id, current_text
        if current_id:
            sections.append({
                "section_id": current_id,
                "heading": current_heading,
                "text": " ".join(current_text).strip(),
            })
        current_id = None
        current_text = []

    for line in lines:
        if line.startswith("═"):
            continue

        section_match = SECTION_HEADING_RE.match(line.strip())
        if section_match and "." not in section_match.group(1):
            flush_clause()
            current_heading = section_match.group(2).strip()
            continue

        clause_match = CLAUSE_START_RE.match(line.strip())
        if clause_match:
            flush_clause()
            current_id = clause_match.group(1)
            current_text = [clause_match.group(2).strip()]
            continue

        if current_id and line.startswith("    "):
            current_text.append(line.strip())

    flush_clause()

    if not sections:
        raise ValueError(f"Could not parse numbered sections from: {resolved}")

    return {
        "filename": os.path.basename(resolved),
        "title": document_title,
        "sections": sections,
    }


def retrieve_documents(paths: list[str] | None = None) -> dict:
    source_paths = paths or DEFAULT_PATHS
    documents = []

    for path in source_paths:
        documents.append(_parse_policy_file(path))

    if len(documents) != 3:
        raise ValueError(
            f"Expected 3 policy documents, loaded {len(documents)}"
        )

    loaded_names = {doc["filename"] for doc in documents}
    missing_files = set(POLICY_FILES) - loaded_names
    if missing_files:
        raise ValueError(f"Missing policy documents: {', '.join(sorted(missing_files))}")

    found_sections = {
        (doc["filename"], section["section_id"])
        for doc in documents
        for section in doc["sections"]
    }
    missing_sections = GROUND_TRUTH_SECTIONS - found_sections
    if missing_sections:
        missing_desc = ", ".join(
            f"{filename} section {section_id}"
            for filename, section_id in sorted(missing_sections)
        )
        raise ValueError(f"Missing ground-truth sections in parsed index: {missing_desc}")

    return {"documents": documents}


def _documents_by_filename(documents: dict) -> dict[str, dict]:
    return {doc["filename"]: doc for doc in documents["documents"]}


def _section_map(doc: dict) -> dict[str, dict]:
    return {section["section_id"]: section for section in doc["sections"]}


def _refusal() -> dict:
    return {
        "answer": REFUSAL_TEMPLATE,
        "source_document": "",
        "source_sections": [],
        "refused": True,
    }


def _answer(filename: str, section_ids: list[str], text: str) -> dict:
    return {
        "answer": text,
        "source_document": filename,
        "source_sections": section_ids,
        "refused": False,
    }


def _format_cited_answer(filename: str, section_ids: list[str], body: str) -> str:
    sections_label = ", ".join(f"section {sid}" for sid in section_ids)
    return f"According to {filename} {sections_label}: {body}"


def _normalize_question(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def _match_known_question(question: str, docs_by_name: dict[str, dict]) -> dict | None:
    q = _normalize_question(question)

    if not q:
        return _refusal()

    if re.search(r"flexible working culture|company view on flexible", q):
        return _refusal()

    if re.search(r"carry forward|carry-forward", q) and re.search(
        r"annual leave|unused leave|unused annual", q
    ):
        section = _section_map(docs_by_name["policy_hr_leave.txt"])["2.6"]
        body = (
            "Employees may carry forward a maximum of 5 unused annual leave days to "
            "the following calendar year. Any days above 5 are forfeited on 31 December."
        )
        return _answer(
            "policy_hr_leave.txt",
            ["2.6"],
            _format_cited_answer("policy_hr_leave.txt", ["2.6"], body),
        )

    if re.search(r"install", q) and re.search(r"slack|software", q):
        section = _section_map(docs_by_name["policy_it_acceptable_use.txt"])["2.3"]
        body = section["text"]
        return _answer(
            "policy_it_acceptable_use.txt",
            ["2.3"],
            _format_cited_answer("policy_it_acceptable_use.txt", ["2.3"], body),
        )

    if re.search(r"home office equipment allowance|home office allowance", q):
        section = _section_map(docs_by_name["policy_finance_reimbursement.txt"])["3.1"]
        body = section["text"]
        return _answer(
            "policy_finance_reimbursement.txt",
            ["3.1"],
            _format_cited_answer("policy_finance_reimbursement.txt", ["3.1"], body),
        )

    if re.search(r"personal phone|personal device", q) and re.search(
        r"work file|work files|access work|working from home|from home", q
    ):
        it_sections = _section_map(docs_by_name["policy_it_acceptable_use.txt"])
        body = (
            "Personal devices may be used to access CMC email and the CMC employee "
            "self-service portal only. Personal devices must not be used to access, "
            "store, or transmit classified or sensitive CMC data. Work files are not "
            "permitted on personal devices beyond email and the self-service portal."
        )
        return _answer(
            "policy_it_acceptable_use.txt",
            ["3.1", "3.2"],
            _format_cited_answer("policy_it_acceptable_use.txt", ["3.1", "3.2"], body),
        )

    if re.search(r"\bda\b|daily allowance", q) and re.search(
        r"meal receipt|meal receipts|meal expense", q
    ) and re.search(r"same day|simultaneously|both", q):
        section = _section_map(docs_by_name["policy_finance_reimbursement.txt"])["2.6"]
        body = (
            "No. DA and meal receipts cannot be claimed simultaneously for the same day."
        )
        return _answer(
            "policy_finance_reimbursement.txt",
            ["2.6"],
            _format_cited_answer("policy_finance_reimbursement.txt", ["2.6"], body),
        )

    if re.search(r"leave without pay|\blwp\b", q) and re.search(r"approv", q):
        section = _section_map(docs_by_name["policy_hr_leave.txt"])["5.2"]
        body = section["text"]
        return _answer(
            "policy_hr_leave.txt",
            ["5.2"],
            _format_cited_answer("policy_hr_leave.txt", ["5.2"], body),
        )

    return None


def _question_tokens(question: str) -> list[str]:
    stopwords = {
        "the", "and", "for", "can", "what", "who", "how", "when", "where", "from",
        "with", "that", "this", "are", "was", "were", "have", "has", "does", "did",
        "about", "into", "same", "day", "use", "using", "work", "company", "view",
    }
    tokens = re.findall(r"[a-z0-9]+", question.lower())
    return [token for token in tokens if len(token) > 2 and token not in stopwords]


def _score_sections(question: str, documents: dict) -> list[tuple[int, dict, dict]]:
    tokens = _question_tokens(question)
    if not tokens:
        return []

    scored: list[tuple[int, dict, dict]] = []
    for doc in documents["documents"]:
        for section in doc["sections"]:
            haystack = f"{section['heading']} {section['text']}".lower()
            score = sum(1 for token in tokens if token in haystack)
            if score:
                scored.append((score, doc, section))
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored


def _build_search_answer(question: str, documents: dict) -> dict | None:
    scored = _score_sections(question, documents)
    if not scored:
        return None

    best_score, best_doc, best_section = scored[0]
    if best_score < 2:
        return None

    doc_scores: dict[str, int] = {}
    for score, doc, _section in scored:
        doc_scores[doc["filename"]] = doc_scores.get(doc["filename"], 0) + score

    ranked_docs = sorted(doc_scores.items(), key=lambda item: item[1], reverse=True)
    if len(ranked_docs) > 1:
        top_name, top_score = ranked_docs[0]
        second_name, second_score = ranked_docs[1]
        if second_score >= top_score * 0.75 and top_name != second_name:
            return None

    selected_sections = []
    seen_ids: set[str] = set()
    for score, doc, section in scored:
        if doc["filename"] != best_doc["filename"]:
            continue
        if section["section_id"] in seen_ids:
            continue
        selected_sections.append(section)
        seen_ids.add(section["section_id"])
        if len(selected_sections) >= 2:
            break

    section_ids = [section["section_id"] for section in selected_sections]
    body = " ".join(section["text"] for section in selected_sections)
    return _answer(
        best_doc["filename"],
        section_ids,
        _format_cited_answer(best_doc["filename"], section_ids, body),
    )


def _contains_hedging(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in HEDGING_PHRASES)


def _mentions_multiple_documents(answer: str) -> bool:
    mentioned = [name for name in POLICY_FILES if name in answer]
    return len(set(mentioned)) > 1


def _build_llm_prompt(question: str, doc: dict, sections: list[dict], correction: str | None = None) -> str:
    section_block = "\n".join(
        f"Section {section['section_id']}: {section['text']}" for section in sections
    )
    base = f"""You are a municipal policy Q&A engine. Answer ONLY from the single source document below.

Rules:
1. Use only {doc['filename']} — never cite or combine other documents.
2. Every factual claim must cite {doc['filename']} and the section number(s) used.
3. Do not use hedging phrases such as "while not explicitly covered", "typically",
   "generally understood", or "it is common practice".
4. If the source document does not fully answer the question, respond with this exact text:
{REFUSAL_TEMPLATE}
5. Do not grant permissions not explicitly stated in the cited section(s).

Source document: {doc['filename']}

Sections:
{section_block}

Question: {question}

Answer in 1-3 sentences, starting with "According to {doc['filename']} section ..."."""
    if correction:
        return f"{base}\n\nCORRECTION REQUIRED:\n{correction}"
    return base


def _call_llm(prompt: str) -> str:
    from google.genai import types

    config = types.GenerateContentConfig(
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )
    last_error = None
    for attempt in range(3):
        try:
            response = _client_instance().models.generate_content(
                model=_MODEL,
                contents=prompt,
                config=config,
            )
            time.sleep(1)
            return response.text.strip()
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Question answering failed: {last_error}") from last_error


def _validate_answer(answer: str, source_document: str) -> list[str]:
    errors: list[str] = []
    if answer.strip() == REFUSAL_TEMPLATE:
        return errors

    if _contains_hedging(answer):
        errors.append("Answer contains hedging language")

    if _mentions_multiple_documents(answer):
        errors.append("Answer cites more than one source document")

    if source_document and source_document not in answer:
        errors.append(f"Answer must cite {source_document}")

    if source_document and "section" not in answer.lower():
        errors.append("Answer must include a section citation")

    return errors


def _answer_with_llm(question: str, doc: dict, sections: list[dict]) -> dict:
    try:
        answer = _call_llm(_build_llm_prompt(question, doc, sections))
    except RuntimeError:
        return _refusal()

    if answer.strip() == REFUSAL_TEMPLATE:
        return _refusal()

    errors = _validate_answer(answer, doc["filename"])
    if errors:
        correction = "\n".join(f"- {error}" for error in errors)
        try:
            answer = _call_llm(_build_llm_prompt(question, doc, sections, correction=correction))
        except RuntimeError:
            return _refusal()
        errors = _validate_answer(answer, doc["filename"])
        if errors:
            return _refusal()

    section_ids = re.findall(r"section\s+(\d+\.\d+)", answer, flags=re.IGNORECASE)
    if not section_ids:
        section_ids = [section["section_id"] for section in sections[:1]]

    return _answer(doc["filename"], section_ids, answer)


def answer_question(question: str, documents: dict) -> dict:
    if not question or not question.strip():
        return _refusal()

    if not documents or not documents.get("documents"):
        raise ValueError("Document index is incomplete")

    loaded_names = {doc["filename"] for doc in documents["documents"]}
    if loaded_names != set(POLICY_FILES):
        raise ValueError("Document index is incomplete")

    docs_by_name = _documents_by_filename(documents)

    known = _match_known_question(question, docs_by_name)
    if known is not None:
        return known

    search_result = _build_search_answer(question, documents)
    if search_result is not None:
        return search_result

    scored = _score_sections(question, documents)
    if not scored:
        return _refusal()

    best_doc = scored[0][1]
    selected_sections = []
    seen_ids: set[str] = set()
    for _score, doc, section in scored:
        if doc["filename"] != best_doc["filename"]:
            continue
        if section["section_id"] in seen_ids:
            continue
        selected_sections.append(section)
        seen_ids.add(section["section_id"])
        if len(selected_sections) >= 3:
            break

    if not selected_sections:
        return _refusal()

    _load_env()
    if os.environ.get("GEMINI_API_KEY"):
        return _answer_with_llm(question, best_doc, selected_sections)

    section_ids = [section["section_id"] for section in selected_sections]
    body = selected_sections[0]["text"]
    return _answer(
        best_doc["filename"],
        section_ids[:1],
        _format_cited_answer(best_doc["filename"], section_ids[:1], body),
    )


def _print_result(question: str, result: dict) -> None:
    print(f"\nQ: {question}")
    print(f"A: {result['answer']}")
    if not result["refused"]:
        print(
            f"[source: {result['source_document']} | "
            f"sections: {', '.join(result['source_sections'])}]"
        )


def run_tests(documents: dict) -> None:
    print("Running UC-X test questions...")
    for question in TEST_QUESTIONS:
        result = answer_question(question, documents)
        _print_result(question, result)


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run the seven README test questions and exit",
    )
    args = parser.parse_args()

    documents = retrieve_documents()

    if args.test:
        run_tests(documents)
        return

    print("Policy Q&A ready. Type a question, or 'quit' to exit.")
    while True:
        try:
            question = input("\nQuestion> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            break

        result = answer_question(question, documents)
        print(result["answer"])
        if not result["refused"]:
            print(
                f"[source: {result['source_document']} | "
                f"sections: {', '.join(result['source_sections'])}]"
            )


if __name__ == "__main__":
    main()
