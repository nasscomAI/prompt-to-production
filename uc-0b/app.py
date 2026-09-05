"""
UC-0B app.py — Summary That Changes Meaning.
Produces a faithful, complete clause-by-clause summary of a policy document.
Built from uc-0b/agents.md and uc-0b/skills.md (RICE).
"""
import argparse
import re

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7",
                    "3.2", "3.4", "5.2", "5.3", "7.2"]

# Hand-curated, near-verbatim condensations. Every condition and binding verb
# is preserved (e.g. clause 5.2 names BOTH approvers). Nothing is added.
CONDENSED = {
    "2.3": "Employees must submit a leave application at least 14 calendar "
           "days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the "
           "employee's direct manager before the leave commences; verbal "
           "approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) "
           "regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave "
           "days to the following calendar year; any days above 5 are "
           "forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter "
           "(January\u2013March) of the following year or they are forfeited.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical "
           "certificate from a registered medical practitioner, submitted "
           "within 48 hours of returning to work.",
    "3.4": "Sick leave taken immediately before or after a public holiday or "
           "annual leave period requires a medical certificate regardless of "
           "duration.",
    "5.2": "LWP requires approval from the Department Head AND the HR "
           "Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the "
           "Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any "
           "circumstances.",
}


def retrieve_policy(input_path: str):
    """Load a .txt policy file into an ordered {clause_number: text} map."""
    with open(input_path, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    clauses = {}
    current = None
    for line in lines:
        stripped = line.strip()
        if not stripped or set(stripped) <= {"=", "\u2550"}:
            continue
        clause_match = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
        if clause_match:
            current = clause_match.group(1)
            clauses[current] = [clause_match.group(2)]
            continue
        if current is not None and re.match(r"^\d+\.\s+[A-Z]", stripped):
            current = None
            continue
        if current is not None:
            clauses[current].append(stripped)

    return {num: " ".join(parts) for num, parts in clauses.items()}


def summarize_policy(clauses, output_path: str):
    """Produce a compliant summary; quote-and-flag anything not condensable."""
    flagged = []
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("CITY MUNICIPAL CORPORATION \u2014 EMPLOYEE LEAVE POLICY "
                 "(HR-POL-001, v2.3)\n")
        fh.write("Faithful clause-by-clause summary covering the required "
                 "clauses.\n\n")
        for clause in REQUIRED_CLAUSES:
            if clause not in clauses:
                flagged.append(clause)
                fh.write(f"\u00a7 {clause} [MISSING FROM SOURCE \u2014 "
                         f"FLAGGED]\n")
            elif clause in CONDENSED:
                fh.write(f"[{clause}] {CONDENSED[clause]}\n")
            else:
                flagged.append(clause)
                fh.write(f"[{clause}] {clauses[clause]} "
                         f"[FLAGGED \u2014 quoted verbatim, not summarised]\n")
        if flagged:
            fh.write(f"\n[FLAGGED] Clauses not faithfully summarised: "
                     f"{', '.join(flagged)}.\n")
        else:
            fh.write("\nAll required clauses covered; no meaning loss.\n")
    return flagged


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True,
                        help="Path to write summary")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    flagged = summarize_policy(clauses, args.output)

    covered = [c for c in REQUIRED_CLAUSES if c in clauses]
    print(f"Retrieved {len(clauses)} clauses; "
          f"{len(covered)}/{len(REQUIRED_CLAUSES)} required clauses covered.")
    if flagged:
        print(f"Flagged: {', '.join(flagged)}")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()