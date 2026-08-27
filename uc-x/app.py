"""
UC-X — Ask My Documents

Deterministic local policy QA implementation.

Uses:
- Three CMC policy documents
- Section-based retrieval
- Single-source answers
- Exact refusal template
- Explicit protection against cross-document blending
- Explicit protection against condition dropping
"""

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

POLICY_DIRECTORY = Path(__file__).resolve().parent.parent / "data" / "policy-documents"

REQUIRED_DOCUMENTS = [
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


# ---------------------------------------------------------------------------
# Explicit question-to-policy concepts
#
# This keeps the system deterministic and conservative.
# If a question does not clearly map to a supported policy concept,
# the system refuses instead of guessing.
# ---------------------------------------------------------------------------

QUESTION_PATTERNS = [
    {
        "patterns": [
            "carry forward",
            "unused annual leave",
            "annual leave carry",
        ],
        "document": "policy_hr_leave.txt",
        "section": "2.6",
    },
    {
        "patterns": [
            "install slack",
            "install software",
            "software on",
            "install application",
        ],
        "document": "policy_it_acceptable_use.txt",
        "section": "2.3",
    },
    {
        "patterns": [
            "home office equipment",
            "equipment allowance",
            "work from home equipment",
        ],
        "document": "policy_finance_reimbursement.txt",
        "section": "3.1",
    },
    {
        "patterns": [
            "personal phone",
            "personal device",
            "work files",
            "access work files",
        ],
        "document": "policy_it_acceptable_use.txt",
        "section": "3.1",
    },
    {
        "patterns": [
            "da and meal",
            "meal receipts",
            "daily allowance",
            "claim da",
        ],
        "document": "policy_finance_reimbursement.txt",
        "section": "2.6",
    },
    {
        "patterns": [
            "leave without pay",
            "lwp",
            "who approves leave",
            "approval for leave",
        ],
        "document": "policy_hr_leave.txt",
        "section": "5.2",
    },
]


# ---------------------------------------------------------------------------
# Document retrieval
# ---------------------------------------------------------------------------

def retrieve_documents(policy_directory=POLICY_DIRECTORY):
    """
    Load all required policy documents and index their subsections.

    Returns:
        dict:
            {
                document_name: {
                    section_number: section_text
                }
            }

    Raises:
        FileNotFoundError:
            If a required policy document does not exist.
    """

    indexed_documents = {}

    # Matches subsection headings such as:
    # 2.6 Employees may carry forward...
    subsection_pattern = re.compile(
        r"^(\d+)\.(\d+)\s+(.*)$"
    )

    # Matches major headings such as:
    # 3. WORK FROM HOME EQUIPMENT
    major_section_pattern = re.compile(
        r"^(\d+)\.\s+"
    )

    for document_name in REQUIRED_DOCUMENTS:

        document_path = Path(policy_directory) / document_name

        if not document_path.exists():
            raise FileNotFoundError(
                f"Required policy document not found: {document_name}"
            )

        text = document_path.read_text(encoding="utf-8")
        lines = text.splitlines()

        document_sections = {}

        current_section = None
        current_content = []

        for line in lines:

            stripped_line = line.strip()

            # Ignore empty lines.
            if not stripped_line:
                continue

            # Ignore decorative separator lines.
            if set(stripped_line) <= {"═", "=", "-", "_"}:
                continue

            major_match = major_section_pattern.match(
                stripped_line
            )

            subsection_match = subsection_pattern.match(
                stripped_line
            )

            # Major section heading.
            if major_match:

                if current_section is not None:
                    document_sections[current_section] = (
                        " ".join(current_content).strip()
                    )

                current_section = None
                current_content = []

                continue

            # Subsection heading.
            if subsection_match:

                if current_section is not None:
                    document_sections[current_section] = (
                        " ".join(current_content).strip()
                    )

                current_section = (
                    f"{subsection_match.group(1)}."
                    f"{subsection_match.group(2)}"
                )

                current_content = [
                    subsection_match.group(3).strip()
                ]

                continue

            # Continuation of the current subsection.
            if current_section is not None:
                current_content.append(
                    stripped_line
                )

        # Save final section.
        if current_section is not None:
            document_sections[current_section] = (
                " ".join(current_content).strip()
            )

        indexed_documents[document_name] = document_sections

    return indexed_documents


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def tokenize(text):
    """Convert text into lowercase keyword tokens."""

    return set(
        re.findall(
            r"\b[a-z0-9]+\b",
            text.lower()
        )
    )


# ---------------------------------------------------------------------------
# Safety checks
# ---------------------------------------------------------------------------

def contains_sensitive_data_question(question):
    """
    Detect questions involving sensitive/restricted information.

    Such questions require special handling because the IT policy contains
    both permissions and explicit restrictions concerning personal devices.
    """

    sensitive_terms = {
        "classified",
        "sensitive",
        "confidential",
        "restricted",
        "work files",
        "work file",
    }

    normalized_question = (
        question.lower()
        .strip()
    )

    return any(
        term in normalized_question
        for term in sensitive_terms
    )


def has_material_restriction(question, documents):
    """
    Determine whether a question involving sensitive data is governed by
    multiple relevant IT policy sections.

    When multiple sections materially govern the question, the safest UC-X
    behavior is refusal rather than constructing a combined rule.
    """

    if not contains_sensitive_data_question(question):
        return False

    it_sections = documents.get(
        "policy_it_acceptable_use.txt",
        {}
    )

    relevant_sections = []

    for section_number in ["3.1", "3.2", "5.1"]:
        section_text = it_sections.get(
            section_number
        )

        if section_text:
            relevant_sections.append(
                section_number
            )

    return len(relevant_sections) > 1


# ---------------------------------------------------------------------------
# Question answering
# ---------------------------------------------------------------------------

def answer_question(question, documents):
    """
    Answer a policy question using explicitly supported policy concepts.

    The system:

    1. Refuses unsupported questions.
    2. Refuses ambiguous questions.
    3. Never combines multiple documents into one answer.
    4. Never creates a new policy rule from separate sections.
    5. Preserves the complete source section.
    6. Cites the source document and section.
    """

    if not isinstance(question, str):
        return REFUSAL_TEMPLATE

    question = question.strip()

    if not question:
        return REFUSAL_TEMPLATE

    # ------------------------------------------------------------------
    # Safety check for questions involving sensitive/restricted data.
    # ------------------------------------------------------------------

    if has_material_restriction(
        question,
        documents
    ):
        return REFUSAL_TEMPLATE

    # ------------------------------------------------------------------
    # Match question to explicitly supported policy concepts.
    # ------------------------------------------------------------------

    normalized_question = " ".join(
        question.lower().split()
    )

    matches = []

    for rule in QUESTION_PATTERNS:

        for pattern in rule["patterns"]:

            if pattern in normalized_question:

                matches.append(rule)

                break

    # No supported policy concept.
    if not matches:
        return REFUSAL_TEMPLATE

    # ------------------------------------------------------------------
    # Safety rule:
    #
    # A response may be supported by exactly one document + section.
    # ------------------------------------------------------------------

    unique_matches = {
        (
            match["document"],
            match["section"],
        )
        for match in matches
    }

    if len(unique_matches) != 1:
        return REFUSAL_TEMPLATE

    document_name, section_number = next(
        iter(unique_matches)
    )

    section_text = (
        documents
        .get(document_name, {})
        .get(section_number)
    )

    if not section_text:
        return REFUSAL_TEMPLATE

    # ------------------------------------------------------------------
    # Return the complete source section.
    #
    # This is important because returning the complete section helps
    # prevent condition dropping.
    # ------------------------------------------------------------------

    return (
        f"{section_text}\n"
        f"Source: {document_name}, Section {section_number}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():

    try:
        documents = retrieve_documents()

    except FileNotFoundError as error:
        print(f"ERROR: {error}")
        return

    print(
        "Policy documents loaded successfully."
    )

    for document_name, sections in documents.items():
        print(
            f"{document_name}: "
            f"{len(sections)} sections"
        )

    questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?",
    ]

    for question in questions:

        print("\n" + "=" * 70)

        print("\nQUESTION:")
        print(question)

        print("\nANSWER:")
        print(
            answer_question(
                question,
                documents
            )
        )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()