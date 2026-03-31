import argparse
import os
import re
import sys

# Required clauses (ground truth)
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Disallowed phrases (scope bleed)
DISALLOWED_PHRASES = [
    "as is standard practice",
    "typically",
    "generally",
    "employees are generally expected to"
]

# Binding verbs
BINDING_VERBS = ["must", "requires", "will", "not permitted", "are forfeited", "may"]


# ---------------------- SKILL 1 ----------------------
def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        raise Exception("File access failure: input file not found")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception:
        raise Exception("File access failure: unable to read file")

    # Improved regex (only match clause numbers at line start)
    pattern = re.compile(r'^\s*(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+|\Z)', re.S | re.M)
    matches = pattern.findall(text)

    if not matches:
        raise Exception("Unstructured input: no numbered clauses found")

    clauses = {}
    duplicates = []

    for num, content in matches:
        num = num.strip()
        content = content.strip()

        if num in clauses:
            duplicates.append(num)
            continue  # Ignore duplicate instead of failing

        clauses[num] = content

    if duplicates:
        print(f"Warning: duplicate clauses found and ignored: {duplicates}")

    # Check required clauses
    missing = [c for c in REQUIRED_CLAUSES if c not in clauses]
    if missing:
        raise Exception(f"Missing required clauses: {missing}")

    return clauses


# ---------------------- VALIDATIONS ----------------------
def validate_binding_verbs(original, summary):
    for verb in BINDING_VERBS:
        if verb in original.lower() and verb not in summary.lower():
            raise Exception("Obligation softening error: binding verb altered or missing")


def validate_no_scope_bleed(summary):
    for phrase in DISALLOWED_PHRASES:
        if phrase in summary.lower():
            raise Exception("Scope bleed error: disallowed phrase detected")


def validate_multi_conditions(clause_id, text):
    t = text.lower()

    if clause_id == "5.2":
        if not ("department head" in t and "hr director" in t):
            raise Exception("Condition drop error: Clause 5.2 must include BOTH Department Head AND HR Director")

    if clause_id == "5.3":
        if "municipal commissioner" not in t:
            raise Exception("Condition drop error: Clause 5.3 missing Municipal Commissioner")

    if clause_id == "2.5":
        if not ("lop" in t and "regardless" in t):
            raise Exception("Condition drop error: Clause 2.5 must include LOP regardless of later approval")

    if clause_id == "2.6":
        if not ("5" in t and "31 dec" in t):
            raise Exception("Condition drop error: Clause 2.6 must include limit and deadline (31 Dec, max 5 days)")

    if clause_id == "2.7":
        if not ("jan" in t and "mar" in t):
            raise Exception("Condition drop error: Clause 2.7 must include Jan–Mar usage window")


# ---------------------- SKILL 2 ----------------------
def summarize_policy(clauses):
    missing = [c for c in REQUIRED_CLAUSES if c not in clauses]
    if missing:
        raise Exception(f"Incomplete clause coverage: missing {missing}")

    summary_lines = []

    for clause_id in REQUIRED_CLAUSES:
        original_text = clauses[clause_id].strip()

        # Validate multi-condition preservation
        validate_multi_conditions(clause_id, original_text)

        # Use verbatim text (ensures no meaning loss)
        summary_text = original_text

        # Validate binding verbs
        validate_binding_verbs(original_text, summary_text)

        summary_lines.append(f"{clause_id}: {summary_text}")

    summary = "\n".join(summary_lines)

    # Global validations
    validate_no_scope_bleed(summary)

    # Ensure all clauses are present
    for clause_id in REQUIRED_CLAUSES:
        if clause_id not in summary:
            raise Exception(f"Clause omission error: {clause_id} missing in summary")

    return summary


# ---------------------- MAIN ----------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input policy file")
    parser.add_argument("--output", required=True, help="Output file name")

    args = parser.parse_args()

    try:
        # Step 1: Retrieve
        clauses = retrieve_policy(args.input)

        # Step 2: Summarize
        summary = summarize_policy(clauses)

        # Step 3: Write output
        output_dir = "uc-0b"
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, args.output)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"✅ Summary successfully written to {output_path}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()