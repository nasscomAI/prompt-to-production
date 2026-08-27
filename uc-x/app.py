import os
import sys
import argparse

try:
    import google.generativeai as genai
except ImportError:
    print("Please install google-generativeai: pip install google-generativeai")
    sys.exit(1)

# Configure API key
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("Warning: GEMINI_API_KEY environment variable is not set. API calls will fail.")

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

SYSTEM_INSTRUCTION = f"""role: >
  Company Policy Q&A Assistant. The operational boundary is restricted strictly to answering employee questions based ONLY on the provided HR, IT, and Finance policy documents.

intent: >
  Provide accurate, single-source factual answers containing explicit citations (document name + section number) for every claim, or return an exact predefined refusal template if the answer is unavailable or ambiguous.

context: >
  The agent is only allowed to use the following files: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt. It must explicitly exclude all external knowledge, assumptions, or inferences not directly stated in these documents.

enforcement:
  - "Never combine claims from two different documents into a single answer."
  - "Never use hedging phrases: 'while not explicitly covered', 'typically', 'generally understood', 'it is common practice'."
  - "Cite source document name + section number for every factual claim."
  - "If question is not in the documents (or if answering requires blending), use the refusal template exactly, no variations: '{REFUSAL_TEMPLATE.replace('\n', ' ')}'\""""

def retrieve_documents(docs_dir):
    """
    Loads all 3 policy files, indexes by document name and section number.
    """
    documents = {}
    expected_files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    for filename in expected_files:
        filepath = os.path.join(docs_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Policy file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            # Storing content; the model will parse section numbers from the text.
            documents[filename] = f.read()
            
    return documents

def answer_question(question, documents):
    """
    Searches indexed documents, returns single-source answer + citation OR refusal template.
    """
    context = "Here are the policy documents:\n\n"
    for doc_name, content in documents.items():
        context += f"--- BEGIN {doc_name} ---\n{content}\n--- END {doc_name} ---\n\n"
        
    prompt = f"{context}\nQuestion: {question}\nAnswer:"
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error communicating with Gemini API: {e}"

def main():
    parser = argparse.ArgumentParser(description="UC-X: Ask My Documents CLI")
    parser.parse_args()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(base_dir, "..", "data", "policy-documents")
    
    try:
        documents = retrieve_documents(docs_dir)
    except Exception as e:
        print(f"Error loading documents: {e}")
        return

    print("Policy Q&A Assistant Initialized.")
    print("Type your questions based on HR, IT, and Finance policies.")
    print("Type 'quit' or 'exit' to stop.")
    print("-" * 60)
    
    while True:
        try:
            question = input("\nQuestion: ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break
            if not question:
                continue
                
            print("Thinking...")
            answer = answer_question(question, documents)
            print(f"\nAnswer:\n{answer}")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()
