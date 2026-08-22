"""
UC-X app.py
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import os
import re
from google import genai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

DOC_PATHS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGE_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "however, the documents do reference",
    "there is no explicit mention",
]


def retrieve_documents() -> dict:
    """Loads all 3 policy files, indexed by document name."""
    docs = {}
    for name, path in DOC_PATHS.items():
        with open(path, encoding="utf-8") as f:
            docs[name] = f.read()
    return docs


def answer_question(docs: dict, question: str) -> str:
    """
    ENFORCED VERSION — strict single-source citation required,
    exact refusal template required for out-of-scope questions,
    hedge phrases explicitly forbidden and checked in code.
    """
    combined_docs = "\n\n".join(f"=== {name} ===\n{text}" for name, text in docs.items())

    prompt = f"""You are a strict policy Q&A system. Answer using ONLY the documents below.

STRICT RULES:
1. Answer from EXACTLY ONE document. Never combine or blend facts from two different documents into one answer.
2. If the question is not covered by any single document's content, respond with EXACTLY this text and nothing else:
"{REFUSAL_TEMPLATE}"
3. Never use hedging phrases like "while not explicitly covered", "typically", "generally understood", "it is common practice", or similar softening language. Either answer directly with a citation, or use the exact refusal template. No middle ground.
4. Every factual claim must cite the source document name and section number, e.g. "(Source: policy_hr_leave.txt, section 2.6)".
5. If answering would require combining two documents to make sense, use the refusal template instead of guessing.

Documents:
{combined_docs}

Question: {question}

Answer:"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )
    answer = response.text.strip()

    # --- ENFORCEMENT: check for hedge phrases in the actual output ---
    lower_answer = answer.lower()
    for phrase in HEDGE_PHRASES:
        if phrase in lower_answer:
            return REFUSAL_TEMPLATE + "\n[ENFORCEMENT: response contained a forbidden hedge phrase and was replaced with the refusal template.]"

    return answer


def main():
    print("Loading documents...")
    docs = retrieve_documents()
    print("Ready. Ask a question (Ctrl+C to exit).\n")

    while True:
        try:
            question = input("Q: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
        if not question.strip():
            continue
        answer = answer_question(docs, question)
        print(f"A: {answer}\n")


if __name__ == "__main__":
    main()