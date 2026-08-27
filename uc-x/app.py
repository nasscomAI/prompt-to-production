import os
import sys
from google import genai
from google.genai import types

def retrieve_documents():
    """
    Loads all three policy files (HR, IT, Finance) and indexes their contents.
    Raises an error if any of the three required policy documents are missing.
    """
    base_dir = os.path.dirname(__file__)
    doc_paths = {
        "policy_hr_leave.txt": os.path.join(base_dir, "../data/policy-documents/policy_hr_leave.txt"),
        "policy_it_acceptable_use.txt": os.path.join(base_dir, "../data/policy-documents/policy_it_acceptable_use.txt"),
        "policy_finance_reimbursement.txt": os.path.join(base_dir, "../data/policy-documents/policy_finance_reimbursement.txt")
    }
    
    indexed_docs = {}
    for doc_name, path in doc_paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required policy document missing: {path}")
        with open(path, "r", encoding="utf-8") as f:
            indexed_docs[doc_name] = f.read()
            
    return indexed_docs

def answer_question(question, indexed_docs):
    """
    Searches the indexed policy documents and returns a single-source factual answer 
    or the exact refusal template.
    """
    client = genai.Client()
    
    system_instruction = """Role:
Policy document Q&A agent. Its operational boundary is to answer questions strictly based on the provided company policy documents without combining claims from multiple documents.

Intent:
Provide accurate, factual answers to user questions. A correct output either answers the question by citing a single source document name and section number for every factual claim, or outputs the exact refusal template.

Context:
The agent is allowed to use only the provided policy documents. Exclude any external knowledge, common practices, or assumptions.

Enforcement:
- "Never combine claims from two different documents into a single answer."
- "Never use hedging phrases: 'while not explicitly covered', 'typically', 'generally understood', 'it is common practice'."
- "Cite source document name + section number for every factual claim."
- "If question is not in the documents — use the refusal template exactly, no variations: 'This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.'"
"""

    context_str = "AVAILABLE POLICY DOCUMENTS:\n\n"
    for doc_name, content in indexed_docs.items():
        context_str += f"--- {doc_name} ---\n{content}\n\n"

    prompt = f"{context_str}\nUser Question: {question}"

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.0
        )
    )
    
    return response.text.strip()

def main():
    print("Loading policy documents...")
    try:
        indexed_docs = retrieve_documents()
    except Exception as e:
        print(f"Error loading documents: {e}")
        sys.exit(1)

    print("Documents loaded successfully.")
    print("Interactive CLI — type questions, read answers. Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            question = input("Question: ")
            if question.lower() in ['exit', 'quit']:
                break
            if not question.strip():
                continue
                
            answer = answer_question(question, indexed_docs)
            print(f"\nAnswer:\n{answer}\n")
            print("-" * 40)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
