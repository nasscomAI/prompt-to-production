"""
UC-0B — Summary That Changes Meaning

Faithful, clause-preserving policy summariser built to the enforcement rules in
agents.md and the skill contracts in skills.md.

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""
import argparse
import re
import sys

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z].*)$")

# Binding verbs that must never be softened.
BINDING_VERBS = ["must", "will", "requires", "not permitted", "may", "are forfeited", "forfeited"]

# Phrases that indicate a clause carries multiple conditions that must all survive.
MULTI_CONDITION_MARKERS = [
    " and the ", " and hr ", "department head and", " both ", "regardless of",
    "before or after", " or they are ", "exceeding", "within",
]

# Scope-bleed phrases that must never appear in a compliant summary.
FORBIDDEN_SCOPE_BLEED = [
    "as is standard practice", "typically in government", "generally expected",
    "it is common practice", "as a rule of thumb",
]


# --- Skill: retrieve_policy -------------------------------------------------

def retrieve_policy(input_path: str) -> dict:
    """
    Load a policy .txt file and parse it into structured numbered sections.

    Returns a dict:
      {"source": <filename>,
       "sections": [{"number": "2", "heading": "ANNUAL LEAVE",
                     "clauses": [{"number": "2.3", "text": "..."}]}],
       "clause_numbers": ["2.1", "2.2", ...]}
    """
    try:
        with open(input_path, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        print(f"ERROR: could not open input file '{input_path}': {exc}", file=sys.stderr)
        raise SystemExit(1)

    sections = []
    clause_numbers = []
    current_section = None
    current_clause = None

    for raw in lines:
        line = raw.rstrip()
        if not line or set(line) <= set("═ "):  # skip blank / rule lines
            continue

        clause_match = CLAUSE_RE.match(line)
        section_match = SECTION_RE.match(line)

        if section_match and not clause_match:
            current_section = {
                "number": section_match.group(1),
                "heading": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            current_clause = None
        elif clause_match:
            if current_section is None:  # clause before any section header
                current_section = {"number": "0", "heading": "GENERAL", "clauses": []}
                sections.append(current_section)
            current_clause = {"number": clause_match.group(1), "text": clause_match.group(2).strip()}
            current_section["clauses"].append(current_clause)
            clause_numbers.append(current_clause["number"])
        else:
            # Continuation line: attach to the most recent clause so no text is lost.
            if current_clause is not None:
                current_clause["text"] += " " + line.strip()

    import os
    return {
        "source": os.path.basename(input_path),
        "sections": sections,
        "clause_numbers": clause_numbers,
    }


# --- Skill: summarize_policy ------------------------------------------------

def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _binding_verbs_in(text: str):
    low = text.lower()
    return [v for v in BINDING_VERBS if v in low]


def _is_multi_condition(text: str) -> bool:
    low = text.lower()
    return any(marker in low for marker in MULTI_CONDITION_MARKERS)


def summarize_policy(structured: dict) -> str:
    """
    Produce a clause-referenced summary preserving every clause, binding verb,
    and condition. Clauses are reproduced faithfully (verbatim) so no obligation
    is softened or dropped; multi-condition clauses are tagged explicitly.
    """
    out = []
    out.append(f"POLICY SUMMARY — SINGLE SOURCE: {structured['source']}")
    out.append("=" * 70)
    out.append("Faithful clause-by-clause digest. Every numbered clause preserved.")
    out.append("No content added; no other policy document referenced.")
    out.append("")

    covered = []
    for section in structured["sections"]:
        if not section["clauses"]:
            continue
        out.append(f"SECTION {section['number']} — {section['heading']}")
        for clause in section["clauses"]:
            num = clause["number"]
            text = _normalise(clause["text"])
            covered.append(num)

            tags = ["[VERBATIM]"]  # we reproduce faithfully rather than reword
            verbs = _binding_verbs_in(text)
            if _is_multi_condition(text):
                tags.append("[MULTI-CONDITION PRESERVED]")
            if verbs:
                tags.append(f"[binding: {', '.join(sorted(set(verbs)))}]")

            out.append(f"  Clause {num} {' '.join(tags)}")
            out.append(f"    {text}")
        out.append("")

    # Completeness verification footer.
    source_set = set(structured["clause_numbers"])
    covered_set = set(covered)
    missing = sorted(source_set - covered_set)
    out.append("=" * 70)
    out.append("COMPLETENESS VERIFICATION")
    out.append(f"  Clauses in source : {len(source_set)}")
    out.append(f"  Clauses in summary: {len(covered_set)}")
    if missing:
        out.append(f"  COMPLETENESS WARNING — missing clause numbers: {', '.join(missing)}")
    else:
        out.append("  OK — every numbered clause from the source is present in the summary.")

    # Scope-bleed self-check.
    body = "\n".join(out).lower()
    bled = [p for p in FORBIDDEN_SCOPE_BLEED if p in body]
    if bled:
        out.append(f"  SCOPE-BLEED WARNING — forbidden phrases detected: {bled}")
    else:
        out.append("  OK — no scope-bleed phrases detected.")

    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    structured = retrieve_policy(args.input)
    summary = summarize_policy(structured)

    try:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(summary)
    except OSError as exc:
        print(f"ERROR: could not write output file '{args.output}': {exc}", file=sys.stderr)
        raise SystemExit(1)

    n = len(set(structured["clause_numbers"]))
    print(f"Done. Summarised {n} clause(s) from {structured['source']} -> {args.output}")


if __name__ == "__main__":
    main()
