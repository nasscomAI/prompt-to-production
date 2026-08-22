import argparse
import glob
import os
import sys
from dotenv import load_dotenv
from groq import Groq

# Load API key from root .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

client = Groq(max_retries=3)

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant team for guidance."
)

def retrieve_documents(policy_dir: str) -> dict:
    """Skill: retrieve_documents - Loads all policy files from directory."""
    documents = {}
    search_path = os.path.join(policy_dir, "*.txt")
    files = glob.glob(search_path)
    
    if not files:
        print(f"Error: No policy documents found in path: {policy_dir}")
        sys.exit(1)
        
    for filepath in files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            documents[filename] = f.read()
            
    return documents

def answer_question(query: str, documents: dict) -> str:
    """Skill: answer_question - Evaluates query strictly against single-source constraint."""
    doc_context = "\n\n=== DOCUMENT SEPARATOR ===\n\n".join(
        [f"--- DOCUMENT: {fname} ---\n{content}" for fname, content in documents.items()]
    )

    system_prompt = f"""You are a strict single-source policy assistant.

RULES YOU MUST FOLLOW AT ALL COSTS:
1. Answer the query strictly using details from AT MOST ONE source document. NEVER blend or synthesize facts from two or more documents into a single answer.
2. Every factual statement MUST cite the source filename and exact section number (e.g. [policy_it_acceptable_use.txt - Section 3.1]).
3. NEVER use hedging language like "while not explicitly covered", "typically", "generally", or "common practice".
4. If the question cannot be directly and fully answered by a single document, OR if it is completely unmentioned, you MUST return EXACTLY this text and nothing else:

{REFUSAL_TEMPLATE}"""

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",  # Replaces deprecated llama3-70b-8192
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context Documents:\n{doc_context}\n\nQuestion: {query}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API Error: {e}")
        return REFUSAL_TEMPLATE

def main():
    parser = argparse.ArgumentParser(description="UC-X Single-Source Policy Q&A")
    parser.add_argument("--policy-dir", default="../data/policy-documents", help="Directory containing policy files")
    args = parser.parse_args()

    print(f"Loading documents from {args.policy_dir}...")
    documents = retrieve_documents(args.policy_dir)
    print(f"Successfully loaded {len(documents)} policy document(s).\n")

    print("Interactive CLI Ready. Type your question (or 'exit' / 'quit' to stop):\n")
    
    while True:
        try:
            user_input = input("Question: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting...")
                break

            answer = answer_question(user_input, documents)
            print(f"\nAnswer:\n{answer}\n")
            print("-" * 60)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()