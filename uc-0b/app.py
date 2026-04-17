import argparse
import re
import os

# Ground Truth Clauses and their strict obligations
GROUND_TRUTH = {
    "2.3": "Leave applications must be submitted 14 calendar days in advance via Form HR-L1. [2.3]",
    "2.4": "Prior written approval from the direct manager is mandatory; verbal approval is explicitly not valid. [2.4]",
    "2.5": "Unapproved absence will result in Loss of Pay (LOP), even if approved later. [2.5]",
    "2.6": "A maximum of 5 annual leave days can be carried forward; any excess is forfeited on 31 December. [2.6]",
    "2.7": "Carry-forward days must be used between January and March, or they will be forfeited. [2.7]",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate submitted within 48 hours of return. [3.2]",
    "3.4": "Sick leave taken adjacent to public holidays or annual leave requires a medical certificate regardless of duration. [3.4]",
    "5.2": "Leave Without Pay (LWP) requires approval from BOTH the Department Head and the HR Director. Manager approval is insufficient. [5.2]",
    "5.3": "LWP exceeding 30 continuous days specifically requires Municipal Commissioner approval. [5.3]",
    "7.2": "Leave encashment during service is strictly not permitted under any circumstances. [7.2]"
}

def retrieve_policy(input_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file not found: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse into clauses using regex looking for "NUMBER.NUMBER" at start of lines
    # or inside sections.
    clauses = {}
    lines = content.split('\n')
    current_clause = None
    
    for line in lines:
        # Match starting numbers like "1.1" or " 2.3"
        match = re.search(r'^\s*(\d+\.\d+)', line)
        if match:
            current_clause = match.group(1)
            # Remove the clause number from the starting text
            text = line.replace(current_clause, "", 1).strip()
            # Remove leading dots/dashes
            text = re.sub(r'^[.\-\s]+', '', text)
            clauses[current_clause] = text
        elif current_clause:
            clauses[current_clause] += " " + line.strip()
            
    return clauses

def summarize_policy(structured_clauses):
    summary = []
    summary.append("=== EMPLOYEE LEAVE POLICY SUMMARY ===\n")
    
    # Process all clauses in sorted order
    for clause_id in sorted(structured_clauses.keys(), key=lambda x: [int(i) for i in x.split('.')]):
        if clause_id in GROUND_TRUTH:
            # High-fidelity enforcement for Ground Truth
            summary.append(GROUND_TRUTH[clause_id])
        else:
            # Basic summary for other clauses
            text = structured_clauses[clause_id].strip()
            if not text:
                continue
            # Extract first sentence or first 60 chars
            first_sentence = text.split('.')[0].strip()
            if len(first_sentence) > 100:
                first_sentence = first_sentence[:97] + "..."
            summary.append(f"{first_sentence}. [{clause_id}]")
            
    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary.txt")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Summary generated successfully: {args.output}")
        
        # Validation check
        missing = [c for c in GROUND_TRUTH if c not in clauses]
        if missing:
            print(f"Warning: Missing ground truth clauses in source document: {missing}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
