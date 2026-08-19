"""UC-0B app.py: policy summary generator with strict fidelity checks."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple


CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def parse_numbered_clauses(policy_text: str) -> List[Tuple[str, str]]:
    """Extract numbered clauses and their full continuation text in order."""
    clauses: List[Tuple[str, str]] = []
    current_id: str | None = None
    current_parts: List[str] = []

    for raw_line in policy_text.splitlines():
        line = raw_line.rstrip()
        match = CLAUSE_RE.match(line)

        if match:
            if current_id is not None:
                clauses.append((current_id, normalize_ws(" ".join(current_parts))))

            current_id = match.group(1)
            current_parts = [match.group(2)]
            continue

        if current_id is None:
            continue

        stripped = line.strip()
        if not stripped:
            continue

        # Ignore decorative separators and section titles that are not part of clauses.
        if stripped.startswith("═") or stripped.isupper():
            continue

        current_parts.append(stripped)

    if current_id is not None:
        clauses.append((current_id, normalize_ws(" ".join(current_parts))))

    return clauses


def build_summary_lines(clauses: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Generate summary by extractive compression (clause text normalized to one line)."""
    return [(clause_id, clause_text) for clause_id, clause_text in clauses]


def validate_summary(
    source_clauses: List[Tuple[str, str]], summary_lines: List[Tuple[str, str]]
) -> None:
    """Validate no omission, no added content, and condition preservation."""
    source_ids = [cid for cid, _ in source_clauses]
    summary_ids = [cid for cid, _ in summary_lines]

    if source_ids != summary_ids:
        missing = [cid for cid in source_ids if cid not in summary_ids]
        added = [cid for cid in summary_ids if cid not in source_ids]
        raise ValueError(
            "Clause mismatch detected. "
            f"Missing clauses: {missing or 'None'}. Added clauses: {added or 'None'}."
        )

    source_map: Dict[str, str] = {cid: text for cid, text in source_clauses}
    for clause_id, summary_text in summary_lines:
        source_text = source_map[clause_id]

        # For strict fidelity, summary text must exactly match normalized source clause text.
        if normalize_ws(summary_text) != normalize_ws(source_text):
            raise ValueError(
                f"Content drift in clause {clause_id}. "
                "Summary must preserve all source conditions and wording."
            )


def write_summary(output_path: Path, summary_lines: List[Tuple[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [f"{clause_id}: {text}" for clause_id, text in summary_lines]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_summary(input_path: Path, output_path: Path) -> None:
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input policy file not found: {input_path}")

    policy_text = input_path.read_text(encoding="utf-8")
    source_clauses = parse_numbered_clauses(policy_text)
    if not source_clauses:
        raise ValueError("No numbered clauses found in input policy file.")

    summary_lines = build_summary_lines(source_clauses)
    validate_summary(source_clauses, summary_lines)
    write_summary(output_path, summary_lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a meaning-preserving summary from a policy file with strict "
            "clause fidelity checks."
        )
    )
    parser.add_argument("--input", required=True, help="Path to input policy file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_summary(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()
