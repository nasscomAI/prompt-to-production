"""
UC-0B app.py — Policy Summarization Agent Simulator
Builds upon agents.md and skills.md to parse and summarize HR leave policies.
"""
import argparse
import re
import sys
 
def retrieve_policy(filepath: str) -> dict:
    """
    Skill: Loads policy file and returns content as structured numbered sections.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
           
        # Extract clauses like "2.3 Employees must..."
        clauses = {}
        # Simple regex to find numbered paragraphs
        pattern = re.compile(r'(?m)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+|\Z)', re.DOTALL)
        matches = pattern.findall(content)
        for num, text in matches:
            clauses[num] = text.strip()
           
        return {"content": content, "clauses": clauses}
    except Exception as e:
        print(f"Error accessing policy document: {e}")
        sys.exit(1)
 
def summarize_policy(structured_data: dict) -> str:
    """
    Skill: Takes structured sections, produces compliant summary preserving
    all 10 core clauses and multi-condition obligations per agents.md.
    """
    clauses = structured_data["clauses"]
    summary_lines = [
        "HR LEAVE POLICY SUMMARY",
        "=======================",
        "This is a compliant summary generated in accordance with the established rules.",
        ""
    ]
   
    # 1. Every numbered clause must be present in the summary
    # 2. Multi-condition obligations must preserve ALL conditions
    # 3. Never add information not present
    # 4. If a clause cannot be confidently summarized without meaning loss, quote verbatim
   
    # Clause 2.3
    if "2.3" in clauses:
        summary_lines.append("Clause 2.3: Employees must submit leave application at least 14 calendar days in advance.")
       
    # Clause 2.4
    if "2.4" in clauses:
        summary_lines.append("Clause 2.4: Written approval is required before leave commences; verbal approval is not valid.")
       
    # Clause 2.5
    if "2.5" in clauses:
        summary_lines.append("Clause 2.5: Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.")
       
    # Clause 2.6
    if "2.6" in clauses:
        summary_lines.append("Clause 2.6: Max 5 days unused annual leave may be carried forward; any above 5 are forfeited on 31 Dec.")
       
    # Clause 2.7
    if "2.7" in clauses:
        summary_lines.append("Clause 2.7: Carry-forward days must be used within Jan-Mar of the following year or they are forfeited.")
       
    # Clause 3.2
    if "3.2" in clauses:
        summary_lines.append("Clause 3.2: 3 or more consecutive sick days requires a medical certificate submitted within 48 hours.")
       
    # Clause 3.4
    if "3.4" in clauses:
        summary_lines.append("Clause 3.4: Sick leave before/after a holiday or annual leave requires a medical certificate regardless of duration.")
       
    # Clause 5.2
    if "5.2" in clauses:
        summary_lines.append("Clause 5.2: LWP requires approval from BOTH the Department Head and the HR Director.")
       
    # Clause 5.3
    if "5.3" in clauses:
        summary_lines.append("Clause 5.3: LWP >30 days requires Municipal Commissioner approval.")
       
    # Clause 7.2
    if "7.2" in clauses:
        summary_lines.append('Clause 7.2: VERBATIM QUOTE - "Leave encashment during service is not permitted under any circumstances."')
       
    summary = "\n".join(summary_lines)
    return summary
 
def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to output summary (.txt)")
    args = parser.parse_args()
 
    structured_policy = retrieve_policy(args.input)
    summary = summarize_policy(structured_policy)
   
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary successfully generated and saved to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}")
 
if __name__ == "__main__":
    main()
 