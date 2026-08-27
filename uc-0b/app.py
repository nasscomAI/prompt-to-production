"""
UC-0B app.py — Summary That Changes Meaning
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

def summarize_policy(input_path: str) -> str:
    """
    Summarize the HR leave policy document, ensuring all clauses are included.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return "Error: Input file not found."
    except Exception as e:
        return f"Error reading file: {e}"
    
    # Extract all numbered clauses
    clauses = re.findall(r'(\d+\.\d+.*?)(?=\n\d+\.\d+|\n═|\Z)', content, re.DOTALL)
    
    summary = "CITY MUNICIPAL CORPORATION EMPLOYEE LEAVE POLICY SUMMARY\n\n"
    
    current_section = ""
    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue
        
        # Get section from clause number
        section_num = clause.split('.')[0]
        if section_num != current_section:
            current_section = section_num
            section_titles = {
                "1": "PURPOSE AND SCOPE",
                "2": "ANNUAL LEAVE", 
                "3": "SICK LEAVE",
                "4": "MATERNITY AND PATERNITY LEAVE",
                "5": "LEAVE WITHOUT PAY (LWP)",
                "6": "PUBLIC HOLIDAYS",
                "7": "LEAVE ENCASHMENT",
                "8": "GRIEVANCES"
            }
            summary += f"**{section_titles.get(section_num, f'Section {section_num}')}**\n"
        
        summary += f"- {clause}\n"
    
    return summary

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document")
    parser.add_argument("--output", required=True, help="Path to write summary")
    
    args = parser.parse_args()
    
    summary = summarize_policy(args.input)
    
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary written to {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}")

if __name__ == "__main__":
    main()
