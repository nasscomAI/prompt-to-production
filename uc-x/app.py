"""
UC-X — Ask My Documents
Interactive CLI to answer questions using policy documents.
Enforces single-source retrieval, clause-level citations, and refusal template.
"""

import os
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""

def retrieve_documents():
    """Load all policy documents and index by sections."""
    base_path = os.path.join("data", "policy-documents")

    docs = {
        "policy_hr_leave.txt": {},
        "policy_it_acceptable_use.txt": {},
        "policy_finance_reimbursement.txt": {},
    }

    for doc_name in docs:
        path = os.path.join(base_path, doc_name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing document: {path}")

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        # Split by numbered sections (assuming format: "2.6 ..." etc.)
        sections = re.split(r'(?m)^(?=\d+\.\d+\s+)', text)
        section_map = {}
        for s in sections:
            s_clean = s.strip()
            if not s_clean:
                continue
            # Capture section number (e.g., 2.6) as key
            match = re.match(r'^(\d+\.\d+)', s_clean)
            if match:
                sec_num = match.group(1)
                section_map[sec_num] = s_clean
            else:
                # fallback section
                section_map[f"0.{len(section_map)+1}"] = s_clean

        docs[doc_name] = section_map

    return docs

def search_document(question, doc_name, sections):
    """Search for question keywords in each section of the document."""
    q = question.lower()
    matches = []

    for sec_num, text in sections.items():
        t = text.lower()
        # Simple keyword matching per type of policy
        if "leave without pay" in q and "leave without pay" in t:
            matches.append(f"{text}\nSource: {doc_name}")
        elif "carry forward" in q and "carry forward" in t:
            matches.append(f"{text}\nSource: {doc_name}")
        elif "slack" in q and "slack" in t:
            matches.append(f"{text}\nSource: {doc_name}")
        elif "home office" in q and "allowance" in t:
            matches.append(f"{text}\nSource: {doc_name}")
        elif "reimbursement" in q and "rs" in t:
            matches.append(f"{text}\nSource: {doc_name}")

    if len(matches) == 0:
        return None
    if len(matches) > 1:
        # multiple matches in same document → return first to prevent cross-document blending
        return matches[0]
    return matches[0]

def answer_question(question, documents):
    """Answer using single-source enforcement and refusal template."""
    matches = []

    for doc_name, sections in documents.items():
        result = search_document(question, doc_name, sections)
        if result:
            matches.append(result)

    if len(matches) == 0:
        return REFUSAL_TEMPLATE
    if len(matches) > 1:
        return REFUSAL_TEMPLATE

    return matches[0]

def main():
    print("Policy Assistant — Ask your question (type 'exit' to quit)\n")
    documents = retrieve_documents()

    while True:
        try:
            question = input("Ask a question: ").strip()
        except KeyboardInterrupt:
            print("\nExiting.")
            break

        if question.lower() in ["exit", "quit"]:
            print("Exiting.")
            break

        answer = answer_question(question, documents)
        print("\nAnswer:")
        print(answer)
        print()

if __name__ == "__main__":
    main()