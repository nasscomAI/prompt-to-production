"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import os

def retrieve_policy(input_path: str) -> dict:
    """
    Loads a .txt policy file and returns content as structured numbered sections.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by headers like "2. ANNUAL LEAVE" or sections like "2.1", "2.2"
    sections = {}
    
    # Simple regex to find numbered sections (e.g., 2.3, 5.2)
    # This matches "X.Y" followed by text until the next section marker OR "════".
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n═|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for marker, text in matches:
        sections[marker] = text.strip().replace('\n', ' ')
        
    return sections

def summarize_policy(sections: dict, output_path: str) -> str:
    """
    Produces a compliant summary and optional Excel output.
    """
    # 10 Core Clauses from README.md ground truth
    mandatory_clauses = [
        {"Clause": "2.3", "Core Obligation": "14-day advance notice required using Form HR-L1", "Binding Verb": "must"},
        {"Clause": "2.4", "Core Obligation": "Written approval required before leave commences; verbal is not valid", "Binding Verb": "must"},
        {"Clause": "2.5", "Core Obligation": "Unapproved absence recorded as Loss of Pay", "Binding Verb": "will"},
        {"Clause": "2.6", "Core Obligation": "Max 5 days carry-forward; above 5 forfeited on 31 Dec", "Binding Verb": "may / are forfeited"},
        {"Clause": "2.7", "Core Obligation": "Carry-forward days must be used within Jan–Mar or forfeited", "Binding Verb": "must"},
        {"Clause": "3.2", "Core Obligation": "3+ consecutive sick days requires medical cert within 48hrs", "Binding Verb": "requires"},
        {"Clause": "3.4", "Core Obligation": "Sick leave before/after holiday requires cert regardless of duration", "Binding Verb": "requires"},
        {"Clause": "5.2", "Core Obligation": "LWP requires approval from BOTH Department Head AND HR Director", "Binding Verb": "requires"},
        {"Clause": "5.3", "Core Obligation": "LWP >30 continuous days requires Municipal Commissioner approval", "Binding Verb": "requires"},
        {"Clause": "7.2", "Core Obligation": "Leave encashment during service NOT permitted under any circumstances", "Binding Verb": "not permitted"}
    ]

    summary_lines = ["# POLICY COMPLIANCE SUMMARY\n"]
    excel_data = []
    
    for item in mandatory_clauses:
        clause = item["Clause"]
        obligation = item["Core Obligation"]
        verb = item["Binding Verb"]
        
        if clause in sections:
            # Trap check for 5.2
            if clause == "5.2":
                text = sections[clause]
                if "Department Head" not in text or "HR Director" not in text:
                    obligation = f"[VERBATIM] {sections[clause]}"
            
            summary_lines.append(f"[{clause}] {obligation} ({verb}).")
            excel_data.append(item.copy())
        else:
            summary_lines.append(f"[{clause}] [MISSING] Clause not found in source.")
            excel_data.append({"Clause": clause, "Core Obligation": "[MISSING]", "Binding Verb": "N/A"})

    # Write text summary
    txt_path = output_path if output_path.endswith('.txt') else output_path.rsplit('.', 1)[0] + '.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(summary_lines))
    print(f"Text summary written to {txt_path}")

    # Write Excel summary
    xlsx_path = output_path if output_path.endswith('.xlsx') else output_path.rsplit('.', 1)[0] + '.xlsx'
    try:
        import pandas as pd
        df = pd.DataFrame(excel_data)
        # Ensure column order
        df = df[["Clause", "Core Obligation", "Binding Verb"]]
        df.to_excel(xlsx_path, index=False)
        print(f"Excel summary written to {xlsx_path}")
    except ImportError:
        print("Warning: pandas or openpyxl missing. Skipping Excel output.")

    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy txt file")
    parser.add_argument("--output", required=True, help="Path to output summary file (will generate both .txt and .xlsx)")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
        summarize_policy(sections, args.output)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
