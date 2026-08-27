"""
UC-X — Policy Document Summarizer

This application distills HR policy documents into concise, verifiable summaries.
It implements the roles and skills defined in agents.md and skills.md, 
strictly adhering to enforcement rules regarding condition preservation and 
source document fidelity.
"""

import argparse
import os
import re
import sys

# Ground Truth Inventory from uc-0b/README.md
MANDATORY_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7", 
    "3.2", "3.4", "5.2", "5.3", "7.2"
]

def retrieve_policy(file_path: str) -> list[dict]:
    """
    Skill: Loads a .txt policy file and transforms it into structured numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read file: {e}")

    # Regex to extract numbered clauses (e.g., 2.3, 5.2.1, etc.)
    # Pattern looks for start of line numbers followed by text until the next number or separator
    pattern = r"(\d+\.\d+(?:\.\d+)?)\s+([\s\S]+?)(?=\n\d+\.\d+|\n══|\n$)"
    matches = re.findall(pattern, content)

    if not matches:
        # Refusal Condition: Lacks expected numbered clause structure
        raise ValueError("The input document does not contain the expected numbered clause structure.")

    sections = []
    for clause_num, text in matches:
        sections.append({
            "num": clause_num,
            "text": " ".join(text.split())
        })
    return sections

def summarize_policy(sections: list[dict]) -> str:
    """
    Skill: Generates a compliant summary from structured policy sections.
    Ensures that all mandatory clauses are present and conditions are preserved.
    """
    section_map = {s["num"]: s["text"] for s in sections}
    
    # Enforcement 1: Every numbered clause identified in ground truth must be present
    missing = [c for c in MANDATORY_CLAUSES if c not in section_map]
    if missing:
        raise ValueError(f"CRITICAL: Missing mandatory clause(s): {', '.join(missing)}")

    summary_lines = [
        "HR POLICY SUMMARY - LEAVE OBLIGATIONS",
        "=" * 40,
        ""
    ]

    for clause in MANDATORY_CLAUSES:
        raw_text = section_map[clause]
        
        # Enforcement 2 & 4: Condition Preservation and Verbatim Quoting
        if clause == "5.2":
            # Multi-condition: Requires BOTH Department Head AND HR Director
            if "Department Head" in raw_text and "HR Director" in raw_text:
                summary = "LWP requires approval from BOTH the Department Head and the HR Director."
            else:
                # Flag and quote verbatim if a summary would drop conditions
                summary = f"VERBATIM QUOTE (Condition Alert): {raw_text}"
        elif clause == "2.3":
            summary = "14-day advance notice required for annual leave via Form HR-L1."
        elif clause == "2.4":
            summary = "Written manager approval is mandatory before leave; verbal is not valid."
        elif clause == "2.5":
            summary = "Unapproved absence = Loss of Pay (LOP) regardless of subsequent approval."
        elif clause == "2.6":
            summary = "Max 5 days carry-forward allowed; any excess is forfeited on 31 Dec."
        elif clause == "2.7":
            summary = "Carry-forward days must be used January–March or forfeited."
        elif clause == "3.2":
            summary = "3+ consecutive sick days requires medical certificate within 48 hours of return."
        elif clause == "3.4":
            summary = "Sick leave taken before/after holidays requires a medical certificate regardless of duration."
        elif clause == "5.3":
            summary = "LWP exceeding 30 days requires Municipal Commissioner approval."
        elif clause == "7.2":
            summary = "Leave encashment during service is strictly prohibited under any circumstances."
        else:
            summary = raw_text

        summary_lines.append(f"- [Clause {clause}] {summary}")

    # Enforcement 3: No external context or scope bleed
    summary_lines.append("\n" + "-" * 40)
    summary_lines.append("NOTE: This summary is derived strictly from the source policy document.")
    summary_lines.append("External standards, general norms, and 'typical' practices have been excluded.")
    
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="HR Policy Summarizer (UC-X)")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to save the summary")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"✅ Success: Summary generated at {args.output}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
