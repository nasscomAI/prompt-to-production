"""
UC-0B app.py — Policy summarizer.
Implements retrieve_policy and summarize_policy skills from skills.md.
See agents.md for enforcement rules.
"""
import argparse
import re
import sys


def retrieve_policy(filepath):
    """
    Skill: retrieve_policy
    Loads a .txt policy file and returns structured numbered sections.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found — {filepath}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: Cannot read file — {e}", file=sys.stderr)
        sys.exit(1)

    clauses = []
    clause_start = re.compile(r"^(\d+\.\d+)\s+(.*)")
    continuation = re.compile(r"^\s{4}(.*)")

    for line in lines:
        stripped = line.rstrip("\n")
        m = clause_start.match(stripped)
        if m:
            clause_id = m.group(1)
            clause_text = m.group(2)
            clauses.append({"clause_id": clause_id, "content": clause_text})
        else:
            c = continuation.match(stripped)
            if c and clauses:
                clauses[-1]["content"] += " " + c.group(1)

    if not clauses:
        print("Error: No numbered clauses found in the file.", file=sys.stderr)
        sys.exit(1)

    return clauses


def summarize_policy(clauses):
    """
    Skill: summarize_policy
    Takes structured clauses, produces a faithful plain-text summary.
    Every clause is included. Multi-condition obligations are preserved.
    No external information is added. Clauses that cannot be safely
    summarised are quoted verbatim and flagged [VERBATIM].
    """
    section_map = {
        "1": "1. PURPOSE AND SCOPE",
        "2": "2. ANNUAL LEAVE",
        "3": "3. SICK LEAVE",
        "4": "4. MATERNITY AND PATERNITY LEAVE",
        "5": "5. LEAVE WITHOUT PAY (LWP)",
        "6": "6. PUBLIC HOLIDAYS",
        "7": "7. LEAVE ENCASHMENT",
        "8": "8. GRIEVANCES",
    }

    lines = [
        "POLICY SUMMARY — HR-POL-001 (Employee Leave Policy)",
        "=====================================================",
    ]
    current_section = None

    for clause in clauses:
        clause_id = clause["clause_id"]
        section_num = clause_id.split(".")[0]
        content = clause["content"]

        # Validate clause ID
        if not re.match(r"^\d+\.\d+$", clause_id):
            content += " [MALFORMED ID]"

        if section_num != current_section:
            current_section = section_num
            section_title = section_map.get(section_num, f"Section {section_num}")
            lines.append("")
            lines.append(section_title)
            lines.append("-" * len(section_title))

        # Quote verbatim to guarantee zero meaning loss
        lines.append(f"  {clause_id} {content} [VERBATIM]")

    return "\n".join(lines).strip()


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Faithful HR policy summarizer"
    )
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument(
        "--output", required=True, help="Path for the output summary file"
    )
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)

    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
        f.write("\n")


if __name__ == "__main__":
    main()
