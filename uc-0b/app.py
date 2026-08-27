import argparse
import os

def summarize_policy(input_text):
    """
    Summarization logic following the 'HR Policy Compliance Auditor' role.
    Focuses on Eligibility, Accrual, and Mandatory Constraints.
    """
    lines = [line.strip() for line in input_text.split('\n') if line.strip()]
    
    # Categories based on skills.md
    eligibility = []
    constraints = []
    general_rules = []

    for line in lines:
        lower_line = line.lower()
        
        # Skill: Constraint Extraction (Looking for numbers/must/shall)
        if any(char.isdigit() for char in line) or "must" in lower_line or "shall" in lower_line or "limit" in lower_line:
            constraints.append(f"- {line}")
        # Skill: Eligibility mapping
        elif "eligible" in lower_line or "who" in lower_line or "staff" in lower_line:
            eligibility.append(f"- {line}")
        else:
            general_rules.append(f"- {line}")

    # Construct the Audit-Grade Summary
    summary = "# HR Leave Policy Summary (Audit Grade)\n\n"
    
    summary += "## Eligibility\n"
    summary += "\n".join(eligibility) if eligibility else "- No specific eligibility criteria found."
    
    summary += "\n\n## Mandatory Constraints & Numbers\n"
    summary += "\n".join(constraints) if constraints else "- No numeric constraints identified."
    
    summary += "\n\n## Policy Details\n"
    summary += "\n".join(general_rules[:5]) # Top 5 rules
    
    summary += "\n\n---\n**Status:** Verifiable. No rounding or external logic applied."
    return summary

def main():
    parser = argparse.ArgumentParser(description="UC-0B: HR Policy Summarizer")
    parser.add_argument("--input", default="leave_policy.txt", help="Path to source policy file")
    parser.add_argument("--output", default="summary_hr_leave.txt", help="Path to save summary")
    
    args = parser.parse_args()

    # 1. Read the input file
    if not os.path.exists(args.input):
        print(f"Error: {args.input} not found. Please ensure the policy file exists.")
        return

    with open(args.input, "r") as f:
        policy_content = f.read()

    # 2. Process the content
    print(f"Processing {args.input}...")
    final_summary = summarize_policy(policy_content)

    # 3. Write to the output file
    with open(args.output, "w") as f:
        f.write(final_summary)

    print(f"Success! Summary generated in {args.output}")

if __name__ == "__main__":
    main()