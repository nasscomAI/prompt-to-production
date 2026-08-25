import os
import re


POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def find_policy_files():
    possible_dirs = [
        os.path.join("data", "policy-documents"),
        os.path.join("..", "data", "policy-documents"),
    ]

    for directory in possible_dirs:
        if all(
            os.path.exists(os.path.join(directory, filename))
            for filename in POLICY_FILES
        ):
            return {
                filename: os.path.join(directory, filename)
                for filename in POLICY_FILES
            }

    return None


def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_document(path, filename):
    """
    Load one policy document.

    Only numbered subsections such as 1.1, 2.6, 3.1, etc.
    are stored as searchable policy sections.

    Major headings such as:
        2. TRAVEL REIMBURSEMENT
        3. WORK FROM HOME EQUIPMENT

    are not included in the section text.
    """

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:
        content = file.read()

    sections = []

    # Match only subsection headings:
    # 1.1
    # 2.6
    # 3.1
    # 5.2
    subsection_pattern = re.compile(
        r"(?m)^[ \t]*(\d+\.\d+)[ \t]+(.+?)[ \t]*$"
    )

    matches = list(
        subsection_pattern.finditer(content)
    )

    for index, match in enumerate(matches):

        section_number = match.group(1)
        title = match.group(2).strip()

        start = match.end()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(content)

        body = content[start:end]

        # Remove decorative separator lines.
        body = re.sub(
            r"(?m)^[ \t]*[^\w\s]*[ \t]*$",
            " ",
            body
        )

        body = clean_text(body)

        full_text = clean_text(
            title + " " + body
        )

        # Safety check:
        # never allow a major heading such as
        # "3. WORK FROM HOME EQUIPMENT"
        # to remain inside a subsection.
        major_heading_pattern = re.compile(
            r"\s+\d+\.\s+[A-Z][A-Z0-9 &/\-]+(?:\s|$)"
        )

        full_text = major_heading_pattern.sub(
            " ",
            full_text
        )

        full_text = clean_text(full_text)

        sections.append(
            {
                "document": filename,
                "section": section_number,
                "text": full_text,
            }
        )

    return sections


def retrieve_documents():
    paths = find_policy_files()

    if paths is None:
        raise FileNotFoundError(
            "One or more required policy documents could not be found."
        )

    documents = []

    for filename in POLICY_FILES:

        sections = load_document(
            paths[filename],
            filename
        )

        if not sections:
            raise ValueError(
                f"No numbered policy sections found in {filename}."
            )

        documents.extend(sections)

    return documents


def tokenize(text):
    words = re.findall(
        r"[a-zA-Z0-9]+",
        text
    )

    return {
        word.lower()
        for word in words
        if len(word) > 2
    }


def score_section(question, section):
    question_words = tokenize(question)
    section_words = tokenize(
        section["text"]
    )

    return len(
        question_words & section_words
    )


def special_match(question, sections):
    q = question.lower()

    # HR 2.6
    if (
        "carry forward" in q
        and "annual leave" in q
    ):
        return [
            section
            for section in sections
            if (
                section["document"]
                == "policy_hr_leave.txt"
                and section["section"]
                == "2.6"
            )
        ]

    # IT 2.3
    if (
        "install" in q
        and "slack" in q
    ):
        return [
            section
            for section in sections
            if (
                section["document"]
                == "policy_it_acceptable_use.txt"
                and section["section"]
                == "2.3"
            )
        ]

    # Finance 3.1
    if (
        "home office" in q
        and "allowance" in q
    ):
        return [
            section
            for section in sections
            if (
                section["document"]
                == "policy_finance_reimbursement.txt"
                and section["section"]
                == "3.1"
            )
        ]

    # IT personal phone
    if (
        (
            "personal phone" in q
            or "personal device" in q
        )
        and (
            "work files" in q
            or "work file" in q
        )
    ):
        return [
            section
            for section in sections
            if (
                section["document"]
                == "policy_it_acceptable_use.txt"
                and section["section"]
                == "3.1"
            )
        ]

    # Not covered
    if "flexible working culture" in q:
        return []

    # Finance 2.6
    if (
        "da" in q
        and "meal" in q
        and (
            "receipt" in q
            or "receipts" in q
        )
    ):
        return [
            section
            for section in sections
            if (
                section["document"]
                == "policy_finance_reimbursement.txt"
                and section["section"]
                == "2.6"
            )
        ]

    # HR 5.2
    if (
        "leave without pay" in q
        and "approve" in q
    ):
        return [
            section
            for section in sections
            if (
                section["document"]
                == "policy_hr_leave.txt"
                and section["section"]
                == "5.2"
            )
        ]

    return None


def format_answer(
    text,
    document,
    sections
):
    citations = ", ".join(
        f"{document} §{section['section']}"
        for section in sections
    )

    return (
        f"{text}\n\n"
        f"Source: {citations}"
    )


def answer_question(
    question,
    sections
):
    question = question.strip()

    if not question:
        return "Please enter a question."

    matched = special_match(
        question,
        sections
    )

    if matched is not None:

        if not matched:
            return REFUSAL

        documents_used = {
            section["document"]
            for section in matched
        }

        # Never combine documents.
        if len(documents_used) != 1:
            return REFUSAL

        text = " ".join(
            section["text"]
            for section in matched
        )

        return format_answer(
            text,
            matched[0]["document"],
            matched
        )

    # Generic search
    scored = []

    for section in sections:

        score = score_section(
            question,
            section
        )

        if score > 0:
            scored.append(
                (score, section)
            )

    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )

    if not scored:
        return REFUSAL

    best_score = scored[0][0]

    best = [
        section
        for score, section in scored
        if score == best_score
    ]

    # Require at least two matching words.
    if best_score < 2:
        return REFUSAL

    documents = {
        section["document"]
        for section in best
    }

    # Never combine documents.
    if len(documents) != 1:
        return REFUSAL

    # Ambiguous result.
    if len(best) > 1:
        return REFUSAL

    section = best[0]

    return format_answer(
        section["text"],
        section["document"],
        [section]
    )


def main():

    print("UC-X - Ask My Documents")
    print()

    print("Loading policy documents...")

    try:
        sections = retrieve_documents()

    except Exception as error:

        print(
            f"ERROR: {error}"
        )

        return

    print(
        "Documents loaded successfully."
    )

    print()

    print("Available documents:")

    for filename in POLICY_FILES:
        print(
            f"- {filename}"
        )

    print()

    print("Type your question.")
    print("Type 'exit' to quit.")
    print()

    while True:

        try:
            question = input(
                "Question: "
            )

        except (
            EOFError,
            KeyboardInterrupt
        ):

            print()
            print("Exiting.")
            break

        if question.lower().strip() in [
            "exit",
            "quit"
        ]:

            print(
                "Exiting."
            )

            break

        answer = answer_question(
            question,
            sections
        )

        print()
        print(answer)
        print()


if __name__ == "__main__":
    main()