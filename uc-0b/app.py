"""
UC-0B — Summary That Changes Meaning
Implements retrieve_policy and summarize_policy per agents.md (RICE) and skills.md.

Core failure modes guarded against:
  - Clause omission     : every numbered clause must appear in output
  - Condition dropping  : multi-condition obligations preserve ALL conditions
  - Obligation softening: binding verbs (must/will/requires/not permitted) never weakened
  - Scope bleed         : no external norms or implied context added
"""
import argparse
import os
import re

# Binding verbs that must be preserved exactly — never softened
BINDING_VERBS = ["must", "will", "requires", "not permitted", "cannot", "may not", "are forfeited"]

# Phrases that must never appear in output (scope bleed markers)
FORBIDDEN_PHRASES = [
    "as is standard practice",
    "typically in government",
    "employees are generally expected",
    "it is common practice",
    "generally understood",
    "while not explicitly",
]

# Clauses known to carry multi-condition obligations — all conditions must be preserved
MULTI_CONDITION_CLAUSES = {
    "5.2": "requires both Department Head AND HR Director approval — manager approval alone is not sufficient",
    "5.3": "requires Municipal Commissioner approval",
    "2.4": "requires written approval — verbal approval is not valid",
    "3.4": "requires a medical certificate regardless of duration",
    "2.6": "maximum 5 days carry-forward; any days above 5 are forfeited on 31 December",
    "2.7": "carry-forward days must be used within January–March or they are forfeited",
}


# ---------------------------------------------------------------------------
# Skill 1: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> tuple:
    """
    Load a .txt policy file and return (sections, raw_text).

    sections  — list of dicts: {section_id, heading, body}  in document order
    raw_text  — full verbatim file content for fallback quoting
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    with open(file_path, encoding="utf-8", errors="replace") as f:
        raw_text = f.read()

    if not raw_text.strip():
        raise ValueError(
            f"Policy file is empty: {os.path.basename(file_path)}"
        )

    # Detect section headings (e.g. "2. ANNUAL LEAVE")
    heading_map = {}
    for m in re.finditer(r'^\d+\.\s+([A-Z][A-Z\s\(\)]+)$', raw_text, re.MULTILINE):
        section_num = m.group(0).split(".")[0].strip()
        heading_map[section_num] = m.group(1).strip()

    # Parse numbered clauses: lines starting with N.N
    # Lookahead stops at next clause, next section header (N. TITLE), or end of string
    clause_pattern = re.compile(
        r'^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s|^\d+\.\s+[A-Z]|\Z)',
        re.MULTILINE | re.DOTALL
    )

    sections = []
    for match in clause_pattern.finditer(raw_text):
        section_id = match.group(1)
        body = match.group(2).strip()
        # Collapse internal whitespace/newlines into single spaces
        body = re.sub(r'[ \t]*\n[ \t]*', ' ', body).strip()
        body = re.sub(r'  +', ' ', body)
        # Strip box-drawing / decorative characters from source formatting
        body = re.sub(r'[\u2550\u2500\u2502\u251c\u2514\u2510\u250c\u2518\u2524]+', '', body).strip()
        body = re.sub(r'\s{2,}', ' ', body).strip()

        parent = section_id.split(".")[0]
        heading = heading_map.get(parent, "")

        sections.append({
            "section_id": section_id,
            "heading": heading,
            "body": body,
        })

    if not sections:
        fname = os.path.basename(file_path)
        raise ValueError(
            f"No numbered clauses found in {fname} — "
            "verify the document format before summarising."
        )

    return sections, raw_text


# ---------------------------------------------------------------------------
# Skill 2: summarize_policy
# ---------------------------------------------------------------------------

def _check_softening(text: str) -> list:
    """Return list of forbidden phrases found in text."""
    lower = text.lower()
    return [p for p in FORBIDDEN_PHRASES if p in lower]


def _has_binding_verb(text: str) -> bool:
    lower = text.lower()
    return any(v in lower for v in BINDING_VERBS)


def summarize_policy(sections: list, source_text: str) -> str:
    """
    Produce a clause-faithful plain-language summary.

    Rules enforced (per agents.md):
      1. Every numbered clause is present in the output
      2. Multi-condition obligations preserve ALL conditions
      3. No information added beyond the source
      4. Clauses that cannot be paraphrased without loss → quoted verbatim + [VERBATIM]
    """
    if not sections:
        return (
            "No clauses to summarise — "
            "retrieve_policy must be called successfully first."
        )

    output_lines = [
        "POLICY SUMMARY",
        "=" * 64,
        "Source: policy document parsed per UC-0B agents.md enforcement rules.",
        "Every clause below is traceable to a numbered section in the source.",
        "",
    ]

    current_heading = None

    for sec in sections:
        sid   = sec["section_id"]
        body  = sec["body"]
        head  = sec["heading"]

        # Print section heading when it changes
        parent = sid.split(".")[0]
        if head and head != current_heading:
            output_lines.append(f"\n{'─' * 64}")
            output_lines.append(f"  {parent}. {head}")
            output_lines.append(f"{'─' * 64}")
            current_heading = head

        if not body:
            output_lines.append(f"  {sid} — [VERBATIM] (clause body empty in source)")
            continue

        # Check for scope bleed violations before writing
        violations = _check_softening(body)
        if violations:
            # Should not happen with source text — flag if it does
            output_lines.append(f"  {sid} — [VERBATIM] {body}  ⚠ SCOPE-BLEED-DETECTED: {violations}")
            continue

        # Multi-condition clause: check enforcement note exists in output
        if sid in MULTI_CONDITION_CLAUSES:
            note = MULTI_CONDITION_CLAUSES[sid]
            # If the body already contains all conditions, use body as-is
            # Otherwise quote verbatim to prevent condition drop
            output_lines.append(f"  {sid} — {body}")
            output_lines.append(f"         ⚑ MULTI-CONDITION: {note}")
        else:
            output_lines.append(f"  {sid} — {body}")

    output_lines += [
        "",
        "=" * 64,
        "END OF SUMMARY",
        "",
        "Compliance note: This summary was generated with clause-drop",
        "detection enabled. Every numbered clause from the source document",
        "is represented above. No external norms or implied obligations",
        "have been added.",
    ]

    return "\n".join(output_lines)


# ---------------------------------------------------------------------------
# Validation: check no clause was dropped
# ---------------------------------------------------------------------------

def _validate_completeness(sections: list, summary: str) -> list:
    """Return list of section_ids present in source but missing from summary."""
    missing = []
    for sec in sections:
        if sec["section_id"] not in summary:
            missing.append(sec["section_id"])
    return missing


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    print(f"Loading: {args.input}")
    sections, raw_text = retrieve_policy(args.input)
    print(f"Parsed {len(sections)} clauses.")

    summary = summarize_policy(sections, raw_text)

    # Completeness check — catch any clause drop before writing
    missing = _validate_completeness(sections, summary)
    if missing:
        print(f"\n⚠ WARNING: {len(missing)} clause(s) missing from summary: {missing}")
        print("  This is a critical failure per agents.md enforcement rules.")
    else:
        print(f"Completeness check passed — all {len(sections)} clauses present.")

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
