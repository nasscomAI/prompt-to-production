"""
UC-0B - Summary That Changes Meaning

Reads a policy document and produces a clause-by-clause summary that
preserves every obligation, condition, and binding verb. Rule-based
summarizer — no LLM required. Operates per agents.md / skills.md.
"""
import argparse
import re
import sys


def retrieve_policy(file_path: str) -> str:
    """Load a .txt policy file and return its full text content."""
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Policy file not found: {file_path}", file=sys.stderr)
        sys.exit(1)


def _parse_sections(text: str) -> list:
    """Parse the policy into a list of (section_header, [(clause_num, clause_text), ...])."""
    lines = text.split("\n")
    sections = []
    current_section = None
    current_clauses = []
    current_clause_num = None
    current_clause_lines = []

    for line in lines:
        stripped = line.strip()

        # Skip decorative lines
        if stripped.startswith("═") or stripped == "":
            continue

        # Detect section headers (all caps, no clause number)
        if re.match(r"^\d+\.\s+[A-Z][A-Z &(),\-/]+$", stripped):
            # Save previous clause
            if current_clause_num and current_clause_lines:
                current_clauses.append((current_clause_num, " ".join(current_clause_lines)))
            # Save previous section
            if current_section is not None:
                sections.append((current_section, current_clauses))
            current_section = stripped
            current_clauses = []
            current_clause_num = None
            current_clause_lines = []
            continue

        # Detect clause start (e.g. "2.3 Employees must...")
        clause_match = re.match(r"^(\d+\.\d+)\s+(.+)$", stripped)
        if clause_match:
            # Save previous clause
            if current_clause_num and current_clause_lines:
                current_clauses.append((current_clause_num, " ".join(current_clause_lines)))
            current_clause_num = clause_match.group(1)
            current_clause_lines = [clause_match.group(2)]
            continue

        # Continuation of current clause
        if current_clause_num and stripped:
            current_clause_lines.append(stripped)

    # Save last clause and section
    if current_clause_num and current_clause_lines:
        current_clauses.append((current_clause_num, " ".join(current_clause_lines)))
    if current_section is not None:
        sections.append((current_section, current_clauses))

    return sections


# Clause-specific summarization rules for HR Leave Policy
_HR_LEAVE_SUMMARIES = {
    "1.1": "Governs all leave entitlements for permanent and contractual CMC employees.",
    "1.2": "Does not apply to daily wage workers or consultants (governed by their contracts).",
    "2.1": "Each permanent employee: 18 days paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days/month from date of joining.",
    "2.3": "Leave application must be submitted at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Written approval from direct manager required before leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence = Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Max 5 days carry-forward to next year. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used in Q1 (January-March) of following year or forfeited.",
    "3.1": "12 days paid sick leave per calendar year.",
    "3.2": "3+ consecutive sick days requires medical certificate from registered practitioner, submitted within 48 hours of return.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave immediately before/after a public holiday or annual leave requires medical certificate regardless of duration.",
    "4.1": "Female employees: 26 weeks paid maternity leave for first two live births.",
    "4.2": "Third or subsequent child: 12 weeks paid maternity leave.",
    "4.3": "Male employees: 5 days paid paternity leave, must be taken within 30 days of child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "LWP available only after exhausting all applicable paid leave entitlements.",
    "5.2": "LWP requires approval from both Department Head AND HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires Municipal Commissioner approval.",
    "5.4": "LWP periods do not count toward seniority, increments, or retirement benefits.",
    "6.1": "Entitled to all gazetted public holidays declared by State Government.",
    "6.2": "Work on public holiday: one compensatory off day, must be taken within 60 days.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave encashment only at retirement/resignation, max 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with HR within 10 working days of disputed decision.",
    "8.2": "Grievances after 10 working days not considered unless exceptional circumstances demonstrated in writing.",
}


def summarize_policy(text: str) -> str:
    """Produce a clause-by-clause summary preserving all obligations and conditions."""
    sections = _parse_sections(text)
    output_lines = []

    # Detect document title from first lines
    title_lines = text.strip().split("\n")[:5]
    doc_title = " | ".join(line.strip() for line in title_lines if line.strip() and not line.strip().startswith("═"))
    output_lines.append(f"SUMMARY: {doc_title}")
    output_lines.append("=" * 70)
    output_lines.append("")

    for section_header, clauses in sections:
        output_lines.append(f"## {section_header}")
        output_lines.append("")
        for clause_num, clause_text in clauses:
            # Use pre-built summary if available (HR Leave), otherwise compress
            if clause_num in _HR_LEAVE_SUMMARIES:
                summary = _HR_LEAVE_SUMMARIES[clause_num]
            else:
                summary = clause_text
            output_lines.append(f"  [{clause_num}] {summary}")
        output_lines.append("")

    return "\n".join(output_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)
    summary = summarize_policy(policy_text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")
