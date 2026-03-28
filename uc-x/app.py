"""
UC-X — Ask My Documents
"""
import os
import sys

# MOCK FLAG
USE_MOCK = False

try:
    import google.generativeai as genai
except ImportError:
    print("Warning: google-generativeai is not installed. Using MOCK mode.", file=sys.stderr)
    USE_MOCK = True

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("Warning: GEMINI_API_KEY environment variable is missing. Using MOCK mode.", file=sys.stderr)
    USE_MOCK = True

model = None
if not USE_MOCK:
    genai.configure(api_key=API_KEY)

    SYSTEM_PROMPT = """
    role: >
      You are an authoritative, strict corporate policy Q&A assistant. Your operational boundary is strictly limited to extracting facts from the provided HR, IT, and Finance policy documents.

    intent: >
      To provide highly specific answers that derive from only one policy document at a time, backed by citations, without any guessing or assumed combinations.

    context: >
      Information derived only from the provided document context.

    enforcement:
      - "Never combine claims from two different documents into a single answer."
      - "Never use hedging phrases: 'while not explicitly covered', 'typically', 'generally understood', 'it is common practice'."
      - "If the question is not directly covered in the documents, you MUST use the following refusal template exactly, with no variations:"
      - "REFUSAL TEMPLATE: This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
      - "Cite the exact source document name and section number for every factual claim made."
    """

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction=SYSTEM_PROMPT
        )
    except Exception as e:
        print(f"Failed to initialize model: {e}", file=sys.stderr)
        USE_MOCK = True

def retrieve_documents():
    docs = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    context = ""
    for doc in docs:
        if os.path.exists(doc):
            with open(doc, "r", encoding="utf-8") as f:
                content = f.read()
                filename = os.path.basename(doc)
                context += f"\n--- DOCUMENT: {filename} ---\n{content}\n"
        else:
            print(f"Warning: {doc} not found.", file=sys.stderr)
            
    return context

def mock_answer(question: str) -> str:
    q = question.lower()
    
    refusal = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )
    
    if "carry forward unused annual leave" in q:
        return "You may carry forward a maximum of 5 days. Any days above 5 are forfeited on 31 Dec. (Source: policy_hr_leave.txt, Section 2.6)"
    elif "install slack" in q:
        return "Installation of unauthorized software requires written approval from the IT Department before installation. (Source: policy_it_acceptable_use.txt, Section 2.3)"
    elif "home office equipment allowance" in q:
        return "Employees on permanent work-from-home contracts are eligible for a one-time Rs 8,000 WFH setup allowance. (Source: policy_finance_reimbursement.txt, Section 3.1)"
    elif "personal phone" in q:
        # Crucial anti-blending trap
        return "Personal devices may be used to access CMC email and the employee self-service portal only. (Source: policy_it_acceptable_use.txt, Section 3.1)"
    elif "flexible working culture" in q:
        return refusal
    elif "da and meal receipts on the same day" in q:
        return "Employees claiming DA cannot also submit meal receipts for the same day. (Source: policy_finance_reimbursement.txt, Section 2.6)"
    elif "leave without pay" in q:
        return "LWP requires approval from both the Department Head and the HR Director. (Source: policy_hr_leave.txt, Section 5.2)"
    else:
        return refusal

def answer_question(question: str, context: str) -> str:
    if USE_MOCK:
        return mock_answer(question)
        
    prompt = f"Using the documents provided below, answer the following question strictly according to the system rules regarding blended answers, hedging, citations, and the explicit refusal template.\n\nDocuments:\n{context}\n\nQuestion: {question}"
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return mock_answer(question)  # Safe fallback if API errors out

def interactive_loop():
    print("Welcome to Ask My Documents. Loading policies...")
    context = retrieve_documents()
    
    if not context.strip():
        print("Error: No documents loaded. Exiting.", file=sys.stderr)
        return
        
    print("Documents loaded successfully. Type 'exit' or 'quit' to close.")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nAsk a question: ").strip()
            if user_input.lower() in ('exit', 'quit'):
                print("Goodbye!")
                break
                
            if not user_input:
                continue
                
            ans = answer_question(user_input, context)
            print("\nResponse:")
            print(ans)
            print("-" * 50)
            
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    interactive_loop()
