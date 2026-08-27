"""
UC-0B app.py — Policy Summary Agent Implementation.
Implements agents.md (Policy Summary Agent) and skills.md (retrieve_policy, summarize_policy).
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path


def retrieve_policy(file_path):
    """
    Skill: retrieve_policy
    Loads a policy .txt file and returns content structured by numbered sections.
    
    Args:
        file_path (str): Path to policy document (.txt)
    
    Returns:
        dict: Keys=clause_numbers, values=clause_text
        Example: {"2.3": "14-day advance notice required...", "2.4": "Written approval required..."}
    
    Raises:
        FileNotFoundError: If file not found
        ValueError: If no numbered clauses detected
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    
    # Extract numbered clauses (e.g., "2.3", "3.4", "5.2")
    clause_pattern = r'^(\d+\.\d+)\s+(.+?)(?=^\d+\.\d+\s|$)'
    matches = re.findall(clause_pattern, content, re.MULTILINE | re.DOTALL)
    
    if not matches:
        raise ValueError("No numbered clauses detected in policy file")
    
    structured = {}
    for clause_num, clause_text in matches:
        structured[clause_num] = clause_text.strip()
    
    return structured


def summarize_policy(structured_clauses, clause_inventory):
    """
    Skill: summarize_policy
    Produces a compliant summary preserving all obligations, conditions, and binding verbs.
    
    Args:
        structured_clauses (dict): Output from retrieve_policy {clause_number: clause_text}
        clause_inventory (dict): Mapping of clause → core obligation → binding verb
    
    Returns:
        tuple: (summary_text, flagged_clauses_list)
    
    Raises:
        ValueError: If any clause from inventory is missing from input
    """
    flagged = []
    
    # Verify all inventory clauses are present
    missing = set(clause_inventory.keys()) - set(structured_clauses.keys())
    if missing:
        raise ValueError(f"Missing clauses from input: {', '.join(sorted(missing))}")
    
    # Build summary preserving all clauses and their conditions
    summary_lines = ["# Policy Summary\n"]
    
    for clause_num in sorted(structured_clauses.keys()):
        clause_text = structured_clauses[clause_num]
        core_obligation = clause_inventory.get(clause_num, {}).get('obligation', '')
        binding_verb = clause_inventory.get(clause_num, {}).get('verb', '')
        
        # Preserve full clause text to avoid condition loss
        summary_lines.append(f"**[{clause_num}]** {clause_text}\n")
        summary_lines.append(f"  - Core obligation: {core_obligation}\n")
        summary_lines.append(f"  - Binding verb: {binding_verb}\n")
    
    return '\n'.join(summary_lines), flagged


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Policy Summary Agent. Produces clause-preserving policy summaries."
    )
    parser.add_argument('--input', required=True, help='Path to policy document (.txt)')
    parser.add_argument('--output', required=True, help='Path to output summary file')
    
    args = parser.parse_args()
    
    try:
        # Skill 1: Retrieve and structure policy
        structured = retrieve_policy(args.input)
        
        # Clause inventory from README.md
        clause_inventory = {
            "2.3": {"obligation": "14-day advance notice required", "verb": "must"},
            "2.4": {"obligation": "Written approval required before leave commences. Verbal not valid.", "verb": "must"},
            "2.5": {"obligation": "Unapproved absence = LOP regardless of subsequent approval", "verb": "will"},
            "2.6": {"obligation": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.", "verb": "may / are forfeited"},
            "2.7": {"obligation": "Carry-forward days must be used Jan–Mar or forfeited", "verb": "must"},
            "3.2": {"obligation": "3+ consecutive sick days requires medical cert within 48hrs", "verb": "requires"},
            "3.4": {"obligation": "Sick leave before/after holiday requires cert regardless of duration", "verb": "requires"},
            "5.2": {"obligation": "LWP requires Department Head AND HR Director approval", "verb": "requires"},
            "5.3": {"obligation": "LWP >30 days requires Municipal Commissioner approval", "verb": "requires"},
            "7.2": {"obligation": "Leave encashment during service not permitted under any circumstances", "verb": "not permitted"},
        }
        
        # Skill 2: Summarize policy with enforcement rules
        summary, flagged = summarize_policy(structured, clause_inventory)
        
        # Write output
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"✓ Summary written to: {args.output}")
        if flagged:
            print(f"⚠ Flagged clauses for review: {', '.join(flagged)}")
    
    except (FileNotFoundError, ValueError) as e:
        print(f"✗ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
