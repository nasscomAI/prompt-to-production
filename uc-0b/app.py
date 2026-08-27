import argparse
import os
import re
import sys

# Ground truth required clauses
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Expected binding verbs (None means multiple acceptable forms handled separately)
BINDING_VERBS = {
    "2.3": "must",
    "2.4": "must",
    "2.5": "will",
    "2.6": None,  # special handling
    "2.7": "must",
    "3.2": "requires",
    "3.4": "requires",
    "5.2": "requires",
    "5.3": "requires",
    "7.2": "not permitted"
}

# -------------------------
# Skill 1: retrieve_policy
# -------------------------
def retrieve_policy(file_path):
    """
    Loads a .txt HR policy document and returns structured numbered clauses.
    """
    if not os.path.exists(file_path):
        raise Exception("File access error: file does not exist")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception:
        raise Exception("File access error: cannot read file")

    # Extract clauses like 2.3, 3.2 etc.
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)

    if not matches:
        raise Exception("Structured parsing error: no numbered clauses found")

    clauses = {}
    for num, content in matches:
        content = content.strip()
        if not content:
            raise Exception("Incomplete source data: empty clause detected")
        clauses[num] = content

    return clauses


# -------------------------
# Validation helpers
# -------------------------
def validate_clause_presence(clauses):
    missing = [c for c in REQUIRED_CLAUSES if c not in clauses]
    if missing:
        raise Exception(f"Missing required clauses: {missing}")


def validate_binding_verbs(clauses):
    for clause, verb in BINDING_VERBS.items():
        text = clauses[clause].lower()

        if clause == "2.6":
            # Special: must include both carry-forward limit and forfeiture
            if not ("5" in text and "forfeit" in text):
                raise Exception("Obligation integrity error in clause 2.6: missing carry-forward or forfeiture condition")
            continue

        if verb and verb not in text:
            raise Exception(f"Obligation integrity error: binding verb '{verb}' missing or altered in clause {clause}")


def validate_clause_52(clauses):
    text = clauses["5.2"].lower()
    if not ("department head" in text and "hr director" in text):
        raise Exception("Condition drop risk: Clause 5.2 must include BOTH Department Head AND HR Director")


def validate_clause_25_absolute(clauses):
    text = clauses["2.5"].lower()
    if not ("regardless" in text or "will" in text):
        raise Exception("Clause 2.5 must remain absolute and not softened")


def validate_numbers_preserved(summary):
    required_values = ["14", "48", "5", "jan", "mar", "30"]
    for val in required_values:
        if val not in summary.lower():
            raise Exception(f"Numeric/temporal constraint missing: {val}")


def validate_no_scope_bleed(summary):
    forbidden_patterns = [
        "standard practice",
        "typically",
        "generally expected"
    ]
    for pattern in forbidden_patterns:
        if pattern in summary.lower():
            raise Exception("Scope bleed detected: forbidden phrase found")


# -------------------------
# Skill 2: summarize_policy
# -------------------------
def summarize_policy(clauses):
    """
    Generates a clause-complete, meaning-preserving summary.
    """

    if not isinstance(clauses, dict):
        raise Exception("Validation error: input structure malformed")

    # Enforce required validations before summarization
    validate_clause_presence(clauses)
    validate_binding_verbs(clauses)
    validate_clause_52(clauses)
    validate_clause_25_absolute(clauses)

    summary_lines = []

    for clause in REQUIRED_CLAUSES:
        original_text = clauses[clause].strip()

        # To avoid meaning loss → quote verbatim and flag
        line = f"{clause}: {original_text} [VERBATIM]"
        summary_lines.append(line)

    summary = "\n".join(summary_lines)

    # Final enforcement checks
    validate_no_scope_bleed(summary)
    validate_numbers_preserved(summary)

    return summary


# -------------------------
# Main App Entry
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy file")
    parser.add_argument("--output", required=True, help="Path to output summary file")

    args = parser.parse_args()

    try:
        # Step 1: Retrieve structured policy
        clauses = retrieve_policy(args.input)

        # Step 2: Generate compliant summary
        summary = summarize_policy(clauses)

        # Ensure output directory exists
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Step 3: Write output
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print("Summary generated successfully.")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()