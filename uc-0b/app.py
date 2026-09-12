"""
UC-0B — Faithful HR leave-policy summariser.

builds a clause inventory from a policy .txt file (retrieve_policy) and
produces a clause-by-clause summary that preserves all conditions and
binding verbs (summarize_policy). Follows the agents.md enforcement rules
and the skills.md error-handling contracts.
"""
import argparse
import io
import os
import re
import sys

REQUIRED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
]

SECTION_HEADER_RE = re.compile(r"^\d+\.\s+[A-Z]")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SEPARATOR_RE = re.compile(r"^═+$")

SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
]


def detect_binding_verb(text):
    lowered = text.lower()
    if "not permitted" in lowered:
        return "not permitted"
    if " will " in lowered or lowered.startswith("will"):
        return "will"
    if "must" in lowered:
        return "must"
    if "requires" in lowered:
        return "requires"
    if "forfeit" in lowered:
        return "may / are forfeited"
    if "may" in lowered:
        return "may"
    return None


def retrieve_policy(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(
            "Retrieve refused: input file does not exist: {}".format(path))
    try:
        with io.open(path, "r", encoding="utf-8-sig") as handle:
            raw_lines = handle.readlines()
    except OSError as exc:
        raise OSError(
            "Retrieve refused: cannot read {}: {}".format(path, exc))

    clauses = {}
    current = None
    for raw in raw_lines:
        line = raw.strip()
        if not line or SEPARATOR_RE.match(line):
            continue
        match = CLAUSE_RE.match(line)
        if match:
            current = {"number": match.group(1), "text": [match.group(2)]}
            clauses[current["number"]] = current
        elif SECTION_HEADER_RE.match(line):
            current = None
        elif current is not None:
            current["text"].append(line)

    if not clauses:
        raise ValueError(
            "Retrieve refused: no numbered clauses found in {}; "
            "clause inventory could not be built.".format(path))

    def sort_key(pair):
        number = pair[0]
        major, minor = number.split(".")
        return (int(major), int(minor))

    sections = []
    for number, item in sorted(clauses.items(), key=sort_key):
        body = " ".join(item["text"]).strip()
        verb = detect_binding_verb(body)
        sections.append({
            "number": number,
            "obligation": body,
            "binding_verb": verb,
            "flagged": verb is None,
        })
    return sections


def summarize_policy(clauses, output_path):
    by_number = {clause["number"]: clause for clause in clauses}

    missing = [number for number in REQUIRED_CLAUSES
               if number not in by_number]
    if missing:
        raise ValueError(
            "Summarize refused: required clause(s) missing from the "
            "inventory: {}. No summary written.".format(", ".join(missing)))

    clause_52 = by_number.get("5.2")
    if clause_52 is not None:
        body_52 = clause_52["obligation"].lower()
        if "department head" not in body_52 or "hr director" not in body_52:
            raise ValueError(
                "Summarize refused: clause 5.2 lost a condition — approval "
                "from BOTH the Department Head AND the HR Director must be "
                "preserved. No summary written.")

    lines = [
        "SUMMARY — EMPLOYEE LEAVE POLICY (HR-POL-001)",
        "Clause-by-clause reference summary. Each entry preserves its clause's",
        "obligation and binding verb exactly as written in the source document.",
        "",
    ]

    for number in REQUIRED_CLAUSES:
        clause = by_number[number]
        if clause["flagged"]:
            lines.append(
                "[{}] [FLAGGED: quoted verbatim — could not be summarised "
                "without meaning loss] {}".format(
                    number, clause["obligation"]))
        else:
            lines.append(
                "[{}] ({}) {}".format(
                    number, clause["binding_verb"], clause["obligation"]))
    lines.append("")

    composed = "\n".join(lines)

    for phrase in SCOPE_BLEED_PHRASES:
        if phrase in composed.lower():
            raise ValueError(
                "Summarize refused: draft contains scope-bleed phrase "
                "'{}' which is not present in the source. No summary "
                "written.".format(phrase))

    for number in REQUIRED_CLAUSES:
        if "[{}]".format(number) not in composed:
            raise ValueError(
                "Summarize refused: clause {} is missing from the draft. "
                "No summary written.".format(number))

    try:
        with io.open(output_path, "w", encoding="utf-8") as handle:
            handle.write(composed)
    except OSError as exc:
        raise OSError(
            "Summarize refused: cannot write output {}: {}".format(
                output_path, exc))

    return composed


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B faithful HR leave-policy summariser.")
    parser.add_argument(
        "--input", required=True,
        help="Path to the plain-text policy document (.txt).")
    parser.add_argument(
        "--output", required=True,
        help="Path to the summary output file.")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summarize_policy(sections, args.output)
    print("Wrote compliant summary to {} covering {} clauses.".format(
        args.output, len(REQUIRED_CLAUSES)))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        sys.exit(1)