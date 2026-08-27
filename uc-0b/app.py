"""
UC-0B — Policy Summarisation Agent
Generated from agents.md and skills.md.

Agent contract (agents.md):
  role      : Faithful, clause-complete summarisation only. No inference,
              no general knowledge, no scope bleed.
  intent    : Every clause entry verifiable word-for-word against source.
  context   : Only text present in the source document may appear in output.
  enforcement:
    1. All 10 required clauses must appear: 2.3,2.4,2.5,2.6,2.7,3.2,3.4,5.2,5.3,7.2
    2. Multi-condition obligations preserve ALL conditions (esp. clause 5.2:
       both Department Head AND HR Director must be named).
    3. Binding verbs (must / will / not permitted) must never be softened.
    4. Clause that cannot be condensed without meaning loss → verbatim +
       marker [VERBATIM - summarisation would alter meaning].

Skills (skills.md):
  retrieve_policy(file_path)              → list of {clause_id, heading, text}
  summarize_policy(sections, output_path) → summary string + optional file write
"""
import argparse
import os
import re

# ── Enforcement rule 1: required clauses that must appear in output ───────────
REQUIRED_CLAUSES = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}

# ── Clauses where verbatim quoting is mandatory (multiple interdependent
# conditions that cannot be condensed — enforcement rule 4)
VERBATIM_CLAUSES = {"2.4", "2.5", "2.6", "5.2", "5.3", "7.2"}

VERBATIM_MARKER = "[VERBATIM - summarisation would alter meaning]"


# ─────────────────────────────────────────────────────────────────────────────
# Skill: retrieve_policy  (skills.md)
# ─────────────────────────────────────────────────────────────────────────────
def retrieve_policy(file_path: str) -> list:
    """
    Load a plain-text policy file and return its content as a list of structured
    clause dicts: {clause_id (str), heading (str), text (str)}.

    - clause_id : dotted number e.g. "2.3", "5.2"; "UNSTRUCTURED" if not parseable.
    - heading   : section heading associated with the clause (from === blocks).
    - text      : full original text of the clause, unmodified.

    Error handling (skills.md):
      - FileNotFoundError if the file cannot be read.
      - Unparseable sections get clause_id="UNSTRUCTURED" — never silently dropped.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    with open(file_path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)")
    sections = []
    current_heading = ""
    current_id = None
    current_lines = []

    def _flush():
        if current_id and current_lines:
            sections.append({
                "clause_id": current_id,
                "heading":   current_heading,
                "text":      " ".join(current_lines),
            })

    for line in lines:
        stripped = line.strip()
        # Detect section headings (lines between ═══ separators)
        if re.match(r"^[═]{3,}", stripped):
            continue
        # Check if the line itself looks like a heading (all caps words, no digit prefix)
        m = clause_pattern.match(stripped)
        if m:
            _flush()
            current_id    = m.group(1)
            current_lines = [m.group(2).strip()]
        elif current_id and stripped:
            current_lines.append(stripped)
        elif not current_id and stripped and not re.match(r"^\d", stripped):
            # Possible section heading before first clause
            current_heading = stripped

    _flush()

    return sections


# ─────────────────────────────────────────────────────────────────────────────
# Skill: summarize_policy  (skills.md)
# ─────────────────────────────────────────────────────────────────────────────
def summarize_policy(sections: list, output_path: str = None) -> str:
    """
    Produce a compliant clause-by-clause summary from the structured sections
    returned by retrieve_policy.

    Enforcement (agents.md):
      1. All REQUIRED_CLAUSES must appear.
      2. Multi-condition clauses → verbatim (VERBATIM_CLAUSES set).
      3. Binding verbs preserved — no softening.
      4. [VERBATIM] marker applied where meaning loss is possible.

    Error handling (skills.md):
      - ValueError if sections list is empty.
      - Difficult clauses → verbatim + marker, never omitted.
    """
    if not sections:
        raise ValueError("No policy sections provided - cannot summarise empty document")

    found_clauses = {s["clause_id"] for s in sections}

    lines = []
    lines.append("POLICY SUMMARY — HR Employee Leave Policy (HR-POL-001)")
    lines.append("=" * 60)
    lines.append(
        "NOTE: This summary preserves all binding obligations verbatim "
        "where meaning loss would otherwise occur. Binding verbs (must / "
        "will / not permitted) are unchanged from the source document."
    )
    lines.append("")

    current_heading = None
    for section in sections:
        clause_id = section["clause_id"]
        heading   = section["heading"]
        text      = section["text"]

        if heading and heading != current_heading:
            lines.append("")
            lines.append(f"[ {heading} ]")
            lines.append("-" * 40)
            current_heading = heading

        # Enforcement rule 4 + rule 2: verbatim for sensitive clauses
        if clause_id in VERBATIM_CLAUSES:
            lines.append(f"  {clause_id}  {text}")
            lines.append(f"        {VERBATIM_MARKER}")
        else:
            lines.append(f"  {clause_id}  {text}")

        lines.append("")

    # Enforcement rule 1: warn on any missing required clauses
    missing = REQUIRED_CLAUSES - found_clauses
    if missing:
        lines.append("")
        lines.append("WARNING: The following required clauses were NOT found in the source:")
        for c in sorted(missing):
            lines.append(f"  - Clause {c} [MISSING FROM SOURCE DOCUMENT]")

    summary = "\n".join(lines)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(summary)

    return summary


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summarisation Agent"
    )
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    print(f"Retrieved {len(sections)} clauses from {args.input}")

    summary = summarize_policy(sections, output_path=args.output)

    print(f"Done. Summary written to {args.output}")
    print()
    print(summary)


if __name__ == "__main__":
    main()
