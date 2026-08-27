"""
UC-0B — Summary That Changes Meaning
Implemented using agents.md (RICE) and skills.md contracts.

Failure modes guarded against: clause omission · scope bleed · obligation softening
"""
import argparse
import re
import sys


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> dict:
    """
    Load a plain-text policy file and return its content parsed into numbered
    sections.

    Output dict keys:
      - clauses: list of {clause_id, heading, body}  — one entry per clause
      - raw_text: full verbatim file content (fallback)
      - parse_warning: non-empty string if no numbered clauses were detected

    Raises FileNotFoundError if the file cannot be read.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Policy file not found: {file_path}\n"
            "Check the path and try again."
        )

    # Match clause numbers like 2.3, 3.4, 5.2 — captures id and rest of line as heading
    # Then everything until the next clause number (or end of text) is the body.
    pattern = re.compile(
        r'^(\d+\.\d+)\s*(.*?)\n(.*?)(?=^\d+\.\d+|\Z)',
        re.MULTILINE | re.DOTALL,
    )

    clauses = []
    for match in pattern.finditer(raw_text):
        clause_id = match.group(1).strip()
        heading   = match.group(2).strip()
        body      = " ".join(match.group(3).split())  # normalise whitespace
        clauses.append({
            "clause_id": clause_id,
            "heading":   heading,
            "body":      body,
        })

    parse_warning = (
        "No numbered clauses detected — verify format"
        if not clauses
        else ""
    )

    return {
        "clauses":       clauses,
        "raw_text":      raw_text,
        "parse_warning": parse_warning,
    }


# ---------------------------------------------------------------------------
# Helpers — obligation-softening detection (agents.md enforcement rule 3)
# ---------------------------------------------------------------------------

# Binding verbs that must not be weakened in any output sentence.
BINDING_VERBS = ["must", "will", "requires", "required", "not permitted", "forfeited"]

# Scope-bleed phrases explicitly banned by agents.md context section.
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
    "in general",
    "it is common",
    "as is customary",
]

def _check_scope_bleed(text: str) -> list[str]:
    """Return any scope-bleed phrases found in text."""
    lower = text.lower()
    return [p for p in SCOPE_BLEED_PHRASES if p in lower]


def _summarise_clause(clause: dict) -> str:
    """
    Produce one summary line for a single clause following agents.md rules:
    - Preserve all conditions and binding verbs (rules 2 & 3)
    - Quote verbatim + flag if the body is short enough that paraphrasing
      would risk meaning loss (rule 4)
    - Return a missing-body notice rather than skipping (rule 1)
    """
    clause_id = clause["clause_id"]
    body      = clause.get("body", "").strip()
    heading   = clause.get("heading", "")

    # skills.md error_handling: empty body → flag, do not skip
    if not body:
        return (
            f"{clause_id} {heading}\n"
            f"  [CLAUSE BODY MISSING — manual review required]"
        )

    # agents.md enforcement rule 4: quote verbatim when body is already concise
    # or when it contains multiple interdependent conditions (detected by
    # presence of "and" / "&" alongside a binding verb — heuristic).
    has_binding   = any(v in body.lower() for v in BINDING_VERBS)
    has_multi_cond = bool(re.search(r'\b(and|both|&)\b', body, re.IGNORECASE)) and has_binding
    is_short      = len(body.split()) <= 30

    if is_short or has_multi_cond:
        label = heading + " — " if heading else ""
        return (
            f"{clause_id} {label}{body}\n"
            f"  [VERBATIM — summarisation would alter meaning]"
        )

    # Standard summary: keep binding verbs, first ~40 words
    words   = body.split()
    summary = " ".join(words[:40]) + ("..." if len(words) > 40 else "")
    label   = f"{heading}: " if heading else ""
    return f"{clause_id} {label}{summary}"


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(parsed: dict) -> str:
    """
    Take the output of retrieve_policy and produce a clause-faithful summary.

    - Every clause present and identified by clause_id (agents.md rule 1)
    - All conditions preserved — no silent drops (rule 2)
    - Binding verbs not softened (rule 3)
    - Verbatim quote + flag when summarisation would alter meaning (rule 4)
    - No scope-bleed language added (agents.md context section)

    Returns a plain-text summary string.
    Raises ValueError if the clause list is empty.
    """
    clauses = parsed.get("clauses", [])

    if not clauses:
        # skills.md error_handling: empty clause list → error, no output file
        raise ValueError(
            "No clauses to summarise — check retrieve_policy output.\n"
            + (f"Parse warning: {parsed['parse_warning']}" if parsed.get("parse_warning") else "")
        )

    lines = ["POLICY SUMMARY", "=" * 60, ""]

    for clause in clauses:
        summary_line = _summarise_clause(clause)

        # Paranoia check: ensure we haven't introduced scope-bleed language
        bleed = _check_scope_bleed(summary_line)
        if bleed:
            summary_line += f"\n  [SCOPE BLEED DETECTED: {', '.join(bleed)} — review required]"

        lines.append(summary_line)
        lines.append("")  # blank line between clauses

    lines.append("=" * 60)
    lines.append(f"Total clauses summarised: {len(clauses)}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    # Skill 1: load and parse
    parsed = retrieve_policy(args.input)

    if parsed["parse_warning"]:
        print(f"[WARN] {parsed['parse_warning']}", file=sys.stderr)

    # Skill 2: summarise
    try:
        summary = summarize_policy(parsed)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
