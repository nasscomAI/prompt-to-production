"""
UC-0B app.py — Policy Summarizer
Built from agents.md (RICE) and skills.md via the CRAFT workflow.
"""
import argparse
import re

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_PATTERN = re.compile(r"^\d+\.\s+[A-Z]")

# Clauses whose obligation joins multiple conditions with AND/OR — condensing
# these risks dropping a condition, so they are quoted verbatim instead.
MULTI_CONDITION_MARKERS = re.compile(
    r"\b(and the|and\b.*\bapproval|within \d+ (hours|days).*\bregardless|"
    r"regardless of|maximum of \d+.*forfeited|must be used.*or they are forfeited)\b",
    re.IGNORECASE,
)


def retrieve_policy(file_path: str) -> list[dict]:
    """
    Load a .txt policy file and return its content as structured numbered
    sections keyed by clause number, in document order.
    """
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    clauses = []
    current = None

    for line in lines:
        stripped = line.strip()
        match = CLAUSE_PATTERN.match(stripped)
        if match:
            if current:
                clauses.append(current)
            current = {"clause_number": match.group(1), "text": match.group(2)}
        elif (
            current
            and stripped
            and not stripped.startswith(("=", "─", "═"))
            and not SECTION_HEADER_PATTERN.match(stripped)
        ):
            # continuation line of the current clause (wrapped text)
            current["text"] += " " + stripped

    if current:
        clauses.append(current)

    if not clauses:
        raise ValueError(f"No numbered clauses found in {file_path}")

    return clauses


def summarize_policy(clauses: list[dict]) -> str:
    """
    Produce a compliant summary: one line per clause, referenced by clause
    number. Multi-condition obligations are quoted verbatim and flagged
    [VERBATIM] rather than condensed, so no condition is silently dropped.
    """
    lines = []
    for clause in clauses:
        text = re.sub(r"\s+", " ", clause["text"]).strip()
        if MULTI_CONDITION_MARKERS.search(text):
            lines.append(f"{clause['clause_number']} [VERBATIM]: {text}")
        else:
            lines.append(f"{clause['clause_number']}: {text}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary + "\n")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
