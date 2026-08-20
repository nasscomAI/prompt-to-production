"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os

def read_policy(file_path):
    """Skill: document_reader"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def compliance_summarizer(text):
    """
    Skill: compliance_summarizer
    Logic: This mimics the 'enforcement' rules from your agents.md.
    In a live workshop, this would be an API call to an LLM.
    """
    lines = text.split('\n')
    summary_lines = ["### HR LEAVE POLICY SUMMARY - COMPLIANCE REVIEW ###\n"]
    
    for line in lines:
        # Rule: Every numbered section must have a bullet point
        if line.strip().startswith(('1.', '2.', '3.')):
            summary_lines.append(f"• SECTION {line.strip()}")
            
        # Rule: Highlight penalties/forfeiture in BOLD
        if "forfeit" in line.lower() or "penalty" in line.lower() or "loss" in line.lower():
            summary_lines.append(f"  **CRITICAL:** {line.strip().upper()}")
            
        # Rule: Quote eligibility dates exactly
        if "months" in line.lower() or "days" in line.lower():
            summary_lines.append(f"  - Eligibility: \"{line.strip()}\"")

    return "\n".join(summary_lines)

def run_uc0b():
    input_path = "data/policy-documents/policy_hr_leave.txt"
    output_path = "uc-0b/summary_hr_leave.txt"
    
    if os.path.exists(input_path):
        raw_text = read_policy(input_path)
        summary = compliance_summarizer(raw_text)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Success! Summary generated at {output_path}")
    else:
        print(f"Error: {input_path} not found.")

if __name__ == "__main__":
    run_uc0b()
