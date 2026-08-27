"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REQUIRED_UC0B_CLAUSES = {
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
}


@dataclass
class Clause:
    id: str
    text: str
    binding_terms: list[str]


def _extract_binding_terms(text: str) -> list[str]:
    terms = []
    patterns = [
        r"\bmust\b",
        r"\brequires?\b",
        r"\bwill\b",
        r"\bmay\b",
        r"\bcannot\b",
        r"\bnot permitted\b",
        r"\bforfeited\b",
    ]
    lowered = text.lower()
    for pattern in patterns:
        if re.search(pattern, lowered):
            terms.append(pattern.replace("\\b", ""))
    return terms


def retrieve_policy(input_path: Path) -> list[Clause]:
    if input_path.suffix.lower() != ".txt":
        raise ValueError("Input must be a .txt policy file")

    try:
        raw = input_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Unable to read input file: {exc}") from exc

    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*\S)?\s*$")
    section_re = re.compile(r"^\d+\.\s+\S")
    lines = raw.splitlines()

    clauses: list[Clause] = []
    current_id: str | None = None
    current_parts: list[str] = []

    def flush_current() -> None:
        nonlocal current_id, current_parts
        if current_id is None:
            return
        text = " ".join(part.strip() for part in current_parts if part.strip())
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            raise ValueError(f"Clause {current_id} has no text")
        clauses.append(Clause(id=current_id, text=text, binding_terms=_extract_binding_terms(text)))
        current_id = None
        current_parts = []

    for line in lines:
        line = line.rstrip("\n")
        match = clause_re.match(line)
        if match:
            flush_current()
            current_id = match.group(1)
            clause_head = match.group(2) or ""
            current_parts = [clause_head]
            continue

        if current_id is None:
            continue

        stripped = line.strip()
        if not stripped:
            continue
        # Keep wrapped lines that belong to the active numbered clause.
        if stripped.startswith("═"):
            continue
        if section_re.match(stripped):
            continue
        current_parts.append(stripped)

    flush_current()

    if not clauses:
        raise ValueError("No parseable numbered clauses found")

    parsed_ids = {clause.id for clause in clauses}
    missing_required = sorted(REQUIRED_UC0B_CLAUSES - parsed_ids)
    if missing_required:
        raise ValueError(
            "Missing required UC-0B clauses in source or parser output: "
            + ", ".join(missing_required)
        )

    return clauses


def summarize_policy(clauses: list[Clause]) -> list[str]:
    if not clauses:
        raise ValueError("No clauses available for summary")

    lines = [f"[{clause.id}] {clause.text}" for clause in clauses]

    summary_ids = {clause.id for clause in clauses}
    if len(summary_ids) != len(clauses):
        raise ValueError("Duplicate clause ids detected; refusing to produce ambiguous summary")

    return lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UC-0B policy summarization with clause fidelity checks")
    parser.add_argument("--input", required=True, help="Path to policy input .txt file")
    parser.add_argument("--output", required=True, help="Path to summary output text file")
    return parser.parse_args()

def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    try:
        clauses = retrieve_policy(input_path)
        summary_lines = summarize_policy(clauses)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(summary_lines)} clause summaries to {output_path}")

if __name__ == "__main__":
    main()
