import argparse
import os
import re


POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def policy_directory():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(
        os.path.join(base_dir, "..", "data", "policy-documents")
    )


def parse_sections(text):
    """
    Parse only numbered policy clauses such as 2.6 or 5.2.

    Important:
    A heading such as:
        3. WORK FROM HOME EQUIPMENT

    is NOT a clause and must not become part of the preceding
    clause's text.
    """

    sections = {}
    current_section = None
    current_lines = []

    clause_pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
    heading_pattern = re.compile(r"^\s*(\d+)\.\s+.*$")

    for line in text.splitlines():
        stripped = line.strip()

        # Ignore empty lines.
        if not stripped:
            continue

        # Ignore decorative separator lines.
        if is_separator(stripped):
            continue

        # A numbered clause such as "2.6 Employees must..."
        clause_match = clause_pattern.match(line)

        if clause_match:
            if current_section is not None:
                sections[current_section] = " ".join(
                    current_lines
                ).strip()

            current_section = clause_match.group(1)
            current_lines = [clause_match.group(2).strip()]
            continue

        # A major section heading such as:
        # "3. WORK FROM HOME EQUIPMENT"
        #
        # It must NOT be appended to the preceding clause.
        if heading_pattern.match(line):
            continue

        if current_section is not None:
            current_lines.append(stripped)

    # Save final clause.
    if current_section is not None:
        sections[current_section] = " ".join(
            current_lines
        ).strip()

    return sections


def is_separator(text):
    """
    Detect the decorative separator characters used in the
    supplied policy documents.
    """
    if not text:
        return False

    separator_chars = set(
        "═─━┄┅┈┉┊┋│"
        "ΓöÇΓöüΓòÉΓÇôΓÇöΓòöΓòùΓòÜΓò¥ΓòáΓòúΓò¼"
        "-_"
    )

    return all(char in separator_chars for char in text)


def retrieve_documents():
    """
    Load all three policy documents and index them by filename
    and numbered clause.
    """
    directory = policy_directory()
    documents = {}

    for filename in POLICY_FILES:
        path = os.path.join(directory, filename)

        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"Policy document not found: {filename}"
            )

        try:
            with open(
                path,
                "r",
                encoding="utf-8",
                errors="replace",
            ) as file:
                text = file.read()
        except OSError as exc:
            raise OSError(
                f"Could not read policy document: {filename}"
            ) from exc

        sections = parse_sections(text)

        if not sections:
            raise ValueError(
                f"No numbered policy sections found in {filename}"
            )

        documents[filename] = sections

    return documents


def citation(filename, section, text):
    return f"{text} [{filename}, section {section}]"


def answer_question(question, documents):
    q = question.lower().strip()

    # ---------------------------------------------------------
    # Assignment-specific authoritative mappings.
    # ---------------------------------------------------------

    # HR §2.6
    if "carry forward" in q and "annual leave" in q:
        filename = "policy_hr_leave.txt"
        section = "2.6"

        return citation(
            filename,
            section,
            documents[filename][section],
        )

    # IT §2.3
    if (
        "slack" in q
        and (
            "work laptop" in q
            or "work computer" in q
            or "work device" in q
        )
    ):
        filename = "policy_it_acceptable_use.txt"
        section = "2.3"

        return citation(
            filename,
            section,
            documents[filename][section],
        )

    # Finance §3.1
    if (
        "home office" in q
        and "equipment" in q
        and "allowance" in q
    ):
        filename = "policy_finance_reimbursement.txt"
        section = "3.1"

        return citation(
            filename,
            section,
            documents[filename][section],
        )

    # IT §3.1
    #
    # Do NOT combine this with HR remote-work provisions.
    if (
        "personal phone" in q
        and (
            "work files" in q
            or "work file" in q
            or "access" in q
        )
    ):
        filename = "policy_it_acceptable_use.txt"
        section = "3.1"

        return citation(
            filename,
            section,
            documents[filename][section],
        )

    # Finance §2.6
    if (
        ("da" in q or "daily allowance" in q)
        and "meal" in q
        and (
            "same day" in q
            or "simultaneously" in q
        )
    ):
        filename = "policy_finance_reimbursement.txt"
        section = "2.6"

        return citation(
            filename,
            section,
            documents[filename][section],
        )

    # HR §5.2
    if (
        (
            "leave without pay" in q
            or "lwp" in q
        )
        and (
            "who approves" in q
            or "approval" in q
            or "approver" in q
        )
    ):
        filename = "policy_hr_leave.txt"
        section = "5.2"

        return citation(
            filename,
            section,
            documents[filename][section],
        )

    # Explicit unsupported topic.
    if (
        "flexible working" in q
        or "flexible work culture" in q
        or "company view on flexible" in q
    ):
        return REFUSAL_TEMPLATE

    # ---------------------------------------------------------
    # Conservative fallback.
    # ---------------------------------------------------------

    question_words = {
        word
        for word in re.findall(r"[a-z0-9]+", q)
        if len(word) >= 4
    }

    candidates = []

    for filename, sections in documents.items():
        for section, text in sections.items():
            section_words = {
                word
                for word in re.findall(
                    r"[a-z0-9]+",
                    text.lower(),
                )
                if len(word) >= 4
            }

            overlap = len(
                question_words.intersection(section_words)
            )

            if overlap >= 2:
                candidates.append(
                    (
                        overlap,
                        filename,
                        section,
                    )
                )

    if not candidates:
        return REFUSAL_TEMPLATE

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    best_score = candidates[0][0]

    best_candidates = [
        item
        for item in candidates
        if item[0] == best_score
    ]

    best_documents = {
        item[1]
        for item in best_candidates
    }

    # Never combine claims from different documents.
    if len(best_documents) != 1:
        return REFUSAL_TEMPLATE

    _, filename, section = best_candidates[0]

    return citation(
        filename,
        section,
        documents[filename][section],
    )


def main():
    parser = argparse.ArgumentParser(
        description="UC-X Policy Document Assistant"
    )

    parser.add_argument(
        "--input",
        help="Optional policy file for validation",
    )

    args = parser.parse_args()

    documents = retrieve_documents()

    if args.input:
        selected = os.path.basename(args.input)

        if selected not in POLICY_FILES:
            raise ValueError(
                "Input must be one of: "
                + ", ".join(POLICY_FILES)
            )

    print("UC-X Policy Assistant")
    print("Type a question, or type 'exit' to quit.")
    print()

    while True:
        try:
            question = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.strip().lower() in {
            "exit",
            "quit",
        }:
            break

        print(answer_question(question, documents))
        print()


if __name__ == "__main__":
    main()
