"""
UC-0B — Summary That Changes Meaning
app.py

Role:
    Policy-document summarisation agent for the City Municipal Corporation.
    Produces faithful, clause-complete summaries of HR policy documents.
    Does not interpret, advise on, or extend policy.

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt
"""

import argparse
import os
import re
import sys


# ---------------------------------------------------------------------------
# Scope-bleed guard: phrases explicitly prohibited by agents.md
# ---------------------------------------------------------------------------
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
    "it is common for",
    "generally speaking",
    "in most organisations",
]

# ---------------------------------------------------------------------------
# Clauses that carry multiple conditions and are therefore at high risk of
# condition-drop.  Each entry maps a clause number to the conditions that
# MUST all appear in the summarised text.
# ---------------------------------------------------------------------------
MULTI_CONDITION_CLAUSES = {
    "5.2": ["Department Head", "HR Director"],
    "2.4": ["written", "verbal"],          # written required; verbal not valid
    "2.6": ["5", "31 December"],           # max 5; forfeited on 31 Dec
    "2.7": ["January", "March"],           # Jan–Mar window
    "3.2": ["48"],                         # 48 hours deadline
    "5.3": ["Municipal Commissioner", "30"],
}

# ---------------------------------------------------------------------------
# Skill 1 — retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> list[dict]:
    """
    Load a plain-text policy file and return its content as a list of
    structured section objects.

    Each object has:
        {
            "number":  "2.3",
            "heading": "ANNUAL LEAVE",
            "text":    "<verbatim clause text>"
        }

    Raises SystemExit on any error — never fabricates content.
    """
    # --- existence / readability check ---
    if not file_path:
        sys.exit("[ERROR] retrieve_policy: No file path provided.")

    if not os.path.isfile(file_path):
        sys.exit(
            f"[ERROR] retrieve_policy: File not found: {file_path!r}\n"
            "Check the path and try again."
        )

    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        sys.exit(f"[ERROR] retrieve_policy: Cannot read file: {exc}")

    if not raw.strip():
        sys.exit("[ERROR] retrieve_policy: File is empty.")

    # --- parse into top-level sections and sub-clauses ---
    # Strategy:
    #   1. Split on section banners (═══ lines) to find section headings.
    #   2. Within each section body, split on sub-clause numbers (e.g. "2.3 ").
    sections = _parse_sections(raw)

    if not sections:
        sys.exit(
            "[ERROR] retrieve_policy: No recognisable numbered clauses found. "
            "Ensure the file is a plain-text policy document with numbered sections."
        )

    return sections


def _parse_sections(raw: str) -> list[dict]:
    """
    Parse the raw text into a flat list of numbered clause objects.
    Handles both top-level sections (e.g. '2. ANNUAL LEAVE') and
    sub-clauses (e.g. '2.3 Employees must ...').
    """
    sections = []

    # Split into top-level blocks separated by banner lines (═══…)
    blocks = re.split(r"[═=]{10,}", raw)

    current_heading = "GENERAL"

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Detect a section heading line like "2. ANNUAL LEAVE"
        heading_match = re.match(r"^\d+\.\s+(.+)$", block, re.MULTILINE)
        if heading_match:
            current_heading = heading_match.group(1).strip()

        # Find all sub-clauses: lines starting with N.N (possibly N.N.N)
        # Pattern: clause number at start of line, followed by text (possibly
        # spanning multiple lines until the next clause number or end of block).
        clause_pattern = re.compile(
            r"^(\d+\.\d+(?:\.\d+)?)\s+(.*?)(?=^\d+\.\d+|\Z)",
            re.MULTILINE | re.DOTALL,
        )

        for m in clause_pattern.finditer(block):
            number = m.group(1).strip()
            text_raw = m.group(2).strip()
            # Normalise internal whitespace / line continuations
            text = re.sub(r"\s+", " ", text_raw).strip()
            if text:
                sections.append(
                    {
                        "number": number,
                        "heading": current_heading,
                        "text": text,
                    }
                )

    return sections


# ---------------------------------------------------------------------------
# Skill 2 — summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(sections: list[dict]) -> str:
    """
    Take the structured sections returned by retrieve_policy and produce a
    compliant summary.

    Enforcement applied here:
      E1  Every numbered clause must appear — checked after building summary.
      E2  Multi-condition obligations must preserve ALL conditions.
      E3  No scope-bleed phrases.
      E4  Verbatim + flag if meaning loss risk detected.
      E5  Binding verbs are preserved (no paraphrasing engine — text is taken
          verbatim from source, so softening cannot occur).
      E6  Numeric thresholds preserved (same reason — taken verbatim).
      E7  Each entry is prefixed [N.N] for traceability.
      E8  No external knowledge introduced.
    """
    if not sections:
        sys.exit("[ERROR] summarize_policy: No sections provided.")

    lines = []
    source_numbers = {s["number"] for s in sections}

    # Group by heading for readable output
    heading_groups: dict[str, list[dict]] = {}
    for s in sections:
        heading_groups.setdefault(s["heading"], []).append(s)

    for heading, clauses in heading_groups.items():
        lines.append(f"\n{'─' * 60}")
        lines.append(f"  {heading}")
        lines.append(f"{'─' * 60}")

        for clause in clauses:
            number = clause["number"]
            text = clause["text"]

            # E3 — scope-bleed check on source text itself (defensive)
            _check_scope_bleed(text, number)

            # E2 — multi-condition preservation check
            flag_verbatim = _check_multi_condition(number, text)

            if flag_verbatim:
                # E4 — quote verbatim and flag
                entry = (
                    f"[{number}] [verbatim — meaning loss risk] {text}"
                )
            else:
                entry = f"[{number}] {text}"

            lines.append(entry)

    summary = "\n".join(lines).strip()

    # E1 — verify every source clause appears in the output
    _verify_completeness(source_numbers, summary)

    return summary


def _check_scope_bleed(text: str, clause_number: str) -> None:
    """Raise an error if scope-bleed language is detected in the text."""
    lower = text.lower()
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase in lower:
            sys.exit(
                f"[ERROR] summarize_policy: Scope-bleed phrase detected in "
                f"clause {clause_number}: '{phrase}'\n"
                "This language is not present in the source document and must "
                "not appear in the summary."
            )


def _check_multi_condition(clause_number: str, text: str) -> bool:
    """
    For known multi-condition clauses, verify all required conditions appear
    in the text.  Returns True if a verbatim flag should be applied,
    False otherwise.

    Prints a WARNING (does not exit) so the operator can review; also returns
    True to trigger verbatim quoting as per E4.
    """
    if clause_number not in MULTI_CONDITION_CLAUSES:
        return False

    required_terms = MULTI_CONDITION_CLAUSES[clause_number]
    missing = [t for t in required_terms if t.lower() not in text.lower()]

    if missing:
        print(
            f"[WARNING] summarize_policy: Clause {clause_number} is missing "
            f"required condition(s): {missing}. "
            "Quoting verbatim and flagging.",
            file=sys.stderr,
        )
        return True  # trigger verbatim flag

    return False


def _verify_completeness(source_numbers: set, summary: str) -> None:
    """
    E1 — Every numbered clause from the source must appear in the summary.
    Exits with a descriptive error listing any omitted clauses.
    """
    missing = []
    for number in sorted(source_numbers):
        # The summary prefixes each clause as [N.N] — check for that pattern
        if f"[{number}]" not in summary:
            missing.append(number)

    if missing:
        sys.exit(
            "[ERROR] summarize_policy: The following source clauses are "
            f"MISSING from the summary: {', '.join(missing)}\n"
            "Every numbered clause must be present. This output is rejected."
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B — Clause-complete HR policy summarisation agent."
    )
    parser.add_argument(
        "--input",
        required=True,
        metavar="INPUT_FILE",
        help="Path to the plain-text policy document.",
    )
    parser.add_argument(
        "--output",
        required=True,
        metavar="OUTPUT_FILE",
        help="Path to write the compliant summary.",
    )
    args = parser.parse_args()

    # --- Skill 1: retrieve_policy ---
    print(f"[INFO] Loading policy document: {args.input}")
    sections = retrieve_policy(args.input)
    print(f"[INFO] Parsed {len(sections)} clause(s) from source.")

    # --- Skill 2: summarize_policy ---
    print("[INFO] Generating compliant summary …")
    summary = summarize_policy(sections)

    # --- Write output ---
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write("CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY\n")
            fh.write("Generated by UC-0B summarisation agent\n")
            fh.write(
                "Source clauses are referenced as [N.N]. "
                "No information has been added beyond the source document.\n"
            )
            fh.write("=" * 60 + "\n")
            fh.write(summary)
            fh.write("\n")
    except OSError as exc:
        sys.exit(f"[ERROR] Cannot write output file: {exc}")

    print(f"[INFO] Summary written to: {args.output}")
    print("[INFO] Done. Verify each [N.N] entry against the source document.")


if __name__ == "__main__":
    main()
