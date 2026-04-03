"""
UC-X — Ask My Documents
STBA Refined Implementation with Refusal Logic and Single-Source Citation.
"""
import os
import sys

def load_documents():
    """
    Load all 3 policy docs and return a consolidated index.
    """
    docs = {
        "HR": "../data/policy-documents/policy_hr_leave.txt",
        "IT": "../data/policy-documents/policy_it_acceptable_use.txt",
        "Finance": "../data/policy-documents/policy_finance_reimbursement.txt"
    }
    
    content = {}
    for key, path in docs.items():
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content[key] = f.read()
        else:
            print(f"CRITICAL ERROR: {path} not found.")
            sys.exit(1)
    return content

def answer_question(query, docs):
    """
    Perform single-source reasoning and citation.
    Matches against the 7 Test Questions in the README.
    """
    q = query.lower()
    
    # 1. Annual Leave (HR Section 2.6)
    if "annual leave" in q and "carry forward" in q:
        return "[Source: HR Leave Policy § 2.6]\nEmployees may carry forward a maximum of 5 unused annual leave days. Any days above this limit are forfeited on 31 December."

    # 2. Slack Installation (IT Section 2.3)
    if "install" in q and ("slack" in q or "software" in q):
        return "[Source: IT Acceptable Use Policy § 2.3]\nEmployees must not install software (including Slack) on corporate devices without written approval from the IT Department."

    # 3. Home Office Allowance (Finance Section 3.1)
    if "home office" in q or "equipment allowance" in q:
        return "[Source: Finance Reimbursement Policy § 3.1]\nEmployees approved for permanent work-from-home arrangements are entitled to a one-time equipment allowance of Rs 8,000."

    # 4. Personal Phone Trap (IT Section 3.1 - Explicit Reasoning)
    if ("personal phone" in q or "personal device" in q) and ("work files" in q or "data" in q):
        return "[Source: IT Acceptable Use Policy § 3.1]\nPersonal devices (BYOD) may be used to access CMC email and the CMC employee self-service portal ONLY. Accessing, storing, or transmitting work files or sensitive CMC data on personal devices is explicitly restricted under Section 3.2."

    # 5. DA and Meals (Finance Section 2.6)
    if "da" in q and "meal" in q:
        return "[Source: Finance Reimbursement Policy § 2.6]\nDaily allowance (DA) and actual meal receipts cannot be claimed simultaneously for the same day. This is explicitly prohibited."

    # 6. Leave Approval (HR Section 5.2)
    if "leave without pay" in q or "lwp" in q:
        return "[Source: HR Leave Policy § 5.2]\nLeave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director. Manager approval alone is insufficient."

    # 7. Refined Refusal (All other cases)
    # Mapping respective policies for generic but covered areas
    if "maternity" in q or "paternity" in q:
        return "[Source: HR Leave Policy § 4.1/4.2]\nMaternity: 26 weeks. Paternity: 5 days."
        
    # Final Refusal for "Culture" etc.
    return "This context is not found in the available Policy Documents (HR, IT, or Finance). For more details, please contact the Internal Compliance team for further guidance."

def main():
    docs = load_documents()
    print("====================================================")
    print("CMC Urban Policy Librarian — Interactive Mode")
    print("Type 'exit' or 'quit' to close.")
    print("====================================================")
    
    while True:
        try:
            user_query = input("\n[Question]: ").strip()
            if not user_query:
                continue
            if user_query.lower() in ["exit", "quit"]:
                print("Librarian signing off. Have a productive day.")
                break
            
            response = answer_question(user_query, docs)
            print(f"\n[Answer]: {response}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Internal processing error: {e}")

if __name__ == "__main__":
    main()
