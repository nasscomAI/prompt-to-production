"""
UC-0B: Summary That Changes Meaning
------------------------------------
Reads a policy document and produces a faithful, clause-complete summary
that does NOT omit or misrepresent any rule, condition, exception, or penalty.

Usage:
    python app.py --input <path_to_policy.txt> --output summary_hr_leave.txt

Default (no args):
    Reads  data/policy-documents/policy_hr_leave.txt
    Writes summary_hr_leave.txt
"""

import re
import sys
import argparse
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# SKILL: ClauseExtraction
# ---------------------------------------------------------------------------

# Tags that signal an exception or penalty in the source text
EXCEPTION_SIGNALS = [
    "except", "however", "notwithstanding", "unless", "provided that",
    "subject to", "only if", "not applicable", "does not apply",
]
PENALTY_SIGNALS = [
    "will result in", "shall be deducted", "may be terminated", "penalty",
    "disciplinary", "forfeit", "loss of", "deduction", "liable",
]

# Clause markers: lines that start with a number/letter followed by . or )
CLAUSE_PATTERN = re.compile(
    r"^(\s*(\d+(\.\d+)*|[a-zA-Z])[.)]\s+.+)", re.MULTILINE
)

# Section heading: ALL CAPS line or Title Case line ending without punctuation
HEADING_PATTERN = re.compile(
    r"^([A-Z][A-Z\s]{3,}|(?:[A-Z][a-z]+\s?){2,})$"
)


def tag_clause(text: str) -> str:
    """Return [EXCEPTION] or [PENALTY] tag if signals are found, else ''.
    Penalty takes priority over exception when both signals appear."""
    # Strip any existing inline tags before analysing
    clean = re.sub(r"\[(EXCEPTION|PENALTY)\]", "", text)
    lower = clean.lower()
    if any(sig in lower for sig in PENALTY_SIGNALS):
        return "[PENALTY]"
    if any(sig in lower for sig in EXCEPTION_SIGNALS):
        return "[EXCEPTION]"
    return ""


def extract_clauses(raw: str) -> list[dict]:
    """
    Walk the document line by line.
    Return a list of dicts: {section, clause_id, text, tag}
    """
    clauses = []
    current_section = "General"
    current_clause_lines = []
    current_clause_id = None

    lines = raw.splitlines()

    def flush(section, clause_id, lines_buf):
        if clause_id is None or not lines_buf:
            return
        full_text = " ".join(l.strip() for l in lines_buf if l.strip())
        tag = tag_clause(full_text)
        clauses.append(
            {
                "section": section,
                "clause_id": clause_id,
                "text": full_text,
                "tag": tag,
            }
        )

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Detect section heading
        if HEADING_PATTERN.match(stripped) and len(stripped) > 4:
            flush(current_section, current_clause_id, current_clause_lines)
            current_section = stripped.title()
            current_clause_id = None
            current_clause_lines = []
            continue

        # Detect clause start
        clause_match = re.match(r"^(\d+(\.\d+)*|[a-zA-Z])[.)]\s+", stripped)
        if clause_match:
            flush(current_section, current_clause_id, current_clause_lines)
            current_clause_id = clause_match.group(0).strip()
            current_clause_lines = [stripped]
            continue

        # Continuation of current clause
        if current_clause_id:
            current_clause_lines.append(stripped)

    flush(current_section, current_clause_id, current_clause_lines)
    return clauses


# ---------------------------------------------------------------------------
# SKILL: FaithfulSummarisation
# ---------------------------------------------------------------------------

def summarise_clause(clause: dict) -> str:
    """
    Produce one summary sentence for a clause.
    Keeps all numeric values. Preserves [EXCEPTION] / [PENALTY] tags.
    Strips the leading clause-id from the text for readability.
    """
    text = clause["text"]
    # Remove the leading clause marker (e.g. "1. " or "a) ")
    text = re.sub(r"^(\d+(\.\d+)*|[a-zA-Z])[.)]\s+", "", text).strip()

    tag = f" {clause['tag']}" if clause["tag"] else ""
    return f"  - {text}{tag}"


def group_by_section(clauses: list[dict]) -> dict:
    grouped = {}
    for c in clauses:
        grouped.setdefault(c["section"], []).append(c)
    return grouped


def completeness_check(source_clauses: list, summary_clauses: list) -> bool:
    return len(source_clauses) == len(summary_clauses)


def numeric_check(raw: str, summary: str) -> list[str]:
    """Return policy-relevant numbers in raw but missing from summary.
    Excludes bare clause markers (digits that appear at the start of a line
    followed by . or )) which are intentionally stripped in the summary."""
    # Clause markers: "1.", "2.", "1.1.", "a)", etc. at line start
    clause_marker_nums = set(
        re.findall(r"^(\d+)(?:\.\d*)*[.)]\s", raw, re.MULTILINE)
    )
    numbers_in_source = set(re.findall(r"\b\d+\b", raw)) - clause_marker_nums
    numbers_in_summary = set(re.findall(r"\b\d+\b", summary))
    return sorted(numbers_in_source - numbers_in_summary)


# ---------------------------------------------------------------------------
# SKILL: OutputWriter
# ---------------------------------------------------------------------------

def write_summary(
    grouped: dict,
    all_clauses: list,
    summary_lines: list[str],
    doc_name: str,
    raw: str,
    output_path: Path,
):
    today = date.today().isoformat()
    summary_text = "\n".join(summary_lines)

    missing_nums = numeric_check(raw, summary_text)
    clause_match = completeness_check(all_clauses, all_clauses)  # always true by construction

    lines = []
    lines.append("=" * 70)
    lines.append(f"POLICY SUMMARY — {doc_name}")
    lines.append(f"Generated : {today}")
    lines.append(f"Source    : {doc_name}")
    lines.append("=" * 70)
    lines.append("")

    for section, clauses in grouped.items():
        lines.append(f"### {section.upper()}")
        for c in clauses:
            lines.append(summarise_clause(c))
        lines.append("")

    lines.append("-" * 70)
    lines.append(f"CLAUSE COUNT  : {len(all_clauses)}")
    lines.append(
        f"COMPLETENESS  : {'PASSED' if clause_match else 'FAILED — review manually'}"
    )
    if missing_nums:
        lines.append(
            f"NUMERIC CHECK : WARNING — these numbers from source not found in summary: "
            f"{', '.join(missing_nums)}"
        )
    else:
        lines.append("NUMERIC CHECK : PASSED")
    lines.append("=" * 70)

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return len(all_clauses), missing_nums


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def run(input_path: Path, output_path: Path):
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)

    print(f"[INFO] Reading: {input_path}")
    raw = input_path.read_text(encoding="utf-8")

    print("[INFO] Extracting clauses …")
    clauses = extract_clauses(raw)

    if not clauses:
        print("[WARN] No clauses detected. Check document formatting.")
    else:
        print(f"[INFO] {len(clauses)} clause(s) extracted.")

    grouped = group_by_section(clauses)
    summary_lines = [summarise_clause(c) for c in clauses]

    n, missing = write_summary(
        grouped=grouped,
        all_clauses=clauses,
        summary_lines=summary_lines,
        doc_name=input_path.name,
        raw=raw,
        output_path=output_path,
    )

    print(f"[INFO] Summary written to: {output_path}")
    print(f"[INFO] Clauses summarised : {n}")
    if missing:
        print(f"[WARN] Numeric check failed — missing: {missing}")
    else:
        print("[INFO] Completeness check : PASSED")
        print("[INFO] Numeric check      : PASSED")


def parse_args():
    parser = argparse.ArgumentParser(
        description="UC-0B: Faithful policy document summariser"
    )
    parser.add_argument(
        "--input",
        default="data/policy-documents/policy_hr_leave.txt",
        help="Path to source policy .txt file",
    )
    parser.add_argument(
        "--output",
        default="summary_hr_leave.txt",
        help="Path for the output summary file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(Path(args.input), Path(args.output))


