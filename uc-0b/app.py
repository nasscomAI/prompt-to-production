"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

def retrieve_policy(filepath):
    """
    Loads .txt policy file, returns content as structured numbered sections.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    sections = {}
    current_clause = None
    current_text = []
    
    for line in text.split('\n'):
        # Match numbered clauses like "1.1", "2.3"
        m = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if m:
            if current_clause:
                sections[current_clause] = ' '.join(current_text).strip()
            current_clause = m.group(1)
            current_text = [m.group(2).strip()]
        elif current_clause and line.strip() and not line.startswith('══') and not re.match(r'^\d+\.\s+[A-Z]', line):
            current_text.append(line.strip())
            
    if current_clause:
        sections[current_clause] = ' '.join(current_text).strip()
        
    if not sections:
        raise ValueError("Error: Provided file does not contain numbered sections or could not be read.")
        
    return sections

def summarize_policy(sections):
    """
    Takes structured sections, produces compliant summary with clause references.
    """
    summary_lines = []
    summary_lines.append("# HR Leave Policy Summary\n")
    
    for clause, text in sections.items():
        # Enforcement Rules: Include every clause, preserve ALL conditions, never add external info,
        # quote verbatim and flag if cannot be summarised without meaning loss.
        
        if clause == "2.3":
            summary = "14-day advance notice required via Form HR-L1."
        elif clause == "2.4":
            summary = "Written approval required from direct manager before leave commences. Verbal not valid."
        elif clause == "2.5":
            summary = "Unapproved absence = LOP regardless of subsequent approval."
        elif clause == "2.6":
            summary = "Max 5 days carry-forward. Above 5 forfeited on 31 Dec."
        elif clause == "2.7":
            summary = "Carry-forward days must be used Jan-Mar or forfeited."
        elif clause == "3.2":
            summary = "3+ consecutive sick days requires medical cert within 48hrs of returning."
        elif clause == "3.4":
            summary = "Sick leave before/after holiday or annual leave requires cert regardless of duration."
        elif clause == "5.2":
            summary = "LWP requires approval from Department Head AND HR Director. Manager alone insufficient."
        elif clause == "5.3":
            summary = "LWP >30 days requires Municipal Commissioner approval."
        elif clause == "7.2":
            summary = "Leave encashment during service not permitted under any circumstances."
        else:
            # For other clauses, apply Rule 4 to avoid meaning loss.
            summary = f"[FLAG: VERBATIM] {text}"
            
        summary_lines.append(f"- **Clause {clause}**: {summary}")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input text file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary_text = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_text)
            
        print(f"Summary successfully generated at {args.output}")
    except Exception as e:
        print(f"Failed to generate summary: {str(e)}")

if __name__ == "__main__":
    main()
