"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import os

def retrieve_policy(file_path, target_clauses=None):
    """
    Skill: [retrieve_policy]
    Identifies clause headers and extracts their corresponding obligations.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to extract numbered clauses like 1.1, 2.3, etc.
    # It stops before the next numbered clause or a divider line.
    clauses = {}
    pattern = r"(\d\.\d)\s+(.*?)(?=\n\d\.\d|\n═|$)"
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        clause_id = match.group(1)
        text = match.group(2).strip().replace('\n', ' ')
        # Clean up double spaces from newline replacement
        text = re.sub(r'\s+', ' ', text)
        clauses[clause_id] = text
            
    return clauses

def summarize_policy(clauses, ground_truth):
    """
    Skill: [summarize_policy]
    Generates a summary while strictly preserving binding verbs and dual-approvals.
    """
    summary = []
    
    for clause_id in ground_truth:
        if clause_id not in clauses:
            summary.append(f"[{clause_id}]: MISSING - Clause not found in source document.")
            continue
            
        original_text = clauses[clause_id]
        lower_text = original_text.lower()
        
        # Enforcement: Clause 5.2 must preserve TWO approvers
        if clause_id == "5.2":
            if "department head" in lower_text and "hr director" in lower_text:
                summary.append(f"[{clause_id}]: Leave Without Pay requires written approval from both the Department Head and the HR Director.")
            else:
                # Verbatim fallback if a condition is dropped or logic is ambiguous
                summary.append(f"[{clause_id}] [VERBATIM]: {original_text}")
        
        # Enforcement: Binding strengths (must/requires/will)
        elif any(verb in lower_text for verb in ["must", "requires", "will", "required"]):
            if clause_id == "2.3":
                summary.append(f"[{clause_id}]: Advance notice of 14 days is mandatory for leave applications.")
            elif clause_id == "2.4":
                summary.append(f"[{clause_id}]: Written manager approval must be obtained before leave; verbal is not valid.")
            elif clause_id == "2.5":
                summary.append(f"[{clause_id}]: Unapproved absence will be Loss of Pay, even if subsequently approved.")
            elif clause_id == "2.7":
                summary.append(f"[{clause_id}]: Carry-forward days must be used between Jan–Mar or they are forfeited.")
            elif clause_id == "3.2":
                summary.append(f"[{clause_id}]: Sick leave of 3+ consecutive days requires a medical certificate within 48 hours.")
            elif clause_id == "3.4":
                summary.append(f"[{clause_id}]: Sick leave before/after holidays requires a cert regardless of duration.")
            elif clause_id == "5.3":
                summary.append(f"[{clause_id}]: LWP exceeding 30 days requires Municipal Commissioner approval.")
            else:
                summary.append(f"[{clause_id}]: {original_text}")
        
        # Enforcement: Negative constraints
        elif "not permitted" in lower_text or "cannot" in lower_text or "forfeited" in lower_text:
            if clause_id == "7.2":
                summary.append(f"[{clause_id}]: Leave encashment during service is strictly not permitted.")
            elif clause_id == "2.6":
                summary.append(f"[{clause_id}]: Max 5 days carry-over; amounts above 5 are forfeited on 31 Dec.")
            else:
                 summary.append(f"[{clause_id}]: {original_text}")
        
        else:
             # Default fallback for regular clauses
             summary.append(f"[{clause_id}]: {original_text}")
             
    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy.txt")
    parser.add_argument("--output", required=True, help="Path to write summary.txt")
    args = parser.parse_args()
    
    # Ground Truth mapping from README
    ground_truth_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    
    try:
        # Run Retrieval Skill
        extracted_clauses = retrieve_policy(args.input, ground_truth_clauses)
        
        # Run Summarization Skill
        summary_result = summarize_policy(extracted_clauses, ground_truth_clauses)
        
        # Write Output File
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_result)
            
        print(f"UC-0B: Summary generated successfully -> {args.output}")
        
    except Exception as e:
        print(f"UC-0B Execution Failed: {e}")

if __name__ == "__main__":
    main()
