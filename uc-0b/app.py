"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

def retrieve_policy(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except FileNotFoundError:
        raise Exception("Input file not found")

    if not content:
        raise Exception("Input file is empty or unreadable")

    pattern = r"(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        raise Exception("Invalid or inconsistent clause structure")

    structured = {num: text.strip() for num, text in matches}

    return structured


def safe_summarize(clause, text):
    high_risk = ["5.2", "5.3", "7.2"]

    if clause in high_risk:
        return f"[VERBATIM] {text}"

    summarized = re.sub(r"\s+", " ", text).strip()

    forbidden = ["generally", "typically", "standard practice"]
    for word in forbidden:
        if word in summarized.lower():
            raise Exception("Scope bleed detected")

    return summarized


def summarize_policy(structured):
    summary = []

    for clause in REQUIRED_CLAUSES:
        if clause not in structured:
            raise Exception("Missing required clauses for summarization")

        text = structured[clause]

        if clause == "5.2":
            if "Department Head" not in text or "HR Director" not in text:
                raise Exception("Incomplete clause conditions detected")

        if clause == "2.5":
            if "regardless of subsequent approval" not in text:
                raise Exception("Incomplete clause conditions detected")

        summarized = safe_summarize(clause, text)
        summary.append(f"{clause}: {summarized}")

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    try:
        structured = retrieve_policy(args.input)
        summary = summarize_policy(structured)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print("✅ Summary generated successfully.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()