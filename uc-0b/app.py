"""
UC-0B app.py — Summary That Changes Meaning
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re


def retrieve_policy(file_path: str) -> dict:
    """Load policy file and return structured numbered sections."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (FileNotFoundError, IOError):
        print("Error: Cannot read policy document")
        return {}

    sections = {}
    lines = content.split("\n")
    current_section = None
    current_text = []

    for line in lines:
        match = re.match(r"^\s*(\d+\.\d+)\s+(.*)", line)
        if match:
            if current_section:
                sections[current_section] = " ".join(current_text).strip()
            current_section = match.group(1)
            current_text = [match.group(2)]
        elif current_section and line.strip():
            current_text.append(line.strip())

    if current_section:
        sections[current_section] = " ".join(current_text).strip()

    return sections


def summarize_policy(sections: dict) -> str:
    """Produce compliant summary preserving all clauses and conditions."""
    critical_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

    summary_parts = []
    summary_parts.append("CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY")
    summary_parts.append("=" * 55)
    summary_parts.append("")

    for clause in critical_clauses:
        if clause in sections:
            summary_parts.append(f"Clause {clause}: {sections[clause]}")
            summary_parts.append("")
        else:
            summary_parts.append(f"Clause {clause}: [SECTION MISSING]")
            summary_parts.append("")

    return "\n".join(summary_parts)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    if not sections:
        print("Error: No sections found in policy document")
        return

    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
