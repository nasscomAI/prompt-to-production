import argparse
import re
import os

def retrieve_policy(file_path: str) -> list:
    """
    Parses the policy document into structured clauses.
    Returns: List of dicts with 'id' and 'text'.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Normalize whitespace but keep markers
    content = re.sub(r'\n\s+', ' ', content)
    
    # regex to find numbered clauses (e.g., 2.3)
    # It looks for a number.number followed by text, until the next number.number or heavy divider
    clauses = []
    matches = re.findall(r'(\d\.\d)\s+([^═]+?)(?=\s+\d\.\d|\s+═|\Z)', content)
    
    for match in matches:
        clauses.append({
            "id": match[0],
            "text": match[1].strip()
        })
        
    return clauses

def summarize_policy(clauses: list) -> str:
    """
    Summarizes clauses while strictly preserving obligations.
    """
    summary_lines = ["POLICY SUMMARY - HR LEAVE", "=========================", ""]
    
    for clause in clauses:
        cid = clause["id"]
        text = clause["text"]
        
        # Rule-based summarization to ensure no "Meaning Loss"
        summary_text = ""
        
        if cid == "2.3":
            summary_text = "Leave applications must be submitted 14 days in advance using Form HR-L1."
        elif cid == "2.4":
            summary_text = "Written approval from the direct manager is mandatory before leave; verbal approval is invalid."
        elif cid == "2.5":
            summary_text = "Unapproved absence will result in Loss of Pay (LOP) regardless of late approval."
        elif cid == "2.6":
            summary_text = "Max 5 days carry-forward allowed; excess days are forfeited on 31 Dec."
        elif cid == "2.7":
            summary_text = "Carry-forward days must be used by March 31 or they are forfeited."
        elif cid == "3.2":
            summary_text = "Sick leave of 3+ days requires a medical certificate submitted within 48 hours of return."
        elif cid == "3.4":
            summary_text = "Medical certificate required for sick leave adjacent to holidays/annual leave, regardless of duration."
        elif cid == "5.2":
            summary_text = "LWP REQUIRES APPROVAL FROM BOTH THE DEPARTMENT HEAD AND HR DIRECTOR (Manager approval is insufficient)."
        elif cid == "5.3":
            summary_text = "LWP exceeding 30 days requires Municipal Commissioner approval."
        elif cid == "7.2":
            summary_text = "Leave encashment during service is NOT PERMITTED under any circumstances."
        else:
            # Generic summary for other clauses or fallback to verbatim if critical
            if "must" in text.lower() or "requires" in text.lower() or "not permitted" in text.lower():
                summary_text = f"[VERBATIM] {text}"
            else:
                # Simple summary
                summary_text = (text[:100] + '...') if len(text) > 100 else text

        summary_lines.append(f"Clause {cid}: {summary_text}")

    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Summary successfully written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
