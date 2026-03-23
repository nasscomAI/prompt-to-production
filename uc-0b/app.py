"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

REQUIRED_CLAUSE_IDS = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def _normalize_clause_text(text: str) -> str:
    return " ".join((text or "").split())


def retrieve_policy(policy_path: str) -> dict:
    """
    Load a policy text file and parse numbered clauses into structured data.
    """
    try:
        with open(policy_path, "r", encoding="utf-8") as infile:
            full_text = infile.read()
    except OSError as exc:
        raise RuntimeError(f"Failed to read input policy file '{policy_path}': {exc}") from exc

    clause_pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
    clauses = []
    current_id = None
    current_lines = []

    for raw_line in full_text.splitlines():
        line = raw_line.rstrip()
        match = clause_pattern.match(line)
        if match:
            if current_id is not None:
                clauses.append(
                    {
                        "clause_id": current_id,
                        "clause_text": _normalize_clause_text(" ".join(current_lines)),
                    }
                )
            current_id = match.group(1)
            current_lines = [match.group(2).strip()]
            continue

        if current_id is None:
            continue

        stripped = line.strip()
        if not stripped:
            continue
        if set(stripped) == {"═"}:
            continue
        if re.match(r"^\d+\.\s+", stripped):
            continue
        if not re.search(r"[A-Za-z0-9]", stripped):
            continue
        current_lines.append(stripped)

    if current_id is not None:
        clauses.append(
            {
                "clause_id": current_id,
                "clause_text": _normalize_clause_text(" ".join(current_lines)),
            }
        )

    clauses_by_id = {clause["clause_id"]: clause["clause_text"] for clause in clauses}
    missing_required_clauses = [cid for cid in REQUIRED_CLAUSE_IDS if cid not in clauses_by_id]
    parse_warning = ""
    if not clauses:
        parse_warning = "No numbered clauses were parsed from the input text."

    return {
        "source_path": policy_path,
        "full_text": full_text,
        "clauses": clauses,
        "clauses_by_id": clauses_by_id,
        "missing_required_clauses": missing_required_clauses,
        "parse_warning": parse_warning,
    }


def summarize_policy(structured_policy: dict) -> str:
    """
    Produce a clause-referenced compliance summary for required UC-0B clauses.
    """
    clauses_by_id = structured_policy.get("clauses_by_id", {})
    missing = structured_policy.get("missing_required_clauses", [])
    parse_warning = structured_policy.get("parse_warning", "")

    output_lines = [
        "UC-0B Policy Summary (Clause-Referenced)",
        "",
    ]

    if parse_warning:
        output_lines.append(f"PARSE_WARNING: {parse_warning}")
        output_lines.append("")

    if missing:
        output_lines.append("COMPLETENESS_WARNING: Missing required clauses: " + ", ".join(missing))
        output_lines.append("")

    for clause_id in REQUIRED_CLAUSE_IDS:
        clause_text = clauses_by_id.get(clause_id)
        if not clause_text:
            output_lines.append(f"Clause {clause_id}: REVIEW_REQUIRED - Clause not found in source document.")
            continue

        # Keep obligations and conditions intact by using faithful clause text with reference.
        output_lines.append(f"Clause {clause_id}: {clause_text}")

    return "\n".join(output_lines) + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    structured_policy = retrieve_policy(args.input)
    summary_text = summarize_policy(structured_policy)

    try:
        with open(args.output, "w", encoding="utf-8") as outfile:
            outfile.write(summary_text)
    except OSError as exc:
        raise RuntimeError(f"Failed to write output summary file '{args.output}': {exc}") from exc

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
