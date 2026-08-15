"""
UC-0B app.py — Faithful policy summariser.
Implements the `retrieve_policy` and `summarize_policy` skills from skills.md
under the role/intent/enforcement rules in agents.md.

Run:
  python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""
import argparse
import re
import sys

EXPECTED_MARKERS = ("CITY MUNICIPAL CORPORATION", "EMPLOYEE LEAVE POLICY", "HR-POL-001")
SCOPE_BLEED_PHRASES = (
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
)
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
HEADING_RE = re.compile(r"^(\d+)\.\s+([A-Z].*)$")
SEPARATOR_RE = re.compile(r"^[\u2500-\u257F\-\s]+$")

CLAUSE_CROSSCHECK = {
    "2.3": ("14 calendar days", "advance"),
    "2.4": ("written approval", "verbal approval is not valid"),
    "2.5": ("loss of pay",),
    "2.6": ("maximum of 5", "31 december"),
    "2.7": ("january", "march"),
    "3.2": ("medical certificate", "48 hours"),
    "3.4": ("medical certificate", "regardless of duration"),
    "5.2": ("department head", "hr director"),
    "5.3": ("municipal commissioner",),
    "7.2": ("not permitted under any circumstances",),
}


def retrieve_policy(path):
    """Load the .txt policy file and return content as structured numbered sections."""
    try:
        with open(path, "r", encoding="utf-8-sig") as fh:
            text = fh.read()
    except OSError as exc:
        sys.exit(f"ERROR: cannot read policy file '{path}': {exc}")

    if not all(marker in text for marker in EXPECTED_MARKERS):
        sys.exit(
            f"ERROR: '{path}' is not the expected leave-policy document "
            "(HR-POL-001); refusing to proceed."
        )

    sections = []
    heading = None
    current = None
    for raw in text.splitlines():
        line = raw.rstrip()
        clause = CLAUSE_RE.match(line)
        heading_match = HEADING_RE.match(line)
        if clause:
            current = {"number": clause.group(1), "heading": heading, "text": [clause.group(2)]}
            sections.append(current)
        elif heading_match:
            heading = line
        elif current is not None:
            stripped = line.strip()
            if stripped and not SEPARATOR_RE.match(stripped):
                current["text"].append(stripped)

    if not sections:
        sys.exit("ERROR: no numbered clauses found; a clause inventory cannot be established.")
    for sec in sections:
        sec["text"] = " ".join(sec["text"]).strip()
    return sections


def _sentence(text):
    text = text.strip()
    return text if text.endswith((".", "!", "?")) else text + "."


def summarize_policy(sections, source_path):
    """Take structured sections and produce a clause-complete summary with clause references."""
    lines = [
        "CITY MUNICIPAL CORPORATION",
        "EMPLOYEE LEAVE POLICY",
        f"Source: {source_path}",
        f"Clauses: {len(sections)}",
        "",
    ]
    current_heading = None
    for sec in sections:
        if sec["heading"] != current_heading:
            current_heading = sec["heading"]
            lines.append(current_heading)
        lines.append(f"- {sec['number']} — {_sentence(sec['text'])}")
    return "\n".join(lines) + "\n"


def _clause_line(summary, number):
    for line in summary.splitlines():
        if line.startswith(f"- {number} —"):
            return line.lower()
    return ""


def verify_summary(sections, summary):
    """Enforce agents.md rules: no omission, no invention, no scope bleed, no dropped conditions."""
    errors = []
    source_numbers = {s["number"] for s in sections}
    summary_numbers = set(re.findall(r"(?m)^- (\d+\.\d+) —", summary))
    missing = sorted(source_numbers - summary_numbers)
    invented = sorted(summary_numbers - source_numbers)
    if missing:
        errors.append(f"clause omission: {', '.join(missing)}")
    if invented:
        errors.append(f"invented clause numbers: {', '.join(invented)}")

    lowered = summary.lower()
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase in lowered:
            errors.append(f"scope bleed: phrase '{phrase}' is not in the source document")

    for number, keywords in CLAUSE_CROSSCHECK.items():
        block = _clause_line(summary, number)
        if not block:
            errors.append(f"clause {number} missing from summary")
            continue
        for kw in keywords:
            if kw not in block:
                errors.append(f"condition dropped in clause {number}: missing '{kw}'")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Produce a faithful clause-complete summary of the leave policy.")
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections, args.input)
    errors = verify_summary(sections, summary)
    if errors:
        sys.exit("VERIFICATION FAILED:\n  - " + "\n  - ".join(errors))

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary)
    print(f"Wrote {len(sections)} clauses to {args.output}")


if __name__ == "__main__":
    main()
