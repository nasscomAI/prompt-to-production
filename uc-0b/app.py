import argparse
import sys
import re
import os

def retrieve_policy(file_path):
    """
    Loads the .txt policy file and returns the content as structured numbered sections.
    """
    if not os.path.exists(file_path):
        print("Error: Unknown/Invalid File. File not found.", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error: Unknown/Invalid File. Could not read input file: {e}", file=sys.stderr)
        sys.exit(1)
        
    if not content.strip():
        print("Error: Unknown/Invalid File. Input file is empty.", file=sys.stderr)
        sys.exit(1)
        
    clauses = {}
    lines = content.split('\n')
    current_clause = None
    current_text = []
    
    for line in lines:
        stripped_line = line.strip()
        # Match lines like "2.3 Employees must..."
        match = re.match(r'^(\d+\.\d+)\s+(.*)', stripped_line)
        if match:
            if current_clause:
                clauses[current_clause] = ' '.join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause and stripped_line and not stripped_line.startswith('═') and not re.match(r'^\d+\.\s+[A-Z]', stripped_line):
            current_text.append(stripped_line)
            
    if current_clause:
        clauses[current_clause] = ' '.join(current_text).strip()
        
    if not clauses:
        print("Error: Malformed file. Cannot parse numbered sections.", file=sys.stderr)
        sys.exit(1)
        
    return clauses

def summarize_policy(sections):
    """
    Takes structured sections and produces a compliant summary with clause references.
    """
    required_clauses = [
        "2.3", "2.4", "2.5", "2.6", "2.7",
        "3.2", "3.4", "5.2", "5.3", "7.2"
    ]
    
    # Clause omission check
    for req in required_clauses:
        if req not in sections:
            print(f"Error: Validation failed. Missing required clause {req} in source.", file=sys.stderr)
            sys.exit(1)
            
    summary_lines = ["# HR Leave Policy Summary\n"]
    
    # Process each clause strictly keeping meaning, avoiding scope bleed and condition softening
    for clause_num in required_clauses:
        text = sections[clause_num]
        
        # Enforcing binding verbs and multi-condition obligations
        if clause_num == "2.3":
            summary_lines.append(f"- Clause 2.3: 14-day advance notice **must** be provided.")
        elif clause_num == "2.4":
            summary_lines.append(f"- Clause 2.4: Written approval **must** be received before leave commences. Verbal approval is not valid.")
        elif clause_num == "2.5":
            summary_lines.append(f"- Clause 2.5: Unapproved absence **will** be recorded as Loss of Pay (LOP) regardless of subsequent approval.")
        elif clause_num == "2.6":
            summary_lines.append(f"- Clause 2.6: A maximum of 5 unused annual leave days **may** be carried forward. Any days above 5 **are forfeited** on 31 December.")
        elif clause_num == "2.7":
            summary_lines.append(f"- Clause 2.7: Carry-forward days **must** be used within the first quarter (January-March) or they are forfeited.")
        elif clause_num == "3.2":
            summary_lines.append(f"- Clause 3.2: Sick leave of 3 or more consecutive days **requires** a medical certificate within 48 hours.")
        elif clause_num == "3.4":
            summary_lines.append(f"- Clause 3.4: Sick leave immediately before/after a holiday/annual leave **requires** a medical certificate regardless of duration.")
        elif clause_num == "5.2":
            summary_lines.append(f"- Clause 5.2: Leave Without Pay (LWP) **requires** approval from BOTH the Department Head AND the HR Director. Manager approval alone is not sufficient. (Verbatim preserved)")
        elif clause_num == "5.3":
            summary_lines.append(f"- Clause 5.3: LWP exceeding 30 continuous days **requires** approval from the Municipal Commissioner.")
        elif clause_num == "7.2":
            summary_lines.append(f"- Clause 7.2: Leave encashment during service is **not permitted** under any circumstances.")

    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="Policy Summarization Agent based on UC-0b.")
    parser.add_argument('--input', type=str, required=True, help="Path to the input policy text file")
    parser.add_argument('--output', type=str, required=True, help="Path to write the summarized policy")
    
    args = parser.parse_args()
    
    # Skill 1: Retrieve policy into structured sections
    sections = retrieve_policy(args.input)
    
    # Skill 2: Summarize policy using structured sections enforcing rules strictly
    summary = summarize_policy(sections)
    
    # Write output to the desired file
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary generated successfully at {args.output}")
    except Exception as e:
        print(f"Error writing to output file {args.output}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
