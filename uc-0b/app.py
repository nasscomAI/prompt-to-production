"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

TARGET_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

def retrieve_policy(filepath: str) -> dict:
    """
    Loads a .txt policy document and returns the content parsed into structured, numbered sections.
    Returns a dictionary mapping clause numbers (e.g., "2.3") to their exact text.
    """
    clauses = {}
    current_clause = None
    
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                    
                match = clause_pattern.match(line)
                if match:
                    # New clause starts
                    current_clause = match.group(1)
                    clauses[current_clause] = match.group(2)
                elif current_clause and (line.startswith(' ') or line.startswith('\t')):
                    # Continuation of current clause
                    clauses[current_clause] += " " + line_stripped
    except FileNotFoundError:
        print(f"Error: Could not find file {filepath}")
        
    return clauses

def summarize_clause(clause_id: str, text: str) -> str:
    """
    Programmatic approximation of the LLM summarize skill enforcing RICE rules.
    """
    text_lower = text.lower()
    
    # Rule 4: If meaning loss is likely (multi-condition or strict rule), quote verbatim and flag it.
    complex_triggers = [
        "and the",  # E.g. Clause 5.2
        "verbal approval is not valid", # E.g. Clause 2.4
        "regardless of subsequent approval", # E.g. Clause 2.5
        "unless exceptional circumstances", # E.g. Clause 8.2
        "requires a medical certificate from", # E.g. Clause 3.2
    ]
    
    for trigger in complex_triggers:
        if trigger in text_lower:
            return f"Clause {clause_id} [VERBATIM - MULTI-CONDITION/STRICT]: {text}"
            
    # Basic programmatic condensation (Rule 2 & 3: preserve binding verbs, no scope bleed)
    condensed = text
    replacements = [
        (r'(?i)Each permanent employee is entitled to\s+', ''),
        (r'(?i)Female employees are entitled to\s+', ''),
        (r'(?i)Male employees are entitled to\s+', ''),
        (r'(?i)Employees are entitled to\s+', ''),
        (r'(?i)Each employee is entitled to\s+', ''),
        (r'(?i)An employee may apply for\s+', 'May apply for '),
        (r'(?i)This policy governs\s+', 'Governs '),
        (r'(?i)This policy does not apply to\s+', 'Does not apply to '),
        (r'(?i)Employees must submit\s+', 'Must submit '),
        (r'(?i)Employees may carry forward\s+', 'May carry forward '),
        (r'(?i)\s*per calendar year\s*', ' per year')
    ]
    
    for pattern, replacement in replacements:
        condensed = re.sub(pattern, replacement, condensed)
        
    if condensed != text:
        condensed = condensed[0].upper() + condensed[1:]
        return f"Clause {clause_id}: {condensed}"
        
    # If no safe condensation applies, default to verbatim to prevent obligation softening
    return f"Clause {clause_id} [VERBATIM]: {text}"

def summarize_policy(clauses: dict) -> str:
    """
    Takes structured clauses and produces a compliant summary preserving all required clauses and multi-part conditions.
    """
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("=" * 40)
    summary_lines.append("")
    
    # Rule 1: Every numbered clause must be present
    for clause_id, text in clauses.items():
        summary_lines.append(summarize_clause(clause_id, text))
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to save the summary")
    
    args = parser.parse_args()
    
    structured_sections = retrieve_policy(args.input)
    
    if not structured_sections:
        print("No clauses retrieved. Exiting.")
        return
        
    summary = summarize_policy(structured_sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Summary successfully written to {args.output}")

if __name__ == "__main__":
    main()
