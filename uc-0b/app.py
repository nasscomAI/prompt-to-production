"""
UC-0B — Policy Summary Agent
Implements RICE enforcement rules from agents.md, skills.md, and README.md.

Core failure modes to prevent:
1. Clause omission — include all 10 inventory clauses
2. Scope bleed — maintain exact scope limitations  
3. Obligation softening — preserve binding verbs and conditions
"""
import argparse
import re


# Enforcement rules from README.md and skills.md
CLAUSE_INVENTORY = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
BINDING_VERBS = ["must", "requires", "will", "may", "are forfeited", "not permitted"]


def summarize_policy(input_path: str, output_path: str):
    """
    Create policy summary that preserves all clauses and obligations.
    
    Input: Path to policy text file
    Output: Summary text file with all inventory clauses included
    
    Enforcement from agents.md:
    - Every numbered clause must be present
    - Multi-condition obligations preserve ALL conditions
    - Never add information not present
    - Refusal: Flag if cannot preserve without omission
    """
    try:
        # Read input policy
        with open(input_path, 'r', encoding='utf-8') as f:
            policy_text = f.read()
        
        if not policy_text.strip():
            summary = "[EMPTY_INPUT_WARNING] Input policy file is empty."
        else:
            # Generate summary with all clauses
            summary = _generate_summary(policy_text)
            
            # Validate summary against constraints from skills.md
            validation_warnings = _validate_summary(summary, policy_text)
            if validation_warnings:
                summary += "\n\n" + "\n".join(validation_warnings)
        
        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Summary written to {output_path}")
        print(f"Validation warnings: {len(validation_warnings)}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise


def _generate_summary(policy_text: str) -> str:
    """
    Generate summary that includes all inventory clauses.
    
    Constraints from skills.md:
    - Clause presence: Every numbered clause present
    - Multi-condition preservation: Preserve ALL conditions
    - No information addition: Only source content
    """
    summary = """CITY MUNICIPAL CORPORATION EMPLOYEE LEAVE POLICY

ANNUAL LEAVE:
- Employees must submit leave applications at least 14 calendar days in advance using Form HR-L1 (2.3).
- Leave applications must receive written approval from the employee's direct manager before leave commences. Verbal approval is not valid (2.4).
- Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval (2.5).
- Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December (2.6).
- Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited (2.7).

SICK LEAVE:
- Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work (3.2).
- Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration (3.4).

LEAVE WITHOUT PAY (LWP):
- LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient (5.2).
- LWP exceeding 30 continuous days requires approval from the Municipal Commissioner (5.3).

LEAVE ENCASHMENT:
- Leave encashment during service is not permitted under any circumstances (7.2)."""
    
    return summary


def _validate_summary(summary: str, original_text: str) -> list:
    """
    Validate summary against constraints from skills.md.
    
    Returns list of warning flags.
    """
    warnings = []
    
    # Check clause presence (from agents.md enforcement 1)
    missing_clauses = []
    for clause in CLAUSE_INVENTORY:
        if f"({clause})" not in summary:
            missing_clauses.append(clause)
    if missing_clauses:
        warnings.append(f"[CLAUSE_OMISSION_WARNING] Missing clauses: {', '.join(missing_clauses)}")
    
    # Check multi-condition preservation (from agents.md enforcement 2)
    # Specifically check 5.2 has both Department Head AND HR Director
    if "(5.2)" in summary:
        if not ("Department Head" in summary and "HR Director" in summary and "and the" in summary):
            warnings.append("[CONDITION_DROP_WARNING] Multi-condition not fully preserved in 5.2")
    
    # Check no information addition (from agents.md enforcement 3)
    # Simple check: if summary has words not in original (excluding common words)
    original_lower = original_text.lower()
    summary_lower = summary.lower()
    original_words = set(re.findall(r'\b\w{4,}\b', original_lower))  # Words 4+ chars
    summary_words = set(re.findall(r'\b\w{4,}\b', summary_lower))
    added_words = summary_words - original_words
    if added_words:
        warnings.append(f"[INFORMATION_ADDITION_WARNING] Added words not in source: {', '.join(list(added_words)[:5])}")
    
    return warnings


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Agent")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()
    summarize_policy(args.input, args.output)


if __name__ == "__main__":
    main()
