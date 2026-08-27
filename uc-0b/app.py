"""
UC-0B app.py
Deterministically extracts mandatory clauses from the HR Leave Policy.
"""
import argparse
import re

def retrieve_policy(file_path):
    """
    Loads the .txt policy file and returns its content as a dictionary
    mapping clause numbers to their exact text content.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Could not find policy document at {file_path}")
        
    clauses = {}
    current_clause = None
    current_text = []
    
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    section_pattern = re.compile(r'^\d+\.\s+')
    
    for line in lines:
        match = clause_pattern.match(line)
        if match:
            # Save the previous clause
            if current_clause:
                clauses[current_clause] = " ".join(current_text).strip()
            
            current_clause = match.group(1)
            current_text = [match.group(2).strip()]
        elif current_clause and line.strip() and not line.startswith('═') and not section_pattern.match(line):
            # Continuation line for the current clause
            current_text.append(line.strip())
            
    # Save the last clause
    if current_clause:
        clauses[current_clause] = " ".join(current_text).strip()
        
    return clauses

def summarize_policy(clauses):
    """
    Produces a compliant summary with explicit clause references,
    ensuring no conditions are dropped.
    """
    mandatory_clauses = [
        "2.3", "2.4", "2.5", "2.6", "2.7", 
        "3.2", "3.4", "5.2", "5.3", "7.2"
    ]
    
    summary_lines = [
        "HR Leave Policy Summary",
        "=======================",
        "The following critical clauses must be strictly adhered to:",
        ""
    ]
    
    for clause_id in mandatory_clauses:
        if clause_id not in clauses:
            raise ValueError(f"MissingClauseError: Mandatory clause {clause_id} is missing from the source document.")
        
        # Format explicitly retaining the verbatim text to avoid dropping conditions
        summary_lines.append(f"Clause {clause_id}: {clauses[clause_id]}")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary txt file")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Success: Compliant summary written to {args.output}")
    except Exception as e:
        print(f"Failed to generate summary: {str(e)}")

if __name__ == "__main__":
    main()
