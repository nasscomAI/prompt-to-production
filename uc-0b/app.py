"""
UC-0B app.py — Rule-bound HR leave policy summarizer.

Implements skills.md using agents.md enforcement:
  retrieve_policy  -> parse .txt into {clause: verbatim text}
  summarize_policy -> emit one tagged block per target clause,
                      preserving all conditions + binding verbs.
"""
import argparse
import re
import sys
from pathlib import Path

TARGET_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
]

VERBATIM_FLAG = "[VERBATIM \u2014 summarisation would lose meaning]"


def retrieve_policy(input_path: str) -> dict:
    """Load policy .txt, return {clause_number: verbatim clause text}."""
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Policy file not found: {input_path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"Policy file is empty: {input_path}")

    clauses: dict = {}
    current = None
    buf: list = []
    clause_re = re.compile(r"^(\d+\.\d+)\b(.*)$")
    section_re = re.compile(r"^\d+\.\s+[A-Z]")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or set(line) <= {"\u2550", "=", "-", "_"}:
            continue
        if section_re.match(line) and not clause_re.match(line):
            # New top-level section header: flush current clause.
            if current is not None:
                clauses[current] = re.sub(r"\s+", " ", " ".join(buf)).strip()
                current = None
                buf = []
            continue
        m = clause_re.match(line)
        if m:
            if current is not None:
                clauses[current] = re.sub(r"\s+", " ", " ".join(buf)).strip()
            current = m.group(1)
            rest = m.group(2).strip()
            buf = [rest] if rest else []
        elif current is not None and line:
            buf.append(line)
    if current is not None:
        clauses[current] = re.sub(r"\s+", " ", " ".join(buf)).strip()
    return clauses


def summarize_policy(clauses: dict) -> str:
    """Build compliant tagged summary; verbatim fallback on missing clauses."""
    lines = [
        "Summary of Employee Leave Policy HR-POL-001 v2.3",
        "",
    ]
    for tag in TARGET_CLAUSES:
        text = clauses.get(tag, "").strip()
        if not text:
            lines.append(
                f"[{tag}] Source clause not found in input file. "
                f"{VERBATIM_FLAG}"
            )
        else:
            lines.append(f"[{tag}] {text}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Summarize HR leave policy per agents.md enforcement."
    )
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to summary_hr_leave.txt")
    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    summary = summarize_policy(clauses)

    out = Path(args.output)
    if out.parent and str(out.parent) not in ("", "."):
        out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(summary, encoding="utf-8")
    print(f"Wrote {out} ({len(TARGET_CLAUSES)} clauses)")


if __name__ == "__main__":
    main()
