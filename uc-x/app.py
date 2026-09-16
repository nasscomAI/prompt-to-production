import argparse
import re
from pathlib import Path

DOCUMENT_NAMES = ("policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt")
REFUSAL = ("This question is not covered in the available policy documents "
           "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
           "policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.")

def retrieve_documents(data_dir):
    documents = {}
    for name in DOCUMENT_NAMES:
        path = data_dir / name
        if not path.is_file():
            raise FileNotFoundError(f"Missing policy document: {path}")
        text = path.read_text(encoding="utf-8")
        matches = list(re.finditer(r"(?m)^(?:section\s+)?(\d+(?:\.\d+)*)\b[^\n]*", text, re.I))
        if not matches:
            documents[name] = [("document", text.strip())]
        else:
            documents[name] = [(m.group(1), text[m.start():matches[i + 1].start() if i + 1 < len(matches) else len(text)].strip())
                                for i, m in enumerate(matches)]
    return documents

def answer_question(question, documents):
    words = {w.lower() for w in re.findall(r"[a-zA-Z0-9]+", question) if len(w) > 2}
    candidates = []
    for document, sections in documents.items():
        for section, content in sections:
            content_words = {w.lower() for w in re.findall(r"[a-zA-Z0-9]+", content)}
            score = len(words & content_words)
            if score:
                candidates.append((score, document, section, content))
    if not candidates:
        return REFUSAL
    candidates.sort(reverse=True)
    best = candidates[0]
    if len(candidates) > 1 and candidates[1][0] == best[0] and candidates[1][1] != best[1]:
        return REFUSAL
    return f"{best[3]}\n\nSource: {best[1]}, section {best[2]}"

def main():
    parser = argparse.ArgumentParser(description="Ask questions about the UC-X policy documents.")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent.parent / "data" / "policy-documents")
    args = parser.parse_args()
    try:
        documents = retrieve_documents(args.data_dir)
    except (OSError, UnicodeError) as error:
        parser.error(str(error))
    while True:
        try:
            question = input("Question (or 'exit'): ").strip()
        except EOFError:
            break
        if question.lower() in {"exit", "quit"}:
            break
        if question:
            print(answer_question(question, documents))

if __name__ == "__main__":
    main()
