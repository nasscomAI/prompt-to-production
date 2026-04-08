"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import sys
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

try:
    from google import genai
except ImportError:
    print("ERROR: Required libraries not found.")
    print("Please install them using: pip install google-genai")
    sys.exit(1)

def get_system_prompt() -> str:
    """Read the system prompt from agents.md."""
    agents_path = os.path.join(os.path.dirname(__file__), 'agents.md')
    if os.path.exists(agents_path):
        with open(agents_path, 'r', encoding='utf-8') as f:
            return f.read()
    print("Warning: agents.md not found.")
    return ""

def retrieve_documents() -> str:
    """Loads all 3 policy files and returns them as a single formatted string formatted by text."""
    docs = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    # Go up one dir to find 'data/policy-documents'
    current_dir = os.path.dirname(__file__)
    # For when __file__ is empty string or '.'
    if not current_dir:
        current_dir = "."
    base_dir = os.path.join(current_dir, '..', 'data', 'policy-documents')
    
    content = []
    for doc in docs:
        path = os.path.join(base_dir, doc)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content.append(f"--- Document: {doc} ---\n{f.read()}\n")
        else:
            print(f"Warning: Could not find {path}")
            
    if not content:
        raise ValueError(f"No policy documents could be read from {base_dir}")
        
    return "\n".join(content)

def answer_question(question: str, documents_text: str) -> str:
    """Answers a question using Gemini based STRICTLY on the policy documents."""
    system_instruction = get_system_prompt()
    
    prompt = f"Documents:\n{documents_text}\n\nUser Question:\n{question}"
    
    if 'GEMINI_API_KEY' not in os.environ:
        return "ERROR: Environment variable GEMINI_API_KEY is not set."
        
    client = genai.Client()
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            'system_instruction': system_instruction,
            'temperature': 0.0,
        },
    )
    return response.text

def main():
    print("UC-X — Ask My Documents")
    print("Loading policy documents...")
    try:
        documents_text = retrieve_documents()
    except Exception as e:
        print(f"Failed to load documents: {e}")
        return
        
    print("Documents loaded. Type your question or 'quit' to exit.")
    
    while True:
        try:
            question = input("\nQ: ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break
            if not question:
                continue
                
            print("Thinking...")
            answer = answer_question(question, documents_text)
            print(f"\nA: {answer}")
        except KeyboardInterrupt:
            break
        except EOFError:
            break
            
if __name__ == "__main__":
    main()
