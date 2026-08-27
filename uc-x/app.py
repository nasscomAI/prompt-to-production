"""
UC-X — Ask My Documents
Gemini integration that fiercely refuses cross-document blending and hedging.
"""
import argparse
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERROR: Please install: pip install google-genai")
    sys.exit(1)

def get_system_prompt() -> str:
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        agents_path = os.path.join(script_dir, 'agents.md')
        with open(agents_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "Answer based on documents only."

def retrieve_documents(doc_paths: list) -> str:
    """Loads and formats all provided files into a strictly segregated index."""
    combined_docs = ""
    for path in doc_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                filename = os.path.basename(path)
                combined_docs += f"--- START OF DOCUMENT: {filename} ---\n"
                combined_docs += content
                combined_docs += f"\n--- END OF DOCUMENT: {filename} ---\n\n"
        except FileNotFoundError:
            print(f"Warning: Could not find {path}")
    return combined_docs

def answer_question(client, documents_context: str, question: str, system_prompt: str) -> str:
    prompt = (
        f"Available Documents:\n{documents_context}\n\n"
        f"User Question: {question}\n\n"
        f"CRITICAL ENFORCEMENT: Never blend documents. Never use hedging phrasing. Output the exact refusal template if uncertain."
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0
            )
        )
        return response.text
    except Exception as e:
        return "This question is not covered in the available policy documents\n(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance."

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(">> WARNING: GEMINI_API_KEY is not set!")
        sys.exit(1)

    print("Loading indexing system...")
    
    # Resolving absolute or relative paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = [
        os.path.join(base_dir, 'data', 'policy-documents', 'policy_hr_leave.txt'),
        os.path.join(base_dir, 'data', 'policy-documents', 'policy_it_acceptable_use.txt'),
        os.path.join(base_dir, 'data', 'policy-documents', 'policy_finance_reimbursement.txt')
    ]
    
    documents_context = retrieve_documents(paths)
    client = genai.Client(api_key=api_key)
    system_prompt = get_system_prompt()
    
    print("\nSystem ready! Type your question below (or type 'exit' to quit).")
    
    while True:
        try:
            q = input("\nQ: ").strip()
            if q.lower() in ['exit', 'quit']:
                print("Exiting...")
                break
            if not q:
                continue
                
            ans = answer_question(client, documents_context, q, system_prompt)
            print(f"\nA: {ans}\n")
        except KeyboardInterrupt:
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
