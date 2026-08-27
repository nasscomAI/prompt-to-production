"""
UC-0B — Policy Summarizer
Starter file. Built using RICE → agents.md → skills.md → CRAFT workflow.
"""

import argparse
import os

# Clause inventory (ground truth)
CLAUSE_INVENTORY = {
    "2.3": {"obligation": "14-day advance notice required", "verb": "must"},
    "2.4": {"obligation": "Written approval required before leave commences. Verbal not valid.", "verb": "must"},
    "2.5": {"obligation": "Unapproved absence = LOP regardless of subsequent approval", "verb": "will"},
    "2.6": {"obligation": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.", "verb": "may / are forfeited"},
    "2.7": {"obligation": "Carry-forward days must be used Jan–Mar or forfeited", "verb": "must"},
    "3.2": {"obligation": "3+ consecutive sick days requires medical cert within 48hrs", "verb": "requires"},
    "3.4": {"obligation": "Sick leave before/after holiday requires cert regardless of duration", "verb": "requires"},
    "5.2": {"obligation": "LWP requires Department Head AND HR Director approval", "verb": "requires"},
    "5.3": {"obligation": "LWP >30 days requires Municipal Commissioner approval", "verb": "requires"},
    "7.2": {"obligation": "Leave encashment during service not permitted under any circumstances", "verb": "not permitted"},
}

# --- Skill: retrieve_policy ---
def retrieve_policy(input_file: str):
    """
    Loads the HR leave policy text file and returns its content as structured numbered sections.
    """
    if not os.path.exists(input_file):
        return {"error": f"File {input_file} not found."}

    structured = {}
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for clause, data in CLAUSE_INVENTORY.items():
            # naive match: look for clause number in text
            clause_text = [line.strip() for line in lines if line.strip().startswith(clause)]
            if clause_text:
                structured[clause] = clause_text[0]
            else:
                # flag missing clause
                structured[clause] = f"[FLAGGED: Clause {clause} missing in source]"
    except Exception as e:
        return {"error": str(e)}

    return structured

# --- Skill: summarize_policy ---
def summarize_policy(structured_sections: dict, output_file: str):
    """
    Produces a compliant summary of the HR leave policy with clause references.
    """
    summary_lines = []
    for clause, text in structured_sections.items():
        if text.startswith("[FLAGGED"):
            summary_lines.append(text)
            continue

        obligation = CLAUSE_INVENTORY[clause]["obligation"]
        verb = CLAUSE_INVENTORY[clause]["verb"]

        # Enforcement: preserve binding verb and all conditions
        if clause == "5.2":
            if "Department Head" not in text or "HR Director" not in text:
                summary_lines.append(f"{clause}: {text} [FLAGGED: Missing approver condition]")
                continue

        # If summarization risks meaning loss, quote verbatim
        if any(word not in text for word in obligation.split()):
            summary_lines.append(f"{clause}: \"{text}\" [FLAGGED: Quoted verbatim to avoid meaning loss]")
        else:
            summary_lines.append(f"{clause}: {obligation} ({verb})")

    try:
        # Only make directories if a folder path is provided
        dir_name = os.path.dirname(output_file)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            for line in summary_lines:
                f.write(line + "\n")
    except Exception as e:
        print(f"Error writing summary: {e}")

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()

    structured = retrieve_policy(args.input)
    if "error" in structured:
        print(structured["error"])
        return

    summarize_policy(structured, args.output)
    print(f"Summary complete. Results written to {args.output}")

if __name__ == "__main__":
    main()
