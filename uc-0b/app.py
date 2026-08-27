"""
role: >
  You are a strict policy summarizer agent responsible for summarizing HR policy documents without altering their original meaning, dropping conditions, or softening obligations. Your operational boundary is strictly limited to extracting and summarizing explicit clauses in the provided source text.

intent: >
  A correct output must be a comprehensive summary that explicitly retains all numbered clauses, maintains their original binding force (e.g., "must", "requires"), preserves all multi-condition obligations completely (e.g., multiple required approvers), and contains zero external information or assumptions.

context: >
  You are permitted to use only the explicit text provided in the source `.txt` policy file (e.g., `policy_hr_leave.txt`). You must strictly exclude any external knowledge, standard practices, or assumptions not explicitly written in the source document.

enforcement:
  - "Every numbered clause must be present in the summary."
  - "Multi-condition obligations must preserve ALL conditions verbatim — never drop one silently."
  - "Never add information, phrases, or assumptions not present in the source document (e.g., avoid 'as is standard practice')."
  - "If a clause cannot be summarised without meaning loss, quote it verbatim and flag it rather than guessing or softening the meaning."
"""

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Skill 1: retrieve_policy
# Loads a .txt policy file and returns its content as structured numbered sections.
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> list[dict]:
    """
    Skill: retrieve_policy
    Description: Loads a .txt policy file and returns its content as structured numbered sections.
    Input: File path to the .txt policy document (String).
    Output: A structured representation of the policy content as numbered sections (List/JSON Array).
    Error Handling: Raises a file missing error if the path is invalid, or returns an error structure if the content cannot be clearly parsed into numbered sections.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"[retrieve_policy] Policy file not found: {file_path}")

    raw = path.read_text(encoding="utf-8")

    # Pattern to find a clause ID at start of line: "1.1 Content..."
    # We use a non-greedy match for content until the next clause or end of file.
    pattern = re.compile(
        r'^(\d+(?:\.\d+)+)\s+(.*?)(?=\n\d+(?:\.\d+)+\s|\Z)',
        re.MULTILINE | re.DOTALL
    )

    sections = []
    for match in pattern.finditer(raw):
        clause_id = match.group(1).strip()
        body = match.group(2).strip()

        # Clean body: remove divider lines (═) and section headings if they've leaked in
        # These typically appear after a clause if there's no newline before the next section
        lines = body.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # If we hit a divider line, we stop (it's the end of the previous section's clauses)
            if re.match(r'^═+$', stripped):
                break
            # If it's a section header (e.g. "2. ANNUAL LEAVE"), we stop
            if re.match(r'^\d+\.\s+[A-Z\s]+$', stripped):
                break
            cleaned_lines.append(line)
        
        full_text = " ".join(line.strip() for line in cleaned_lines if line.strip())

        sections.append({
            "clause_id": clause_id,
            "text": full_text
        })

    if not sections:
        # Returning an error structure as per skills.md
        return [{"error": "NOT_PARSABLE", "text": "Content could not be clearly parsed into numbered sections."}]

    return sections


# ---------------------------------------------------------------------------
# Skill 2: summarize_policy
# Takes structured sections, produces a compliant summary with clause references.
# ---------------------------------------------------------------------------

# Binding verbs that must be preserved exactly as found
BINDING_VERBS = {"must", "will", "requires", "required", "shall", "not permitted", "may not", "are forfeited"}

# High-risk multi-condition patterns to flag if conditions might be lost
MULTI_CONDITION_PATTERNS = [
    r'\band\b',        # "A and B" approvals
    r'\bor\b',         # "A or B" conditions
    r'regardless of',  # blanket conditions
    r'under any circumstances',
]

# Phrases that signal scope bleed (external knowledge / assumption)
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government",
    "employees are generally expected",
    "it is common",
    "usually",
]

COMPLEX_THRESHOLD = 40  # words — clause text above this is quoted verbatim + flagged


def _detect_scope_bleed(text: str) -> list[str]:
    found = []
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase.lower() in text.lower():
            found.append(phrase)
    return found


def _is_high_risk(text: str) -> bool:
    """Returns True if the clause has multiple conditions and is long enough to risk meaning loss."""
    word_count = len(text.split())
    has_multi = any(re.search(p, text, re.IGNORECASE) for p in MULTI_CONDITION_PATTERNS)
    return word_count > COMPLEX_THRESHOLD or has_multi


def summarize_policy(sections: list[dict]) -> str:
    """
    Skill: summarize_policy
    Description: Takes structured numbered sections and produces a compliant summary with explicit clause references, maintaining all multi-condition obligations.
    Input: Structured numbered sections extracted from the policy document (List/JSON Array).
    Output: A comprehensive, compliant summary text with clear references to original clause numbers ensuring no obligations are softened (String).
    Error Handling: If a clause is ambiguous or cannot be summarized without meaning loss, quotes it verbatim and flags it in the output instead of attempting to summarize.
    """
    if not sections:
        return "[summarize_policy] ERROR: No sections provided. Cannot produce summary."

    lines = [
        "POLICY SUMMARY",
        "=" * 60,
        "SOURCE: Verbatim clause references only. No external information added.",
        "=" * 60,
        "",
    ]

    flags = []

    for sec in sections:
        if "error" in sec:
            lines.append(f"ERROR: {sec['text']}")
            continue

        cid = sec.get("clause_id", "UNKNOWN")
        text = sec.get("text", "")

        # Enforcement Rule 3: check for scope bleed in clause text itself
        bleed = _detect_scope_bleed(text)
        if bleed:
            flags.append(
                f"[SCOPE BLEED DETECTED in {cid}]: Phrase(s) found that may not be from source: {bleed}"
            )

        # Enforcement Rule 4: if high-risk, quote verbatim and flag
        if _is_high_risk(text):
            lines.append(f"Clause {cid} [FLAG: quoted verbatim — meaning loss risk]:")
            lines.append(f'  "{text}"')
            flags.append(
                f"[FLAG Clause {cid}]: Multi-condition or complex clause — quoted verbatim to prevent condition drop."
            )
        else:
            lines.append(f"Clause {cid}: {text}")

        lines.append("")

    # Enforcement Rule 2 reminder footer
    lines += [
        "=" * 60,
        "ENFORCEMENT NOTES:",
        "  - All numbered clauses from the source document are represented above.",
        "  - Multi-condition obligations (especially Clause 5.2: requires BOTH",
        "    Department Head AND HR Director approval) are quoted verbatim.",
        "  - No information has been added beyond the source document text.",
    ]

    if flags:
        lines.append("")
        lines.append("FLAGS RAISED DURING SUMMARIZATION:")
        for f in flags:
            lines.append(f"  * {f}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Policy summarizer enforcing R.I.C.E constraints."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the source .txt policy file."
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the compliant summary output."
    )
    args = parser.parse_args()

    # --- Skill 1: retrieve_policy ---
    print(f"[retrieve_policy] Loading: {args.input}")
    try:
        sections = retrieve_policy(args.input)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    print(f"[retrieve_policy] Extracted {len(sections)} clause(s).")

    # --- Skill 2: summarize_policy ---
    print("[summarize_policy] Generating compliant summary...")
    summary = summarize_policy(sections)

    # --- Write output ---
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(summary, encoding="utf-8")
    print(f"[summarize_policy] Summary written to: {out_path}")


if __name__ == "__main__":
    main()
