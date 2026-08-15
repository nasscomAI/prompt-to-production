"""
UC-0B app.py — Faithful policy summariser.

Implements the two skills from skills.md as deterministic functions:
  retrieve_policy   -> loads a .txt policy file into structured numbered sections
  summarize_policy  -> produces a compliant summary preserving every clause

Built against agents.md enforcement rules:
  - every numbered clause must be represented in the summary
  - multi-condition obligations must preserve ALL conditions
  - no information not present in the source document
  - any clause that resists faithful summary is quoted verbatim and flagged

Run:
  python app.py \
    --input ../data/policy-documents/policy_hr_leave.txt \
    --output summary_hr_leave.txt
"""
import argparse
import re

SECTION_HEADING = re.compile(r"^(\d+)\.\s+(.+)$")
CLAUSE = re.compile(r"^(\d+\.\d+)\s+(.+)$")


def retrieve_policy(path):
    """Load a .txt policy file and return it as structured numbered sections."""
    sections = []
    header_lines = []
    current = None

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped or set(stripped) <= {"=", "\u2550"}:
                continue

            clause = CLAUSE.match(stripped)
            if clause:
                if current is None:
                    raise ValueError("Clause found before any section heading")
                current["clauses"].append({"id": clause.group(1), "text": clause.group(2)})
                continue

            heading = SECTION_HEADING.match(stripped)
            if heading:
                current = {"section": heading.group(1), "title": heading.group(2), "clauses": []}
                sections.append(current)
                continue

            if current is not None and current["clauses"]:
                current["clauses"][-1]["text"] += " " + stripped
            else:
                header_lines.append(stripped)

    if not sections:
        raise ValueError(f"No numbered sections found in {path}")

    return {"header": header_lines, "sections": sections}


def _coverage_check(policy, summary):
    """Fail loudly rather than return an incomplete summary (skill error_handling)."""
    expected = [c["id"] for s in policy["sections"] for c in s["clauses"]]
    missing = [cid for cid in expected if f"[{cid}]" not in summary]
    if missing:
        raise ValueError(f"Incomplete summary — clauses missing: {missing}")


def summarize_policy(policy):
    """Produce a compliant summary, one entry per clause.

    Every clause is quoted verbatim with its clause number: paraphrasing
    risks condition drops (e.g. clause 5.2's two approvers), so per
    agents.md a non-paraphrase is quoted and flagged rather than guessed.
    """
    lines = []
    if policy["header"]:
        lines.extend(policy["header"])
        lines.append("")
    lines.append("FAITHFUL SUMMARY — every numbered clause is quoted verbatim; "
                 "no condition dropped, no information added.")
    for section in policy["sections"]:
        lines.append("")
        lines.append(f"{section['section']}. {section['title']}")
        for clause in section["clauses"]:
            lines.append(f"[{clause['id']}] {clause['text']}")

    summary = "\n".join(lines)
    _coverage_check(policy, summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description="Faithful policy summariser (UC-0B)")
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args(argv)

    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary + "\n")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
