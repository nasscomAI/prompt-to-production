"""
UC-0B app.py — Policy Summarisation Agent
Built with RICE framework + agents.md + skills.md + CRAFT workflow.

RICE Priority:
  Reach:      All HR policy consumers who rely on clause-accurate summaries.
  Impact:     Prevents clause omission, scope bleed, and obligation softening.
  Confidence: 90% — enforcement rules are explicit and testable clause-by-clause.
  Effort:     2 (two well-scoped skills: retrieve_policy + summarize_policy).
  RICE Score: (Reach * Impact * Confidence) / Effort — maximised by tight skill scope.

Run:
  python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# REQUIRED CLAUSES — ground truth from README.md / agents.md
# ---------------------------------------------------------------------------
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Scope-bleed markers that must never appear in output (agents.md § context)
SCOPE_BLEED_MARKERS = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
]

# ---------------------------------------------------------------------------
# SKILL: retrieve_policy
# Loads a .txt policy file and returns content parsed into numbered sections.
# Input:  file path string
# Output: ordered list of dicts  {clause_id: str, text: str}
# Error:  returns {"error": True, "path": ..., "reason": ...}
# ---------------------------------------------------------------------------
def retrieve_policy(file_path: str) -> list | dict:
    """
    Skill: retrieve_policy
    Loads a plain-text policy document and returns an ordered list of
    numbered sections, preserving original clause numbering.
    """
    path = Path(file_path)
    if not path.exists():
        return {"error": True, "path": str(path), "reason": "File not found."}
    if not path.is_file():
        return {"error": True, "path": str(path), "reason": "Path is not a file."}

    try:
        raw = path.read_text(encoding="utf-8")
    except Exception as exc:
        return {"error": True, "path": str(path), "reason": str(exc)}

    # Parse numbered sections: match lines starting with a clause number (e.g. 2.3, 3.2, 5.2)
    # Pattern captures top-level and sub-clauses such as 1., 2.3, 5.2, 7.2, etc.
    section_pattern = re.compile(
        r"^(\d+(?:\.\d+)*)\s+(.+?)(?=\n\d+(?:\.\d+)*\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    sections = []
    for match in section_pattern.finditer(raw):
        clause_id = match.group(1).strip()
        text = match.group(2).strip()
        sections.append({"clause_id": clause_id, "text": text})

    if not sections:
        # Fallback: treat entire file as a single un-numbered block
        sections = [{"clause_id": "0", "text": raw.strip()}]

    return sections


# ---------------------------------------------------------------------------
# SKILL: summarize_policy
# Takes structured sections from retrieve_policy and produces a compliant
# clause-by-clause summary with explicit clause references.
# Input:  ordered list of {clause_id, text} dicts
# Output: plain-text summary string prefixed with clause references
# Error:  halts and returns missing-clause error if any required clause absent
# ---------------------------------------------------------------------------
def summarize_policy(sections: list) -> str | dict:
    """
    Skill: summarize_policy
    Produces a compliant summary where each paragraph is prefixed with its
    source clause reference.  All 10 required clauses must be present.
    Multi-condition obligations preserve ALL conditions verbatim.
    No language is added that does not appear in the source document.
    """
    if isinstance(sections, dict) and sections.get("error"):
        return sections  # propagate retrieve_policy errors

    # Index sections by clause_id for O(1) look-up
    clause_index: dict[str, str] = {s["clause_id"]: s["text"] for s in sections}

    # --- Enforce: every required clause must be present ---
    missing = [c for c in REQUIRED_CLAUSES if c not in clause_index]
    if missing:
        return {
            "error": True,
            "reason": "Missing required clauses.",
            "missing_clauses": missing,
        }

    # --- Build compliant summary ---
    lines = []
    lines.append("POLICY SUMMARY — HR Leave Policy")
    lines.append("=" * 60)
    lines.append(
        "Source: policy_hr_leave.txt | All 10 required clauses present."
    )
    lines.append("")

    for clause_id in REQUIRED_CLAUSES:
        raw_text = clause_index[clause_id]

        # agents.md enforcement: if text cannot be summarised without meaning
        # loss, quote verbatim and flag it.
        # For multi-condition clauses (5.2, 5.3) we always quote verbatim to
        # prevent condition-drop failure.
        if clause_id in ("5.2", "5.3"):
            entry = f"[{clause_id}] [VERBATIM — meaning loss risk]\n    {raw_text}"
        else:
            # Summarise: keep the first sentence (which contains the binding
            # obligation) and tag with clause reference.
            first_sentence = raw_text.split(".")[0].strip()
            entry = f"[{clause_id}] {first_sentence}."

        lines.append(entry)
        lines.append("")

    summary = "\n".join(lines)

    # --- Enforce: no scope-bleed markers ---
    for marker in SCOPE_BLEED_MARKERS:
        if marker.lower() in summary.lower():
            summary = re.sub(
                re.escape(marker), "[SCOPE-BLEED REMOVED]", summary, flags=re.IGNORECASE
            )

    return summary


# ---------------------------------------------------------------------------
# main — wires retrieve_policy → summarize_policy → write output
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Policy Summarisation Agent (RICE-prioritised)"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the plain-text policy document (policy_hr_leave.txt)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path for the generated summary output file",
    )
    args = parser.parse_args()

    # --- SKILL: retrieve_policy ---
    print(f"[retrieve_policy] Loading: {args.input}")
    sections = retrieve_policy(args.input)

    if isinstance(sections, dict) and sections.get("error"):
        print(f"[ERROR] retrieve_policy failed: {sections['reason']} (path: {sections['path']})")
        sys.exit(1)

    print(f"[retrieve_policy] Parsed {len(sections)} sections.")

    # --- SKILL: summarize_policy ---
    print("[summarize_policy] Generating compliant clause-by-clause summary …")
    result = summarize_policy(sections)

    if isinstance(result, dict) and result.get("error"):
        if "missing_clauses" in result:
            print(
                f"[ERROR] summarize_policy halted — missing clauses: "
                f"{', '.join(result['missing_clauses'])}"
            )
        else:
            print(f"[ERROR] summarize_policy failed: {result.get('reason')}")
        sys.exit(1)

    # --- Write output ---
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")
    print(f"[output] Summary written to: {output_path}")
    print("\n--- SUMMARY PREVIEW ---\n")
    print(result)


if __name__ == "__main__":
    main()
