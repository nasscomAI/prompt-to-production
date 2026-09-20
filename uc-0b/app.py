"""
UC-0B — Summary That Changes Meaning
Implements retrieve_policy and summarize_policy per agents.md and skills.md.
"""
import argparse
import re
import sys
from pathlib import Path

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_TITLE_RE = re.compile(r"^\d+\.\s+[A-Z]")
CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
FORBIDDEN_BLEED = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
]


def retrieve_policy(input_path: str):
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"REFUSED: input file not found: {input_path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    clauses = []
    current_id = None
    current_parts = []

    def flush():
        if current_id is None:
            return
        text = " ".join(part.strip() for part in current_parts if part.strip())
        text = re.sub(r"\s+", " ", text).strip()
        clauses.append({"clause_id": current_id, "text": text})

    for line in lines:
        stripped = line.strip()
        match = CLAUSE_RE.match(stripped)
        if match:
            flush()
            current_id = match.group(1)
            current_parts = [match.group(2)]
        elif current_id is not None and stripped and not stripped.startswith("═") and not SECTION_TITLE_RE.match(stripped):
            current_parts.append(stripped)
    flush()

    if not clauses:
        raise ValueError("REFUSED: no numbered clauses found. Will not invent policy text.")
    return clauses


def _must_quote(clause_id: str, text: str) -> bool:
    if clause_id == "5.2":
        return True
    if clause_id in CRITICAL_CLAUSES and (" and " in text.lower() or "regardless" in text.lower()):
        return True
    return False


def summarize_policy(clauses, output_path: str):
    present = {item["clause_id"] for item in clauses}
    missing = [cid for cid in CRITICAL_CLAUSES if cid not in present]
    if missing:
        raise ValueError(
            "REFUSED: critical clauses missing from source parse: " + ", ".join(missing)
        )

    lines = [
        "HR Leave Policy summary — every numbered clause retained.",
        "Source: policy_hr_leave.txt only. No external practice added.",
        "",
    ]
    for item in clauses:
        clause_id = item["clause_id"]
        text = item["text"]
        if _must_quote(clause_id, text):
            entry = f"Clause {clause_id} [VERBATIM]: {text}"
        else:
            entry = f"Clause {clause_id}: {text}"
        lowered = entry.lower()
        for phrase in FORBIDDEN_BLEED:
            if phrase in lowered:
                raise ValueError(f"REFUSED: scope bleed phrase detected: {phrase}")
        lines.append(entry)

    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return lines


def main():
    parser = argparse.ArgumentParser(description="UC-0B policy summariser")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to summary_hr_leave.txt")
    args = parser.parse_args()
    try:
        clauses = retrieve_policy(args.input)
        summarize_policy(clauses, args.output)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
