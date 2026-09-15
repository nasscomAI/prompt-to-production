"""
UC-X — Ask My Documents
Interactive grounded policy assistant enforcing single-source answers and strict refusal.
"""
import os
import re
import sys
from google import genai
from google.genai import types

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("MODEL_NAME", "models/gemini-3.5-flash-lite")

if not api_key:
    print("Error: GEMINI_API_KEY environment variable is not set.")
    print("Run: set GEMINI_API_KEY=your_actual_key")
    sys.exit(1)

client = genai.Client(api_key=api_key)

DOC_PATHS = [
    os.path.join("..", "data", "policy-documents", "policy_hr_leave.txt"),
    os.path.join("..", "data", "policy-documents", "policy_it_acceptable_use.txt"),
    os.path.join("..", "data", "policy-documents", "policy_finance_reimbursement.txt"),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

CRAFT_SYSTEM_PROMPT = f"""You are a strict compliance officer answering employee questions based ONLY on the provided policy documents.

CORE ENFORCEMENT RULES:
1. NEVER COMBINE OR BLEND CLAIMS from different documents. Your answer must originate from exactly ONE document. If answering requires synthesizing permissions across HR and IT, you must NOT give combined permission.
2. NEVER USE HEDGING LANGUAGE: Ban phrases like "while not explicitly covered", "typically", "generally understood", "it is common practice", or "usually".
3. RETAIN ALL CONDITIONS: Never drop approval prerequisites, monetary limits, or forfeiture dates.
4. CITE SOURCE: Every valid answer must include the exact document filename and section number.
5. MANDATORY REFUSAL TEMPLATE: If the question is not directly covered in the documents, or if you cannot answer from a single document with certainty, you MUST respond ONLY with the exact text below, replacing [relevant team] with HR, IT, or Finance as appropriate:

{REFUSAL_TEMPLATE}
"""

def retrieve_documents() -> str:
    """Load and index all three policy documents."""
    combined_docs = []
    for path in DOC_PATHS:
        # Fallback check if running from repository root instead of uc-x
        target_path = path
        if not os.path.exists(target_path):
            alt_path = path.replace(".." + os.sep, "")
            if os.path.exists(alt_path):
                target_path = alt_path
            else:
                raise FileNotFoundError(f"Could not locate policy file: {path}")

        filename = os.path.basename(target_path)
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            combined_docs.append(f"=== START OF DOCUMENT: {filename} ===\n{content}\n=== END OF DOCUMENT: {filename} ===")

    return "\n\n".join(combined_docs)

def answer_question(question: str, context: str) -> str:
    """Query the model with single-source enforcement and refusal rules."""
    prompt = f"""CONTEXT DOCUMENTS:
{context}

USER QUESTION:
{question}

RESPONSE:"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=CRAFT_SYSTEM_PROMPT,
                temperature=0.0
            )
        )
        return response.text.strip()
    except Exception as e:
        return f"Error querying model: {e}"

def main():
    print("Loading policy documents...")
    try:
        context = retrieve_documents()
        print("Documents successfully loaded:")
        print(" - policy_hr_leave.txt")
        print(" - policy_it_acceptable_use.txt")
        print(" - policy_finance_reimbursement.txt")
        print("\nUC-X Policy Assistant Ready. (Type 'exit' or 'quit' to stop)\n" + "-"*50)
    except FileNotFoundError as e:
        print(f"Startup Error: {e}")
        return

    while True:
        try:
            user_query = input("\nAsk a question: ").strip()
            if not user_query:
                continue
            if user_query.lower() in ["exit", "quit", "q"]:
                print("Exiting...")
                break

            answer = answer_question(user_query, context)
            print(f"\nAnswer:\n{answer}\n" + "-"*50)
        except KeyboardInterrupt:
            print("\nSession ended.")
            break

if __name__ == "__main__":
    main()