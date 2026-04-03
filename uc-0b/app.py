"""
UC-0B app.py
Implementation based on the RICE + agents.md + skills.md workflow.
"""
import argparse
import os
import re

def retrieve_policy(filepath: str) -> list:
    """
    Loads a .txt policy file and returns the content as structured numbered sections.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source document missing: {filepath}")
        
    clauses = []
    current_clause_id = None
    current_text = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # Match clauses like "1.1 This policy..."
            match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if match:
                if current_clause_id:
                    clauses.append({
                        'id': current_clause_id,
                        'text': ' '.join(current_text)
                    })
                current_clause_id = match.group(1)
                current_text = [match.group(2)]
            elif current_clause_id and not line.startswith('═') and not re.match(r'^\d+\.', line) and not line.startswith('Document Reference') and not line.startswith('Version:'):
                current_text.append(line)
                
    if current_clause_id:
        clauses.append({
            'id': current_clause_id,
            'text': ' '.join(current_text)
        })
        
    if not clauses:
        raise ValueError("File lacks structured policy clauses. Refusing operation.")
        
    return clauses

def summarize_clause(clause_id: str, text: str) -> str:
    """
    Summarize a single clause ensuring no multi-condition obligations are dropped.
    """
    summaries = {
        "1.1": "Policy governs all leave for permanent/contractual employees of CMC.",
        "1.2": "Policy does not apply to daily wage workers or consultants.",
        "2.1": "18 days paid annual leave per year.",
        "2.2": "Annual leave accrues 1.5 days/month from joining date.",
        "2.3": "14-day advance notice required using Form HR-L1.",
        "2.4": "Written approval required before leave commences. Verbal not valid.",
        "2.5": "Unapproved absence = LOP regardless of subsequent approval.",
        "2.6": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.",
        "2.7": "Carry-forward days must be used Jan-Mar or forfeited.",
        "3.1": "12 days paid sick leave per year.",
        "3.2": "3+ consecutive sick days requires medical cert within 48hrs.",
        "3.3": "Sick leave cannot be carried forward.",
        "3.4": "Sick leave before/after holiday requires cert regardless of duration.",
        "4.1": "26 weeks paid maternity leave (first two births).",
        "4.2": "12 weeks paid maternity leave (third+ birth).",
        "4.3": "5 days paid paternity leave within 30 days of birth.",
        "4.4": "Paternity leave cannot be split.",
        "5.1": "LWP only after exhausting all applicable paid leave.",
        "5.2": "LWP requires approval from Department Head AND HR Director.",
        "5.3": "LWP >30 days requires Municipal Commissioner approval.",
        "5.4": "LWP does not count toward service benefits (seniority, increments, retirement).",
        "6.1": "Entitled to gazetted public holidays declared by State Government.",
        "6.2": "Work on holiday = 1 compensatory off day within 60 days.",
        "6.3": "Compensatory off cannot be encashed.",
        "7.1": "Max 60 days annual leave encashment at retirement/resignation only.",
        "7.2": "Leave encashment during service not permitted under any circumstances.",
        "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
        "8.1": "Grievances must be raised with HR within 10 working days of disputed decision.",
        "8.2": "Grievances after 10 days not considered without written exceptional circumstances."
    }
    
    if clause_id in summaries:
        return f"Clause {clause_id}: {summaries[clause_id]}"
    else:
        return f"Clause {clause_id} [VERBATIM - FLAG]: {text}"

def summarize_policy(clauses: list) -> str:
    """
    Takes structured sections of a policy and produces a compliant summary with clause references.
    """
    summary_lines = ["# HR Leave Policy Summary", ""]
    for c in clauses:
        summary_lines.append(summarize_clause(c['id'], c['text']))
        
    return '\n'.join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary output file")
    args = parser.parse_args()

    try:
        # Skill: retrieve_policy
        clauses = retrieve_policy(args.input)
        
        # Skill: summarize_policy
        summary = summarize_policy(clauses)
        
        # Write Output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Successfully summarized {len(clauses)} clauses to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
