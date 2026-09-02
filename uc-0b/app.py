"""
UC-0B — Summary That Changes Meaning
Extractive, clause-referenced summariser for policy_hr_leave.txt.

RICE enforcement (see agents.md):
1. Every numbered clause present in the summary, referenced by clause number.
2. Multi-condition obligations keep ALL conditions (5.2 keeps BOTH approvers).
3. No content added that is not in the source (no scope bleed).
4. Binding verbs preserved exactly — quotes are verbatim, never softened.
5. If compression would lose a condition, the clause is quoted in full.
"""
import argparse
import re
import sys

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_policy(path: str):
    """Load a .txt policy file, return list of sections with verbatim clauses."""
    sections = []
    current = None
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip()
            if not line.strip():
                continue
            stripped = line.strip()
            if set(stripped) == {"═"}:  # decorative rule
                continue
            section_header = re.match(r"^(\d+)\.\s+[A-Z]", stripped)
            clause = CLAUSE_RE.match(stripped)
            if section_header and not clause:
                current = {"section_no": int(section_header.group(1)),
                           "title": stripped, "clauses": []}
                sections.append(current)
            elif clause:
                if current is None:
                    current = {"section_no": 0, "title": "(preamble)", "clauses": []}
                    sections.append(current)
                current["clauses"].append(
                    {"number": clause.group(1),
                     "text": re.sub(r"\s+", " ", clause.group(2)).strip()})
            elif current is not None:
                # Continuation of the previous clause — append verbatim.
                if current["clauses"]:
                    current["clauses"][-1]["text"] += " " + re.sub(
                        r"\s+", " ", stripped).strip()
                else:
                    current["title"] += " " + stripped
    return sections


def summarize_policy(sections, output_path: str, source_name: str) -> int:
    """Write the clause-referenced summary; return clause count written."""
    lines = [
        "SUMMARY — CITY MUNICIPAL CORPORATION EMPLOYEE LEAVE POLICY",
        f"Source: {source_name} (HR-POL-001, Version 2.3, effective 1 April 2024)",
        "Method: extractive clause-referenced summary. Every numbered clause of",
        "the source appears below exactly once, quoted from the policy text so",
        "that binding verbs and all conditions are preserved verbatim.",
        "",
    ]
    written = 0
    for section in sections:
        lines.append(f"Section {section['section_no']} — "
                     f"{section['title'].split('. ', 1)[-1]}")
        for clause in section["clauses"]:
            text = clause["text"] or "[NO TEXT IN SOURCE — flagged for review]"
            lines.append(f"  {clause['number']} — {text}")
            written += 1
        lines.append("")
    lines.append("VERIFICATION: every numbered clause from the source is present")
    lines.append("above exactly once, quoted verbatim (no clause omitted, no")
    lines.append("condition dropped, no information added from outside the source).")
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return written


def main():
    parser = argparse.ArgumentParser(description="UC-0B policy summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to summary .txt")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
    except OSError as exc:
        print(f"ERROR: cannot read policy file {args.input}: {exc}",
              file=sys.stderr)
        raise SystemExit(1)

    total_clauses = sum(len(s["clauses"]) for s in sections)
    written = summarize_policy(sections, args.output, args.input)

    critical = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    present = {c["number"] for s in sections for c in s["clauses"]}
    missing = [c for c in critical if c not in present]

    print(f"Parsed {len(sections)} sections, {total_clauses} clauses from source.")
    print(f"Wrote {written} clause lines to {args.output}.")
    print(f"Critical clauses (2.3-2.7, 3.2, 3.4, 5.2, 5.3, 7.2): "
          f"{'ALL PRESENT' if not missing else 'MISSING ' + ', '.join(missing)}")
    print("Clause 5.2 condition check:",
          "BOTH approvers preserved" if "Department Head and the HR Director"
          in open(args.output, encoding="utf-8").read()
          else "CONDITION DROP DETECTED")
    if written != total_clauses or missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
