
import argparse
import sys
import re
from pathlib import Path
from collections import defaultdict


def load_policy(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_clauses(text: str):
    """
    Extract numbered clauses like 2.3, 5.2 and
    safely merge wrapped lines.
    """
    pattern = re.compile(r"^(\d+\.\d+)\s+(.*)")
    clauses = []
    current = None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        match = pattern.match(line)
        if match:
            if current:
                clauses.append(current)
            current = {
                "id": match.group(1),
                "section": match.group(1).split(".")[0],
                "text": match.group(2),
            }
        elif current:
            # continuation of previous clause
            current["text"] += " " + line

    if current:
        clauses.append(current)

    return clauses


def summarize_clause(text: str) -> str:
    """
    Real summarization:
    remove fluff but keep obligations, limits, approvals.
    """
    fluff_phrases = [
        "each employee is entitled to",
        "employees are entitled to",
        "this policy",
        "are entitled to",
        "may be",
    ]

    summary = text.lower()
    for phrase in fluff_phrases:
        summary = summary.replace(phrase, "")

    summary = re.sub(r"\s+", " ", summary).strip()
    summary = summary.capitalize()

    return summary


def summarize_policy(clauses):
    sections = defaultdict(list)

    for clause in clauses:
        summarized = summarize_clause(clause["text"])
        sections[clause["section"]].append(summarized)

    output = []

    for section in sorted(sections.keys(), key=int):
        output.append(f"SECTION {section}")
        output.append("-" * (8 + len(section)))

        for rule in sections[section]:
            output.append(f"- {rule}")

        output.append("")

    return "\n".join(output).strip()


def main():
    parser = argparse.ArgumentParser(description="Policy summarizer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        policy_text = load_policy(Path(args.input))
        clauses = extract_clauses(policy_text)
        summary = summarize_policy(clauses)
        Path(args.output).write_text(summary, encoding="utf-8")

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

