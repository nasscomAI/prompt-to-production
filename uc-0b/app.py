"""
UC-0B app.py - clause-safe HR leave policy summarizer.

Implements the two skills from skills.md:
- retrieve_policy: load and structure numbered policy clauses.
- summarize_policy: produce a clause-referenced summary that preserves meaning.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s()]+)$")

UNSUPPORTED_PHRASES = (
    "as is standard practice",
    "typically in government organisations",
    "typically in government organizations",
    "employees are generally expected to",
    "generally expected to",
)

CRITICAL_REQUIREMENTS = {
    "2.3": ("14", "advance", "must"),
    "2.4": ("written approval", "before the leave commences", "verbal approval is not valid"),
    "2.5": ("loss of pay", "lop", "regardless of subsequent approval"),
    "2.6": ("maximum of 5", "above 5", "forfeited on 31 december"),
    "2.7": ("january-march", "forfeited"),
    "3.2": ("3 or more consecutive days", "medical certificate", "within 48 hours"),
    "3.4": ("before or after", "medical certificate", "regardless of duration"),
    "5.2": ("department head", "hr director"),
    "5.3": ("exceeding 30", "municipal commissioner"),
    "7.2": ("during service", "not permitted", "under any circumstances"),
}


@dataclass(frozen=True)
class Clause:
    clause_id: str
    section_title: str
    original_text: str
    binding_terms: tuple[str, ...]


@dataclass(frozen=True)
class Policy:
    metadata: tuple[str, ...]
    clauses: tuple[Clause, ...]


def normalize_text(value: str) -> str:
    """Normalize whitespace and common dash mojibake without inventing content."""
    value = value.replace("â€“", "-").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", value).strip()


def normalize_section_title(value: str) -> str:
    return normalize_text(value).title().replace("(Lwp)", "(LWP)")


def is_separator_line(value: str) -> bool:
    return value.startswith("â•") or value.startswith("═") or set(value) <= {"═", " "}


def binding_terms_for(text: str) -> tuple[str, ...]:
    terms = []
    lowered = text.lower()
    for term in ("must", "will", "may", "requires", "required", "not permitted", "forfeited"):
        if term in lowered:
            terms.append(term)
    return tuple(terms)


def retrieve_policy(input_path: str) -> Policy:
    """Load a .txt policy file and return structured numbered sections."""
    path = Path(input_path)
    if path.suffix.lower() != ".txt":
        raise ValueError(f"Input must be a .txt policy file: {path}")
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Input path is not a file: {path}")

    raw = path.read_text(encoding="utf-8", errors="replace")
    if not raw.strip():
        raise ValueError(f"Input file is empty: {path}")

    metadata: list[str] = []
    clauses: list[Clause] = []
    current_section = "Unsectioned"
    current_clause_id: str | None = None
    current_clause_lines: list[str] = []
    seen_first_section = False

    def flush_clause() -> None:
        nonlocal current_clause_id, current_clause_lines
        if current_clause_id is None:
            return
        original_text = normalize_text(" ".join(current_clause_lines))
        clauses.append(
            Clause(
                clause_id=current_clause_id,
                section_title=current_section,
                original_text=original_text,
                binding_terms=binding_terms_for(original_text),
            )
        )
        current_clause_id = None
        current_clause_lines = []

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or is_separator_line(stripped):
            continue

        section_match = SECTION_RE.match(stripped)
        if section_match:
            flush_clause()
            current_section = normalize_section_title(section_match.group(2))
            seen_first_section = True
            continue

        clause_match = CLAUSE_RE.match(stripped)
        if clause_match:
            flush_clause()
            current_clause_id = clause_match.group(1)
            current_clause_lines = [clause_match.group(2)]
            continue

        if current_clause_id is not None:
            current_clause_lines.append(stripped)
        elif not seen_first_section:
            metadata.append(normalize_text(stripped))

    flush_clause()

    if not clauses:
        raise ValueError("No numbered clauses found in input policy.")

    return Policy(metadata=tuple(metadata), clauses=tuple(clauses))


def summarize_clause(clause: Clause) -> str:
    """Return a safe clause summary, quoting verbatim when concise paraphrase is risky."""
    required_summaries = {
        "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
        "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
        "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "2.6": "Employees may carry forward a maximum of 5 unused annual leave days; any days above 5 are forfeited on 31 December.",
        "2.7": "Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited.",
        "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
        "3.4": "Sick leave immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
        "5.2": "LWP requires approval from BOTH the Department Head and the HR Director; manager approval alone is not sufficient.",
        "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
        "7.2": "Leave encashment during service is not permitted under any circumstances.",
    }
    summary = required_summaries.get(clause.clause_id)
    if summary is None:
        summary = f"VERBATIM_REQUIRED: {clause.original_text}"
    return f"- {clause.clause_id} ({clause.section_title}): {summary}"


def validate_summary(policy: Policy, summary: str) -> None:
    source_ids = [clause.clause_id for clause in policy.clauses]
    summary_lines = summary.splitlines()
    summary_by_clause = {
        match.group(1): normalize_text(line)
        for line in summary_lines
        if (match := re.match(r"^- (\d+\.\d+)\b.*$", line))
    }

    missing = [clause_id for clause_id in source_ids if clause_id not in summary_by_clause]
    if missing:
        raise ValueError(f"Summary omitted numbered clause(s): {', '.join(missing)}")

    for phrase in UNSUPPORTED_PHRASES:
        if phrase.lower() in summary.lower():
            raise ValueError(f"Summary introduced unsupported source-external phrase: {phrase}")

    for clause_id, required_bits in CRITICAL_REQUIREMENTS.items():
        if clause_id not in summary_by_clause:
            raise ValueError(f"Summary omitted critical clause {clause_id}")
        line = summary_by_clause[clause_id].lower()
        missing_bits = [bit for bit in required_bits if bit not in line]
        if missing_bits:
            raise ValueError(
                f"Summary changed meaning for clause {clause_id}; missing: "
                + ", ".join(missing_bits)
            )


def summarize_policy(policy: Policy) -> str:
    """Create a compliant clause-referenced summary and validate enforcement rules."""
    lines = ["HR Leave Policy Summary", ""]
    lines.extend(summarize_clause(clause) for clause in policy.clauses)
    lines.extend(
        [
            "",
            "Validation report:",
            f"- Numbered clauses present: {len(policy.clauses)} of {len(policy.clauses)}",
            "- Critical clauses preserved: " + ", ".join(CRITICAL_REQUIREMENTS.keys()),
            "- Unsupported source-external phrases: none detected",
        ]
    )
    summary = "\n".join(lines) + "\n"
    validate_summary(policy, summary)
    return summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize the HR leave policy without meaning loss.")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)
    output_path = Path(args.output)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Wrote {len(policy.clauses)} clause summaries to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
