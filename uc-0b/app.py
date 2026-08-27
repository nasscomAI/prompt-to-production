"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
from pathlib import Path
import re
from typing import Dict, Iterable

REQUIRED_CLAUSES = (
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.7",
    "3.2",
    "3.4",
    "5.2",
    "5.3",
    "7.2",
)

SCOPE_BLEED_PHRASES = (
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
)


def retrieve_policy(input_path: str) -> Dict[str, Dict[str, str]]:
    """Load policy text and extract numbered clauses."""
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    raw_text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"(?m)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|\Z)",
        re.DOTALL,
    )

    sections: Dict[str, str] = {}
    for clause_id, clause_text in pattern.findall(raw_text):
        normalized = " ".join(clause_text.split())
        if normalized:
            sections[clause_id] = normalized

    if not sections:
        raise ValueError("No numbered clauses detected in input policy.")

    return {"raw_text": raw_text, "sections": sections}


def summarize_policy(sections: Dict[str, str], required_clause_ids: Iterable[str]) -> str:
    """Create clause-referenced summary with strict coverage and no scope bleed."""
    missing = [clause_id for clause_id in required_clause_ids if clause_id not in sections]
    if missing:
        raise ValueError(
            "MANUAL_REVIEW_REQUIRED: Missing required clauses: " + ", ".join(missing)
        )

    summary_lines = []
    for clause_id in required_clause_ids:
        # Preserve meaning by keeping clause text source-grounded.
        summary_lines.append(f"{clause_id}: {sections[clause_id]}")

    summary = "\n".join(summary_lines)
    lowered = summary.lower()
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase in lowered:
            raise ValueError(
                "MANUAL_REVIEW_REQUIRED: scope bleed phrase detected in summary."
            )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0B compliant policy summarizer")
    parser.add_argument("--input", required=True, help="Path to source policy .txt file")
    parser.add_argument("--output", required=True, help="Path for generated summary file")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy["sections"], REQUIRED_CLAUSES)
    Path(args.output).write_text(summary + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
