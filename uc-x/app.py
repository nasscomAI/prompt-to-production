
import os
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."""

DOC_PATHS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
}


def retrieve_documents():
    index = {}

    for doc_name, path in DOC_PATHS.items():
        if not os.path.exists(path):
            raise Exception(f"Error: Failed to load document {doc_name}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            raise Exception(f"Error: Failed to read document {doc_name}")

        # Extract sections like "2.6", "3.1", etc.
        pattern = r'(\d+\.\d+)\s*(.*?)((?=\n\d+\.\d+)|$)'
        matches = re.findall(pattern, content, re.DOTALL)

        if not matches:
            raise Exception(f"Error: Invalid document format in {doc_name}")

        sections = {}
        for section_num, section_text, _ in matches:
            cleaned_text = section_text.strip()
            if cleaned_text:
                sections[section_num.strip()] = cleaned_text

        if not sections:
            raise Exception(f"Error: Invalid document format in {doc_name}")

        index[doc_name] = sections

    return index


def normalize(text):
    return re.sub(r'[^a-z0-9\s]', '', text.lower())


def answer_question(question, index):
    # input validation
    if not question or not isinstance(question, str) or not question.strip():
        return REFUSAL_TEMPLATE

    q_norm = normalize(question)
    matches = []

    for doc_name, sections in index.items():
        for section_num, content in sections.items():
            content_norm = normalize(content)

            # simple keyword matching
            # score match by number of overlapping words
            q_words = set(q_norm.split())
            content_words = set(content_norm.split())

            overlap = q_words.intersection(content_words)

            if overlap:
                matches.append((doc_name, section_num, content, len(overlap)))

    if not matches:
        return REFUSAL_TEMPLATE

    # sort by best overlap
    matches.sort(key=lambda x: x[3], reverse=True)

    # Take top match
    top_doc, top_section, top_content, top_score = matches[0]

    # Check if there are competing matches from different documents
    competing = [
        m for m in matches
        if m[3] == top_score and (m[0] != top_doc or m[1] != top_section)
    ]

    if competing:
        # cross-document ambiguity OR multiple sections ambiguity
        return REFUSAL_TEMPLATE

    # Ensure single source (only one doc)
    same_doc_all = [m for m in matches if m[0] == top_doc and m[3] == top_score]
    if len(same_doc_all) > 1:
        return REFUSAL_TEMPLATE

    # Return exact content with citation
    answer = top_content.strip()

    # Enforce no hedging phrases
    forbidden_phrases = [
        "while not explicitly covered",
        "typically",
        "generally understood",
        "it is common practice"
    ]

    for phrase in forbidden_phrases:
        if phrase in answer.lower():
            return REFUSAL_TEMPLATE

    return f"{answer} ({top_doc}, section {top_section})"


def main():
    try:
        index = retrieve_documents()
    except Exception as e:
        print(str(e))
        return

    print("Ask your question (type 'exit' to quit):")

    while True:
        try:
            user_input = input("> ").strip()
        except EOFError:
            break

        if user_input.lower() in ["exit", "quit"]:
            break

        response = answer_question(user_input, index)
        print(response)


if __name__ == "__main__":
    main()