"""
UC-X app.py
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import os
from google import genai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

DOC_PATHS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}


def retrieve_documents_naive() -> str:
    combined = ""
    for name, path in DOC_PATHS.items():
        with open(path, encoding="utf-8") as f:
            combined += f"\n\n=== {name} ===\n" + f.read()
    return combined


def answer_question_naive(all_docs_text: str, question: str) -> str:
    """NAIVE VERSION — deliberately weak, no enforcement yet."""
    prompt = f"Answer questions about company policy.\n\nDocuments:\n{all_docs_text}\n\nQuestion: {question}"
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )
    return response.text


def main():
    print("Loading documents...")
    all_docs_text = retrieve_documents_naive()
    print("Ready. Ask a question (Ctrl+C to exit).\n")

    while True:
        try:
            question = input("Q: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
        answer = answer_question_naive(all_docs_text, question)
        print(f"A: {answer}\n")


if __name__ == "__main__":
    main()