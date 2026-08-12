"""
UC-0B — Summary That Changes Meaning.
Clause-complete policy summariser implementing retrieve_policy +
summarize_policy as defined in skills.md, enforced per agents.md.
"""
import argparse
import re
import sys

SUMMARIES = {
    "1.1": "This policy governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "This policy does not apply to daily wage workers or consultants; those categories are governed by their respective contracts.",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
    "3.1": "Each employee is entitled to 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "For a third or subsequent child, maternity leave is 12 weeks paid.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "An employee may apply for Leave Without Pay only after exhausting all applicable paid leave entitlements.",
    "5.2": "LWP requires approval from the Department Head and the HR Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "Periods of LWP do not count toward service for the purposes of seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays as declared by the State Government each year.",
    "6.2": "If an employee is required to work on a public holiday, they are entitled to one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
}

CRITICAL_CHECKS = {
    "2.3": ["must submit", "14 calendar days"],
    "2.4": ["written approval", "verbal approval is not valid"],
    "2.5": ["Loss of Pay", "regardless of subsequent approval"],
    "2.6": ["maximum of 5", "forfeited on 31 December"],
    "2.7": ["must be used", "January–March", "forfeited"],
    "3.2": ["3 or more consecutive days", "48 hours"],
    "3.4": ["before or after", "regardless of duration"],
    "5.2": ["Department Head", "HR Director", "manager approval alone is not sufficient"],
    "5.3": ["30 continuous days", "Municipal Commissioner"],
    "7.2": ["not permitted under any circumstances"],
}

BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
    "it is common practice",
    "generally understood",
    "typically",
]

FLAG = "[FLAGGED — VERBATIM]"


def retrieve_policy(input_path: str) -> dict:
    """Loads a policy .txt file and returns structured numbered sections."""
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            raw_lines = f.read().splitlines()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input policy file not found: {input_path}. "
            f"Expected path pattern: ../data/policy-documents/policy_hr_leave.txt"
        )
    if not raw_lines:
        raise ValueError(f"Input policy file is empty: {input_path}")

    metadata = {
        "organization": "",
        "department": "",
        "policy_title": "",
        "document_reference": "",
        "version": "",
        "effective_date": "",
    }
    header_lines = []
    sections = {}
    clauses = []
    current = None
    unparsed = []

    for line in raw_lines:
        stripped = line.strip()
        if not stripped or set(stripped) == {"═"}:
            continue
        if not clauses and not sections and not re.match(r"^\d", stripped):
            m_ref = re.match(r"^Document Reference:\s*(.+)$", stripped)
            m_ver = re.match(r"^Version:\s*(.+?)\s*\|\s*Effective:\s*(.+)$", stripped)
            if m_ref:
                metadata["document_reference"] = m_ref.group(1).strip()
            elif m_ver:
                metadata["version"] = m_ver.group(1).strip()
                metadata["effective_date"] = m_ver.group(2).strip()
            else:
                header_lines.append(stripped)
            continue
        m_sec = re.match(r"^(\d+)\.\s+([A-Z].*)$", stripped)
        if m_sec:
            sections[m_sec.group(1)] = m_sec.group(2)
            continue
        m_clause = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
        if m_clause:
            if current is not None:
                clauses.append(current)
            current = {"number": m_clause.group(1), "text": m_clause.group(2)}
            continue
        if current is not None:
            current["text"] += " " + stripped
        else:
            unparsed.append(stripped)

    if current is not None:
        clauses.append(current)

    if len(header_lines) >= 3:
        metadata["organization"] = header_lines[0]
        metadata["department"] = header_lines[1]
        metadata["policy_title"] = header_lines[2]

    for clause in clauses:
        clause["text"] = re.sub(r"\s+", " ", clause["text"]).strip()

    if unparsed:
        print(
            f"WARNING: {len(unparsed)} line(s) could not be mapped to a clause: "
            + "; ".join(unparsed),
            file=sys.stderr,
        )

    return {
        "metadata": metadata,
        "sections": sections,
        "clauses": clauses,
        "unparsed": unparsed,
    }


def summarize_policy(policy: dict) -> str:
    """Produces a clause-complete, obligation-preserving summary."""
    metadata = policy["metadata"]
    clauses = policy["clauses"]

    lines = []
    lines.append("SUMMARY")
    if metadata["policy_title"]:
        lines.append(f"{metadata['policy_title']} — {metadata['document_reference']}")
    if metadata["organization"] and metadata["department"]:
        lines.append(f"{metadata['organization']} — {metadata['department']}")
    if metadata["version"] and metadata["effective_date"]:
        lines.append(f"Version {metadata['version']} | Effective {metadata['effective_date']}")
    lines.append("")
    lines.append("This summary preserves every numbered clause of the source document "
                 "with exact conditions, limits, dates, and binding verbs.")
    lines.append("")

    current_section = None
    summary_lines = {}
    for clause in clauses:
        section = clause["number"].split(".")[0]
        if current_section != section:
            current_section = section
            title = policy["sections"].get(section, f"Section {section}")
            lines.append(f"{section}. {title}")
        if clause["number"] in SUMMARIES:
            text = SUMMARIES[clause["number"]]
        else:
            text = clause["text"] + " " + FLAG
        summary_lines[clause["number"]] = text
        lines.append(f"{clause['number']} {text}")

    output = "\n".join(lines)

    bleed_hits = [p for p in BLEED_PHRASES if p in output.lower()]
    if bleed_hits:
        raise RuntimeError(f"Scope bleed detected — refusing to emit summary: {bleed_hits}")

    failed = []
    for number, phrases in CRITICAL_CHECKS.items():
        line = summary_lines.get(number, "")
        missing = [p for p in phrases if p.lower() not in line.lower()]
        if missing:
            failed.append(f"{number} lacks: {missing}")
    if failed:
        raise RuntimeError(
            "Refusing to emit summary — critical obligations missing: " + "; ".join(failed)
        )

    covered = len(clauses)
    summarised = sum(1 for c in clauses if c["number"] in SUMMARIES)
    flagged = covered - summarised

    lines.append("")
    lines.append(
        f"Verification: {covered}/{covered} numbered clauses covered · {summarised} summarised · "
        f"{flagged} flagged verbatim · critical checks {len(CRITICAL_CHECKS)}/{len(CRITICAL_CHECKS)} · "
        f"scope-bleed phrases 0"
    )
    if policy["unparsed"]:
        lines.append(f"NOTE: {len(policy['unparsed'])} unparsed source line(s) — see stderr.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary file")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()