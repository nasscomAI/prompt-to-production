"""
UC-X app.py — Ask My Documents
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print("Please install openai: pip install openai")
    sys.exit(1)

client = OpenAI()

def retrieve_documents():
    """
    Skill: loads all 3 policy files, indexes by document name and section number.
    Since the files are small, we load them as text blocks prefixed by their source filename.
    """
    files = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    docs = {}
    for fpath in files:
        if os.path.exists(fpath):
            filename = os.path.basename(fpath)
            with open(fpath, 'r', encoding='utf-8') as f:
                docs[filename] = f.read()
        else:
            print(f"Warning: Could not find document {fpath}")
            
    return docs

def answer_question(question: str, docs: dict) -> str:
    """
    Skill: searches indexed documents, returns single-source answer + citation OR refusal template.
    Uses the agent definition from agents.md.
    """
    
    # RICE prompt derived from agents.md
    system_prompt = """
# role
Company policy assistant that answers employee questions based strictly on the provided policy documents.

# intent
Provide exact, factual, single-source answers with precise citations, and refuse any questions not covered without attempting to guess or blend information.

# context
You must rely entirely on the three provided documents: policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt. External knowledge is strictly prohibited.

# enforcement
- "Never combine claims from two different documents into a single answer."
- "Never use hedging phrases: 'while not explicitly covered', 'typically', 'generally understood', 'it is common practice'."
- "Cite source document name + section number for every factual claim."
- If the question is not covered in the documents, use the refusal template exactly, no variations:
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance.
"""
    
    # Construct context from retrieved documents
    context = ""
    for doc_name, content in docs.items():
        context += f"\n--- {doc_name} ---\n{content}\n"
        
    user_prompt = f"Available Documents Context:\n{context}\n\nEmployee Question: {question}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error connecting to AI: {e}"

def main():
    print("Loading documents...")
    docs = retrieve_documents()
    if not docs:
        print("No policy documents found. Please check paths.")
        return
        
    print(f"Loaded {len(docs)} documents.")
    print("\n--- UC-X Ask My Documents ---")
    print("Type your question below (or 'quit' to exit).")
    
    while True:
        try:
            question = input("\nQ: ").strip()
            if not question:
                continue
            if question.lower() in ['quit', 'exit', 'q']:
                break
                
            answer = answer_question(question, docs)
            print(f"\nA: {answer}")
            
        except KeyboardInterrupt:
            break
        except EOFError:
            break

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set. Classification will fail.")
    main()
