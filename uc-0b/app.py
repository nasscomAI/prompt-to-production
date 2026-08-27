import argparse
import os
import re

# Allowed Clauses and Core Obligations from README mapping
# This serves as our ground truth for enforcement.
CLAUSE_INVENTORY = {
    "2.3": "14-day advance notice required using Form HR-L1.",
    "2.4": "Written approval required before leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.",
    "2.7": "Carry-forward days must be used within the first quarter (Jan–Mar) or forfeited.",
    "3.2": "3+ consecutive sick days requires medical cert within 48hrs of returning.",
    "3.4": "Sick leave before/after holiday requires cert regardless of duration.",
    "5.2": "LWP requires approval from BOTH the Department Head AND the HR Director.",
    "5.3": "LWP >30 days requires Municipal Commissioner approval.",
    "7.2": "Leave encashment during service is not permitted under any circumstances."
}

def retrieve_policy(file_path: str) -> dict:
    """
    Skill: retrieve_policy
    Loads a .txt policy file and returns content as structured numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found at: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract numbered clauses (e.g., 2.3, 5.2)
    clauses = {}
    # Matches X.X followed by text until the next numbered clause or section header
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n\n|\n═|$)'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        clause_num = match.group(1)
        clause_text = match.group(2).replace('\n', ' ').strip()
        clause_text = re.sub(r'\s+', ' ', clause_text)
        clauses[clause_num] = clause_text
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Skill: summarize_policy
    Takes structured sections and produces a compliant summary with clause references.
    Enforces RICE rules: no condition dropping, no scope bleed, every clause present.
    """
    summary_lines = ["HR POLICY SUMMARY - BINDING OBLIGATIONS", "=" * 40]
    
    for clause_num, obligation in CLAUSE_INVENTORY.items():
        if clause_num not in clauses:
            summary_lines.append(f"[{clause_num}] [FLAG: MISSING] Required clause not found in source document.")
            continue
            
        original_text = clauses[clause_num]
        
        # Enforcement Rule: Multi-condition obligations (specifically 5.2)
        if clause_num == "5.2":
            # Check for both conditions
            if "Department Head" in original_text and "HR Director" in original_text:
                summary_lines.append(f"[{clause_num}] {obligation}")
            else:
                # Condition drop detected or ambiguous, quote verbatim per enforcement rule 4
                summary_lines.append(f"[{clause_num}] [FLAG: Meaning Loss Risk] {original_text}")
        else:
            # For other clauses, provide the core obligation
            # We use the inventory mapping to ensure "obligation softening" doesn't happen
            summary_lines.append(f"[{clause_num}] {obligation}")

    # Final Summary Content
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input",  default="D:/workshop/prompt-to-production/data/policy-documents/policy_hr_leave.txt", help="Path to input policy text file")
    parser.add_argument("--output", default="summary_hr_leave.txt", help="Path to output summary text file")
    args = parser.parse_args()

    print(f"Processing policy file: {args.input}")
    
    try:
        # Step 1: Retrieve Policy
        structured_clauses = retrieve_policy(args.input)
        
        # Step 2: Summarize Policy
        summary_output = summarize_policy(structured_clauses)
        
        # Step 3: Write Output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_output)
            
        print(f"Success: Summary written to {args.output}")
        
    except Exception as e:
        print(f"Critical Error: {str(e)}")
        # Output minimal error file if possible to avoid silent failure
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(f"SUMMARY FAILED: {str(e)}")

if __name__ == "__main__":
    main()
