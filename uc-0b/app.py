"""
UC-0B — Summary That Changes Meaning
Built per agents.md (RICE enforcement rules) and skills.md.
"""
import argparse
import re

GROUND_TRUTH_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2",
]

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_policy(file_path: str) -> dict:
    """
    Load the .txt policy file and return content as structured numbered sections.
    Returns: dict {clause_number: raw_text}
    """
    sections = {}
    current_num = None
    with open(file_path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            # Section divider (Unicode box-drawing "═", not ASCII "=") or an
            # ALL-CAPS section header line — hard stop, never a continuation
            # of the previous clause. Bug found via testing: startswith("=")
            # missed the Unicode "═" divider, so clause 2.7/3.4 (immediately
            # followed by a divider + header) silently swallowed the next
            # section's divider lines into their own text.
            if set(line) <= {"═"} or (line.isupper() and current_num is not None):
                current_num = None
                continue
            m = CLAUSE_RE.match(line)
            if m:
                current_num = m.group(1)
                sections[current_num] = m.group(2)
            elif current_num is not None:
                # continuation line of a wrapped clause — append, don't drop.
                sections[current_num] += " " + line
    return sections


def summarize_policy(sections: dict) -> str:
    """
    Produce a compliant clause-by-clause summary with clause references.
    Returns: str
    """
    lines = ["CMC EMPLOYEE LEAVE POLICY — CLAUSE SUMMARY (verbatim per clause, no paraphrase)", ""]
    for num in GROUND_TRUTH_CLAUSES:
        raw = sections.get(num)
        if raw is None:
            lines.append(f"[{num}] MISSING FROM SOURCE — cannot summarise.")
            continue
        lines.append(f"[{num}] [VERBATIM] \"{raw}\"")

    lines.append("")
    lines.append("COMPLIANCE CHECK")
    for num in GROUND_TRUTH_CLAUSES:
        status = "PRESENT (verbatim)" if num in sections else "MISSING"
        lines.append(f"  {num}: {status}")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary text")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary + "\n")
    print(f"Done. Summary written to {args.output}")
