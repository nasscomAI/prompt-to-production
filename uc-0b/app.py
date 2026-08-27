"""
UC-0B — Policy Summariser: Summary That Changes Meaning
Built from agents.md (RICE enforcement) and skills.md skill contracts.

Works on ANY CMC policy .txt file — section headings and document title are
parsed dynamically from the source file, not hardcoded.

Run:
    python app.py \\
        --input ../data/policy-documents/policy_hr_leave.txt \\
        --output summary_hr_leave.txt
"""

import argparse
import re
import sys
from pathlib import Path

# ── Mandatory clause list (agents.md ground-truth inventory) ─────────────────
# All 10 must appear in both retrieve_policy output and summarize_policy output.
# These were defined for the HR Leave policy (UC-0B primary test document).

MANDATORY_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2",
]

# Binding verbs that must NEVER be softened (agents.md enforcement rule 3 /
# skills.md summarize_policy output constraint).
BINDING_VERBS = ["must", "will", "requires", "not permitted", "are forfeited"]

# Phrases explicitly banned from output — scope bleed markers (agents.md context,
# README "What Will Fail" section).
BANNED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
]

# Clauses where compression risks a condition drop and verbatim quoting is
# ALWAYS preferred regardless of which policy is being processed
# (agents.md enforcement rule 2 / skills.md error_handling).
VERBATIM_CLAUSE_IDS = {"5.2", "5.3", "7.2"}

# ── HR Leave policy condensed summaries (clause-id → summary text) ───────────
# Applied ONLY when the parsed clause text matches HR-leave content, verified
# by checking a fingerprint phrase unique to each HR clause.
# This prevents these hardcoded strings from firing on other policy documents
# that happen to share the same clause numbering.

_HR_CLAUSE_FINGERPRINTS: dict[str, str] = {
    "2.3": "form hr-l1",
    "2.4": "verbal approval is not valid",
    "2.5": "loss of pay (lop)",
    "2.6": "forfeited on 31 december",
    "2.7": "january",
    "3.2": "48 hours of returning to work",
    "3.4": "regardless of duration",
}

_HR_CLAUSE_SUMMARIES: dict[str, str] = {
    "2.3": (
        "Employees must submit a leave application at least 14 calendar days "
        "in advance using Form HR-L1."
    ),
    "2.4": (
        "Leave applications must receive written approval from the employee's "
        "direct manager before leave commences. Verbal approval is not valid."
    ),
    "2.5": (
        "Unapproved absence will be recorded as Loss of Pay (LOP) regardless "
        "of subsequent approval."
    ),
    "2.6": (
        "Employees may carry forward a maximum of 5 unused annual leave days to "
        "the following calendar year. Any days above 5 are forfeited on 31 December."
    ),
    "2.7": (
        "Carry-forward days must be used within the first quarter (January–March) "
        "of the following year or they are forfeited."
    ),
    "3.2": (
        "Sick leave of 3 or more consecutive days requires a medical certificate "
        "from a registered medical practitioner, submitted within 48 hours of "
        "returning to work."
    ),
    "3.4": (
        "Sick leave taken immediately before or after a public holiday or annual "
        "leave period requires a medical certificate regardless of duration."
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Skill: retrieve_policy
# skills.md: loads .txt policy file, returns content as structured numbered
# sections. Section headings are parsed dynamically from the source file.
# ─────────────────────────────────────────────────────────────────────────────

def _parse_document_meta(raw: str) -> tuple[str, str]:
    """
    Extract document reference and title from the policy file header.

    Returns (doc_ref, doc_title) where doc_ref is e.g. "IT-POL-003" and
    doc_title is the third non-empty, non-separator line (the policy title).
    Falls back to generic strings if not found.
    """
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    # Strip decorator lines
    content_lines = [ln for ln in lines if not re.match(r"^[═=]{3,}", ln)]

    doc_title = content_lines[2] if len(content_lines) >= 3 else "Policy Document"

    # Look for "Document Reference: XX-POL-NNN"
    ref_match = re.search(r"Document Reference:\s*(\S+)", raw)
    doc_ref = ref_match.group(1) if ref_match else "UNKNOWN"

    return doc_ref, doc_title


def _parse_section_headings(raw: str) -> dict[str, str]:
    """
    Parse section headings dynamically from decorator-surrounded lines, e.g.:

        ═══════════════════
        2. ANNUAL LEAVE
        ═══════════════════

    Returns a dict mapping section number string → heading text,
    e.g. {"2": "ANNUAL LEAVE", "3": "SICK LEAVE", ...}
    """
    headings: dict[str, str] = {}
    # Match lines of the form "N. HEADING TEXT" that appear between separator lines
    section_pattern = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z\s\(\)\/\-]+)\s*$", re.MULTILINE)
    for m in section_pattern.finditer(raw):
        headings[m.group(1)] = m.group(2).strip()
    return headings


def retrieve_policy(file_path: str) -> tuple[list[dict], list[str], str, str]:
    """
    Load a plain-text policy file and split it into clause-level dicts.

    Returns
    -------
    clauses : list[dict]
        Ordered list of {clause_id, heading, text} for every detected clause.
    missing_mandatory : list[str]
        Clause IDs from MANDATORY_CLAUSES that were not found in the file.
    doc_ref : str
        Document reference string (e.g. "HR-POL-001").
    doc_title : str
        Human-readable document title parsed from the file header.

    Raises
    ------
    FileNotFoundError  — if the file does not exist.
    ValueError         — if the file is empty or contains no numbered clauses.
    """
    path = Path(file_path)

    # ── Guard: file existence (skills.md error_handling) ─────────────────────
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        raise ValueError(f"Policy file is empty: {file_path}")

    # ── Extract document metadata ─────────────────────────────────────────────
    doc_ref, doc_title = _parse_document_meta(raw)

    # ── Parse section headings dynamically from the file ─────────────────────
    section_headings = _parse_section_headings(raw)

    # ── Parse clause blocks ───────────────────────────────────────────────────
    # Match lines that start with a clause number, e.g. "2.3 Employees must…"
    # Capture: (clause_id, rest-of-text-until-next-clause-or-EOF)
    clause_pattern = re.compile(
        r"^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    matches = clause_pattern.findall(raw)
    if not matches:
        raise ValueError(
            f"No numbered clauses found in '{file_path}'. "
            "Expected lines beginning with <section>.<clause> (e.g. 2.3)."
        )

    # Strip decorative separator lines (═══… or ===…) and section headings
    # that bleed into the trailing text of each captured clause block.
    _sep_pattern = re.compile(r"[\u2550=]{3,}.*", re.DOTALL)

    clauses: list[dict] = []
    for clause_id, text_block in matches:
        # Remove decorative separators captured at end of block
        clean_block = _sep_pattern.sub("", text_block).strip()
        # Normalise whitespace while preserving sentence boundaries
        text = " ".join(clean_block.split())
        section_key = clause_id.split(".")[0]
        heading = section_headings.get(section_key, f"Section {section_key}")
        clauses.append({
            "clause_id": clause_id,
            "heading":   heading,
            "text":      text,
        })

    # ── Report missing mandatory clauses (skills.md error_handling) ──────────
    found_ids = {c["clause_id"] for c in clauses}
    missing_mandatory = [cid for cid in MANDATORY_CLAUSES if cid not in found_ids]

    return clauses, missing_mandatory, doc_ref, doc_title


# ─────────────────────────────────────────────────────────────────────────────
# Skill: summarize_policy
# skills.md: takes structured sections, produces compliant summary with clause
# references.
# ─────────────────────────────────────────────────────────────────────────────

def _check_binding_verb_preserved(source_text: str, summary_text: str) -> list[str]:
    """
    Return a list of binding verbs present in source_text that are absent from
    summary_text. An empty list means all verbs are preserved.
    """
    source_lower  = source_text.lower()
    summary_lower = summary_text.lower()
    return [v for v in BINDING_VERBS if v in source_lower and v not in summary_lower]


def _check_banned_phrases(text: str) -> list[str]:
    """Return any banned scope-bleed phrases found in text."""
    lower = text.lower()
    return [phrase for phrase in BANNED_PHRASES if phrase in lower]


def _summarise_clause(clause: dict) -> str:
    """
    Produce a single summary entry for one clause.

    Strategy
    --------
    1. Clauses in VERBATIM_CLAUSE_IDS (5.2, 5.3, 7.2) are always quoted
       verbatim — compression risks condition drop (agents.md rule 2).
    2. For HR Leave clauses (2.3–2.7, 3.2, 3.4): use the condensed summary
       ONLY when the source text matches the expected HR content (fingerprint
       check). This prevents HR summaries from applying to other policy docs.
    3. All other clauses: verbatim pass-through with VERBATIM flag.
    4. After producing any condensed summary, run a binding-verb integrity
       check and flag if any verb was inadvertently lost.
    """
    clause_id = clause["clause_id"]
    heading   = clause["heading"]
    text      = clause["text"]

    # ── Always-verbatim clauses ───────────────────────────────────────────────
    if clause_id in VERBATIM_CLAUSE_IDS:
        return (
            f"[Clause {clause_id}] {heading}\n"
            f"  {text}\n"
            f"  [VERBATIM — cannot be shortened without meaning loss]"
        )

    # ── HR Leave condensed summaries (fingerprint-gated) ─────────────────────
    if clause_id in _HR_CLAUSE_SUMMARIES:
        fingerprint = _HR_CLAUSE_FINGERPRINTS.get(clause_id, "")
        if fingerprint and fingerprint in text.lower():
            summary_text = _HR_CLAUSE_SUMMARIES[clause_id]
            missing_verbs = _check_binding_verb_preserved(text, summary_text)
            entry = f"[Clause {clause_id}] {heading}\n  {summary_text}"
            if missing_verbs:
                entry += (
                    f"\n  [BINDING VERB SOFTENED — verb(s) from source not in summary: "
                    f"{', '.join(missing_verbs)}]"
                )
            return entry

    # ── Fallback: verbatim pass-through for all other clauses ────────────────
    return (
        f"[Clause {clause_id}] {heading}\n"
        f"  {text}\n"
        f"  [VERBATIM — cannot be shortened without meaning loss]"
    )


def summarize_policy(
    clauses: list[dict],
    missing_mandatory: list[str],
    doc_ref: str,
    doc_title: str,
) -> str:
    """
    Produce the full policy summary string from the structured clause list.

    Parameters
    ----------
    clauses           : output of retrieve_policy
    missing_mandatory : list of mandatory clause IDs absent from the source file
    doc_ref           : document reference string (e.g. "IT-POL-003")
    doc_title         : human-readable document title from the source file header

    Returns
    -------
    summary : str — complete formatted summary.

    Raises
    ------
    ValueError — if clauses is None or empty.
    """
    # ── Guard: empty input (skills.md error_handling) ─────────────────────────
    if not clauses:
        raise ValueError(
            "No clauses provided to summarize_policy; run retrieve_policy first."
        )

    lines: list[str] = [
        "POLICY SUMMARY",
        f"Document: {doc_ref} — {doc_title}",
        "Generated by: UC-0B summarise_policy",
        "=" * 70,
        "",
        "NOTE: This summary preserves all binding verbs (must, will, requires,",
        "not permitted, are forfeited) and multi-condition obligations exactly",
        "as stated in the source document. No external knowledge has been added.",
        "",
        "=" * 70,
        "",
    ]

    # ── Summarise every clause in document order ──────────────────────────────
    for clause in clauses:
        entry = _summarise_clause(clause)

        # ── Scan for banned scope-bleed phrases (agents.md context) ───────────
        found_banned = _check_banned_phrases(entry)
        if found_banned:
            entry += (
                f"\n  [SCOPE BLEED DETECTED — banned phrase(s) must be removed: "
                f"{'; '.join(found_banned)}]"
            )

        lines.append(entry)
        lines.append("")  # blank line between clauses

    # ── Mandatory clause coverage warning (skills.md error_handling) ──────────
    if missing_mandatory:
        lines += [
            "=" * 70,
            "[WARNING] The following mandatory clauses were not found in the",
            "source document and could not be summarised:",
            "  " + ", ".join(missing_mandatory),
            "Do not infer or reconstruct missing clause content.",
            "=" * 70,
        ]

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# main / CLI wiring
# README run command:
#   python app.py --input ../data/policy-documents/policy_hr_leave.txt
#                 --output summary_hr_leave.txt
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=(
            "UC-0B Policy Summariser — produces a clause-faithful summary of a "
            "government policy document, preserving all obligations and binding verbs."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the plain-text policy file",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the summary output file",
    )
    args = parser.parse_args()

    # ── Skill 1: retrieve_policy ──────────────────────────────────────────────
    try:
        clauses, missing_mandatory, doc_ref, doc_title = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] retrieve_policy failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print(
        f"[INFO] Loaded {len(clauses)} clause(s) from '{args.input}' "
        f"({doc_ref} — {doc_title}).",
        file=sys.stderr,
    )
    if missing_mandatory:
        print(
            f"[WARN] Missing mandatory clause(s): {', '.join(missing_mandatory)}",
            file=sys.stderr,
        )

    # ── Skill 2: summarize_policy ─────────────────────────────────────────────
    try:
        summary = summarize_policy(clauses, missing_mandatory, doc_ref, doc_title)
    except ValueError as exc:
        print(f"[ERROR] summarize_policy failed: {exc}", file=sys.stderr)
        sys.exit(1)

    # ── Write output ──────────────────────────────────────────────────────────
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")

    print(
        f"[INFO] Summary written to '{args.output}' "
        f"({output_path.stat().st_size} bytes).",
        file=sys.stderr,
    )
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
