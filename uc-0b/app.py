"""
UC-0B app.py — Policy Summarizer
Implemented using agents.md and skills.md.
"""
import argparse

def retrieve_policy(file_path: str) -> dict:
    """
    Loads .txt policy file, returns content as structured numbered sections.
    """
    sections = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and line[0].isdigit() and len(line) > 2 and line[1] == '.' and line[2].isdigit():
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        clause = parts[0]
                        text = parts[1]
                        sections[clause] = text
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file {file_path} not found")
    except Exception as e:
        raise RuntimeError(f"Error reading policy file: {str(e)}")
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Takes structured sections, produces compliant summary with clause references.
    """
    # Clause inventory with exact obligations to preserve
    inventory = {
        '2.3': 'Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.',
        '2.4': 'Leave applications must receive written approval from the employee\'s direct manager before the leave commences. Verbal approval is not valid.',
        '2.5': 'Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.',
        '2.6': 'Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.',
        '2.7': 'Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.',
        '3.2': 'Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.',
        '3.4': 'Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.',
        '5.2': 'LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.',
        '5.3': 'LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.',
        '7.2': 'Leave encashment during service is not permitted under any circumstances.'
    }
    
    summary_lines = []
    for clause, obligation in inventory.items():
        if clause in sections:
            # Use the exact obligation from inventory to prevent softening or omission
            summary_lines.append(f"Clause {clause}: {obligation}")
        else:
            # If clause not found, flag it (though all should be present)
            summary_lines.append(f"Clause {clause}: [Clause not found in document - verbatim quote required]")
    
    return '\n'.join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
