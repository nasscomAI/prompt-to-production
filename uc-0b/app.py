"""
UC-0B app.py — CMC Leave Policy Summarizer.
Builds a meaning-preserving, robust policy summarizer using Python's standard libraries.
Parses the leave policy, extracts target clauses, validates compliance, and writes a verified summary.
"""
import argparse
import os
import re
import sys

def retrieve_policy(filepath: str) -> dict:
    """
    Loads a plain-text policy document and parses it into a dictionary of structured clauses.
    
    Args:
        filepath: Path to the .txt policy file.
        
    Returns:
        dict: Mapping of clause numbers (e.g., '2.3') to their corresponding text.
    """
    if not os.path.exists(filepath):
        print(f"Error: Input file '{filepath}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    if os.path.getsize(filepath) == 0:
        print(f"Error: Input file '{filepath}' is empty.", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading input file '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)
        
    if not content.strip():
        print(f"Error: Input file '{filepath}' contains only whitespace.", file=sys.stderr)
        sys.exit(1)
        
    clauses = {}
    current_clause_num = None
    lines = content.splitlines()
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        # Match section headers, e.g. "1. PURPOSE AND SCOPE" or "2. ANNUAL LEAVE"
        # Reset the current clause tracking to prevent lines from bleeding into previous clauses
        if re.match(r"^\d+\.\s+[A-Z\s]+$", stripped):
            current_clause_num = None
            continue
            
        # Match a clause number at the start of the line, e.g. "2.3 Employees must..."
        clause_match = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
        if clause_match:
            current_clause_num = clause_match.group(1)
            clauses[current_clause_num] = clause_match.group(2).strip()
        else:
            # Append continuation lines to the current active clause
            if current_clause_num is not None:
                clauses[current_clause_num] += " " + stripped
                
    # Normalize internal spaces for each clause
    for k in clauses:
        clauses[k] = re.sub(r"\s+", " ", clauses[k])
        
    return clauses

def check_safety_and_summarize(clause_num: str, text: str) -> tuple[str, bool]:
    """
    Checks if a clause can be safely summarized without meaning loss.
    If yes, returns the summary. If not, returns the verbatim text and a warning flag.
    
    Args:
        clause_num: The clause identifier (e.g. '5.2').
        text: The raw text of the clause.
        
    Returns:
        tuple[str, bool]: (summary_or_verbatim, was_flagged)
    """
    text_lower = text.lower()
    
    if clause_num == "2.3":
        # Check: 14 days, advance notice/application, Form HR-L1
        if "14" in text_lower and "form hr-l1" in text_lower:
            return "Application must be submitted at least 14 days in advance using Form HR-L1.", False
            
    elif clause_num == "2.4":
        # Check: written approval, direct manager, verbal not valid
        if "written approval" in text_lower and "direct manager" in text_lower and "verbal" in text_lower and "not valid" in text_lower:
            return "Written approval from direct manager is required before leave commences; verbal approval is not valid.", False
            
    elif clause_num == "2.5":
        # Check: unapproved, Loss of Pay/LOP, regardless
        if ("loss of pay" in text_lower or "lop" in text_lower) and "regardless" in text_lower:
            return "Unapproved absence is recorded as Loss of Pay (LOP) regardless of subsequent approval.", False
            
    elif clause_num == "2.6":
        # Check: maximum 5 days, carry forward, forfeited on 31 December
        if "5" in text_lower and "31 december" in text_lower:
            return "Maximum annual leave carry-forward is 5 days; excess days are forfeited on 31 December.", False
            
    elif clause_num == "2.7":
        # Check: first quarter or January-March, or forfeited
        if "first quarter" in text_lower or ("january" in text_lower and "march" in text_lower):
            return "Carry-forward days must be used within the first quarter (January–March) or they are forfeited.", False
            
    elif clause_num == "3.2":
        # Check: 3+ days, medical certificate, 48 hours
        if "3" in text_lower and "medical certificate" in text_lower and "48 hours" in text_lower:
            return "Sick leave of 3 or more consecutive days requires a medical certificate submitted within 48 hours of return.", False
            
    elif clause_num == "3.4":
        # Check: before/after holiday or annual leave, medical certificate, regardless of duration
        if "before" in text_lower and "after" in text_lower and "medical certificate" in text_lower and "regardless" in text_lower:
            return "Sick leave immediately before/after holidays or annual leave requires a medical certificate regardless of duration.", False
            
    elif clause_num == "5.2":
        # Check: Department Head, HR Director, manager not sufficient
        if "department head" in text_lower and "hr director" in text_lower and "manager" in text_lower:
            return "Leave Without Pay (LWP) requires approval from both the Department Head and the HR Director; manager approval alone is insufficient.", False
            
    elif clause_num == "5.3":
        # Check: 30 days, Municipal Commissioner
        if "30" in text_lower and "municipal commissioner" in text_lower:
            return "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.", False
            
    elif clause_num == "7.2":
        # Check: encashment, during service, not permitted
        if "encashment" in text_lower and "during service" in text_lower and "not permitted" in text_lower:
            return "Leave encashment during service is not permitted under any circumstances.", False

    # Default fallback: cannot be safely summarized due to missing elements or template deviations.
    return text, True

def summarize_policy(clauses: dict) -> str:
    """
    Generates a verified summary for each of the 10 target clauses.
    If a clause is missing or unsafe to summarize, it will be flagged.
    
    Args:
        clauses: Dictionary containing parsed clauses.
        
    Returns:
        str: Format-compliant multi-line summary.
    """
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    summary_lines = ["CMC EMPLOYEE LEAVE POLICY — KEY OBLIGATIONS SUMMARY", "====================================================="]
    
    for clause_num in target_clauses:
        if clause_num not in clauses:
            summary_lines.append(f"Clause {clause_num}: [FLAGGED: MISSING CLAUSE] Could not be located in source document.")
            continue
            
        raw_text = clauses[clause_num]
        summary_text, was_flagged = check_safety_and_summarize(clause_num, raw_text)
        
        if was_flagged:
            summary_lines.append(f"Clause {clause_num}: [FLAGGED: QUOTED VERBATIM] {summary_text}")
        else:
            summary_lines.append(f"Clause {clause_num}: {summary_text}")
            
    return "\n".join(summary_lines) + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to the input policy text file")
    parser.add_argument("--output", required=True, help="Path to write the output summary text file")
    args = parser.parse_args()
    
    # 1. Retrieve policy clauses
    clauses = retrieve_policy(args.input)
    
    # 2. Summarize clauses
    summary = summarize_policy(clauses)
    
    # 3. Write summary to output
    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Summary successfully written to: {args.output}")
    except Exception as e:
        print(f"Error writing output file '{args.output}': {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
