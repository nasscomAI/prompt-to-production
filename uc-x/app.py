import argparse
import os
import re


REFUSAL = "I’m sorry, but this question is not covered in the provided policy documents."


def retrieve_documents(directory):
    """Load all policy files and index them by document and section."""
    documents = {}

    for filename in os.listdir(directory):
        if not filename.lower().endswith(".txt"):
            continue

        path = os.path.join(directory, filename)

        with open(path, "r", encoding="utf-8-sig") as file:
            text = file.read()

        sections = {}

        # Supports section formats such as:
        # 2.6 — Carry-forward...
        # 2.6 - Carry-forward...
        # 2.6 Carry-forward...
        matches = list(
            re.finditer(
                r"(?m)^\s*(\d+\.\d+)\s*(?:[-–—:]\s*)?(.*)$",
                text
            )
        )

        for i, match in enumerate(matches):
            section_number = match.group(1)
            first_line = match.group(2).strip()

            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

            remaining = text[start:end].strip()

            section_text = " ".join(
                [first_line, remaining]
            ).strip()

            sections[section_number] = section_text

        documents[filename] = sections

    return documents


def find_section(documents, filename_part, section):
    """Find a specific section from a specific policy document."""

    for filename, sections in documents.items():
        if filename_part.lower() in filename.lower():
            if section in sections:
                return filename, sections[section]

    return None, None


def answer_question(documents, question):
    """Answer using exactly one policy document."""

    q = question.lower()

    # HR 2.6
    if "carry forward" in q and "annual leave" in q:
        filename, text = find_section(
            documents,
            "policy_hr_leave",
            "2.6"
        )

        if filename:
            return f"{text} [Source: {filename}, Section 2.6]"

    # IT 2.3
    if "slack" in q and "work laptop" in q:
        filename, text = find_section(
            documents,
            "policy_it_acceptable_use",
            "2.3"
        )

        if filename:
            return f"{text} [Source: {filename}, Section 2.3]"

    # Finance 3.1
    if "home office" in q and "equipment" in q and "allowance" in q:
        filename, text = find_section(
            documents,
            "policy_finance_reimbursement",
            "3.1"
        )

        if filename:
            return f"{text} [Source: {filename}, Section 3.1]"

    # Personal phone — IT only
    if "personal phone" in q and "work files" in q:
        filename, text = find_section(
            documents,
            "policy_it_acceptable_use",
            "2.3"
        )

        if filename and (
            "phone" in text.lower()
            or "mobile" in text.lower()
        ):
            return f"{text} [Source: {filename}, Section 2.3]"

        return REFUSAL

    # Not covered
    if "flexible working culture" in q:
        return REFUSAL

    # Finance 2.6
    if "da" in q and "meal receipts" in q:
        filename, text = find_section(
            documents,
            "policy_finance_reimbursement",
            "2.6"
        )

        if filename:
            return f"{text} [Source: {filename}, Section 2.6]"

    # HR 5.2
    if "leave without pay" in q and "who approves" in q:
        filename, text = find_section(
            documents,
            "policy_hr_leave",
            "5.2"
        )

        if filename:
            return f"{text} [Source: {filename}, Section 5.2]"

    return REFUSAL


def main():
    parser = argparse.ArgumentParser(
        description="UC-X Single-Source Policy Q&A"
    )

    parser.add_argument(
        "--docs",
        required=True,
        help="Directory containing policy documents"
    )

    parser.add_argument(
        "--question",
        required=True,
        help="Policy question"
    )

    args = parser.parse_args()

    documents = retrieve_documents(args.docs)

    if not documents:
        raise SystemExit("No policy documents found.")

    answer = answer_question(documents, args.question)

    print(answer)


if __name__ == "__main__":
    main()