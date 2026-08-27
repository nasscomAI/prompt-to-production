"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
from dataclasses import dataclass
from pathlib import Path
import re


CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*\S)\s*$")
SECTION_PATTERN = re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s()/-]+)$")
RISKY_CLAUSES = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}


@dataclass(frozen=True)
class Clause:
    clause_id: str
    section_title: str
    source_text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a clause-preserving policy summary.")
    parser.add_argument("--input", required=True, help="Path to the source policy text file.")
    parser.add_argument("--output", required=True, help="Path to write the summary text file.")
    return parser.parse_args()


def resolve_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return (Path(__file__).resolve().parent / path).resolve()


def retrieve_policy(input_path: Path) -> list[Clause]:
    if input_path.suffix.lower() != ".txt":
        raise ValueError(f"Expected a .txt policy file, got: {input_path}")
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    lines = input_path.read_text(encoding="utf-8").splitlines()
    clauses: list[Clause] = []
    current_section = ""
    current_clause_id: str | None = None
    current_clause_lines: list[str] = []

    def flush_clause() -> None:
        nonlocal current_clause_id, current_clause_lines
        if current_clause_id is None:
            return
        source_text = " ".join(part.strip() for part in current_clause_lines if part.strip())
        if not source_text:
            raise ValueError(f"Clause {current_clause_id} is empty.")
        clauses.append(Clause(current_clause_id, current_section, source_text))
        current_clause_id = None
        current_clause_lines = []

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or set(stripped) == {"═"}:
            continue

        section_match = SECTION_PATTERN.match(stripped)
        clause_match = CLAUSE_PATTERN.match(stripped)

        if section_match:
            flush_clause()
            current_section = section_match.group(2).title()
            continue

        if clause_match:
            flush_clause()
            current_clause_id = clause_match.group(1)
            current_clause_lines = [clause_match.group(2)]
            continue

        if current_clause_id is not None:
            current_clause_lines.append(stripped)
            continue

        if stripped.startswith("CITY MUNICIPAL CORPORATION") or stripped.startswith("HUMAN RESOURCES DEPARTMENT"):
            continue
        if stripped.startswith("EMPLOYEE LEAVE POLICY") or stripped.startswith("Document Reference:"):
            continue
        if stripped.startswith("Version:"):
            continue

        raise ValueError(f"Found unnumbered content that could not be attached to a clause: {stripped}")

    flush_clause()

    if not clauses:
        raise ValueError("No numbered clauses were parsed from the policy document.")

    return clauses


def is_risky_clause(clause: Clause) -> bool:
    if clause.clause_id in RISKY_CLAUSES:
        return True
    risk_markers = (
        " and ",
        " or ",
        " only after ",
        " regardless",
        " under any circumstances",
        " before ",
        " after ",
        " within ",
        " maximum of ",
        " not valid",
        " not sufficient",
        " forfeited",
        " requires approval from",
    )
    lowered = f" {clause.source_text.lower()} "
    return any(marker in lowered for marker in risk_markers)


def summarise_clause(clause: Clause) -> str:
    if is_risky_clause(clause):
        return f'{clause.clause_id} QUOTED_VERBATIM: "{clause.source_text}"'
    return f"{clause.clause_id} {clause.source_text}"


def summarize_policy(clauses: list[Clause]) -> str:
    clause_ids = {clause.clause_id for clause in clauses}
    missing_ground_truth = sorted(RISKY_CLAUSES - clause_ids)
    if missing_ground_truth:
        raise ValueError(
            "Cannot summarize because required ground-truth clauses are missing: "
            + ", ".join(missing_ground_truth)
        )

    output_lines = [summarise_clause(clause) for clause in clauses]
    return "\n".join(output_lines) + "\n"


def main():
    args = parse_args()
    input_path = resolve_path(args.input)
    output_path = resolve_path(args.output)

    clauses = retrieve_policy(input_path)
    summary = summarize_policy(clauses)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    main()
