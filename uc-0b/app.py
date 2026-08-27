"""
UC-0B app.py — Summary That Changes Meaning
Built using the RICE (agents.md) -> skills.md -> CRAFT workflow.
"""
import argparse
import re
import sys

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Clauses whose obligation carries more than one condition/approver/threshold —
# per agents.md these must be quoted verbatim rather than paraphrased.
MULTI_CONDITION_CLAUSES = {"2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}

SECTION_RE = re.compile(r"^(\d+)\.\s+(.+)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.+)$")
SEPARATOR_RE = re.compile(r"^═+$")


def retrieve_policy(path: str) -> dict:
    """
    Load a .txt policy file and parse it into structured sections and clauses.
    Returns: {source_path, header, section_order, sections}
    """
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Policy file not found: {path}. Expected a .txt policy document at this path."
        ) from None

    header = []
    sections = {}
    section_order = []
    current_section = None
    current_clause_id = None

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or SEPARATOR_RE.match(stripped):
            continue

        clause_match = CLAUSE_RE.match(stripped)
        if clause_match:
            clause_id, text = clause_match.groups()
            if current_section is None:
                current_section = "0"
                if "0" not in sections:
                    sections["0"] = {"title": "UNSECTIONED", "clauses": {}}
                    section_order.append("0")
            sections[current_section]["clauses"][clause_id] = text.strip()
            current_clause_id = clause_id
            continue

        section_match = SECTION_RE.match(stripped)
        if section_match:
            sec_num, title = section_match.groups()
            current_section = sec_num
            if sec_num not in sections:
                sections[sec_num] = {"title": title.strip(), "clauses": {}}
                section_order.append(sec_num)
            current_clause_id = None
            continue

        # Continuation line: belongs to whichever clause is currently open.
        if current_clause_id is not None:
            sections[current_section]["clauses"][current_clause_id] += " " + stripped
        elif current_section is None:
            header.append(stripped)

    return {
        "source_path": path,
        "header": header,
        "section_order": section_order,
        "sections": sections,
    }


def summarize_policy(policy: dict) -> str:
    """
    Produce a compliant summary from retrieve_policy's structured output.
    Every clause is reproduced in full; multi-condition clauses are flagged.
    """
    sections = policy["sections"]
    section_order = policy["section_order"]

    lines = []
    header_text = " | ".join(policy["header"]) if policy["header"] else policy["source_path"]
    lines.append(f"SUMMARY: {header_text}")
    lines.append(
        "Every clause below is reproduced in full from the source document; "
        "clauses with more than one condition, approver, or threshold are marked "
        "[MULTI-CONDITION - VERBATIM] and quoted exactly so nothing is dropped."
    )

    for sec_num in section_order:
        section = sections[sec_num]
        lines.append("")
        lines.append(f"{sec_num}. {section['title']}")
        for clause_id in sorted(section["clauses"], key=lambda c: [int(p) for p in c.split(".")]):
            text = section["clauses"][clause_id]
            flag = " [MULTI-CONDITION - VERBATIM]" if clause_id in MULTI_CONDITION_CLAUSES else ""
            lines.append(f"  {clause_id}{flag} {text}")

    lines.append("")
    lines.append("Required Clause Coverage Check:")
    all_clause_ids = {cid for sec in sections.values() for cid in sec["clauses"]}
    missing = [cid for cid in REQUIRED_CLAUSES if cid not in all_clause_ids]
    if missing:
        for cid in missing:
            lines.append(
                f"  MISSING: clause {cid} was not found in the source document "
                "- flagged for manual review, not silently dropped."
            )
    else:
        lines.append(
            f"  All {len(REQUIRED_CLAUSES)} required clauses "
            f"({', '.join(REQUIRED_CLAUSES)}) are present above."
        )

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write the summary text file")
    args = parser.parse_args()

    try:
        policy = retrieve_policy(args.input)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    summary = summarize_policy(policy)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
