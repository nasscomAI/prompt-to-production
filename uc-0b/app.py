import argparse
import re
import sys
from pathlib import Path

# Required clauses from UC README
REQUIRED_CLAUSES = [
    "2.3","2.4","2.5","2.6","2.7",
    "3.2","3.4","5.2","5.3","7.2"
]


# -------------------------------
# Skill 1: retrieve_policy
# -------------------------------
def retrieve_policy(file_path):
    try:
        path = Path(file_path)

        if not path.exists():
            raise Exception("File access error: policy file not found")

        text = path.read_text(encoding="utf-8").strip()

        if not text:
            raise Exception("Invalid policy format: file is empty")

        # Extract numbered clauses
        pattern = r"(?m)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s+|\Z)"
        matches = re.findall(pattern, text, re.DOTALL)

        if not matches:
            raise Exception("Ambiguity error: numbered clauses not identifiable")

        clauses = {}

        for clause_id, clause_text in matches:
            clauses[clause_id.strip()] = clause_text.strip()

        return clauses

    except Exception as e:
        print("ERROR:", e)
        sys.exit(1)


# -------------------------------
# Skill 2: summarize_policy
# -------------------------------
def summarize_policy(clauses):

    summary = []

    # Check missing clauses
    missing = [c for c in REQUIRED_CLAUSES if c not in clauses]

    if missing:
        raise Exception(f"Clause omission error: missing clauses {missing}")

    for clause_id in REQUIRED_CLAUSES:

        text = clauses[clause_id]

        # Detect multi-condition obligations
        multi_condition_words = [
            "and",
            "within",
            "before",
            "regardless",
            "or"
        ]

        if any(word in text.lower() for word in multi_condition_words):
            # preserve verbatim
            summary.append(f"{clause_id} [VERBATIM]: {text}")
        else:
            summary.append(f"{clause_id}: {text}")

    return "\n\n".join(summary)


# -------------------------------
# Main
# -------------------------------
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output summary file"
    )

    args = parser.parse_args()

    try:

        # Step 1: Retrieve policy
        policy = retrieve_policy(args.input)

        # Step 2: Generate summary
        summary = summarize_policy(policy)

        # Step 3: Write output
        output_path = Path(args.output)

        output_path.write_text(summary, encoding="utf-8")

        print("Summary generated successfully:", output_path)

    except Exception as e:
        print("Processing error:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()