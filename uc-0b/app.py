"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from dataclasses import dataclass
from typing import List

OBLIGATION_TERMS = (
    "must",
    "will",
    "requires",
    "not permitted",
    "may",
    "forfeited",
)

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


@dataclass
class Clause:
    clause_id: str
    source_text: str
    obligation_terms: List[str]
    explicit_conditions: List[str]


def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_obligation_terms(text: str) -> List[str]:
    text_lc = text.lower()
    found = []
    for term in OBLIGATION_TERMS:
        if term in text_lc:
            found.append(term)
    return found


def _extract_explicit_conditions(text: str) -> List[str]:
    conditions = []
    text_norm = _normalize_spaces(text)

    # Capture explicit condition-like fragments that often get dropped in summaries.
    patterns = [
        r"at least [^.]+",
        r"before [^.]+",
        r"within [^.]+",
        r"regardless of [^.]+",
        r"only after [^.]+",
        r"maximum of [^.]+",
        r"above [^.]+",
        r"or they are forfeited",
        r"and the [^.]+",
        r"not valid",
        r"not sufficient",
        r"under any circumstances",
    ]

    text_lc = text_norm.lower()
    for pattern in patterns:
        for match in re.finditer(pattern, text_lc):
            conditions.append(text_norm[match.start():match.end()])

    return sorted(set(conditions))


def _read_policy_lines(input_path: str) -> List[str]:
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            return infile.readlines()
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Policy file not found: {input_path}") from exc
    except OSError as exc:
        raise OSError(f"Unable to read policy file: {input_path}") from exc


def _append_continuation_line(clause_lines: dict, current_clause: str, line: str) -> None:
    stripped = line.strip()
    if not stripped or stripped.startswith("═"):
        return
    clause_lines[current_clause].append(stripped)


def _collect_clause_lines(lines: List[str]) -> dict:
    clause_lines = {}
    current_clause = None

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        clause_match = re.match(r"^\s*(\d+\.\d+)\s+(.*)$", line)
        if clause_match:
            current_clause = clause_match.group(1)
            clause_lines[current_clause] = [clause_match.group(2).strip()]
            continue

        if current_clause is None:
            continue

        if re.match(r"^\d+\.\s", line.strip()):
            current_clause = None
            continue

        _append_continuation_line(clause_lines, current_clause, line)

    return clause_lines


def _build_structured_clauses(clause_lines: dict) -> List[Clause]:
    structured = []
    for clause_id in sorted(clause_lines.keys(), key=lambda cid: tuple(int(p) for p in cid.split("."))):
        source_text = _normalize_spaces(" ".join(clause_lines[clause_id]))
        structured.append(
            Clause(
                clause_id=clause_id,
                source_text=source_text,
                obligation_terms=_extract_obligation_terms(source_text),
                explicit_conditions=_extract_explicit_conditions(source_text),
            )
        )
    return structured


def retrieve_policy(input_path: str) -> List[Clause]:
    """Load policy text file and return structured numbered sections."""
    lines = _read_policy_lines(input_path)
    clause_lines = _collect_clause_lines(lines)
    structured = _build_structured_clauses(clause_lines)

    if not structured:
        raise ValueError("No numbered clauses could be parsed from policy document.")

    return structured


def _validate_required_clauses(clauses: List[Clause]) -> None:
    available = {clause.clause_id for clause in clauses}
    missing = [clause_id for clause_id in REQUIRED_CLAUSES if clause_id not in available]
    if missing:
        raise ValueError(f"Missing required clauses in input policy: {', '.join(missing)}")


def summarize_policy(clauses: List[Clause]) -> str:
    """Create clause-referenced summary while preserving obligations and conditions."""
    _validate_required_clauses(clauses)

    clause_map = {clause.clause_id: clause for clause in clauses}
    lines = []
    lines.append("Policy Summary (Clause-Referenced, Meaning-Preserving)")
    lines.append("")

    for clause in clauses:
        text = clause.source_text
        review_required = False

        # If source is too short/unclear to summarize safely, emit verbatim with review tag.
        if len(text) < 20:
            review_required = True

        # Keep wording close to source to avoid obligation softening or condition loss.
        entry = f"[{clause.clause_id}] {text}"
        if review_required:
            entry = f"{entry} REVIEW_REQUIRED"

        lines.append(entry)

    # Targeted enforcement checks for known high-risk clauses.
    c52 = clause_map["5.2"].source_text.lower()
    if "department head" not in c52 or "hr director" not in c52:
        raise ValueError("Clause 5.2 integrity check failed: both approvers are required.")

    c24 = clause_map["2.4"].source_text.lower()
    if "written approval" not in c24 or "verbal approval is not valid" not in c24:
        raise ValueError("Clause 2.4 integrity check failed: written approval and verbal invalidity must be present.")

    c72 = clause_map["7.2"].source_text.lower()
    if "not permitted under any circumstances" not in c72:
        raise ValueError("Clause 7.2 integrity check failed: strict prohibition wording is required.")

    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as outfile:
        outfile.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
