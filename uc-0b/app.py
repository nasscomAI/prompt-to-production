"""
UC-0B — Policy summary with mandatory clause preservation.
See README.md for run command.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

# Ground truth from uc-0b/README.md — all must appear in output with full conditions.
REQUIRED_CLAUSES = ("2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2")

CLAUSE_LINE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_policy(path: Path) -> str:
    """Load policy text (UTF-8)."""
    return path.read_text(encoding="utf-8")


def parse_numbered_clauses(text: str) -> dict[str, str]:
    """Split body into clause id -> full clause text (including continuations)."""
    lines = text.splitlines()
    current_id: str | None = None
    chunks: dict[str, list[str]] = {}

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("═"):
            continue
        # Skip ALL-CAPS section banners like "2. ANNUAL LEAVE" (not "2.3 ...")
        if re.match(r"^\d+\.\s+[A-Z]", stripped) and not re.match(r"^\d+\.\d+", stripped):
            continue
        m = CLAUSE_LINE.match(stripped)
        if m:
            current_id = m.group(1)
            chunks.setdefault(current_id, []).append(stripped)
        elif current_id:
            chunks[current_id].append(stripped)

    return {k: " ".join(v) for k, v in chunks.items()}


def summarize_policy(clauses: dict[str, str]) -> str:
    """Build executive summary plus verbatim preserved clauses."""
    missing = [c for c in REQUIRED_CLAUSES if c not in clauses]
    if missing:
        raise ValueError(f"Missing required clauses in source: {missing}")

    intro = """EXECUTIVE SUMMARY — EMPLOYEE LEAVE POLICY (HR-POL-001, v2.3)

This summary highlights annual leave mechanics, sick-leave documentation rules,
Leave Without Pay (LWP) approval chains, and encashment limits. The numbered
clauses listed below are quoted verbatim from the source so that multi-party
approvals, deadlines, and prohibitions are not softened or dropped.

"""
    preserved = ["PRESERVED POLICY CLAUSES (VERBATIM)\n", "—" * 60 + "\n"]
    for cid in REQUIRED_CLAUSES:
        preserved.append(f"{clauses[cid]}\n\n")

    closing = """NOTES FOR READERS
- Clause 5.2 requires approval from BOTH the Department Head and the HR Director;
  manager approval alone is explicitly insufficient.
- Clause 7.2 prohibits leave encashment during service under any circumstances.

End of summary.
"""
    return intro + "".join(preserved) + closing


def main() -> None:
    p = argparse.ArgumentParser(description="Summarize HR leave policy with clause preservation.")
    p.add_argument("--input", required=True, type=Path, help="Path to policy_hr_leave.txt")
    p.add_argument("--output", required=True, type=Path, help="Output summary path")
    args = p.parse_args()

    raw = retrieve_policy(args.input)
    clauses = parse_numbered_clauses(raw)
    out = summarize_policy(clauses)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(out, encoding="utf-8")


if __name__ == "__main__":
    main()
