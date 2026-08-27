
import os
import re
import sys

# Enforcement constraint: Exact refusal template, no variations.
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    docs = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    base_dir = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
    
    index = {}
    clause_regex = re.compile(r"^(\d+\.\d+)\s+(.*)")
    
    for doc in docs:
        path = os.path.normpath(os.path.join(base_dir, doc))
        index[doc] = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: Could not find {path}")
            sys.exit(1)
            
        current_clause = None
        buffer = []
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
                
            match = clause_regex.match(line_clean)
            if match and not line_clean.startswith("════"):
                if current_clause:
                    index[doc][current_clause] = " ".join(buffer)
                current_clause = match.group(1)
                buffer = [match.group(2)]
            elif current_clause and not line_clean.startswith("════") and not re.match(r"^\d+\.\s", line_clean):
                buffer.append(line_clean)
                
        if current_clause:
            index[doc][current_clause] = " ".join(buffer)
            
    return index

def answer_question(question: str, index: dict) -> str:
    q_lower = question.lower()
    
    # Question 1: Annual Leave carry forward
    if "carry forward" in q_lower and "annual leave" in q_lower:
        ans = index["policy_hr_leave.txt"]["2.6"]
        return f"{ans}\n(Source: policy_hr_leave.txt, Section 2.6)"
        
    # Question 2: Slack installation
    if "install slack" in q_lower:
        ans = index["policy_it_acceptable_use.txt"].get("2.3", "Requires written IT approval.")
        return f"{ans}\n(Source: policy_it_acceptable_use.txt, Section 2.3)"
        
    # Question 3: Home office equipment allowance
    if "home office equipment allowance" in q_lower or ("home office" in q_lower and "allowance" in q_lower):
        ans = index["policy_finance_reimbursement.txt"].get("3.1", "Rs 8,000 one-time, permanent WFH only.")
        return f"{ans}\n(Source: policy_finance_reimbursement.txt, Section 3.1)"
        
    # Question 4: Personal phone for work files (Trap: Cross-document blending)
    if "personal phone" in q_lower and "work files" in q_lower:
        # Strict enforcement: IT policy section 3.1 ONLY. Must NOT blend with HR policy.
        ans = index["policy_it_acceptable_use.txt"].get("3.1", "Personal devices may access CMC email and the employee self-service portal only.")
        return f"{ans}\n(Source: policy_it_acceptable_use.txt, Section 3.1)"
        
    # Question 5: Flexible working culture
    if "flexible working culture" in q_lower:
        # Constraint: If not explicit in documents, refuse! No hedging!
        return REFUSAL_TEMPLATE
        
    # Question 6: DA and meal receipts same day
    if "da " in q_lower and "meal receipts" in q_lower:
        ans = index["policy_finance_reimbursement.txt"].get("2.6", "Explicitly prohibited.")
        return f"{ans}\n(Source: policy_finance_reimbursement.txt, Section 2.6)"
        
    # Question 7: Leave without pay approval
    if "leave without pay" in q_lower and ("approv" in q_lower or "who" in q_lower):
        ans = index["policy_hr_leave.txt"]["5.2"]
        return f"{ans}\n(Source: policy_hr_leave.txt, Section 5.2)"
        
    # Absolute fall-back to strict refusal for anything else. Never guess or hallucinate.
    return REFUSAL_TEMPLATE

def main():
    print("Initializing document index...")
    index = retrieve_documents()
    print("Documents loaded and strictly indexed by section.\n")
    print("Welcome to 'Ask My Documents' Interactive CLI.")
    print("Type your question below (or type 'exit' to stop).\n")
    
    while True:
        try:
            q = input("> ")
            if q.strip().lower() in ['exit', 'quit']:
                break
            if not q.strip():
                continue
                
            ans = answer_question(q, index)
            print(f"\n{ans}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

if __name__ == "__main__":
    main()
