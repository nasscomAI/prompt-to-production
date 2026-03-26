import os
import re
import litellm  # type: ignore
from typing import Dict, List

# Configuration
POLICY_FILES = {
    "HR Policy": "../data/policy-documents/policy_hr_leave.txt",
    "IT Policy": "../data/policy-documents/policy_it_acceptable_use.txt",
    "Finance Policy": "../data/policy-documents/policy_finance_reimbursement.txt"
}

AGENTS_FILE = "agents.md"

def retrieve_documents() -> str:
    """
    Skill: Loads all 3 policy files and combines them into an indexed context string.
    """
    context = ""
    for doc_name, file_path in POLICY_FILES.items():
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Missing mandatory policy file: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            context += f"--- START OF DOCUMENT: {doc_name} ---\n"
            context += content
            context += f"\n--- END OF DOCUMENT: {doc_name} ---\n\n"
    return context

def get_system_prompt() -> str:
    """
    Loads agent rules from agents.md to use as the system prompt.
    """
    if not os.path.exists(AGENTS_FILE):
        return "You are a policy assistant. Answer questions based only on provided documents."
    
    with open(AGENTS_FILE, "r", encoding="utf-8") as f:
        return f.read()

def answer_question(question: str, context: str, system_prompt: str) -> str:
    """
    Skill: Searches indexed documents and returns single-source answer + citation OR refusal template.
    Uses an LLM with strict enforcement from agents.md.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"POLICY DOCUMENTS:\n\n{context}\n\nUSER QUESTION: {question}"}
    ]
    
    try:
        response = litellm.completion(
            model="gpt-4o", # Defaulting to gpt-4o, can be changed via env var
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error connecting to AI service: {str(e)}"

def main():
    print("=== UC-X Ask My Documents ===")
    print("Loading documents and agent rules...")
    
    try:
        context = retrieve_documents()
        system_prompt = get_system_prompt()
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return

    print("System ready. Type your question or 'exit' to quit.\n")
    
    while True:
        try:
            query = input("Ask a policy question: ").strip()
            if query.lower() in ["exit", "quit"]:
                break
            if not query:
                continue
                
            print("\nThinking...")
            answer = answer_question(query, context, system_prompt)
            print(f"\nANSWER:\n{answer}\n")
            print("-" * 40)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}\n")

if __name__ == "__main__":
    # Ensure OPENAI_API_KEY is checked if using default gpt-4o
    if not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable is not set.")
        print("The system may fail unless you configure litellm for a different model/provider.")
    
    main()
