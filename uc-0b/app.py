"""
UC-0B — Summary That Changes Meaning

Extractive policy summarizer: preserves every numbered clause, every binding
verb, and every condition verbatim. Adds nothing, drops no obligations.
Enforcement rules mirror agents.md; skill contracts mirror skills.md.

Usage:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
        --output summary_hr_leave.txt
"""
import argparse
import re
from collections import OrderedDict

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z &()\-]+)\s*$")
DIVIDER_RE = re.compile(r"^[\s═─=_-]+$")

# A sentence is kept only if it carries an obligation, condition, negation,
# entitlement, or boundary. Everything else is descriptive filler.
KEEP_RE = re.compile(
    r"\b(must|shall|will|may|requires?|required|entitled|forfeit\w*|cannot|"
    r"not\s+permitted|not\s+valid|not\s+sufficient|not\s+apply|not\s+count|"
    r"regardless|within|before|after|unless|exceeding|maximum|minimum|"
    r"only|at\s+least|under\s+any\s+circumstances|if\b|or\b|and\b)\b",
    re.IGNORECASE,
)

FLAG = "[QUOTED VERBATIM - summarisation risked meaning loss]"


def _sentences(text):
    normalized = re.sub(r"\s+", " ", text).strip()
    return re.split(r"(?<=[.!?])\s+", normalized) if normalized else []


def _parse_clauses(raw_text):
    """Walk the document once, attaching wrapped lines to their clause."""
    clauses = OrderedDict()
    current = None
    for line in raw_text.splitlines():
        if DIVIDER_RE.match(line):
            continue  # box-drawing section dividers are not clause content
        m = CLAUSE_RE.match(line)
        if m:
            current = m.group(1)
            clauses[current] = m.group(2)
        elif current is not None and line.strip() and \
                not SECTION_RE.match(line):
            clauses[current] += " " + line.strip()
    return clauses


def retrieve_policy(path: str) -> dict:
    """Load a .txt policy file, return {clause_number: clause_text}."""
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    return _parse_clauses(raw)


def summarize_policy(clauses: dict) -> str:
    """Produce a compliant summary: every clause present, conditions intact."""
    if not clauses:
        return "No numbered clauses found in source document."

    lines = [
        "SUMMARY - EMPLOYEE LEAVE POLICY (extractive)",
        "All numbered clauses present; obligations and multi-condition",
        "rules preserved word-for-word from the source document.",
        "",
    ]
    for num in sorted(clauses, key=lambda k: tuple(map(int, k.split(".")))):
        text = clauses[num]
        kept = [s for s in _sentences(text) if KEEP_RE.search(s)]
        if not kept or len(kept) < len(_sentences(text)):
            # Anything filtered (or nothing filterable safely) -> quote whole
            # clause verbatim and flag rather than risk a dropped condition.
            body = re.sub(r"\s+", " ", text)
            lines.append(f"{num} {body}")
            lines.append(f"   {FLAG}")
        else:
            body = " ".join(kept)
            lines.append(f"{num} {body}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True,
                        help="Path to policy .txt file")
    parser.add_argument("--output", required=True,
                        help="Path to write summary .txt")
    args = parser.parse_args()
    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
