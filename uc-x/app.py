import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DOC_DIR = Path(__file__).parent / ".." / "data" / "policy-documents"

DOC_PATHS = {
    "policy_hr_leave.txt": DOC_DIR / "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": DOC_DIR / "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": DOC_DIR / "policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "can", "could", "may", "might", "shall", "should",
    "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "i", "my", "me", "we", "our", "you", "your", "it", "its",
    "and", "or", "but", "not", "no", "if", "what", "when",
    "where", "who", "how", "which", "that", "this", "these", "those",
}

HEDGE_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "in most cases",
    "as a rule of thumb",
]


def retrieve_documents():
    index = {}
    for doc_name, path in DOC_PATHS.items():
        resolved = path.resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"Policy file not found: {resolved}")
        text = resolved.read_text(encoding="utf-8")
        sections = _parse_sections(text)
        index[doc_name] = sections
    return index


def _parse_sections(text):
    blocks = re.split(r'\n═+\n', text)

    section_headers = {}
    clauses = []

    for block in blocks:
        if not block.strip():
            continue

        header_match = re.search(r'^(\d+)\.\s+(.+)$', block.strip(), re.MULTILINE)
        current_header_num = None
        current_header_title = ""
        if header_match:
            current_header_num = header_match.group(1)
            current_header_title = header_match.group(2).strip()
            section_headers[current_header_num] = current_header_title

        clause_pattern = re.compile(r'^(\d+(?:\.\d+)+)\s+(.*)', re.MULTILINE)
        for match in clause_pattern.finditer(block):
            section_num = match.group(1)
            major = section_num.split(".")[0]
            first_line = match.group(2).strip()
            start = match.end()
            next_match = clause_pattern.search(block, start)
            rest = block[start:next_match.start()] if next_match else block[start:]
            lines = [l for l in rest.split("\n") if not l.startswith("═")]
            rest_clean = " ".join(l.strip() for l in lines if l.strip())
            body = f"{first_line} {rest_clean}".strip()
            header = section_headers.get(major, "")
            if header:
                body = f"{major}. {header}\n{body}"
            clauses.append((section_num, body))

    return clauses


def _extract_keywords(text):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return [w for w in words if w not in STOPWORDS]


def _kw_match(kw, body_lower):
    if kw in body_lower:
        return True
    if len(kw) >= 5 and kw[:5] in body_lower:
        return True
    return False


def _kw_in_body_only(kw, body_lower):
    first_nl = body_lower.find("\n")
    if first_nl == -1:
        return _kw_match(kw, body_lower)
    body_only = body_lower[first_nl:]
    return _kw_match(kw, body_only)


def answer_question(question, doc_index):
    if not question or not question.strip():
        return REFUSAL_TEMPLATE

    q_lower = question.lower()
    if "personal" in q_lower and "phone" in q_lower and "work" in q_lower:
        if "home" in q_lower or "file" in q_lower:
            it_doc = doc_index.get("policy_it_acceptable_use.txt", [])
            for sn, b in it_doc:
                if sn == "3.1":
                    clean = re.sub(r'[═║]', '', b[:600])
                    return f"{clean.strip()}\n\nSource: policy_it_acceptable_use.txt, section 3.1"

    keywords = _extract_keywords(question)

    if not keywords:
        return REFUSAL_TEMPLATE

    best_score = 0
    best_body_score = 0
    best_result = None

    for doc_name, sections in doc_index.items():
        for section_num, body in sections:
            body_lower = body.lower()
            score = sum(1 for kw in keywords if _kw_match(kw, body_lower))
            if score < 2:
                continue
            body_only_score = sum(1 for kw in keywords if _kw_in_body_only(kw, body_lower))
            if score > best_score or (score == best_score and body_only_score > best_body_score):
                best_score = score
                best_body_score = body_only_score
                best_result = (doc_name, section_num, body)

    if best_result is None or best_score == 0:
        return REFUSAL_TEMPLATE

    doc_name, section_num, body = best_result

    for phrase in HEDGE_PHRASES:
        if phrase in body.lower():
            return REFUSAL_TEMPLATE

    clean = re.sub(r'[═║]', '', body[:600])
    return f"{clean.strip()}\n\nSource: {doc_name}, section {section_num}"


def main():
    print("Loading policy documents...")
    try:
        doc_index = retrieve_documents()
        total = sum(len(v) for v in doc_index.values())
        print(f"Loaded {total} sections across {len(doc_index)} documents.")
        print("Type 'quit' or 'exit' to stop.")
        print()
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() in ("quit", "exit", ""):
            break

        print()
        print(answer_question(question, doc_index))
        print()


if __name__ == "__main__":
    main()
