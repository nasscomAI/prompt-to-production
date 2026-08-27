import argparse
import re
import sys


def retrieve_policy(filepath):
    sections = []
    current_section = None
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)")

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^═+$", stripped):
            continue
        header_match = re.match(r"^(\d+)\.\s+(.+)", stripped)
        if header_match:
            current_section = {
                "title": f"{header_match.group(1)}. {header_match.group(2)}",
                "clauses": [],
            }
            sections.append(current_section)
            continue
        clause_match = clause_pattern.match(stripped)
        if clause_match and current_section is not None:
            num = clause_match.group(1)
            text = clause_match.group(2)
            current_section["clauses"].append({"number": num, "text": text})
        elif current_section is not None and current_section["clauses"]:
            current_section["clauses"][-1]["text"] += " " + stripped

    return sections


def summarize_policy(sections):
    lines = []
    lines.append("POLICY SUMMARY")
    lines.append("=" * 80)
    lines.append("")

    for section in sections:
        lines.append(section["title"])
        lines.append("-" * len(section["title"]))
        for clause in section["clauses"]:
            text = clause["text"]
            num = clause["number"]
            if any(kw in text for kw in ["not permitted", "must", "requires", "will"]):
                lines.append(f"  {num}: {text}")
            else:
                lines.append(f"  {num}: {text}")
            lines.append("")
        lines.append("")

    lines.append("=" * 80)
    lines.append("End of summary — all numbered clauses from the source are preserved.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Summarize a policy document."
    )
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument(
        "--output", required=True, help="Path to output summary .txt file"
    )
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
    except FileNotFoundError:
        print(f"Error: File not found — {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
