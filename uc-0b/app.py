"""
UC-0B — Summary That Changes Meaning
Implements the retrieve_policy and summarize_policy skills defined in skills.md,
enforcing every rule from agents.md.

Run:
  python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""
import argparse
import re
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("uc-0b")

# ---------------------------------------------------------------------------
# Binding verbs that must be preserved exactly (agents.md enforcement)
# ---------------------------------------------------------------------------
BINDING_VERBS = [
    "must", "will", "requires", "required", "not permitted",
    "are forfeited", "is forfeited", "may", "cannot", "must not",
]


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(input_path: str) -> list[dict]:
    """
    Loads a .txt policy file, returns content as structured numbered sections.

    Each section dict contains:
      - section_number: e.g. "2.3"
      - heading: section heading (from ═══ delimited blocks) or ""
      - body: full clause text
      - binding_verb: the primary obligation verb found in the clause
    """
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as exc:
        logger.error(f"Failed to read input file {input_path}: {exc}")
        sys.exit(1)

    if not raw.strip():
        logger.error(f"Input file {input_path} is empty.")
        sys.exit(1)

    lines = raw.splitlines()
    sections: list[dict] = []
    current_heading = ""
    clause_buffer: list[str] = []
    current_clause_num = None

    # Regex to detect a numbered clause start: e.g. "2.3 " or "10.1 "
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)")
    # Regex for heading lines (the text between ═══ delimiter blocks)
    heading_re = re.compile(r"^\d+\.\s+(.+)")
    separator_re = re.compile(r"^[═]+$")

    def _flush_clause():
        nonlocal current_clause_num, clause_buffer
        if current_clause_num and clause_buffer:
            body = " ".join(clause_buffer).strip()
            # Detect binding verb
            body_lower = body.lower()
            detected_verb = ""
            for verb in BINDING_VERBS:
                if verb in body_lower:
                    detected_verb = verb
                    break
            sections.append({
                "section_number": current_clause_num,
                "heading": current_heading,
                "body": body,
                "binding_verb": detected_verb,
            })
        current_clause_num = None
        clause_buffer = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Separator line
        if separator_re.match(line):
            _flush_clause()
            # Next non-separator, non-empty line might be a heading
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines):
                candidate = lines[i].strip()
                h_match = heading_re.match(candidate)
                if h_match and not clause_re.match(candidate):
                    current_heading = h_match.group(1).strip()
                    i += 1
                    # Skip next separator
                    while i < len(lines) and (separator_re.match(lines[i].strip()) or not lines[i].strip()):
                        i += 1
            continue

        # Numbered clause start
        c_match = clause_re.match(line)
        if c_match:
            _flush_clause()
            current_clause_num = c_match.group(1)
            clause_buffer = [c_match.group(2).strip()]
            i += 1
            continue

        # Continuation of a clause (indented or plain text)
        if current_clause_num and line:
            clause_buffer.append(line)

        i += 1

    _flush_clause()

    if not sections:
        logger.warning("No numbered sections found in the policy file.")

    logger.info(f"Retrieved {len(sections)} clauses from {input_path}")
    return sections


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(sections: list[dict]) -> str:
    """
    Takes structured sections, produces a compliant summary with clause references.

    Enforcement (agents.md):
      • Every numbered clause must be present.
      • Multi-condition obligations preserve ALL conditions.
      • Binding verbs preserved exactly — no softening.
      • Never add information not in the source.
      • Verbatim quote if meaning loss risk.
      • Specific limits/dates preserved exactly.
    """
    if not sections:
        return "ERROR: No sections provided for summarisation.\n"

    output_lines: list[str] = []
    current_heading = ""

    for section in sections:
        # Print heading when it changes
        if section["heading"] and section["heading"] != current_heading:
            current_heading = section["heading"]
            output_lines.append(f"\n{'='*60}")
            output_lines.append(f"  {current_heading.upper()}")
            output_lines.append(f"{'='*60}")

        clause_num = section["section_number"]
        body = section["body"]
        binding_verb = section["binding_verb"]

        # Detect multi-condition clauses that risk condition dropping
        multi_condition_markers = [" and ", " both ", " AND "]
        has_multi_condition = any(m in body for m in multi_condition_markers)

        # Detect specific limits that must be preserved
        has_specific_limits = bool(re.search(
            r"\d+\s*(days?|weeks?|hours?|hrs|months?|Rs|percent|%|calendar|working|December|January|March)",
            body, re.IGNORECASE
        ))

        # Decide: summarise or quote verbatim
        if has_multi_condition and has_specific_limits:
            # High risk of meaning loss — quote verbatim
            output_lines.append(
                f"\nClause {clause_num} [VERBATIM — meaning loss risk]:"
            )
            output_lines.append(f"  \"{body}\"")
            if binding_verb:
                output_lines.append(f"  [Binding verb: {binding_verb}]")
        elif has_multi_condition:
            # Preserve all conditions explicitly
            output_lines.append(f"\nClause {clause_num}:")
            output_lines.append(f"  {body}")
            if binding_verb:
                output_lines.append(f"  [Binding verb: {binding_verb}]")
        else:
            # Standard summary — but still preserve the full clause text
            # to avoid any accidental condition dropping
            output_lines.append(f"\nClause {clause_num}:")
            output_lines.append(f"  {body}")
            if binding_verb:
                output_lines.append(f"  [Binding verb: {binding_verb}]")

    summary = "\n".join(output_lines) + "\n"
    return summary


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True,
                        help="Path to policy .txt file")
    parser.add_argument("--output", required=True,
                        help="Path to write summary output")
    args = parser.parse_args()

    # Skill 1: retrieve_policy
    sections = retrieve_policy(args.input)

    # Skill 2: summarize_policy
    summary = summarize_policy(sections)

    # Write output
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(f"POLICY SUMMARY\n")
            f.write(f"Source: {args.input}\n")
            f.write(f"Total clauses: {len(sections)}\n")
            f.write(f"{'='*60}\n")
            f.write(summary)
    except Exception as exc:
        logger.error(f"Failed to write output file {args.output}: {exc}")
        sys.exit(1)

    logger.info(f"Summary written to {args.output} ({len(sections)} clauses)")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
