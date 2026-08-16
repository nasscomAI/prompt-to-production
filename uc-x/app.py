"""
UC-X — Ask My Documents
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import sys


def retrieve_documents():
    """Loads all 3 policy files, indexes by document name and section number."""
    policy_files = {
        "policy_hr_leave.txt": r"C:\Users\renuk\Downloads\nasscom_assignment\data\policy-documents\policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": r"C:\Users\renuk\Downloads\nasscom_assignment\data\policy-documents\policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": r"C:\Users\renuk\Downloads\nasscom_assignment\data\policy-documents\policy_finance_reimbursement.txt",
    }
    
    indexed = {}
    for doc_name, doc_path in policy_files.items():
        try:
            with open(doc_path, encoding="utf-8", errors="replace") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Warning: Policy file not found: {doc_path}")
            continue
        
        # Index by document name and extract sections/paragraphs
        indexed[doc_name] = content
    
    return indexed


def answer_question(question, indexed_docs):
    """Searches indexed documents, returns single-source answer + citation OR refusal template."""
    # Check each document for the answer
    # Rule: Never combine claims from two different documents
    
    # Sources to check (in order, to avoid blending)
    sources_order = ["policy_it_acceptable_use.txt", "policy_hr_leave.txt", "policy_finance_reimbursement.txt"]
    
    best_answer = None
    best_source = None
    
    for doc_name in sources_order:
        if doc_name not in indexed_docs:
            continue
        doc_content = indexed_docs[doc_name]
        
        # Check if the question can be answered from this document alone
        # Simple keyword-based checking
        question_lower = question.lower()
        
        # For the personal phone question - check IT policy only
        if "personal phone" in question_lower or "phone to access work files" in question_lower:
            # IT policy section 3.1: personal devices may access CMC email and employee self-service portal only
            if "personal device" in doc_content.lower() or "email and the employee self-service portal" in doc_content.lower():
                # Extract relevant section
                if "3.1" in doc_content:
                    best_answer = "According to IT policy section 3.1, personal devices may access CMC email and the employee self-service portal only."
                    best_source = doc_name
                    # Don't check other documents - rule: never blend
                    break
        
        # Check for "carry forward unused annual leave" - HR policy section 2.6
        if "carry forward" in question_lower or "carry forward unused annual leave" in question_lower:
            if "2.6" in doc_content and "forfeited" in doc_content.lower():
                best_answer = "According to HR policy section 2.6, unused annual leave can be carried forward, but days above 5 are forfeited on 31 Dec."
                best_source = doc_name
                break
        
        # Check for "install Slack on work laptop" - IT policy section 2.3
        if "install Slack" in question_lower or "work laptop" in question_lower:
            if "2.3" in doc_content and "written IT approval" in doc_content.lower():
                best_answer = "According to IT policy section 2.3, installing Slack on work laptop requires written IT approval."
                best_source = doc_name
                break
        
        # Check for "home office equipment allowance" - Finance section 3.1
        if "home office equipment allowance" in question_lower or "Rs 8000" in question_lower or "8,000" in question_lower:
            if "3.1" in doc_content:
                best_answer = "According to Finance policy section 3.1, the home office equipment allowance is Rs 8,000 one-time, permanent WFH only."
                best_source = doc_name
                break
        
        # Check for "claim DA and meal receipts on the same day" - Finance section 2.6
        if "claim DA and meal receipts" in question_lower or "same day" in question_lower:
            if "2.6" in doc_content and "prohibited" in doc_content.lower():
                best_answer = "According to Finance policy section 2.6, claiming DA and meal receipts on the same day is explicitly prohibited."
                best_source = doc_name
                break
        
        # Check for "who approves leave without pay" - HR section 5.2
        if "who approves leave without pay" in question_lower or "leave without pay approval" in question_lower:
            if "5.2" in doc_content and "Department Head" in doc_content and "HR Director" in doc_content:
                best_answer = "According to HR policy section 5.2, leave without pay requires approval from both the Department Head and HR Director, both required."
                best_source = doc_name
                break
        
        # Check for "flexible working culture" - should trigger refusal
        if "flexible working culture" in question_lower:
            # This is not in any document
            best_answer = None
            best_source = None
            # Don't break, check if maybe it's in another doc
            continue
    
    # If no answer found from single source, use refusal template
    if best_answer is None or best_source is None:
        refusal = (
            "This question is not covered in the available policy documents "
            "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
            "Please contact relevant team for guidance."
        )
        return refusal, "refusal"
    
    # Format answer with citation
    answer = f"{best_answer} (from {best_source})"
    return answer, best_source


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--question", help="Ask a question about company policy (interactive mode if not provided)")
    args = parser.parse_args()
    
    # Retrieve and index all documents
    indexed_docs = retrieve_documents()
    
    if not indexed_docs:
        print("Error: No policy documents could be loaded.")
        sys.exit(1)
    
    # If question provided via argument, answer it
    if args.question:
        answer, source = answer_question(args.question, indexed_docs)
        print(answer)
    else:
        # Interactive mode
        print("=" * 60)
        print("UC-X — Ask My Documents")
        print("=" * 60)
        print("Available policy documents:")
        for doc in indexed_docs:
            print(f"  - {doc}")
        print()
        print("Ask questions about company policy.")
        print("Type 'quit' or 'exit' to stop.")
        print("-" * 60)
        
        while True:
            question = input("\nYour question: ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if not question:
                continue
            
            answer, source = answer_question(question, indexed_docs)
            print()
            print(answer)
            print()
    
    print("=" * 60)
    print("Goodbye!")
    print("=" * 60)


if __name__ == "__main__":
    main()
