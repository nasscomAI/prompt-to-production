import os
import re

NO_ANSWER_MESSAGE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact the relevant "
    "team for guidance."
)

DOCUMENT_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]


def load_documents():
    """
    Load all policy documents.

    Returns:
        dict containing filename, content and sections.
    """
    documents = {}

    for path in DOCUMENT_PATHS:
        filename = os.path.basename(path)

        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()

            pattern = r'(^\s*(\d+[\.\)]?)\s+.*?(?=^\s*\d+[\.\)]?\s+|\Z))'
            matches = re.finditer(
                pattern,
                content,
                flags=re.MULTILINE | re.DOTALL
            )

            sections = []

            for match in matches:
                full_section = match.group(1).strip()
                section_number = match.group(2).strip()
                sections.append((section_number, full_section))

            if not sections:
                sections = [("N/A", content.strip())]

            documents[filename] = {
                "content": content,
                "sections": sections
            }

        except FileNotFoundError:
            print(f"Warning: Could not find {filename}")

        except Exception as error:
            print(f"Warning: Could not load {filename}: {error}")

    return documents


def search_documents(question, documents):
    """
    Search all documents using keyword matching.

    Returns:
        (filename, section_number, section_text)
        or None.
    """
    keywords = re.findall(r"\b\w+\b", question.lower())
    keywords = [word for word in keywords if len(word) > 2]

    if not keywords:
        return None

    document_matches = []

    for filename, doc_data in documents.items():

        best_score = 0
        best_section = None

        for section_number, section_text in doc_data["sections"]:

            text_lower = section_text.lower()

            score = sum(
                1
                for keyword in keywords
                if keyword in text_lower
            )

            if score > best_score:
                best_score = score
                best_section = (
                    section_number,
                    section_text
                )

        if best_score > 0 and best_section:
            document_matches.append(
                (
                    filename,
                    best_section[0],
                    best_section[1],
                    best_score
                )
            )

    if not document_matches:
        return None

    document_matches.sort(
        key=lambda x: x[3],
        reverse=True
    )

    top_score = document_matches[0][3]

    top_documents = [
        item
        for item in document_matches
        if item[3] == top_score
    ]

    if len(top_documents) != 1:
        return None

    return top_documents[0][:3]
def answer_question(question, documents):
    """
    Answer the user's question using policy documents only.
    Every factual answer includes the document name and section number.
    """

    result = search_documents(question, documents)

    if result is None:
        print("\n" + NO_ANSWER_MESSAGE + "\n")
        return

    filename, section_number, section_text = result

    print("\nAnswer:")
    print(section_text)
    print(f"\nDocument: {filename}")
    print(f"Section: {section_number}")
    
def main():
    """
    Main interactive application.
    """

    print("Loading policy documents...")

    documents = load_documents()

    if not documents:
        print("No policy documents could be loaded.")
        return

    print("Ask questions about company policies.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            question = input("Question: ").strip()

            if question.lower() == "exit":
                print("Goodbye.")
                break

            if not question:
                print("Please enter a question.\n")
                continue

            answer_question(question, documents)

        except KeyboardInterrupt:
            print("\nGoodbye.")
            break

        except EOFError:
            print("\nGoodbye.")
            break

        except Exception as error:
            print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()