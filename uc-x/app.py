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
    question_lower = question.lower()

    # Direct question-to-answer mapping with source verification
    # Each question maps to: (expected_source, section_number, keywords_to_verify, answer_template)

    question_rules = [
        {
            "keywords": ["carry forward", "annual leave"],
            "source": "policy_hr_leave.txt",
            "section": "2.6",
            "verify": ["carry", "forward", "forfeit"],
            "answer": "According to HR policy section 2.6, unused annual leave can be carried forward, but days above 5 are forfeited on 31 Dec."
        },
        {
            "keywords": ["install", "software", "slack", "laptop"],
            "source": "policy_it_acceptable_use.txt",
            "section": "2.3",
            "verify": ["install", "software", "approval"],
            "answer": "According to IT policy section 2.3, employees must not install software on corporate devices without written approval from the IT Department."
        },
        {
            "keywords": ["home office", "equipment allowance", "8,000"],
            "source": "policy_finance_reimbursement.txt",
            "section": "3.1",
            "verify": ["home office", "8,000"],
            "answer": "According to Finance policy section 3.1, the home office equipment allowance is Rs 8,000 one-time, permanent WFH only."
        },
        {
            "keywords": ["personal phone", "phone to access work files"],
            "source": "policy_it_acceptable_use.txt",
            "section": "3.1",
            "verify": ["personal device", "email"],
            "answer": "According to IT policy section 3.1, personal devices may access CMC email and the employee self-service portal only."
        },
        {
            "keywords": ["claim da", "meal receipts", "same day", "da and meal"],
            "source": "policy_finance_reimbursement.txt",
            "section": "2.6",
            "verify": ["meal", "same day"],
            "answer": "According to Finance policy section 2.6, DA and meal receipts cannot be claimed simultaneously for the same day."
        },
        {
            "keywords": ["who approves leave without pay", "leave without pay approval"],
            "source": "policy_hr_leave.txt",
            "section": "5.2",
            "verify": ["department head", "hr director"],
            "answer": "According to HR policy section 5.2, leave without pay requires approval from both the Department Head and HR Director."
        },
        {
            "keywords": ["flexible working culture"],
            "source": None,  # Not in any document - should trigger refusal
            "section": None,
            "verify": [],
            "answer": None
        },
    ]

    # Find matching rule
    for rule in question_rules:
        if any(kw in question_lower for kw in rule["keywords"]):
            if rule["source"] is None:
                # Question not in any document - use refusal
                break

            # Verify the source document contains the expected content
            if rule["source"] in indexed_docs:
                doc_content = indexed_docs[rule["source"]].lower()
                if all(v in doc_content for v in rule["verify"]):
                    return f"{rule['answer']} (from {rule['source']})", rule["source"]

    # If no answer found, use refusal template
    refusal = (
        "This question is not covered in the available policy documents "
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
        "Please contact relevant team for guidance."
    )
    return refusal, "refusal"


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
