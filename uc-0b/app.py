import argparse
import os
import re
import sys


# =========================
# SKILL 1: retrieve_policy
# =========================
def retrieve_policy(file_path):
    # File validation
    if not os.path.exists(file_path):
        raise ValueError(f"Input file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        raise ValueError(f"Failed to read file: {str(e)}")

    if not text.strip():
        raise ValueError("Document is empty")

    # Extract numbered clauses like 2.3, 3.2 etc.
    pattern = r"(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)"
    matches = re.findall(pattern, text, re.DOTALL)

    if not matches:
        raise ValueError("Could not identify numbered clauses reliably")

    clauses = {}
    for clause_id, clause_text in matches:
        clean_text = clause_text.strip().replace("\n", " ")
        clauses[clause_id] = clean_text

    return clauses


# =========================
# SKILL 2: summarize_policy
# =========================
def summarize_policy(clauses):
    if not isinstance(clauses, dict) or len(clauses) == 0:
        raise ValueError("Invalid structured clauses input")

    summary_lines = []

    # Sort clauses numerically (2.3, 2.4, 3.2...)
    sorted_ids = sorted(clauses.keys(), key=lambda x: list(map(int, x.split("."))))

    for clause_id in sorted_ids:
        text = clauses[clause_id]

        # Enforcement: preserve ALL conditions
        # If multiple conditions detected → use VERBATIM
        if any(word in text.lower() for word in [" and ", " or ", " both "]):
            summary = f"{clause_id}: [VERBATIM] {text}"
        else:
            summary = f"{clause_id}: {text}"

        summary_lines.append(summary)

    # Enforcement: no clause omission
    if len(summary_lines) != len(clauses):
        raise ValueError("Clause omission detected")

    return "\n".join(summary_lines)


# =========================
# MAIN APP
# =========================
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    try:
        # Step 1: Load + validate policy
        clauses = retrieve_policy(args.input)

        # Step 2: Generate summary
        summary = summarize_policy(clauses)

        # Final enforcement check
        for clause_id in clauses.keys():
            if clause_id not in summary:
                raise ValueError(f"Missing clause in summary: {clause_id}")

        # Step 3: Write output file
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"✅ Summary written to {args.output}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()