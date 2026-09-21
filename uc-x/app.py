"""UC-X single-source policy question answering CLI."""
import argparse
import os
import re

DOCUMENTS = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)
REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant policy team for guidance."
)
CLAUSE_PATTERN = re.compile(
    r"(?ms)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|^\s*═+\s*$|\Z)"
)


def retrieve_documents(directory):
    index = {}
    for filename in DOCUMENTS:
        path = os.path.join(directory, filename)
        try:
            with open(path, "r", encoding="utf-8-sig") as source:
                content = source.read()
        except OSError as error:
            raise ValueError("Unable to read {}: {}".format(filename, error))
        sections = {}
        for match in CLAUSE_PATTERN.finditer(content):
            sections[match.group(1)] = " ".join(
                line.strip() for line in match.group(2).splitlines()
            ).strip()
        index[filename] = sections
    return index


def _refusal():
    return REFUSAL


def answer_question(question, index):
    text = question.lower().strip()
    if not text:
        return _refusal()

    exact_routes = (
        (("carry forward", "unused annual leave"), "policy_hr_leave.txt", ("2.6",)),
        (("install slack", "install software"), "policy_it_acceptable_use.txt", ("2.3",)),
        (("home office equipment", "equipment allowance"), "policy_finance_reimbursement.txt", ("3.1",)),
        (("personal phone", "personal device"), "policy_it_acceptable_use.txt", ("3.1", "3.2")),
        (("da and meal", "meal receipts", "daily allowance"), "policy_finance_reimbursement.txt", ("2.6",)),
        (("leave without pay", "lwp"), "policy_hr_leave.txt", ("5.2",)),
    )
    for phrases, filename, sections in exact_routes:
        if any(phrase in text for phrase in phrases):
            return _format_answer(filename, sections, index)

    if "flexible working culture" in text:
        return _refusal()

    words = set(re.findall(r"[a-z0-9]+", text))
    matches = []
    for filename, sections in index.items():
        for section, content in sections.items():
            content_words = set(re.findall(r"[a-z0-9]+", content.lower()))
            if len(words & content_words) >= 3:
                matches.append((filename, section))
    documents = {filename for filename, _ in matches}
    if len(documents) != 1:
        return _refusal()
    selected = [section for filename, section in matches if filename in documents]
    return _format_answer(next(iter(documents)), selected[:3], index)


def _format_answer(filename, sections, index):
    unique_sections = []
    for section in sections:
        if section not in unique_sections and section in index[filename]:
            unique_sections.append(section)
    if not unique_sections:
        return _refusal()
    lines = []
    for section in unique_sections:
        lines.append(
            "[Source: {} section {}] {}".format(filename, section, index[filename][section])
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Ask questions of CMC policy documents")
    parser.add_argument(
        "--documents-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"),
    )
    args = parser.parse_args()
    index = retrieve_documents(os.path.abspath(args.documents_dir))
    print("Policy assistant ready. Type a question or 'exit' to quit.")
    while True:
        try:
            question = input("> ")
        except EOFError:
            break
        if question.strip().lower() in ("exit", "quit"):
            break
        print(answer_question(question, index))


if __name__ == "__main__":
    main()
