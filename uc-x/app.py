"""
UC-X — Ask My Documents
Interactive policy Q&A that answers strictly from three CMC policy documents.
Single-source answers with citation. Refusal template when not covered.
"""
import os
import re

POLICY_FILES = {
    "policy_hr_leave.txt":           "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt":  "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department for guidance."
)

SCORE_THRESHOLD = 2

STOP_WORDS = {
    "i", "can", "a", "the", "is", "are", "what", "how", "when", "where",
    "my", "me", "for", "on", "of", "to", "in", "do", "does", "at", "be",
    "was", "with", "from", "an", "and", "or", "if", "it", "this", "that",
    "have", "has", "will", "would", "should", "could", "we", "our", "any",
    "get", "use", "used", "using", "about", "than", "more", "all", "not",
}

# Simple suffix stripping for better keyword matching across word forms
def _stem(word: str) -> str:
    for suffix in ("tion", "ing", "al", "ed", "es", "s"):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def retrieve_documents(doc_paths: dict) -> dict:
    """
    Loads and indexes all policy files.
    Returns {doc_name: {sec_num: {title, clauses: [{num, text}]}}}
    """
    index = {}

    def is_sep(line: str) -> bool:
        s = line.strip()
        return len(s) >= 3 and all(c in ("═", "=") for c in s)

    for doc_name, file_path in doc_paths.items():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"[WARNING] {file_path} not found — skipping. Coverage reduced.")
            continue

        sections = {}
        i = 0
        while i < len(lines):
            if is_sep(lines[i]) and i + 2 < len(lines):
                title_line = lines[i + 1].strip()
                m = re.match(r"^(\d+)\.\s+(.+)$", title_line)
                if m and is_sep(lines[i + 2]):
                    sec_num = m.group(1)
                    sec_title = m.group(2).strip()
                    i += 3

                    clauses = []
                    cur_num = None
                    cur_words = []

                    while i < len(lines):
                        if is_sep(lines[i]):
                            break
                        ls = lines[i].strip()
                        sub = re.match(r"^(\d+\.\d+)\s+(.*)", ls)
                        if sub:
                            if cur_num:
                                clauses.append({"num": cur_num, "text": " ".join(cur_words).strip()})
                            cur_num = sub.group(1)
                            cur_words = [sub.group(2).strip()]
                        elif cur_num and ls:
                            cur_words.append(ls)
                        i += 1

                    if cur_num:
                        clauses.append({"num": cur_num, "text": " ".join(cur_words).strip()})

                    sections[sec_num] = {"title": sec_title, "clauses": clauses}
                    continue
            i += 1

        index[doc_name] = sections

    return index


def answer_question(question: str, index: dict, threshold: int = SCORE_THRESHOLD) -> str:
    """
    Returns a single-source cited answer or the refusal template.
    Never blends from two documents.
    """
    if not index:
        return REFUSAL_TEMPLATE

    raw_tokens = set(re.findall(r"\b\w+\b", question.lower())) - STOP_WORDS
    q_tokens = {_stem(t) for t in raw_tokens}

    best_score = 0
    best_doc = None
    best_sec_num = None
    best_sec_title = None
    best_clause = None

    for doc_name, sections in index.items():
        for sec_num, section in sections.items():
            for clause in section["clauses"]:
                raw_text = set(re.findall(r"\b\w+\b", clause["text"].lower()))
                text_tokens = {_stem(t) for t in raw_text}
                score = len(q_tokens & text_tokens)
                if score > best_score:
                    best_score = score
                    best_doc = doc_name
                    best_sec_num = sec_num
                    best_sec_title = section["title"]
                    best_clause = clause

    if best_score < threshold or best_clause is None:
        return REFUSAL_TEMPLATE

    return (
        f"[Source: {best_doc} — Section {best_sec_num}: {best_sec_title}, Clause {best_clause['num']}]\n\n"
        f"{best_clause['text']}"
    )


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    doc_paths = {
        name: os.path.normpath(os.path.join(script_dir, path))
        for name, path in POLICY_FILES.items()
    }

    print("Loading policy documents...", end=" ", flush=True)
    index = retrieve_documents(doc_paths)
    section_count = sum(len(s) for s in index.values())
    clause_count = sum(
        len(sec["clauses"])
        for secs in index.values()
        for sec in secs.values()
    )
    print(f"Done. {len(index)} documents | {section_count} sections | {clause_count} clauses indexed.")
    print("\nAsk My Documents — UC-X Policy Assistant")
    print("Type your question and press Enter. Type 'quit' to exit.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        answer = answer_question(question, index)
        print(f"\nAnswer:\n{answer}\n")


if __name__ == "__main__":
    main()
