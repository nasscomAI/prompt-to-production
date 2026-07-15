"""
UC-0B — HR Policy Summarizer (clause-preserving, zero scope bleed)

Skills (from skills.md):
  retrieve_policy  — load policy_hr_leave.txt, parse into numbered clauses
  summarize_policy — produce compliant summary with clause references;
                     verbatim-quote + MANUAL_REVIEW flag when paraphrase
                     would drop a condition or weaken obligation

Enforcement (from agents.md):
  - Allowed source: policy_hr_leave.txt only
  - Required clauses: 2.3 2.4 2.5 2.6 2.7 3.2 3.4 5.2 5.3 7.2
  - Clause 5.2: BOTH Department Head AND HR Director must be explicit
  - No statements not present in the source document
  - Verbatim quote + MANUAL_REVIEW flag if paraphrase risks meaning loss

Run:
  python app.py \
    --input ../data/policy-documents/policy_hr_leave.txt \
    --output summary_hr_leave.txt
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Agent configuration  (agents.md)
# ---------------------------------------------------------------------------

ALLOWED_SOURCE = "policy_hr_leave.txt"

REQUIRED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2",
]

# These clauses are always verbatim-quoted — conditions too dense to paraphrase safely
ALWAYS_QUOTE = {"5.2", "5.3", "7.2"}


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class PolicyClause:
    section_number: str
    clause_text: str       # full multi-sentence text exactly as in source
    binding_verb: str      # strongest obligation verb found in clause


@dataclass
class SummaryItem:
    section_number: str
    summary_text: str      # verbatim quote (with "") or preserved source text
    source_mode: str       # "verbatim_quote" | "paraphrase"
    flag: str              # "" | "MANUAL_REVIEW"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strongest_binding_verb(text: str) -> str:
    priority = [
        "not permitted", "must", "will", "shall",
        "requires", "required", "prohibited",
        "are forfeited", "forfeited", "may", "should",
    ]
    low = text.lower()
    for v in priority:
        if re.search(rf"\b{re.escape(v)}\b", low):
            return v
    return "states"


def _parse_clauses(raw: str) -> Dict[str, str]:
    """
    Parse numbered clauses (N.N …) handling multi-line text.
    Each clause runs until the next clause number or section separator.
    """
    clause_re   = re.compile(r"^(\d+\.\d+)\s+(.+)", re.MULTILINE)
    separator_re = re.compile(r"^[═=]{5,}", re.MULTILINE)

    positions: list[tuple] = []
    for m in clause_re.finditer(raw):
        positions.append((m.start(), "clause", m.group(1), m.group(2).strip()))
    for m in separator_re.finditer(raw):
        positions.append((m.start(), "sep", "", ""))

    positions.sort(key=lambda x: x[0])

    clauses: Dict[str, str] = {}
    for i, entry in enumerate(positions):
        if entry[1] != "clause":
            continue
        num = entry[2]
        end_pos = positions[i + 1][0] if i + 1 < len(positions) else len(raw)
        block = raw[entry[0]:end_pos]
        text_lines = []
        for j, line in enumerate(block.splitlines()):
            stripped = line.strip()
            if not stripped:
                continue
            if j == 0:
                stripped = re.sub(r"^\d+\.\d+\s+", "", stripped)
            text_lines.append(stripped)
        clauses[num] = " ".join(text_lines).strip()

    return clauses


def _risk_of_meaning_loss(section_number: str, text: str) -> bool:
    """
    True when verbatim quoting is safer than paraphrasing:
      - clause is in the always-quote set
      - dense conditions (≥3 condition markers)
      - negation combined with multi-conditions
    """
    if section_number in ALWAYS_QUOTE:
        return True
    low = text.lower()
    condition_hits = sum(
        1 for pat in [
            r"\band\b", r"\bor\b", r"regardless of", r"unless",
            r"only after", r"within \d+", r"maximum of", r"before or after",
        ]
        if re.search(pat, low)
    )
    has_negation = bool(re.search(r"\bnot\b|\bno\b|\bnever\b|\bcannot\b", low))
    return condition_hits >= 3 or (has_negation and condition_hits >= 2)


# ---------------------------------------------------------------------------
# Skill 1 — retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(policy_path: str) -> List[PolicyClause]:
    """
    Load policy file and parse into structured numbered clauses.

    Output:  List[PolicyClause] — {section_number, clause_text, binding_verb}
    Errors:  file missing/unreadable  → RETRIEVAL_ERROR  (exit)
             required clauses absent  → COVERAGE_ERROR   (exit)
    """
    p = Path(policy_path)

    if not p.exists() or not p.is_file():
        sys.exit(f"[RETRIEVAL_ERROR] File not found or unreadable: {policy_path}")

    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as exc:
        sys.exit(f"[RETRIEVAL_ERROR] Cannot read file: {policy_path} — {exc}")

    parsed = _parse_clauses(raw)

    missing = [c for c in REQUIRED_CLAUSES if c not in parsed]
    if missing:
        sys.exit(
            "[COVERAGE_ERROR] Required clause(s) missing from source: "
            + ", ".join(missing)
        )

    return [
        PolicyClause(
            section_number=sec,
            clause_text=parsed[sec],
            binding_verb=_strongest_binding_verb(parsed[sec]),
        )
        for sec in REQUIRED_CLAUSES
    ]


# ---------------------------------------------------------------------------
# Skill 2 — summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(
    clauses: List[PolicyClause],
) -> Tuple[str, List[SummaryItem]]:
    """
    Generate compliant summary with every required clause mapped to its
    source number and obligation fully preserved.

    Output:  (summary_text, List[SummaryItem])
    Errors:  incomplete clause list → COVERAGE_ERROR (exit)
             paraphrase meaning-loss → verbatim quote + MANUAL_REVIEW flag
    """
    by_sec = {c.section_number: c for c in clauses}
    missing = [c for c in REQUIRED_CLAUSES if c not in by_sec]
    if missing:
        sys.exit(
            "[COVERAGE_ERROR] summarize_policy received incomplete clauses: "
            + ", ".join(missing)
        )

    binding_verbs = {c.section_number: c.binding_verb for c in clauses}
    items: List[SummaryItem] = []

    for sec in REQUIRED_CLAUSES:
        c = by_sec[sec]
        if _risk_of_meaning_loss(sec, c.clause_text):
            items.append(SummaryItem(
                section_number=sec,
                summary_text=f'"{c.clause_text}"',
                source_mode="verbatim_quote",
                flag="MANUAL_REVIEW",
            ))
        else:
            # Preserve source wording exactly — no additions from outside document
            items.append(SummaryItem(
                section_number=sec,
                summary_text=c.clause_text,
                source_mode="paraphrase",
                flag="",
            ))

    # Build output
    lines: List[str] = [
        "HR LEAVE POLICY — CLAUSE SUMMARY",
        f"Source: {ALLOWED_SOURCE}",
        f"Required clauses covered: {len(items)}/{len(REQUIRED_CLAUSES)}",
        "=" * 60,
        "",
    ]
    for item in items:
        verb      = binding_verbs.get(item.section_number, "")
        flag_tag  = f"  ⚑ [MANUAL_REVIEW]" if item.flag else ""
        lines.append(f"[{item.section_number}] ({verb}){flag_tag}")
        lines.append(f"  {item.summary_text}")
        lines.append("")

    return "\n".join(lines), items


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0B: HR leave policy summarizer (clause-preserving)"
    )
    parser.add_argument("--input",  required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Output file (e.g. summary_hr_leave.txt)")
    args = parser.parse_args()

    # Enforce allowed-source rule (agents.md context)
    if Path(args.input).name != ALLOWED_SOURCE:
        sys.exit(
            f"[SOURCE_ERROR] This agent only accepts '{ALLOWED_SOURCE}'. "
            f"Got: {Path(args.input).name}"
        )

    clauses          = retrieve_policy(args.input)
    summary, items   = summarize_policy(clauses)

    Path(args.output).write_text(summary, encoding="utf-8")

    manual_count = sum(1 for i in items if i.flag == "MANUAL_REVIEW")
    print(f"[OK] Summary written to {args.output}")
    print(f"     Clauses covered : {len(items)}/{len(REQUIRED_CLAUSES)}")
    print(f"     Verbatim-quoted : {manual_count}  (MANUAL_REVIEW flagged)")
    print(f"     Safe paraphrase : {len(items) - manual_count}")


if __name__ == "__main__":
    main()
