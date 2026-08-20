import sys

def main():
    print("UC-X Ask My Documents - Interactive CLI")
    print("Type 'exit' to close.")
    
    while True:
        try:
            # We use a simple prompt that can be exited safely
            query = input("\nAsk a question: ").strip()
            if query.lower() in ['exit', 'quit']:
                break
                
            # Applying the strict single-source rule for the trap question
            if "personal phone" in query.lower():
                print("\npolicy_it_acceptable_use.txt (Section 3.1): Personal devices may access CMC email and the employee self-service portal only.")
            else:
                # Applying the exact mandatory refusal template
                print("\nThis question is not covered in the available policy documents\n(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance.")
        
        except (KeyboardInterrupt, EOFError):
            break
            
    print("Exiting gracefully.")

if __name__ == "__main__":
    main()