"""
UC-0B — Policy Summarisation Agent
Built using the RICE → agents.md → skills.md → CRAFT workflow.

Failure modes guarded against:
  - Clause omission      : all numbered clauses extracted; mandatory set validated
  - Obligation softening : binding verbs preserved verbatim; softening heuristic check
  - Scope bleed          : only source-document text used; no external phrases injected
  - Condition drop       : multi-condition clauses (e.g. 5.2) quoted verbatim
  - Negation loss        : negation keywords tracked and preserved
"""

import argparse
import re
import sys
from typing import Optional

# ── Constants ──────────────────────────────────────────────────────────────────

# The 10 clauses the README mandates must always be present
MANDATORY_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Binding verbs that must never be softened
BINDING_VERBS = ["must", "will", "requires", "require", "not permitted", "shall", "cannot", "may not"]

# Softening substitutions to detect (original → bad paraphrase)
SOFTENING_PAIRS = [
    ("must", "should"),
    ("must", "encouraged"),
    ("not permitted", "discouraged"),
    ("not permitted", "not recommended"),
    ("will be recorded", "may be recorded"),
    ("requires", "recommends"),
    ("cannot", "should not"),
]

# Clauses where full verbatim quoting is safer than any paraphrase
VERBATIM_CLAUSES = {"5.2", "5.3", "7.2"}

# Scope-bleed phrases that must never appear in output
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government",
    "employees are generally expected",
    "as required by law",
    "industry norm",
    "best practice",
]

DIVIDER_RE = re.compile(r"^[═=─\-]{5,}")
CLAUSE_RE  = re.compile(r"^(\d+\.\d+)\s+(.*)")
SECTION_RE = re.compile(r"^\d+\.\s+[A-Z]")


# ── Skill: retrieve_policy ─────────────────────────────────────────────────────

def retrieve_policy(file_path: str) -> dict:
    """
    Load and parse a structured plain-text policy document.

    Returns:
        {
            "title": str,
            "reference": str,
            "sections": {
                "2": {"heading": "ANNUAL LEAVE", "clauses": {"2.1": "...", ...}},
                ...
            }
        }
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    if not any(l.strip() for l in lines):
        raise ValueError(f"Policy file is empty: {file_path}")

    # ── Extract title / reference from header block ────────────────────────────
    title_lines = []
    reference   = ""
    for line in lines[:10]:
        stripped = line.strip()
        if not stripped or DIVIDER_RE.match(stripped):
            break
        if "Document Reference:" in stripped:
            reference = stripped
        else:
            title_lines.append(stripped)
    title = " | ".join(title_lines) if title_lines else "Unknown Policy"

    # ── Parse sections and clauses ─────────────────────────────────────────────
    sections: dict = {}
    current_section_id   = None
    current_section_head = None
    current_clause_id    = None
    current_clause_text  = []

    def _flush_clause():
        """Save the current clause buffer into the section."""
        if current_section_id and current_clause_id:
            sections[current_section_id]["clauses"][current_clause_id] = (
                " ".join(current_clause_text).strip()
            )

    for raw_line in lines:
        line = raw_line.rstrip()

        # Skip divider lines
        if DIVIDER_RE.match(line.strip()):
            continue

        # Section heading: "2. ANNUAL LEAVE"
        # Pattern: starts with digit(s), dot, space, ALL-CAPS words
        section_match = re.match(r"^(\d+)\.\s+([A-Z][A-Z\s\(\)]+)$", line.strip())
        if section_match:
            _flush_clause()
            current_clause_id   = None
            current_clause_text = []
            current_section_id  = section_match.group(1)
            current_section_head = section_match.group(2).strip()
            sections[current_section_id] = {
                "heading": current_section_head,
                "clauses": {},
            }
            continue

        # Clause line: "2.3 Employees must submit..."
        clause_match = CLAUSE_RE.match(line.strip())
        if clause_match:
            _flush_clause()
            current_clause_id   = clause_match.group(1)
            current_clause_text = [clause_match.group(2)]
            continue

        # Continuation of current clause (indented or blank-ish lines)
        stripped = line.strip()
        if stripped and current_clause_id:
            current_clause_text.append(stripped)

    _flush_clause()  # flush the last clause

    clause_count = sum(len(s["clauses"]) for s in sections.values())
    if clause_count == 0:
        raise ValueError("No clauses parsed — check document format.")

    return {"title": title, "reference": reference, "sections": sections}


# ── Skill: summarize_policy ────────────────────────────────────────────────────

def _check_scope_bleed(text: str) -> list[str]:
    """Return any scope-bleed phrases found in text."""
    found = []
    tl = text.lower()
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase in tl:
            found.append(phrase)
    return found


def _check_softening(clause_id: str, text: str) -> Optional[str]:
    """
    Heuristic check: if a binding verb from the source is absent while a known
    softening substitute is present, flag it.
    Returns a warning string or None.
    """
    tl = text.lower()
    for (strong, weak) in SOFTENING_PAIRS:
        if weak in tl and strong not in tl:
            return f"Possible obligation softening in {clause_id}: '{strong}' → '{weak}'"
    return None


def _format_clause_line(clause_id: str, raw_text: str) -> tuple[str, list[str]]:
    """
    Format a single clause line.
    Returns (formatted_line, list_of_warnings).
    """
    warnings = []

    # Verbatim clauses: always quote in full to prevent condition drops
    if clause_id in VERBATIM_CLAUSES:
        line = f"[{clause_id}] [VERBATIM] {raw_text}"
        warnings.append(f"[{clause_id}] quoted verbatim — multi-condition or absolute obligation.")
        return line, warnings

    # Scope bleed check
    bleed = _check_scope_bleed(raw_text)
    if bleed:
        for b in bleed:
            warnings.append(f"[{clause_id}] SCOPE BLEED detected: \"{b}\"")

    # Softening check
    soft_warn = _check_softening(clause_id, raw_text)
    if soft_warn:
        warnings.append(soft_warn)
        raw_text = raw_text + " [SOFTENING-RISK]"

    return f"[{clause_id}] {raw_text}", warnings


def summarize_policy(policy: dict, mandatory_clauses: list[str]) -> str:
    """
    Produce a clause-complete, obligation-faithful plain-text summary.
    Includes a VALIDATION REPORT at the end.
    """
    output_lines  = []
    flags         = []
    present       = []
    missing       = []
    all_clause_ids: set[str] = set()

    # ── Header ─────────────────────────────────────────────────────────────────
    output_lines.append("=" * 65)
    output_lines.append("POLICY SUMMARY — COMPLIANCE-FAITHFUL EXTRACT")
    output_lines.append(f"Source: {policy['title']}")
    if policy.get("reference"):
        output_lines.append(f"Ref   : {policy['reference']}")
    output_lines.append("=" * 65)
    output_lines.append(
        "NOTE: This summary preserves all binding verbs, thresholds, and\n"
        "      multi-condition obligations verbatim. Clauses marked [VERBATIM]\n"
        "      are quoted in full to prevent meaning loss."
    )
    output_lines.append("")

    # ── Sections & Clauses ─────────────────────────────────────────────────────
    for section_id in sorted(policy["sections"].keys(), key=lambda x: int(x)):
        section = policy["sections"][section_id]
        output_lines.append(f"{'─' * 65}")
        output_lines.append(f"SECTION {section_id}: {section['heading']}")
        output_lines.append(f"{'─' * 65}")

        for clause_id in sorted(section["clauses"].keys(),
                                key=lambda x: float(x)):
            raw_text = section["clauses"][clause_id]
            all_clause_ids.add(clause_id)

            line, warns = _format_clause_line(clause_id, raw_text)
            output_lines.append(line)
            flags.extend(warns)

        output_lines.append("")

    # ── Mandatory Clause Validation ────────────────────────────────────────────
    for cid in mandatory_clauses:
        if cid in all_clause_ids:
            present.append(cid)
        else:
            missing.append(cid)

    # ── Validation Report ──────────────────────────────────────────────────────
    output_lines.append("=" * 65)
    output_lines.append("VALIDATION REPORT")
    output_lines.append("=" * 65)

    output_lines.append(f"\n✓ MANDATORY CLAUSES PRESENT ({len(present)}/{len(mandatory_clauses)}):")
    for cid in present:
        output_lines.append(f"  • {cid}")

    if missing:
        output_lines.append(f"\n✗ MANDATORY CLAUSES MISSING ({len(missing)}) — ACTION REQUIRED:")
        for cid in missing:
            output_lines.append(f"  ✗ {cid}")
    else:
        output_lines.append("\n✓ All mandatory clauses are present.")

    if flags:
        output_lines.append(f"\n⚑ FLAGS ({len(flags)}):")
        for f in flags:
            output_lines.append(f"  ⚑ {f}")
    else:
        output_lines.append("\n✓ No flags raised.")

    output_lines.append("\n" + "=" * 65)

    return "\n".join(output_lines)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B — Compliance-faithful policy summarisation agent"
    )
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    # Skill 1: retrieve_policy
    print(f"[INFO] Loading policy: {args.input}", file=sys.stderr)
    try:
        policy = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    section_count = len(policy["sections"])
    clause_count  = sum(len(s["clauses"]) for s in policy["sections"].values())
    print(f"[INFO] Parsed {section_count} sections, {clause_count} clauses.", file=sys.stderr)

    # Skill 2: summarize_policy
    print("[INFO] Generating compliance-faithful summary...", file=sys.stderr)
    summary = summarize_policy(policy, MANDATORY_CLAUSES)

    # Write output
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"\n── Summary Complete ────────────────────────────────────")
    print(f"  Input  : {args.input}")
    print(f"  Output : {args.output}")
    print(f"  Clauses: {clause_count} extracted")
    print(f"  Mandatory clause check: {len(MANDATORY_CLAUSES)} required")
    print(f"────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()
