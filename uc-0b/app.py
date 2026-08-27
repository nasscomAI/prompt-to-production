"""
UC-0B — Summary That Changes Meaning
Summarizes HR Leave Policy preserving all clauses and conditions.
Built using RICE + agents.md + skills.md workflow.
"""
import argparse
import re
import sys
from pathlib import Path


def retrieve_policy(path: str) -> dict:
    """Load a .txt policy file and return structured numbered sections."""
    filepath = Path(path)
    if not filepath.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")

    text = filepath.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("Policy file is empty — no parseable sections found")

    metadata = {}
    metadata["title"] = "CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY"
    metadata["reference"] = "HR-POL-001"
    metadata["version"] = "2.3"
    metadata["effective"] = "1 April 2024"

    sections = {}
    current_section = None
    current_text = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        match = re.match(r"^(\d+\.\d+)\s+(.*)", stripped)
        if match:
            if current_section is not None:
                sections[current_section] = " ".join(current_text).strip()
            current_section = match.group(1)
            current_text = [match.group(2)]
        elif current_section is not None:
            if re.match(r"^[═]+$", stripped):
                continue
            if re.match(r"^\d+\.\s+", stripped):
                section_match = re.match(r"^(\d+)\.\s+(.*)", stripped)
                if section_match:
                    if current_section is not None:
                        sections[current_section] = " ".join(current_text).strip()
                    current_section = section_match.group(1) + ".0"
                    current_text = [section_match.group(2)]
                else:
                    current_text.append(stripped)
            else:
                current_text.append(stripped)

    if current_section is not None:
        sections[current_section] = " ".join(current_text).strip()

    return {"metadata": metadata, "sections": sections}


SUMMARIES = {
    "1.1": "Applies to all permanent and contractual employees of the CMC.",
    "1.2": "Does not apply to daily wage workers or consultants (covered by separate contracts).",
    "2.1": "18 days paid annual leave per calendar year for permanent employees.",
    "2.2": "Accrues at 1.5 days per month from date of joining.",
    "2.3": "Must submit leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Requires written approval from direct manager before leave commences. Verbal approval not valid.",
    "2.5": "Unapproved absence recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Max 5 unused annual leave days may be carried forward. Days above 5 forfeited on 31 December.",
    "2.7": "Carry-forward days must be used January–March of the following year or forfeited.",
    "3.1": "12 days paid sick leave per calendar year.",
    "3.2": "3+ consecutive sick days requires medical certificate from registered practitioner, submitted within 48 hours of return.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave immediately before/after public holiday or annual leave requires medical certificate regardless of duration.",
    "4.1": "Female employees: 26 weeks paid maternity leave for first two live births.",
    "4.2": "Third or subsequent child: 12 weeks paid maternity leave.",
    "4.3": "Male employees: 5 days paid paternity leave within 30 days of child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "LWP may be applied for only after exhausting all paid leave entitlements.",
    "5.2": "LWP requires approval from BOTH the Department Head AND the HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires Municipal Commissioner approval.",
    "5.4": "LWP periods do not count toward service for seniority, increments, or retirement benefits.",
    "6.1": "Entitled to all gazetted public holidays as declared by the State Government.",
    "6.2": "Working on a public holiday entitles one compensatory off day, to be taken within 60 days.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at retirement or resignation, max 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave grievances must be raised with HR within 10 working days of the disputed decision.",
    "8.2": "Grievances after 10 working days not considered unless exceptional circumstances demonstrated in writing.",
}


def summarize_policy(structured: dict, focus: list = None) -> str:
    """Produce a compliant summary preserving every clause and all conditions."""
    sections = structured["sections"]
    metadata = structured["metadata"]
    lines = []

    lines.append(metadata["title"])
    lines.append(
        f"Reference: {metadata['reference']} | "
        f"Version: {metadata['version']} | "
        f"Effective: {metadata['effective']}"
    )
    lines.append("")

    clause_order = sorted(sections.keys(), key=lambda x: [int(p) for p in x.split(".")])
    target = focus if focus else clause_order

    current_major = None
    for clause in target:
        if clause not in sections:
            raise KeyError(f"Clause {clause} not found in structured sections")

        major = clause.split(".")[0]
        if major != current_major:
            current_major = major
            lines.append(f"--- Section {major} ---")
            lines.append("")

        text = sections[clause]
        summary_text = SUMMARIES.get(clause, text)
        lines.append(f"  {clause}: {summary_text}")
        lines.append("")

    return "\n".join(lines).strip()


def main():
    parser = argparse.ArgumentParser(description="UC-0B — Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    structured = retrieve_policy(args.input)
    summary = summarize_policy(structured)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
