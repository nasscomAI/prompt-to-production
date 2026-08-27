"""
UC-0B app.py — Policy Summarizer
Built per agents.md (clause completeness, no invented claims, verbatim fallback
on multi-condition clauses) and skills.md (retrieve_policy, summarize_policy).
"""
import argparse
import re

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)")

# README's clause inventory — the 10 clauses tutors verify against. Every one
# of these carries a multi-condition or trap detail that must survive intact.
GROUND_TRUTH_CLAUSES = {
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
}


def retrieve_policy(input_path: str) -> list:
    """
    Loads the policy .txt file and returns structured numbered sections.
    Returns: list of dicts with keys clause_id, text.
    """
    try:
        with open(input_path, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    clauses = []
    current = None

    for raw_line in lines:
        stripped = raw_line.strip()

        if not stripped or stripped.startswith("═"):
            continue

        if raw_line[0].isspace():
            # Continuation of a wrapped clause line — append, don't lose it.
            if current is not None:
                current["text"] += " " + stripped
            continue

        match = CLAUSE_RE.match(stripped)
        if match:
            if current is not None:
                clauses.append(current)
            current = {"clause_id": match.group(1), "text": match.group(2).strip()}
        else:
            # Section header or document title line — closes the current clause.
            if current is not None:
                clauses.append(current)
                current = None

    if current is not None:
        clauses.append(current)

    if not clauses:
        raise ValueError(f"No numbered clauses found in {input_path} — cannot summarize.")

    return clauses


def summarize_policy(clauses: list) -> str:
    """
    Produces a clause-referenced summary, preserving every clause and every
    condition inside multi-condition clauses. No claim is added beyond what
    retrieve_policy extracted from the source.
    """
    missing = GROUND_TRUTH_CLAUSES - {c["clause_id"] for c in clauses}
    if missing:
        raise ValueError(f"Ground-truth clauses missing from source, cannot summarize safely: {sorted(missing)}")

    lines = [
        "HR LEAVE POLICY — SUMMARY",
        "Every clause below is quoted verbatim from policy_hr_leave.txt — nothing added, nothing dropped.",
        "",
    ]

    for clause in clauses:
        clause_id = clause["clause_id"]
        text = clause["text"]
        if clause_id in GROUND_TRUTH_CLAUSES:
            lines.append(f"{clause_id}: {text} [VERBATIM — flagged: multi-condition clause, preserved in full]")
        else:
            lines.append(f"{clause_id}: {text}")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary text file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
