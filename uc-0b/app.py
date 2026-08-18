"""
UC-0B app.py — Summary That Changes Meaning
Built from agents.md (enforcement rules) and skills.md (skill contracts).
"""
import argparse
import re

CLAUSE_LINE = re.compile(r"^(\d+\.\d+)\s+(.*)$")

# Multi-condition signals: two named roles joined by "and", multiple distinct
# numeric thresholds, or an "or"-joined second consequence (e.g. forfeiture).
ROLE_AND = re.compile(r"[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\s+and\s+(?:the\s+)?[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*")
OR_CONSEQUENCE = re.compile(r"\bor\b.*\b(forfeited|not (?:valid|sufficient|permitted)|regardless)\b", re.IGNORECASE)
REGARDLESS = re.compile(r"\bregardless\b", re.IGNORECASE)


def retrieve_policy(file_path: str) -> list:
    """
    Load a .txt policy file and parse it into structured numbered clauses.
    Returns: list of dicts with keys: clause_number, text
    """
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    clauses = []
    current = None

    for line in lines:
        match = CLAUSE_LINE.match(line)
        if match:
            if current is not None:
                clauses.append(current)
            current = {"clause_number": match.group(1), "text": match.group(2).strip()}
        elif current is not None and line.strip() and line.startswith((" ", "\t")):
            # Wrapped continuation line — append to the clause in progress.
            current["text"] = f"{current['text']} {line.strip()}"
        elif current is not None and (not line.strip() or not line.startswith((" ", "\t"))):
            # Blank line or a new unindented non-clause line (heading, divider)
            # closes the clause currently being accumulated.
            clauses.append(current)
            current = None

    if current is not None:
        clauses.append(current)

    return clauses


def _is_multi_condition(text: str) -> bool:
    numbers = set(re.findall(r"\d+", text))
    if len(numbers) >= 2:
        return True
    if ROLE_AND.search(text):
        return True
    if OR_CONSEQUENCE.search(text) or REGARDLESS.search(text):
        return True
    return False


def summarize_policy(clauses: list) -> str:
    """
    Produce a compliant summary, one line per clause, in clause-number order.
    Multi-condition clauses that risk meaning loss are output verbatim and
    flagged, per agents.md enforcement rule 4.
    """
    lines = []
    for clause in clauses:
        number = clause["clause_number"]
        text = re.sub(r"\s+", " ", clause["text"]).strip()
        if _is_multi_condition(text):
            lines.append(f"Clause {number}: [VERBATIM] {text}")
        else:
            lines.append(f"Clause {number}: {text}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary text")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. {len(clauses)} clauses summarized. Output written to {args.output}")


if __name__ == "__main__":
    main()
