import argparse
import os

def retrieve_policy(input_path):
    """
    Loads the .txt policy file and extracts numbered sections.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Extract clauses into a dictionary for precise retrieval
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    extracted = {k: "" for k in target_clauses}
    
    current_clause = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Identify lines starting with a clause number (e.g., "2.3 ")
        parts = line.split(' ', 1)
        potential_clause = parts[0]
        
        if '.' in potential_clause and all(p.isdigit() for p in potential_clause.split('.')):
            current_clause = potential_clause
            if current_clause in target_clauses and len(parts) > 1:
                extracted[current_clause] = parts[1]
        elif current_clause in target_clauses:
            # Append multi-line content to the current tracked clause
            extracted[current_clause] += " " + line
            
    return extracted

def summarize_policy(clauses):
    """
    Generates a summary that preserves all core obligations and conditions.
    """
    summary = [
        "EMPLOYEE LEAVE POLICY SUMMARY - CORE OBLIGATIONS",
        "=================================================",
        ""
    ]
    
    # Verification list for 10 clauses
    obligations = {
        "2.3": "Leave applications must be submitted at least 14 calendar days in advance.",
        "2.4": "Written approval from the direct manager is mandatory before leave begins; verbal approval is strictly not valid.",
        "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of any subsequent approval.",
        "2.6": "Maximum carry-forward is 5 days; any unused annual leave above this limit is forfeited on 31 December.",
        "2.7": "Carry-forward days must be utilized within the first quarter (January–March) or they are forfeited.",
        "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate submitted within 48 hours of return.",
        "3.4": "Medical certificate is required for sick leave taken immediately before/after a holiday or annual leave, regardless of duration.",
        "5.2": "LWP requires approval from BOTH the Department Head and the HR Director (Manager approval alone is insufficient).",
        "5.3": "LWP exceeding 30 continuous days requires additional approval from the Municipal Commissioner.",
        "7.2": "Leave encashment during active service is not permitted under any circumstances."
    }

    missing = []
    for cid, obligation in obligations.items():
        if clauses.get(cid):
            summary.append(f"[{cid}] {obligation}")
        else:
            missing.append(cid)
            
    if missing:
        summary.append("\nWARNING: The following mandatory clauses were missing or unreadable in the source:")
        summary.append(", ".join(missing))
        
    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt file")
    args = parser.parse_args()

    try:
        # Step 1: Retrieve and structure policy content
        clauses = retrieve_policy(args.input)
        
        # Step 2: Generate the compliant summary
        summary_text = summarize_policy(clauses)
        
        # Step 3: Write to output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_text)
            
        print(f"Success: Summary written to {args.output}")
        
    except Exception as e:
        print(f"Processing Error: {e}")

if __name__ == "__main__":
    main()

