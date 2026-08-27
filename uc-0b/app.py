"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
# See README.md for run command and expected behaviour.
"""
import argparse
import re
import json


# -----------------------------
# Skill 1: retrieve_policy
# -----------------------------
def retrieve_policy(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        raise ValueError(f"Error reading file: {e}")

    clauses = []

    # Match proper clauses like 1.1, 2.3 etc.
    lines = text.split("\n")

    current_clause = None
    current_text = []

    for line in lines:
        line = line.strip()

        # Match clause number
        match = re.match(r"^(\d+\.\d+)\s+(.*)", line)

        if match:
            # Save previous clause
            if current_clause:
                clauses.append({
                    "clause": current_clause,
                    "text": " ".join(current_text).strip()
                })

            current_clause = match.group(1)
            current_text = [match.group(2)]

        elif current_clause:
            # Continue same clause
            if line and not line.startswith("═") and not re.match(r"^\d+\.\s", line):
                current_text.append(line)

    # Add last clause
    if current_clause:
        clauses.append({
            "clause": current_clause,
            "text": " ".join(current_text).strip()
        })

    if not clauses:
        raise ValueError("No structured clauses found.")

    return clauses


# -----------------------------
# Skill 2: summarize_policy
# -----------------------------
def summarize_policy(clauses):
    summary_lines = []

    for item in clauses:
        clause_num = item["clause"]
        text = item["text"]

        # Only flag if text is actually unclear or too short
        if len(text) < 20:
            summary = f"{clause_num}: {text} [REQUIRES REVIEW]"
        else:
            summary = f"{clause_num}: {text}"

        summary_lines.append(summary)

    return "\n".join(summary_lines)


# -----------------------------
# Main
# -----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(clauses, f, indent=2)

        print("✅ Summary generated successfully.")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()