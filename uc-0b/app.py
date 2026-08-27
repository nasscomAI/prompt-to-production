"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import json
import re
from pathlib import Path


CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADING_RE = re.compile(r"^\d+\.\s+.+$")
CRITICAL_INVENTORY = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def _normalize_space(text: str) -> str:
    return " ".join(text.split())


def _extract_constraints(raw_text: str) -> dict:
    """
    Extract constraint-like signals from source wording.
    These are copied as exact snippets where possible to preserve fidelity.
    """
    text = _normalize_space(raw_text)
    lower = text.lower()

    keywords = [
        "must",
        "requires",
        "will",
        "shall",
        "not permitted",
        "only",
        "within",
        "at least",
        "maximum",
        "exceeding",
        "regardless",
        "forfeited",
        "cannot",
    ]
    obligation_terms = [k for k in keywords if k in lower]

    actor_hits = []
    for actor in [
        "employee",
        "employees",
        "direct manager",
        "manager",
        "department head",
        "hr director",
        "municipal commissioner",
        "hr department",
    ]:
        if actor in lower:
            actor_hits.append(actor)

    return {
        "obligation_terms": obligation_terms,
        "actors": actor_hits,
    }


def retrieve_policy(input_path: str) -> list[dict]:
    """
    Load a .txt policy file and return numbered sections with source-faithful text.
    """
    path = Path(input_path)
    if not path.exists() or not path.is_file():
        raise ValueError(f"Input file not found: {input_path}")

    try:
        raw_lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError(f"Input file is not valid UTF-8: {input_path}") from exc

    clauses = []
    current_id = None
    current_lines = []

    for line in raw_lines:
        stripped = line.strip()

        if not stripped:
            continue

        # Skip visual separators and section headings like "2. ANNUAL LEAVE".
        if stripped.startswith("═") or SECTION_HEADING_RE.match(stripped):
            continue

        match = CLAUSE_RE.match(stripped)
        if match:
            if current_id is not None:
                clause_text = _normalize_space(" ".join(current_lines))
                clauses.append(
                    {
                        "clause_id": current_id,
                        "raw_text": clause_text,
                        "constraints": _extract_constraints(clause_text),
                    }
                )
            current_id = match.group(1)
            current_lines = [match.group(2)]
            continue

        if current_id is not None:
            current_lines.append(stripped)

    if current_id is not None:
        clause_text = _normalize_space(" ".join(current_lines))
        clauses.append(
            {
                "clause_id": current_id,
                "raw_text": clause_text,
                "constraints": _extract_constraints(clause_text),
            }
        )

    if not clauses:
        raise ValueError("No numbered clauses found in source policy.")

    return clauses


def _requires_verbatim(raw_text: str) -> bool:
    """
    Conservative heuristic: quote clauses that are likely to lose meaning if compressed.
    """
    lower = raw_text.lower()
    risk_markers = [
        " and ",
        " or ",
        "regardless",
        "not ",
        "must",
        "requires",
        "only",
        "within",
        "at least",
        "maximum",
        "exceeding",
        "cannot",
        "forfeited",
        "approval",
    ]
    return any(marker in lower for marker in risk_markers)


def _validate_inventory(clauses: list[dict]) -> tuple[list[str], list[str]]:
    present_ids = {str(c.get("clause_id", "")).strip() for c in clauses}
    present = [cid for cid in CRITICAL_INVENTORY if cid in present_ids]
    missing = [cid for cid in CRITICAL_INVENTORY if cid not in present_ids]
    return present, missing


def _append_coverage_checklist(lines: list[str], present: list[str], missing: list[str]):
    lines.append("")
    lines.append("Critical Clause Coverage Checklist")
    for cid in CRITICAL_INVENTORY:
        status = "present" if cid in present else "missing"
        lines.append(f"- Clause {cid}: {status}")
    if missing:
        lines.append(
            f"- Inventory validation error: missing critical clauses {', '.join(missing)}"
        )


def summarize_policy(clauses: list[dict]) -> str:
    """
    Create a clause-referenced summary with full coverage and meaning-preserving fallback.
    """
    if not clauses:
        raise ValueError("No clauses provided for summarization.")

    present, missing = _validate_inventory(clauses)
    if missing:
        raise ValueError(
            f"Source policy is missing required critical clauses: {', '.join(missing)}"
        )

    lines = []
    lines.append("Policy Summary (Clause-Referenced)")
    lines.append("")

    for clause in clauses:
        clause_id = clause.get("clause_id", "")
        raw_text = clause.get("raw_text", "").strip()
        if not clause_id or not raw_text:
            raise ValueError("Invalid clause structure: missing clause_id or raw_text.")

        # To avoid silent condition drops, high-risk clauses are quoted verbatim.
        if _requires_verbatim(raw_text):
            lines.append(
                f"Clause {clause_id}: \"{raw_text}\" [verbatim to prevent meaning loss]"
            )
        else:
            lines.append(f"Clause {clause_id}: {raw_text}")

    _append_coverage_checklist(lines, present, missing)

    return "\n".join(lines) + "\n"


def write_output(output_path: str, summary_text: str):
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(summary_text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    parser.add_argument(
        "--emit-structured",
        action="store_true",
        help="Also emit structured clause extraction next to output as .json",
    )
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    write_output(args.output, summary)

    if args.emit_structured:
        structured_path = str(Path(args.output).with_suffix(".json"))
        Path(structured_path).write_text(
            json.dumps(clauses, indent=2, ensure_ascii=True), encoding="utf-8"
        )

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
