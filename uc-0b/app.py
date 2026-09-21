"""UC-0B clause-preserving HR policy summarizer."""
import argparse
import re

REQUIRED_CLAUSES = ("2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2")
CLAUSE_PATTERN = re.compile(
    r"(?ms)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|^\s*═+\s*$|\Z)"
)


def retrieve_policy(input_path):
    with open(input_path, "r", encoding="utf-8-sig") as source:
        content = source.read()
    clauses = {}
    for match in CLAUSE_PATTERN.finditer(content):
        number = match.group(1)
        text = " ".join(line.strip() for line in match.group(2).splitlines()).strip()
        clauses[number] = text
    missing = [number for number in REQUIRED_CLAUSES if number not in clauses]
    if missing:
        raise ValueError("Required policy clauses not found: {}".format(", ".join(missing)))
    return [{"section": number, "text": clauses[number]} for number in REQUIRED_CLAUSES]


def summarize_policy(sections):
    lines = [
        "HR Leave Policy — Required Clause Summary",
        "",
        "The following required clauses are preserved verbatim from the source policy:",
        "",
    ]
    for section in sections:
        lines.append("Section {} (verbatim): {}".format(section["section"], section["text"]))
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Summarize required HR leave policy clauses")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    summary = summarize_policy(retrieve_policy(args.input))
    with open(args.output, "w", encoding="utf-8", newline="") as target:
        target.write(summary)
    print("Wrote {} required clauses to {}".format(len(REQUIRED_CLAUSES), args.output))


if __name__ == "__main__":
    main()
