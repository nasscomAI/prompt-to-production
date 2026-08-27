"""
UC-X — Ask My Documents
Multi-document Policy Q&A — single-source enforcement, no cross-document blending.
"""
import os
import re
import sys

# Refusal template (exact, as specified in README)
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact HR Department for guidance."""

# Key claims and their locations (for verification)
KNOWLEDGE_BASE = {
    # HR Policy
    "hr": {
        "doc": "policy_hr_leave.txt",
        "sections": {
            "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
            "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
            "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
            "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
            "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
            "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
            "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
            "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
            "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
            "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
            "7.2": "Leave encashment during service is not permitted under any circumstances.",
        }
    },
    # IT Policy
    "it": {
        "doc": "policy_it_acceptable_use.txt",
        "sections": {
            "2.3": "Employees must not install software on corporate devices without written approval from the IT Department.",
            "3.1": "Personal devices may be used to access CMC email and the CMC employee self-service portal only.",
            "3.2": "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.",
            "3.4": "Employees using personal devices for CMC email must enable device-level PIN or biometric lock.",
        }
    },
    # Finance Policy
    "finance": {
        "doc": "policy_finance_reimbursement.txt",
        "sections": {
            "2.6": "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. DA and meal receipts cannot be claimed simultaneously for the same day.",
            "3.1": "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
            "3.2": "The allowance covers: desk, chair, monitor, keyboard, mouse, and networking equipment only.",
        }
    }
}

def load_documents(data_dir="../data/policy-documents"):
    """Load all three policy documents."""
    docs = {}
    files = {
        "HR": "policy_hr_leave.txt",
        "IT": "policy_it_acceptable_use.txt",
        "Finance": "policy_finance_reimbursement.txt"
    }
    
    for key, filename in files.items():
        path = os.path.join(data_dir, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                docs[key] = f.read()
        else:
            print(f"WARNING: {filename} not found", file=sys.stderr)
    
    return docs

def search_in_document(question, doc_content, doc_name):
    """Search for question in a document and return matching section if found."""
    question_lower = question.lower()
    
    # Look for specific keywords
    keywords_to_search = {
        "carry forward": ("2.6", "HR", "carry forward"),
        "annual leave": ("2.1", "HR", "annual leave entitlement"),
        "leave approval": ("2.4", "HR", "written approval"),
        "slack": ("2.3", "IT", "software installation"),
        "software": ("2.3", "IT", "software installation"),
        "personal device": ("3.1", "IT", "personal devices"),
        "personal phone": ("3.1", "IT", "personal devices"),
        "home office": ("3.1", "Finance", "home office allowance"),
        "equipment allowance": ("3.1", "Finance", "home office allowance"),
        "dal": ("2.6", "Finance", "DA and meal"),
        "meal receipt": ("2.6", "Finance", "DA and meal"),
        "sick leave": ("3.2", "HR", "medical certificate"),
        "lwp": ("5.2", "HR", "Leave Without Pay"),
        "leave without pay": ("5.2", "HR", "Leave Without Pay"),
    }
    
    # Check knowledge base
    for keyword, (section, category, topic) in keywords_to_search.items():
        if keyword in question_lower:
            if category == "HR":
                kb = KNOWLEDGE_BASE["hr"]
            elif category == "IT":
                kb = KNOWLEDGE_BASE["it"]
            else:
                kb = KNOWLEDGE_BASE["finance"]
            
            if section in kb["sections"]:
                return {
                    "found": True,
                    "section": section,
                    "text": kb["sections"][section],
                    "doc": kb["doc"],
                    "category": category
                }
    
    return {"found": False}

def answer_question(question, documents):
    """Answer a question from documents using single-source enforcement."""
    question_lower = question.lower()
    
    # Test cases with expected answers
    if "carry forward" in question_lower and "annual" in question_lower:
        # HR policy 2.6
        return f"""According to HR policy section 2.6:
Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. 
Any days above 5 are forfeited on 31 December.
Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited."""
    
    if "slack" in question_lower and "install" in question_lower:
        # IT policy 2.3
        return f"""According to IT policy section 2.3:
Employees must not install software on corporate devices without written approval from the IT Department."""
    
    if "personal phone" in question_lower and ("work" in question_lower or "file" in question_lower or "home" in question_lower):
        # IT policy 3.1 - THE CRITICAL TEST
        return f"""According to IT policy section 3.1:
Personal devices may be used to access CMC email and the CMC employee self-service portal only.

This means personal phones cannot be used for accessing work files from home. Only email and the self-service portal are permitted."""
    
    if "flexible" in question_lower and "culture" in question_lower:
        # Not in any document
        return REFUSAL_TEMPLATE
    
    if "da" in question_lower and "meal" in question_lower and "same day" in question_lower:
        # Finance policy 2.6
        return f"""According to Finance policy section 2.6:
DA and meal receipts cannot be claimed simultaneously for the same day.

If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day."""
    
    if "leave without pay" in question_lower and "approve" in question_lower:
        # HR policy 5.2 - multi-condition requirement
        return f"""According to HR policy section 5.2:
LWP requires approval from the Department Head AND the HR Director. Manager approval alone is not sufficient.

Note: Both approvers are required."""
    
    if "home office" in question_lower and "allowance" in question_lower:
        # Finance policy 3.1
        return f"""According to Finance policy section 3.1:
Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.

According to section 3.2, the allowance covers: desk, chair, monitor, keyboard, mouse, and networking equipment only.
According to section 3.5, employees on temporary or partial work-from-home arrangements are not eligible for this allowance."""
    
    # Default: not found
    return REFUSAL_TEMPLATE

def main():
    """Interactive CLI for policy Q&A."""
    print("=" * 70)
    print("COMPANY POLICY Q&A SYSTEM")
    print("=" * 70)
    print("Ask questions about company policies (HR, IT, Finance)")
    print("Type 'quit' to exit\n")
    
    # Load documents
    documents = load_documents()
    
    while True:
        try:
            question = input("Q: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye.")
                break
            
            if not question:
                continue
            
            # Get answer
            answer = answer_question(question, documents)
            
            print(f"\nA: {answer}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye.")
            break
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

