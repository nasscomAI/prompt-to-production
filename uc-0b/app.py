import argparse
import os
import re

# --- Ground Truth Clauses (from agents.md) ---
REQUIRED_CLAUSES = {
    "2.3": "14-day advance notice required",
    "2.4": "Written approval required before leave commences. Verbal not valid.",
    "2.5": "Unapproved absence = LOP regardless of subsequent approval",
    "2.6": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.",
    "2.7": "Carry-forward days must be used Jan–Mar or forfeited",
    "3.2": "3+ consecutive sick days requires medical cert within 48hrs",
    "3.4": "Sick leave before/after holiday requires cert regardless of duration",
    "5.2": "LWP requires Department Head AND HR Director approval",
    "5.3": "LWP >30 days requires Municipal Commissioner approval",
    "7.2": "Leave encashment during service not permitted under any circumstances",
}

# --- VERB ENFORCEMENT ---
BINDING_VERBS = ["must", "requires", "will", "not permitted"]


# -------------------------------
# SKILL 1: retrieve_policy
# -------------------------------
def retrieve_policy(file_path):
    """
    Reads a .txt file and extracts clauses into a dictionary.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError("Input file not found")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex for clause numbers like 2.3, 5.2 etc.
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)

    clauses = {}

    for clause_num, clause_text in matches:
        clean_text = " ".join(clause_text.strip().split())
        clauses[clause_num] = clean_text

    if not clauses:
        return {}, "NEEDS_REVIEW"

    return clauses, ""


# -------------------------------
# HELPER: Check verb presence
# -------------------------------
def preserve_binding_verb(text):
    text_lower = text.lower()
    for verb in BINDING_VERBS:
        if verb in text_lower:
            return True
    return False


# -------------------------------
# SKILL 2: summarize_policy
# -------------------------------
def summarize_policy(clauses):
    """
    Produces clause-by-clause compliant summary.
    """
    summary_lines = []
    flag_review = False

    for clause_id in REQUIRED_CLAUSES.keys():

        if clause_id not in clauses:
            summary_lines.append(f"{clause_id}: Clause not found in document [NEEDS_REVIEW]")
            flag_review = True
            continue

        original_text = clauses[clause_id]

        # --- MULTI-CONDITION CHECK (important trap handling) ---
        multi_condition = " and " in original_text.lower() or "AND" in original_text

        # --- VERB CHECK ---
        has_binding = preserve_binding_verb(original_text)

        # --- DECISION: summarize OR quote ---
        if multi_condition or not has_binding:
            # Too risky → quote verbatim
            summary = f"{clause_id}: {original_text} [VERBATIM]"
            flag_review = True
        else:
            # Safe summarization (minimal compression)
            summary = f"{clause_id}: {original_text}"

        summary_lines.append(summary)

    return "\n".join(summary_lines), flag_review


# -------------------------------
# MAIN APP LOGIC
# -------------------------------
def process_policy(input_path, output_path):
    clauses, retrieve_flag = retrieve_policy(input_path)

    summary, summary_flag = summarize_policy(clauses)

    final_output = summary

    if retrieve_flag or summary_flag:
        final_output += "\n\n[NOTE]: Some clauses required verbatim handling or review."

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_output)


# -------------------------------
# CLI ENTRY
# -------------------------------
def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Input policy file path")
    parser.add_argument("--output", required=True, help="Output summary file path")

    args = parser.parse_args()

    # Ensure input path is inside required directory
    if not os.path.normpath(args.input).startswith(os.path.normpath("../data/policy-documents")):
        raise ValueError("Input must be from ../data/policy-documents/ folder")

    process_policy(args.input, args.output)


if __name__ == "__main__":
    main()
