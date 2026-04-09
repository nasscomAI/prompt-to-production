"""
UC-X app.py — Policy Query Assistant
Built using RICE framework, agents.md constraints, and skills.md logic.
"""
import os
import sys

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Please install the google-genai SDK first: pip install google-genai")
    sys.exit(1)

def retrieve_documents(file_paths):
    """
    Skill: retrieve_documents
    Loads policy files and prepares them for the context block.
    """
    indexed_docs = {}
    for filepath in file_paths:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Missing policy file: {filepath}")
        
        filename = os.path.basename(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            indexed_docs[filename] = f.read()
            
    return indexed_docs

def generate_system_prompt(indexed_docs):
    """Builds the system prompt precisely as dictated by agents.md"""
    prompt = """ROLE:
A strict policy query assistant that answers questions exclusively using provided HR, IT, and Finance policy documents.

INTENT:
Provide accurate, single-source answers with explicit document and section citations, strictly adhering to the provided documents without blending policies or hallucinating permissions.

CONTEXT:
The agent is only allowed to use the three provided policy documents below.
The agent must absolutely NOT use any external knowledge or general assumptions.

--- POLICY DOCUMENTS ---
"""
    for title, content in indexed_docs.items():
        prompt += f"\n--- {title} ---\n{content}\n"
        
    prompt += """
ENFORCEMENT:
- "Never combine claims from two different documents into a single answer."
- "Never use hedging phrases: 'while not explicitly covered', 'typically', 'generally understood', 'it is common practice'."
- "Cite source document name + section number for every factual claim."
- "If question is not in the documents or if compliance relies on combining policies, output the exact refusal template: 'This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.' No other variations are permitted."
"""
    return prompt

def answer_question(client, question, system_prompt):
    """
    Skill: answer_question
    Calls Gemini to answer based strictly on the policies and refusal conditions.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0
            )
        )
        return response.text
    except Exception as e:
        return f"Error generating answer: {e}"

def main():
    print("Initializing Ask My Documents...")
    policy_files = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    try:
        indexed_docs = retrieve_documents(policy_files)
    except Exception as e:
        print(f"Initialization Failed: {e}")
        return
        
    system_prompt = generate_system_prompt(indexed_docs)
    
    try:
        client = genai.Client()
    except Exception as e:
        print("Failed to initialize Google GenAI client. Ensure GEMINI_API_KEY is set in your environment.")
        return

    print("\n✅ Setup complete. Policy Assistant Ready!")
    print("Type your questions below. Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            q = input("Question: ").strip()
            if q.lower() in ['exit', 'quit']:
                break
            if not q:
                continue
                
            ans = answer_question(client, q, system_prompt)
            print(f"\nAnswer:\n{ans}\n")
            print("-" * 40)
            
        except KeyboardInterrupt:
            break
        except EOFError:
            break
            
    print("\nExiting Policy Assistant.")

if __name__ == "__main__":
    main()
