"""
UC-0B — Summary That Changes Meaning
Built with the RICE workflow; enforcement rules in agents.md.
Reads data/policy-documents/policy_hr_leave.txt and writes uc-0b/summary_hr_leave.txt.
"""
import argparse
import re

CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z].*)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_policy(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        raw_lines = f.read().splitlines()

    metadata = []
    sections = []
    current = None

    for line in raw_lines:
        stripped = line.strip()
        if not stripped or set(stripped) == {"═"}:
            continue

        m = SECTION_RE.match(stripped)
        if m:
            current = {"number": m.group(1), "title": m.group(2), "clauses": []}
            sections.append(current)
            continue

        m = CLAUSE_RE.match(stripped)
        if m:
            if current is None:
                current = {"number": "0", "title": "PREAMBLE", "clauses": []}
                sections.insert(0, current)
            current["clauses"].append({"number": m.group(1), "text": m.group(2)})
            continue

        # Continuation of the current clause (wrapped line) or doc header.
        if current and current["clauses"]:
            current["clauses"][-1]["text"] += " " + stripped
        else:
            metadata.append(stripped)

    return {"metadata": metadata, "sections": sections}


def summarize_policy(policy: dict) -> str:
    lines = []
    lines.append("EMPLOYEE LEAVE POLICY — FAITHFUL CLAUSE SUMMARY")
    lines.append("Source: data/policy-documents/policy_hr_leave.txt")
    if policy["metadata"]:
        lines.append(" | ".join(policy["metadata"]))
    lines.append(
        "Every numbered clause is quoted verbatim from the source so that no condition "
        "can be dropped, softened, or invented. No information is added."
    )
    lines.append("")

    all_clause_numbers = []
    for section in policy["sections"]:
        lines.append(f"{section['number']}. {section['title']}")
        for clause in section["clauses"]:
            all_clause_numbers.append(clause["number"])
            lines.append(f"{clause['number']} {clause['text']}")
        lines.append("")

    # Enforcement rule 1: every numbered clause must be present in the output.
    expected = set(all_clause_numbers)
    if len(expected) != len(all_clause_numbers):
        raise ValueError("Duplicate clause numbers detected in source document.")

    missing_critical = [c for c in CRITICAL_CLAUSES if c not in expected]
    if missing_critical:
        raise ValueError(f"Completeness check failed — critical clauses missing: {missing_critical}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Faithful Policy Summary")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary + "\n")

    clause_numbers = [c["number"] for s in policy["sections"] for c in s["clauses"]]
    print(f"Wrote {args.output}")
    print(f"  Sections: {len(policy['sections'])}")
    print(f"  Numbered clauses: {len(clause_numbers)}")
    print(f"  All 10 critical clauses present: {all(c in clause_numbers for c in CRITICAL_CLAUSES)}")
    print(f"  Critical clauses: {', '.join(CRITICAL_CLAUSES)}")


if __name__ == "__main__":
    main()
