"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
from google import genai

def retrieve_documents():
    base_dir = os.path.dirname(__file__)
    docs = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    content = ""
    for doc in docs:
        path = os.path.join(base_dir, "..", "data", "policy-documents", doc)
        with open(path, 'r', encoding='utf-8') as f:
            content += f"--- BEGIN DOCUMENT: {doc} ---\n"
            content += f.read()
            content += f"\n--- END DOCUMENT: {doc} ---\n\n"
    return content

def get_system_instruction():
    agents_path = os.path.join(os.path.dirname(__file__), 'agents.md')
    with open(agents_path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    print("Loading documents...")
    documents_context = retrieve_documents()
    system_instruction = get_system_instruction()
    client = genai.Client()
    
    print("Ready. Type your question (or 'exit' to quit):")
    while True:
        try:
            question = input("\nQ: ")
            if not question.strip():
                continue
            if question.strip().lower() in ['exit', 'quit']:
                break
            
            prompt = f"Documents:\n{documents_context}\n\nQuestion: {question}"
            
            # Using gemini-3.5-flash-lite to avoid restrictive limits on free tier during repeated testing
            response = client.models.generate_content(
                model='gemini-3.5-flash-lite',
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.0
                )
            )
            print(f"\nA: {response.text.strip()}")
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
