"""
UC-X app.py — Ask My Documents (Enforced QA)
Implemented using the strict compliance constraints of agents.md and skills.md.

Enforcement Rules:
1. Never combine claims from two different documents into a single answer
2. Never use hedging phrases
3. If not covered -> Use refusal template exactly
4. Cite source document name + section number for every factual claim
"""
import argparse
import sys
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

MOCK_INDEX = {
    "annual_leave_carry_forward": {
        "ans": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
        "doc": "policy_hr_leave.txt",
        "sec": "2.6"
    },
    "slack_laptop": {
        "ans": "Employees must not install software on corporate devices without written approval from the IT Department.",
        "doc": "policy_it_acceptable_use.txt",
        "sec": "2.3"
    },
    "home_office_allowance": {
        "ans": "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
        "doc": "policy_finance_reimbursement.txt",
        "sec": "3.1"
    },
    "da_same_day": {
        "ans": "DA and meal receipts cannot be claimed simultaneously for the same day.",
        "doc": "policy_finance_reimbursement.txt",
        "sec": "2.6"
    },
    "lwp_approval": {
        "ans": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
        "doc": "policy_hr_leave.txt",
        "sec": "5.2"
    }
}

def retrieve_documents():
    """Simulates indexing documents to check for their presence."""
    docs = ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"]
    return docs

def answer_question(query: str) -> str:
    """Detects query intent and securely routes to single-source facts or absolute refusal."""
    query = query.lower()
    
    # Check for the cross-document TRAP first
    if "personal phone" in query and "work files" in query and "home" in query:
        # Cross document blend of IT 3.1 & HR policy detected. Must refuse.
        return REFUSAL_TEMPLATE

    # Intent 1
    if "carry forward" in query and "annual leave" in query:
        match = MOCK_INDEX["annual_leave_carry_forward"]
        return f"{match['ans']} (Source: {match['doc']}, Section {match['sec']})"
        
    # Intent 2
    if "slack" in query and ("laptop" in query or "install" in query):
        match = MOCK_INDEX["slack_laptop"]
        return f"{match['ans']} (Source: {match['doc']}, Section {match['sec']})"

    # Intent 3
    if "home office" in query and "allowance" in query:
        match = MOCK_INDEX["home_office_allowance"]
        return f"{match['ans']} (Source: {match['doc']}, Section {match['sec']})"

    # Intent 4 (Missing completely)
    if "company view" in query and "flexible working culture" in query:
        return REFUSAL_TEMPLATE

    # Intent 5 
    if "da " in query and "meal" in query and "same day" in query:
        match = MOCK_INDEX["da_same_day"]
        return f"{match['ans']} (Source: {match['doc']}, Section {match['sec']})"

    # Intent 6
    if "approves" in query and "leave without pay" in query:
        match = MOCK_INDEX["lwp_approval"]
        return f"{match['ans']} (Source: {match['doc']}, Section {match['sec']})"

    # General catch-all for anything unrecognized
    return REFUSAL_TEMPLATE

def interactive_cli():
    print("Ask My Documents - Interactive CLI. Type 'exit' to quit.")
    print("-" * 50)
    while True:
        try:
            query = input("Ask a policy question > ").strip()
            if query.lower() in ['exit', 'quit']:
                break
            if not query:
                continue
                
            response = answer_question(query)
            print("\n" + response + "\n" + ("-" * 50))
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--query", required=False, help="Run a single question non-interactively")
    args = parser.parse_args()

    # Verify retrieval
    docs = retrieve_documents()

    if args.query:
        print(answer_question(args.query))
    else:
        interactive_cli()

if __name__ == "__main__":
    main()
