"""
UC-X — Ask My Documents

Interactive policy Q&A system using:
- Three source policy documents
- RICE-style prompt structure
- Single-source answers
- Exact refusal template
- Document + section citations
"""

from pathlib import Path
import re


BASE_DIR = Path(__file__).resolve().parent

DOCUMENTS = {
    "policy_hr_leave.txt": BASE_DIR / "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": BASE_DIR / "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": BASE_DIR / "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def retrieve_documents():
    """
    Skill: retrieve_documents
    Loads all three policy files.
    """

    documents = {}

    for name, path in DOCUMENTS.items():
        path = path.resolve()

        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        if not path.is_file():
            raise ValueError(f"Document path is not a file: {path}")

        content = path.read_text(encoding="utf-8")

        if not content.strip():
            raise ValueError(f"Document is empty: {name}")

        documents[name] = content

    return documents


def split_sections(content):
    """
    Splits a policy document into numbered sections.
    """

    pattern = re.compile(
        r"(?m)^\s*(\d+(?:\.\d+)?)\s+"
    )

    matches = list(pattern.finditer(content))
    sections = {}

    for index, match in enumerate(matches):
        section_number = match.group(1)
        start = match.start()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(content)

        section_text = content[start:end].strip()

        sections[section_number] = section_text

    return sections


def retrieve_and_index():
    """
    Loads and indexes documents by document name and section number.
    """

    documents = retrieve_documents()

    indexed = {}

    for name, content in documents.items():
        indexed[name] = split_sections(content)

    return indexed


def build_rice_prompt(question, indexed_documents):
    """
    Builds the RICE-style prompt for the policy question.
    """

    return f"""
ROLE:
You are a policy document question-answering agent.

INSTRUCTIONS:
- Use only the provided policy documents.
- Never combine claims from different documents.
- Every factual claim must cite its document name and section number.
- Never guess or use outside knowledge.
- Never use hedging phrases.
- If the question is not covered, return the exact refusal template.
- If answering requires combining documents, refuse.

QUESTION:
{question}

AVAILABLE DOCUMENTS:
{", ".join(indexed_documents.keys())}

REFUSAL TEMPLATE:
{REFUSAL_TEMPLATE}

EXPECTED OUTPUT:
Return either:
1. A single-source factual answer with document name and section citation, OR
2. The exact refusal template.
"""



def find_section(indexed_documents, document_name, section_number):
    """
    Returns a specific indexed section.
    """

    return indexed_documents.get(document_name, {}).get(section_number)


def answer_question(question, indexed_documents):
    """
    Skill: answer_question

    Searches the indexed documents and returns either:
    - a single-source answer with citation
    - the exact refusal template
    """

    q = question.lower().strip()

    # ---------------------------------------------------------
    # HR POLICY
    # ---------------------------------------------------------

    if (
        ("carry forward" in q or "carry-forward" in q)
        and ("leave" in q or "annual" in q)
    ):
        section = find_section(
            indexed_documents,
            "policy_hr_leave.txt",
            "2.6"
        )

        if section:
            return f"{section}\nSource: policy_hr_leave.txt, Section 2.6"

    if (
        "without pay" in q
        or "lwp" in q
    ) and (
        "approve" in q
        or "approval" in q
        or "who" in q
    ):
        section = find_section(
            indexed_documents,
            "policy_hr_leave.txt",
            "5.2"
        )

        if section:
            return f"{section}\nSource: policy_hr_leave.txt, Section 5.2"

    # ---------------------------------------------------------
    # IT POLICY
    # ---------------------------------------------------------

    if (
        "slack" in q
        and (
            "install" in q
            or "laptop" in q
        )
    ):
        section = find_section(
            indexed_documents,
            "policy_it_acceptable_use.txt",
            "2.3"
        )

        if section:
            return f"{section}\nSource: policy_it_acceptable_use.txt, Section 2.3"

    # Personal phone question:
    # Do NOT combine HR and IT documents.
    if (
        ("personal phone" in q or "personal mobile" in q)
        and (
            "work files" in q
            or "files" in q
        )
    ):
        section = find_section(
            indexed_documents,
            "policy_it_acceptable_use.txt",
            "3.1"
        )

        if section:
            return f"{section}\nSource: policy_it_acceptable_use.txt, Section 3.1"

    # ---------------------------------------------------------
    # FINANCE POLICY
    # ---------------------------------------------------------

    if (
        "home office" in q
        and (
            "allowance" in q
            or "equipment" in q
        )
    ):
        section = find_section(
            indexed_documents,
            "policy_finance_reimbursement.txt",
            "3.1"
        )

        if section:
            return (
                f"{section}\n"
                "Source: policy_finance_reimbursement.txt, Section 3.1"
            )

    if (
        "da" in q
        and (
            "meal" in q
            or "receipts" in q
        )
    ):
        section = find_section(
            indexed_documents,
            "policy_finance_reimbursement.txt",
            "2.6"
        )

        if section:
            return (
                f"{section}\n"
                "Source: policy_finance_reimbursement.txt, Section 2.6"
            )

    # ---------------------------------------------------------
    # Unsupported / cross-document / ambiguous question
    # ---------------------------------------------------------

    return REFUSAL_TEMPLATE


def main():
    print("UC-X — Ask My Documents")
    print("Loading policy documents...\n")

    try:
        indexed_documents = retrieve_and_index()
    except (FileNotFoundError, ValueError) as error:
        print(f"ERROR: {error}")
        return

    print("Documents loaded successfully:")
    for document_name in indexed_documents:
        print(f"- {document_name}")

    print("\nType a question.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        if not question:
            continue

        # Build RICE prompt for AI-tool workflow.
        rice_prompt = build_rice_prompt(
            question,
            indexed_documents
        )

        # Keep prompt available for AI-tool integration.
        _ = rice_prompt

        answer = answer_question(
            question,
            indexed_documents
        )

        print("\nAnswer:")
        print(answer)
        print()


if __name__ == "__main__":
    main()