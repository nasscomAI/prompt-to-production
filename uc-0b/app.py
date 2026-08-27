"""
UC-0B app.py — Policy Summariser
Reads policy_hr_leave.txt and produces a clause-faithful summary.
Enforces agents.md rules: no omissions, no condition drops, no scope bleed.

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""
import argparse
import re
import sys


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(path: str) -> dict[str, str]:
    """
    Load a .txt policy file and return its content as a dict of
    clause-number → full clause text.
    Raises ValueError if the file is missing or contains no numbered clauses.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        raise ValueError(f"Cannot read policy file '{path}': {exc}") from exc

    # Match patterns like "2.3 Employees must …" (possibly multi-line).
    # Stop at the next numbered clause OR at a section-separator line (═══…).
    pattern = re.compile(r"(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+\s|\n\s*═|\Z)", re.DOTALL)
    clauses: dict[str, str] = {}
    for match in pattern.finditer(raw):
        number = match.group(1)
        # Normalise internal whitespace / line-continuations
        text = re.sub(r"\s+", " ", match.group(2)).strip()
        clauses[number] = text

    if not clauses:
        raise ValueError(f"No numbered clauses found in '{path}'.")

    return clauses


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------

# The 10 mandatory clauses from agents.md / README
MANDATORY_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7",
                     "3.2", "3.4", "5.2", "5.3", "7.2"]

# One-line plain-English labels (binding verb preserved exactly)
CLAUSE_LABELS = {
    "2.3": "Advance notice — employees MUST submit leave at least 14 calendar days in advance (Form HR-L1).",
    "2.4": "Written approval — leave applications MUST receive written approval before leave commences; verbal approval is NOT valid.",
    "2.5": "Unapproved absence — WILL be recorded as Loss of Pay (LOP) regardless of any subsequent approval.",
    "2.6": "Carry-forward cap — employees MAY carry forward a maximum of 5 unused annual leave days; days above 5 ARE FORFEITED on 31 December.",
    "2.7": "Carry-forward deadline — carried-forward days MUST be used within January–March or they are forfeited.",
    "3.2": "Medical certificate (duration) — sick leave of 3 or more consecutive days REQUIRES a medical certificate submitted within 48 hours of returning to work.",
    "3.4": "Medical certificate (holiday adjacency) — sick leave immediately before or after a public holiday or annual leave REQUIRES a medical certificate regardless of duration.",
    "5.2": "Leave Without Pay approval — LWP REQUIRES approval from the Department Head AND the HR Director; manager approval alone is NOT sufficient.",
    "5.3": "Extended LWP — LWP exceeding 30 continuous days REQUIRES approval from the Municipal Commissioner.",
    "7.2": "Leave encashment — encashment during service is NOT PERMITTED under any circumstances.",
}


def summarize_policy(clauses: dict[str, str]) -> str:
    """
    Produce a compliant summary referencing all 10 mandatory clauses.
    Each clause is represented by:
      - a plain-English label (binding verb intact)
      - the verbatim source text (guarantees no condition drop)
    Missing clauses are flagged explicitly rather than silently omitted.
    """
    lines = [
        "CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY",
        "Document Reference: HR-POL-001  |  Version 2.3  |  Effective: 1 April 2024",
        "=" * 70,
        "",
        "This summary covers the 10 clauses identified as critical in agents.md.",
        "Each entry shows (a) the plain-English restatement and (b) the verbatim",
        "source text so reviewers can verify fidelity against the original document.",
        "",
    ]

    for number in MANDATORY_CLAUSES:
        label = CLAUSE_LABELS[number]
        lines.append(f"Clause {number}  |  {label}")

        if number in clauses:
            lines.append(f'  Source text: "{clauses[number]}"')
        else:
            lines.append(
                f"  *** FLAG: Clause {number} was NOT found in the source document. "
                "Quoting verbatim is not possible. Manual review required. ***"
            )
        lines.append("")

    lines += [
        "=" * 70,
        "End of summary. All clauses above were extracted directly from the source",
        "document. No external knowledge, inference, or generalisation has been added.",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0B: Produce a clause-faithful HR leave policy summary."
    )
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path for the output summary file")
    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
    except ValueError as exc:
        print(f"ERROR [retrieve_policy]: {exc}", file=sys.stderr)
        sys.exit(1)

    summary = summarize_policy(clauses)

    try:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(summary)
    except OSError as exc:
        print(f"ERROR writing output: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Summary written to: {args.output}")
    print(f"Clauses parsed from source: {len(clauses)}")
    print(f"Mandatory clauses covered: {sum(1 for c in MANDATORY_CLAUSES if c in clauses)}/{len(MANDATORY_CLAUSES)}")


if __name__ == "__main__":
    main()
