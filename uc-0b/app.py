"""
UC-0B - Summary That Changes Meaning
Produces a compliant clause-referenced summary of an HR policy document
without dropping conditions, omitting clauses, or adding invented scope
language ("as is standard practice", etc).
"""
import argparse
import re

TARGET_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

CLAUSE_HEADER_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_RE = re.compile(r"^\d+\.\s+[A-Z]")


def _is_divider(line: str) -> bool:
    """True if the line is a decorative divider (any repeated symbol char)."""
    if len(line) < 5:
        return False
    chars = set(line)
    return len(chars) == 1 and not line[0].isalnum()


def retrieve_policy(input_path: str) -> dict:
    """Loads .txt policy file, returns content as structured numbered sections."""
    sections = {}
    current_num = None
    current_lines = []

    with open(input_path, encoding="utf-8") as f:
        lines = f.readlines()

    def flush():
        nonlocal current_num, current_lines
        if current_num:
            sections[current_num] = " ".join(current_lines).strip()
        current_num = None
        current_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        clause_match = CLAUSE_HEADER_RE.match(stripped)
        if clause_match:
            flush()
            current_num = clause_match.group(1)
            current_lines = [clause_match.group(2)]
            continue

        if _is_divider(stripped) or SECTION_HEADER_RE.match(stripped):
            flush()
            continue

        if current_num:
            current_lines.append(stripped)

    flush()
    return sections


def summarize_policy(sections: dict) -> str:
    """Takes structured sections, produces compliant summary with clause references."""
    lines = []
    missing = []

    for clause in TARGET_CLAUSES:
        if clause not in sections:
            missing.append(clause)
            continue
        text = sections[clause]
        lines.append(f"[Clause {clause}] {text}")

    summary = "\n\n".join(lines)

    if missing:
        summary += f"\n\n[FLAG] Missing from source, could not summarise: {', '.join(missing)}"

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt")
    parser.add_argument("--output", required=True, help="Path to output summary .txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    found = sum(1 for c in TARGET_CLAUSES if c in sections)
    print(f"Summarized {found}/{len(TARGET_CLAUSES)} target clauses -> {args.output}")
