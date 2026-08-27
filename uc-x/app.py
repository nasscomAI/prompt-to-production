import argparse
import os
import re

# ---------------- CONSTANT: REFUSAL TEMPLATE ----------------
REFUSAL_RESPONSE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


# ---------------- SKILL 1 ----------------
def retrieve_documents(file_paths):
    documents = {}

    for path in file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract sections like 2.3, 3.1 etc.
        pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)

        if not matches:
            raise ValueError(f"No section structure found in {path}")

        doc_name = os.path.basename(path)
        documents[doc_name] = {}

        for sec, text in matches:
            documents[doc_name][sec.strip()] = text.strip().replace("\n", " ")

    if len(documents) != len(file_paths):
        raise ValueError("Some documents failed to load.")

    return documents


# ---------------- SKILL 2 ----------------
def answer_question(question, documents):
    q = question.lower()

    # keyword mapping (STRICT, no hallucination)
    intent_map = {
        "carry forward": ("policy_hr_leave.txt", "2.6"),
        "unused leave": ("policy_hr_leave.txt", "2.6"),
        "slack": ("policy_it_acceptable_use.txt", "2.3"),
        "install": ("policy_it_acceptable_use.txt", "2.3"),
        "home office equipment": ("policy_finance_reimbursement.txt", "3.1"),
        "equipment allowance": ("policy_finance_reimbursement.txt", "3.1"),
        "personal phone": ("policy_it_acceptable_use.txt", "3.1"),
        "work files": ("policy_it_acceptable_use.txt", "3.1"),
        "da and meal": ("policy_finance_reimbursement.txt", "2.6"),
        "meal receipts": ("policy_finance_reimbursement.txt", "2.6"),
        "leave without pay": ("policy_hr_leave.txt", "5.2"),
    }

    for key, (doc, sec) in intent_map.items():
        if key in q:
            if doc in documents and sec in documents[doc]:
                text = documents[doc][sec]
                return f"{text} (Source: {doc}, Section {sec})"

    return REFUSAL_RESPONSE

# ---------------- MAIN ----------------
def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    args = parser.parse_args()

    try:
        file_paths = [
            "../data/policy-documents/policy_hr_leave.txt",
            "../data/policy-documents/policy_it_acceptable_use.txt",
            "../data/policy-documents/policy_finance_reimbursement.txt"
        ]

        documents = retrieve_documents(file_paths)

        print("📄 Documents loaded. Ask your questions (type 'exit' to quit):\n")

        while True:
            question = input("❓ ").strip()

            if question.lower() == "exit":
                print("👋 Exiting...")
                break

            if not question:
                print("⚠️ Please enter a valid question.")
                continue

            answer = answer_question(question, documents)
            print(f"\n👉 {answer}\n")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()