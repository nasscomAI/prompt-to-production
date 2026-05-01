"""
UC-0B app.py

Implements two skills described in skills.md:
- retrieve_policy
- summarize_policy

Enforces UC-0B constraints from agents.md and README.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


REQUIRED_CLAUSE_ORDER = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
DISALLOWED_SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
]


class SkillError(Exception):
    """Structured skill error with stable error code."""

    def __init__(self, error_code: str, message: str):
        super().__init__(message)
        self.error_code = error_code
        self.message = message


@dataclass
class ClauseSection:
    clause_id: str
    text: str
    binding_verb: str


def infer_binding_verb(clause_text: str) -> str:
    lower = clause_text.lower()
    if " not permitted " in f" {lower} ":
        return "not permitted"
    if " must " in f" {lower} ":
        return "must"
    if " requires " in f" {lower} " or " require " in f" {lower} ":
        return "requires"
    if " will " in f" {lower} ":
        return "will"
    if " may " in f" {lower} ":
        return "may"
    if " forfeited " in f" {lower} ":
        return "are forfeited"
    return "unspecified"


def _parse_numbered_clauses(raw_text: str) -> List[ClauseSection]:
    lines = raw_text.splitlines()
    clause_start = re.compile(r"^\s*(\d+\.\d+)\s+(.+?)\s*$")
    all_caps_heading = re.compile(r"^\s*\d+\.\s+[A-Z][A-Z\s\-\(\)&]+$")

    parsed: List[ClauseSection] = []
    current_id: str | None = None
    current_parts: List[str] = []

    def flush_current() -> None:
        nonlocal current_id, current_parts
        if current_id is None:
            return
        text = " ".join(p.strip() for p in current_parts if p.strip())
        if text:
            parsed.append(ClauseSection(current_id, text, infer_binding_verb(text)))
        current_id = None
        current_parts = []

    for line in lines:
        start = clause_start.match(line)
        if start:
            flush_current()
            current_id = start.group(1)
            current_parts = [start.group(2)]
            continue

        if current_id is not None:
            stripped = line.strip()
            if not stripped:
                # Keep reading until next clause; blank line is not a hard stop.
                continue
            if stripped.startswith("═"):
                continue
            if all_caps_heading.match(stripped):
                continue
            current_parts.append(stripped)

    flush_current()
    return parsed


def retrieve_policy(input_path: str) -> List[ClauseSection]:
    """Loads .txt policy file and returns structured numbered sections."""
    path = Path(input_path)
    if path.suffix.lower() != ".txt":
        raise SkillError("INVALID_INPUT_FILE", f"Expected a .txt file, got: {path}")
    if not path.exists() or not path.is_file():
        raise SkillError("INVALID_INPUT_FILE", f"Input file not found: {path}")

    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SkillError("INVALID_INPUT_FILE", f"Unable to read input file: {exc}") from exc

    sections = _parse_numbered_clauses(raw_text)
    if not sections:
        raise SkillError("AMBIGUOUS_STRUCTURE", "No numbered clauses found in input policy document.")

    by_id = {s.clause_id: s for s in sections}
    missing_required = [cid for cid in REQUIRED_CLAUSE_ORDER if cid not in by_id]
    if missing_required:
        raise SkillError(
            "CLAUSE_INVENTORY_MISMATCH",
            f"Missing required clause IDs: {', '.join(missing_required)}",
        )

    return sections


def _validate_summary_scope_bleed(summary_text: str) -> None:
    lower = summary_text.lower()
    leaked = [p for p in DISALLOWED_SCOPE_BLEED_PHRASES if p in lower]
    if leaked:
        raise SkillError(
            "UNSUPPORTED_ADDITION",
            "Scope-bleed language detected: " + ", ".join(f"'{p}'" for p in leaked),
        )


def summarize_policy(structured_sections: List[ClauseSection]) -> str:
    """Builds compliant summary with clause references and enforcement checks."""
    if not structured_sections:
        raise SkillError("INVALID_SECTION_INPUT", "Structured sections cannot be empty.")
    for idx, section in enumerate(structured_sections):
        if not getattr(section, "clause_id", None) or not getattr(section, "text", None):
            raise SkillError(
                "INVALID_SECTION_INPUT",
                f"Invalid section at index {idx}: missing clause_id or text.",
            )

    by_id: Dict[str, ClauseSection] = {s.clause_id: s for s in structured_sections}
    missing_required = [cid for cid in REQUIRED_CLAUSE_ORDER if cid not in by_id]
    if missing_required:
        raise SkillError(
            "CLAUSE_OMISSION_RISK",
            f"Cannot summarize; required clauses missing: {', '.join(missing_required)}",
        )

    # Explicit trap check for clause 5.2 two-approver condition.
    clause_52 = by_id["5.2"].text.lower()
    if not ("department head" in clause_52 and "hr director" in clause_52):
        raise SkillError(
            "CONDITION_DROP_RISK",
            "Clause 5.2 must preserve both Department Head and HR Director approvals.",
        )

    lines: List[str] = []
    lines.append("Compliant summary (grounded in source clauses):")

    for clause_id in REQUIRED_CLAUSE_ORDER:
        section = by_id[clause_id]
        # Verbatim clause text avoids meaning drift and unsupported additions.
        lines.append(f"- Clause {clause_id} [{section.binding_verb}]: {section.text}")

    summary = "\n".join(lines).strip() + "\n"

    _validate_summary_scope_bleed(summary)

    # Enforcement: every required clause must appear in final summary text.
    missing_in_summary = [cid for cid in REQUIRED_CLAUSE_ORDER if f"Clause {cid}" not in summary]
    if missing_in_summary:
        raise SkillError(
            "CLAUSE_OMISSION_RISK",
            f"Final summary omitted clause references: {', '.join(missing_in_summary)}",
        )

    return summary


def write_output(output_path: str, content: str) -> None:
    path = Path(output_path)
    if path.parent and str(path.parent) != ".":
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UC-0B policy summarization app")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        write_output(args.output, summary)
    except SkillError as exc:
        print(f"{exc.error_code}: {exc.message}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:  # Defensive fallback
        print(f"UNEXPECTED_ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
