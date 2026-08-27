import argparse
import os
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Loads a .txt policy file and returns the content as structured numbered sections.
    As defined in skills.md.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Policy file not found: {filepath}")
        
    sections = {}
    current_clause = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip borders, headers, and document metadata
            if not line or line.startswith("═") or line == "CITY MUNICIPAL CORPORATION" or \
               line == "HUMAN RESOURCES DEPARTMENT" or line.startswith("Document") or \
               line.startswith("Version") or line.startswith("EMPLOYEE") or \
               re.match(r'^\d+\.\s+[A-Z\s]+$', line):
                continue
                
            # Match clause numbering like "1.1", "2.3"
            clause_match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if clause_match:
                current_clause = clause_match.group(1)
                sections[current_clause] = clause_match.group(2).strip()
            elif current_clause:
                sections[current_clause] += " " + line
                
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Takes structured sections and produces a compliant summary with correct clause references and maintaining all condition requirements.
    Follows enforcement rules from agents.md:
    1. Every numbered clause must be present in the summary.
    2. Multi-condition obligations must preserve ALL conditions.
    3. Never add information not present.
    4. If it cannot be summarised without meaning loss - quote it verbatim and flag it.
    """
    summary_lines = []
    summary_lines.append("────────────────────────────────────────")
    summary_lines.append(" HR LEAVE POLICY SUMMARY (COMPLIANT) ")
    summary_lines.append("────────────────────────────────────────\n")
    
    for clause_id, text in sections.items():
        lower_text = text.lower()
        
        # Determine if it has strict binding verbs or multi-condition obligations
        is_strict = any(word in lower_text for word in ["must", "requires", "will", "are forfeited", "not permitted", "not valid"])
        has_multiple_conditions = " and " in lower_text or " both " in lower_text or " or " in lower_text

        if is_strict or has_multiple_conditions:
            # Rule 4: Quote it verbatim and flag it to prevent meaning loss or dropping conditions (Rule 2)
            summary_lines.append(f"• [Clause {clause_id}] [FLAG: VERBATIM TO PRESERVE CONDITIONS]: {text}")
        else:
            # Safe to slightly condense
            condensed_text = text.replace("Each permanent employee is entitled to", "Entitlement:")\
                                 .replace("This policy governs", "Governs")\
                                 .replace("Female employees are entitled to", "Maternity entitlement:")\
                                 .replace("Male employees are entitled to", "Paternity entitlement:")
            summary_lines.append(f"• [Clause {clause_id}]: {condensed_text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B App: HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy document (e.g., policy_hr_leave.txt)")
    parser.add_argument("--output", required=True, help="Path to write the compliant summary text")
    args = parser.parse_args()
    
    try:
        print(f"Retrieving policy from {args.input}...")
        sections = retrieve_policy(args.input)
        
        print("Summarizing policy using agent constraints...")
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as out_f:
            out_f.write(summary)
            
        print(f"Success! Compliant summary written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
