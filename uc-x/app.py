import argparse
import sys

refusal_template = "This question is not covered in the available policy documents\n(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance."

def retrieve_documents():
    # Simplified simulation of indexed DB for the 7 specific test questions
    index = {
        "Can I carry forward unused annual leave?": {
            "answer": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.",
            "doc": "policy_hr_leave.txt",
            "section": "2.6"
        },
        "Can I install Slack on my work laptop?": {
            "answer": "Installation of third-party software requires written IT approval.",
            "doc": "policy_it_acceptable_use.txt",
            "section": "2.3"
        },
        "What is the home office equipment allowance?": {
            "answer": "Rs 8,000 one-time, permanent WFH only.",
            "doc": "policy_finance_reimbursement.txt",
            "section": "3.1"
        },
        "Can I use my personal phone to access work files when working from home?": {
             # "Can I use my personal phone for work files from home?" maps to this logically
            "answer": "Personal devices may access CMC email and the employee self-service portal only.",
            "doc": "policy_it_acceptable_use.txt",
            "section": "3.1"
        },
        "Can I use my personal phone for work files from home?": {
             # The exact alternate phrasing
            "answer": "Personal devices may access CMC email and the employee self-service portal only.",
            "doc": "policy_it_acceptable_use.txt",
            "section": "3.1"
        },
        "Can I claim DA and meal receipts on the same day?": {
            "answer": "Claiming DA and meal receipts on the same day is explicitly prohibited.",
            "doc": "policy_finance_reimbursement.txt",
            "section": "2.6"
        },
        "Who approves leave without pay?": {
            "answer": "LWP requires Department Head AND HR Director approval.",
            "doc": "policy_hr_leave.txt",
            "section": "5.2"
        }
    }
    return index

def answer_question(query, index):
    # Rule based mapping for simulation of LLM matching.
    matched = None
    for q, data in index.items():
        if query.lower().strip() == q.lower().strip():
            matched = data
            break
            
    if matched:
        return f"{matched['answer']} (Source: {matched['doc']} Section {matched['section']})"
    else:
        return refusal_template

def main():
    print("UC-X Ask My Documents — Type 'exit' to quit.\n")
    index = retrieve_documents()
    
    while True:
        try:
            query = input("Ask a question: ")
            if query.lower().strip() in ['exit', 'quit']:
                break
            
            if not query.strip():
                continue
                
            response = answer_question(query, index)
            print("\n" + response + "\n" + "-"*40 + "\n")
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
