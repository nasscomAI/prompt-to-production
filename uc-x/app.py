import os
import sys

# Try to import the OpenAI library, or warn the user
try:
    from openai import OpenAI
except ImportError:
    print("Error: The 'openai' library is required.")
    print("Please install it running: pip install openai")
    sys.exit(1)

def load_documents():
    """Loads the policy documents and returns them as a single string."""
    docs = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    content = ""
    for doc in docs:
        try:
            with open(doc, 'r', encoding='utf-8') as f:
                content += f"\n--- Start of {os.path.basename(doc)} ---\n"
                content += f.read()
                content += f"\n--- End of {os.path.basename(doc)} ---\n"
        except FileNotFoundError:
            print(f"Warning: Could not find document {doc}")
            
    return content

def get_system_prompt(docs_content):
    """Returns the strict system prompt incorporating the agents.md constraints."""
    return f"""You are a strict corporate policy answering assistant.
Your operational boundary, intent, context, and enforcement rules are absolute.

AVAILABLE DOCUMENTS:
{docs_content}

INTENT:
Provide highly accurate, verifiable answers citing specific document names and section numbers. When information is unavailable or requires combining rules from different documents, explicitly refuse to answer.

CONTEXT:
You may only use the provided policy documents. You are explicitly forbidden from using external knowledge, common sense, "standard practice" assumptions, or blending rules across multiple policies to create new permissions.

ENFORCEMENT RULES:
1. Never combine claims from two different policy documents into a single blended answer.
2. Never use hedging phrases such as: 'while not explicitly covered', 'typically', 'generally understood', or 'it is common practice'.
3. Cite the exact source document name and section number for every factual claim made.
4. If the question is not answered in the available documents, or if it requires blending multiple policies, you MUST use EXACTLY this refusal template:
"This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
"""

def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable.")
        print("Example (Windows PowerShell): $env:OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
        
    client = OpenAI()
    print("Loading documents...")
    docs_content = load_documents()
    system_prompt = get_system_prompt(docs_content)
    
    print("\n" + "="*50)
    print("UC-X Ask My Documents — Interactive Mode")
    print("Type 'exit' or 'quit' to exit.")
    print("="*50 + "\n")
    
    while True:
        try:
            user_input = input("\nAsk a policy question: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input:
                continue
                
            response = client.chat.completions.create(
                model="gpt-4o-mini", # or gpt-3.5-turbo depending on preference
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.0 # Essential for strict adherence
            )
            
            answer = response.choices[0].message.content
            print(f"\nAnswer:\n{answer}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
