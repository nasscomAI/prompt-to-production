"""
UC-X — Ask My Documents
Interactive QA CLI on CMC policy documents.
"""
import os
import sys
from dotenv import load_dotenv

# Lazy load client helper to prevent immediate crash on import if API key is missing
_client = None

def get_client():
    """
    Initialize and return the GenAI client.
    """
    global _client
    if _client is None:
        load_dotenv()
        from google import genai
        if not os.environ.get("GEMINI_API_KEY"):
            # Try loading from the root folder directory
            load_dotenv(dotenv_path="../.env")
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it in your .env file.")
        _client = genai.Client()
    return _client


def retrieve_documents() -> dict:
    """
    Skill: Loads all 3 policy text files and returns them as a dictionary.
    """
    paths = {
        "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
    }
    documents = {}
    for doc_name, path in paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required policy document missing: {path}")
        with open(path, "r", encoding="utf-8") as f:
            documents[doc_name] = f.read().strip()
    return documents


def answer_question(documents: dict, question: str) -> str:
    """
    Skill: Uses Gemini model to search the indexed policies and returns a single-source answer with section citation,
    or outputs the verbatim refusal template.
    """
    refusal_template = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )
    
    # Format policy documents context
    context_str = ""
    for doc_name, doc_content in documents.items():
        context_str += f"=== DOCUMENT: {doc_name} ===\n{doc_content}\n\n"
        
    prompt = f"""
    You are an HR/IT/Finance Policy QA Assistant.
    Your task is to answer the user's question based strictly on the provided policy documents.
    
    Available Policy Documents:
    {context_str}
    
    CRITICAL ENFORCEMENT RULES:
    1. NEVER combine or blend claims from two different documents into a single answer. 
       - For example, if a question (such as "Can I use my personal phone to access work files when working from home?") asks about something that involves details from different documents (HR remote work tools vs IT acceptable use device limits), you must NOT blend them. You must either answer strictly from IT policy section 3.1 only (personal devices may access email and self-service portal only) or refuse. Do not state that personal phones can be used for remote work tools unless it is explicitly written in a single document.
    2. NEVER use hedging/softening phrases such as "while not explicitly covered", "typically", "generally understood", "it is common practice", or "employees are usually expected to".
    3. If the question cannot be answered directly, completely, and unambiguously from a single source document, you MUST refuse by returning the following exact refusal template verbatim and nothing else:
    This question is not covered in the available policy documents
    (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    Please contact [relevant team] for guidance.
    4. For every factual claim you make, you MUST cite the source document name and the section number (e.g., "[policy_hr_leave.txt section 2.3]").
    
    User Question:
    "{question}"
    """
    
    try:
        client = get_client()
        from google.genai import types
        
        # Using gemini-3.1-flash-lite as standard
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return refusal_template


def main():
    print("Loading CMC policy documents...")
    try:
        documents = retrieve_documents()
        print("Documents loaded successfully.")
    except Exception as e:
        print(f"Error loading documents: {e}")
        sys.exit(1)
        
    print("\n=======================================================")
    print("Welcome to CMC Policy Assistant CLI.")
    print("Type your policy questions below. Type 'exit' or 'quit' to end.")
    print("=======================================================\n")
    
    while True:
        try:
            question = input("Ask a question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
            
        if not question:
            continue
            
        if question.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
            
        print("Analyzing...")
        answer = answer_question(documents, question)
        print(f"\nAnswer:\n{answer}\n")
        print("-" * 50)


if __name__ == "__main__":
    main()
