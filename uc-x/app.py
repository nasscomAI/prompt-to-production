"""
UC-X app.py — Interactive Ask My Documents CLI
"""
import argparse
import os
import sys
from openai import OpenAI

def retrieve_documents():
    """
    Skill: retrieve_documents — loads all 3 policy files, indexes by document name and section number.
    """
    documents = {}
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, 'data', 'policy-documents')
    
    files = [
        'policy_hr_leave.txt',
        'policy_it_acceptable_use.txt',
        'policy_finance_reimbursement.txt'
    ]
    
    for filename in files:
        filepath = os.path.join(docs_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                documents[filename] = f.read()
        except FileNotFoundError:
            print(f"Warning: Could not find {filepath}", file=sys.stderr)
            
    return documents

def answer_question(client, documents, question):
    """
    Skill: answer_question — searches indexed documents, returns single-source answer + citation OR refusal template.
    """
    
    context_str = "\n\n".join([f"--- Document: {name} ---\n{content}" for name, content in documents.items()])
    
    system_prompt = f"""You are a strict company policy assistant.
ROLE: A strict policy assistant that only provides factual answers derived directly from the provided company policy documents without hallucination or cross-document blending.

INTENT: Return factual, single-source answers with exact section citations from the policy documents, or use an exact refusal template if the answer cannot be found.

CONTEXT: Information is strictly limited to the provided documents. You must explicitly exclude any outside knowledge or common sense.

ENFORCEMENT RULES:
1. Never combine claims from two different documents into a single answer
2. Never use hedging phrases: "while not explicitly covered", "typically", "generally understood", "it is common practice"
3. If question is not in the documents — use the refusal template exactly, no variations:
"This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."
4. Cite source document name + section number for every factual claim

DOCUMENTS:
{context_str}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.0
    )
    
    return response.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents CLI")
    args = parser.parse_args()

    # Initialize OpenAI client
    try:
        client = OpenAI()
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        print("Please ensure OPENAI_API_KEY environment variable is set.")
        sys.exit(1)

    print("Loading documents...")
    documents = retrieve_documents()
    if not documents:
        print("Error: No policy documents found. Please check the data/policy-documents directory.")
        sys.exit(1)
        
    print(f"Loaded {len(documents)} documents.")
    print("Interactive CLI started. Type 'exit' or 'quit' to exit.")
    
    while True:
        try:
            question = input("\nQuestion: ").strip()
            if question.lower() in ['exit', 'quit']:
                break
            if not question:
                continue
                
            answer = answer_question(client, documents, question)
            print(f"\nAnswer:\n{answer}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError processing question: {e}")

if __name__ == "__main__":
    main()
