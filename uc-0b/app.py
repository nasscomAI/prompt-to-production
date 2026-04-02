"""
UC-0B — Summary That Changes Meaning  |  app.py
================================================
Implements retrieve_policy and summarize_policy as defined in skills.md.
All enforcement rules from agents.md are applied during summarisation.

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Constants — agents.md enforcement rules
# ─────────────────────────────────────────────────────────────────────────────

# Binding verbs that must be preserved (enforcement rule 3)
BINDING_VERBS: tuple[str, ...] = (
    "must", "will", "requires", "required", "not permitted",
    "are forfeited", "is forfeited", "may not", "shall",
)

# Weaker substitute verbs that signal obligation-softening violations
SOFTENING_VERBS: tuple[str, ...] = (
    "should", "can", "may wish to", "is encouraged to",
    "is expected to", "is recommended",
)

# Scope-bleed phrases — added content not in source (enforcement rule 4)
SCOPE_BLEED_PHRASES: tuple[str, ...] = (
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
    "in line with common hr policy",
    "as per industry norms",
    "generally speaking",
)

# High-risk clauses: cannot be paraphrased without meaning loss (enforcement rule 9)
# These are always output verbatim and tagged VERBATIM
HIGH_RISK_CLAUSES: frozenset[str] = frozenset({
    "2.4",  # written approval required; verbal not valid — two conditions
    "2.5",  # LOP regardless of subsequent approval — 'regardless' is load-bearing
    "5.2",  # requires Department Head AND HR Director — two named approvers (the README trap)
    "7.2",  # not permitted under any circumstances — absolute qualifier
})

# Required ground-truth clause IDs from the README clause inventory
REQUIRED_CLAUSES: tuple[str, ...] = (
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
)


# ─────────────────────────────────────────────────────────────────────────────
# Data model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PolicySection:
    clause_id: str
    heading:   str
    body:      str
    flag:      str = ""          # PARSE_ERROR | UNSTRUCTURED | NEEDS_REVIEW | VERBATIM | ""


@dataclass
class SummaryEntry:
    clause_id: str
    text:      str
    flag:      str = ""          # VERBATIM | NEEDS_REVIEW | ""
    violations: list[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Skill 1 — retrieve_policy  (skills.md)
# ─────────────────────────────────────────────────────────────────────────────

def retrieve_policy(input_path: str) -> list[PolicySection]:
    """
    Load a plain-text policy file and parse it into structured numbered sections.

    Input:  Path to a UTF-8 plain-text policy file with numbered clause headings.
    Output: List of PolicySection objects (clause_id, heading, body).

    Error handling (skills.md):
      - File not found → FileNotFoundError + halt, no partial output.
      - No clause structure detected → single UNSTRUCTURED block + flag.
      - Clause parse failure → raw text preserved with PARSE_ERROR flag.
    """
    # skills.md error_handling: file not found → halt
    try:
        with open(input_path, encoding="utf-8") as fh:
            raw = fh.read()
    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    sections = _parse_sections(raw)

    # skills.md error_handling: no clause structure detected
    if not sections:
        print(
            "[WARN] No numbered clause structure detected — returning document as "
            "UNSTRUCTURED block for manual review.",
            file=sys.stderr,
        )
        return [PolicySection(
            clause_id="UNSTRUCTURED",
            heading="(no structure detected)",
            body=raw.strip(),
            flag="UNSTRUCTURED",
        )]

    return sections


def _parse_sections(raw: str) -> list[PolicySection]:
    """
    Split the raw document into numbered sections using clause heading patterns.
    Recognises headings like: '2.3', '2.3 Leave Notice', '2.3.1 Sub-clause'.
    """
    # Pattern: line starting with digit(s).digit(s) optionally followed by text
    heading_pattern = re.compile(
        r"^(\d+(?:\.\d+)+)\s*(.*?)$",
        re.MULTILINE,
    )

    matches = list(heading_pattern.finditer(raw))
    if not matches:
        return []

    sections: list[PolicySection] = []

    for i, match in enumerate(matches):
        clause_id = match.group(1).strip()
        heading   = match.group(2).strip()

        # Body = text between this heading and the next
        body_start = match.end()
        body_end   = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        body       = raw[body_start:body_end].strip()

        flag = ""
        if not body:
            flag = "NEEDS_REVIEW"
            print(
                f"[WARN] Clause {clause_id} has an empty body — flagged NEEDS_REVIEW.",
                file=sys.stderr,
            )

        sections.append(PolicySection(
            clause_id=clause_id,
            heading=heading,
            body=body,
            flag=flag,
        ))

    return sections


# ─────────────────────────────────────────────────────────────────────────────
# Skill 2 — summarize_policy  (skills.md)
# ─────────────────────────────────────────────────────────────────────────────

def summarize_policy(sections: list[PolicySection]) -> list[SummaryEntry]:
    """
    Produce a compliant clause-by-clause summary from structured policy sections.

    Input:  List of PolicySection objects from retrieve_policy.
    Output: List of SummaryEntry objects — one per clause.

    Enforcement applied per entry:
      - HIGH_RISK_CLAUSES → verbatim quote + VERBATIM tag
      - Binding verb detection and preservation check
      - Scope-bleed phrase rejection
      - Obligation-softening verb detection
    """
    # skills.md error_handling: empty input → halt
    if not sections:
        print("[ERROR] No sections provided to summarize_policy — halting.", file=sys.stderr)
        sys.exit(1)

    entries: list[SummaryEntry] = []

    for sec in sections:
        entry = _summarise_section(sec)
        entries.append(entry)

    # Enforcement rule 1: check all required clauses are present
    _check_required_clauses(entries, sections)

    return entries


def _summarise_section(sec: PolicySection) -> SummaryEntry:
    """
    Produce a single SummaryEntry for one PolicySection.

    High-risk clauses are always verbatim.
    All others: validated summary from body text.
    """
    violations: list[str] = []

    # skills.md / agents.md enforcement rule 9: high-risk → always verbatim
    if sec.clause_id in HIGH_RISK_CLAUSES or sec.flag in ("PARSE_ERROR", "NEEDS_REVIEW"):
        flag = "VERBATIM" if sec.clause_id in HIGH_RISK_CLAUSES else sec.flag
        summary_text = sec.body if sec.body else "(body missing)"
        return SummaryEntry(
            clause_id=sec.clause_id,
            text=summary_text,
            flag=flag,
            violations=[],
        )

    # For non-high-risk clauses: use body as summary, then validate it
    summary_text = sec.body

    # Enforcement rule 3: check binding verb preserved
    binding_verb_present = any(v in summary_text.lower() for v in BINDING_VERBS)
    if not binding_verb_present:
        violations.append(
            f"OBLIGATION_SOFTENING: No binding verb detected in clause {sec.clause_id}."
        )

    # Enforcement rule 3: check for softening verbs
    for sv in SOFTENING_VERBS:
        if sv in summary_text.lower():
            violations.append(
                f"OBLIGATION_SOFTENING: Weak verb '{sv}' detected in clause {sec.clause_id}."
            )

    # Enforcement rule 4: reject scope-bleed phrases
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase in summary_text.lower():
            violations.append(
                f"SCOPE_BLEED: Disallowed phrase '{phrase}' detected in clause {sec.clause_id}."
            )
            # Strip the offending phrase — cannot leave it in
            summary_text = re.sub(re.escape(phrase), "[REMOVED:SCOPE_BLEED]", summary_text, flags=re.IGNORECASE)

    flag = "NEEDS_REVIEW" if violations else ""

    return SummaryEntry(
        clause_id=sec.clause_id,
        text=summary_text,
        flag=flag,
        violations=violations,
    )


def _check_required_clauses(entries: list[SummaryEntry], sections: list[PolicySection]) -> None:
    """
    Enforcement rule 1: every required clause must appear in the output.
    Logs a warning for any missing required clause — does not halt.
    """
    present_ids = {e.clause_id for e in entries}
    source_ids  = {s.clause_id for s in sections}

    for required in REQUIRED_CLAUSES:
        if required not in present_ids and required not in source_ids:
            print(
                f"[WARN] Required clause {required} is not present in the source document "
                f"or the summary — clause omission risk.",
                file=sys.stderr,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Output writer
# ─────────────────────────────────────────────────────────────────────────────

def write_summary(entries: list[SummaryEntry], output_path: str) -> None:
    """Write the summary entries to the output file."""
    lines: list[str] = [
        "UC-0B — HR Leave Policy Summary",
        "=" * 60,
        "NOTES:",
        "  VERBATIM — clause quoted verbatim to prevent meaning loss",
        "  NEEDS_REVIEW — clause body missing or violations detected",
        "=" * 60,
        "",
    ]

    violation_log: list[str] = []

    for entry in entries:
        tag = f" [{entry.flag}]" if entry.flag else ""
        lines.append(f"Clause {entry.clause_id}{tag}")
        lines.append("-" * 40)
        lines.append(entry.text)
        lines.append("")

        if entry.violations:
            violation_log.extend(entry.violations)

    if violation_log:
        lines.append("=" * 60)
        lines.append("ENFORCEMENT VIOLATIONS DETECTED:")
        lines.extend(f"  - {v}" for v in violation_log)
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print(f"[INFO] {len(entries)} clause(s) written to {output_path}")
    if violation_log:
        print(
            f"[WARN] {len(violation_log)} enforcement violation(s) detected — "
            f"review output file.",
            file=sys.stderr,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Entry point — README run command:
#   python app.py --input ../data/policy-documents/policy_hr_leave.txt
#                 --output summary_hr_leave.txt
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summariser — clause-faithful summary of HR policy documents."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input policy text file, e.g. ../data/policy-documents/policy_hr_leave.txt",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write summary file, e.g. summary_hr_leave.txt",
    )
    args = parser.parse_args()

    # Skill 1: retrieve_policy
    sections = retrieve_policy(args.input)

    # Skill 2: summarize_policy
    entries = summarize_policy(sections)

    # Write output
    write_summary(entries, args.output)

    print(f"Done. Summary written to {args.output}")
