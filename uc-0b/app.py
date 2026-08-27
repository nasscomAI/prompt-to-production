"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re


def retrieve_policy(file_path):
    """
    Reads the policy file and extracts numbered clauses.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to capture clauses like 2.3, 2.4 etc.
    pattern = r"(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    clauses = {}
    for num, text in matches:
        clauses[num.strip()] = text.strip()

    return clauses


def summarize_policy(clauses):
    """
    Creates a strict summary without losing meaning.
    """
    summary_lines = []

    for clause_num, text in sorted(clauses.items()):
        # Preserve original text if complex
        if "and" in text.lower() or "or" in text.lower():
            summary = f"{clause_num}: {text} [VERBATIM - complex clause]"
        else:
            summary = f"{clause_num}: {text}"

        summary_lines.append(summary)

    return "\n".join(summary_lines)


def save_summary(output_path, summary_text):
    """
    Saves summary to file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_text)


def main():
    parser = argparse.ArgumentParser(description="HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Input policy file path")
    parser.add_argument("--output", required=True, help="Output summary file path")

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    save_summary(args.output, summary)

    print("✅ Summary generated successfully!")


if __name__ == "__main__":
    main()