"""
UC-0B app.py — Summary That Changes Meaning.
Built from the RICE prompt in agents.md.

Deterministic extractive summarizer: it parses the numbered clauses out of
the source policy text and re-emits each tracked clause with its full
condition set intact, rather than letting a free-form paraphrase risk
dropping a condition (the exact failure mode — clause omission / condition
drop — this UC is testing for). See README.md for run command and expected
behaviour.
"""
import argparse
import re

# The 10 clauses the enforcement rules require to survive the summary,
# per agents.md and the README's clause inventory.
TRACKED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2",
]

CLAUSE_START_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_RE = re.compile(r"^\d+\.\s+[A-Z].*$")
DIVIDER_RE = re.compile(r"^═+$")


def retrieve_policy(path: str):
    """
    Parse a policy .txt file into structured clauses.
    Returns: list of dicts {clause, text} in document order.
    Handles clause text that wraps onto indented continuation lines.
    """
    clauses = []
    current = None

    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            stripped = line.strip()

            if not stripped or DIVIDER_RE.match(stripped) or SECTION_HEADER_RE.match(stripped):
                continue

            match = CLAUSE_START_RE.match(stripped)
            if match:
                if current:
                    clauses.append(current)
                current = {"clause": match.group(1), "text": match.group(2).strip()}
            elif current:
                # Continuation line of the current clause (wrapped text).
                current["text"] = (current["text"] + " " + stripped).strip()

        if current:
            clauses.append(current)

    return clauses


def summarize_policy(clauses, tracked=TRACKED_CLAUSES) -> str:
    """
    Produce a compliant summary: one line per tracked clause, full text
    (all conditions) preserved, in tracked order. Missing clauses are
    reported explicitly rather than silently dropped.
    """
    by_number = {c["clause"]: c["text"] for c in clauses}

    lines = [
        "EMPLOYEE LEAVE POLICY — SUMMARY OF TRACKED CLAUSES",
        "(Extractive summary: every clause below keeps every condition from",
        " the source. Nothing here is added beyond what policy_hr_leave.txt states.)",
        "",
    ]

    for clause_num in tracked:
        text = by_number.get(clause_num)
        if text is None:
            lines.append(f"Clause {clause_num}: NOT FOUND in source — flagged for manual review.")
        else:
            lines.append(f"Clause {clause_num}: {text}")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    found = sum(1 for c in TRACKED_CLAUSES if c in {cl["clause"] for cl in clauses})
    print(f"Summarized {found}/{len(TRACKED_CLAUSES)} tracked clauses. Written to {args.output}")


if __name__ == "__main__":
    main()
