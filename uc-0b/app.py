"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

# Only the clauses the trainer wants preserved
TARGET_CLAUSES = {
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2"
}


def retrieve_policy(path):

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    clauses = []

    # Extract numbered clauses
    pattern = r'\n(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)

    for num, text in matches:

        if num in TARGET_CLAUSES:

            # Normalize whitespace
            clean = " ".join(text.split())

            # Remove section headers accidentally captured
            clean = re.sub(r'\d+\.\s+[A-Z][A-Z\s]+', '', clean)

            clauses.append({
                "clause": num,
                "text": clean.strip()
            })

    return clauses


def summarize_policy(clauses):

    summary = []

    for clause in clauses:

        text = clause["text"]
        lower = text.lower()

        # Detect legal clauses needing verbatim preservation
        if " and " in lower or "not permitted" in lower:
            line = f"{clause['clause']} VERBATIM_REQUIRED: {text}"

        else:
            short = text.split(".")[0]
            line = f"{clause['clause']} {short}"

        summary.append(line)

    return "\n\n".join(summary)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)

    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Policy summary generated successfully.")


if __name__ == "__main__":
    main()