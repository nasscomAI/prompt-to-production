#!/usr/bin/env python3
"""
app.py — UC-0B: HR Leave Policy Summarization Agent

Role (agents.md):
    Reads policy_hr_leave.txt, structures it into numbered clause
    sections (skill: retrieve_policy), and produces a compliant
    clause-referenced summary (skill: summarize_policy) written to the
    output file specified on the command line.

This script is intentionally conservative: every transformation is
verified against the source clause's binding-verb strength and
multi-condition terms before it is allowed into the output. If a
transformation cannot be verified, the clause is emitted verbatim and
flagged, per enforcement rule 4 in agents.md.
"""

import argparse
import os
import re
import sys


# ---------------------------------------------------------------------------
# Ground truth: clause inventory (from README + agents.md context)
# ---------------------------------------------------------------------------

# Enforcement rule 1: every one of these clauses must be present in the
# summary; no clause may be silently dropped.
REQUIRED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
]

# Enforcement rule 4 / obligation-softening guard: the binding-verb
# keyword(s) that MUST survive any compression for a given clause.
BINDING_VERBS = {
    "2.3": ["must"],
    "2.4": ["must"],
    "2.5": ["will"],
    "2.6": ["may", "forfeit"],
    "2.7": ["must", "forfeit"],
    "3.2": ["require"],
    "3.4": ["require"],
    "5.2": ["require"],
    "5.3": ["require"],
    "7.2": ["not permitted"],
}

# Enforcement rule 2: multi-condition obligations whose individual
# conditions must ALL survive any compression.
MULTI_CONDITION_TERMS = {
    "5.2": ["department head", "hr director"],
}

# Enforcement rule 3 / context: scope-bleed phrases that must never
# appear in the output because they are not present in the source.
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "typically in government organizations",
    "employees are generally expected to",
    "generally expected to",
    "standard practice",
    "common practice",
    "best practice",
]


# ---------------------------------------------------------------------------
# Clause-header parsing
# ---------------------------------------------------------------------------

# Matches a clean "X.Y" clause header (optionally prefixed with
# "Clause"/"Section" and followed by punctuation), e.g.:
#   "2.3 Advance Notice ..."
#   "Clause 2.4: Written approval ..."
#   "Section 5.2) LWP requires ..."
# The negative lookahead prevents matching the first two segments of a
# longer numbering scheme such as "2.3.1" or "2.34".
CLAUSE_HEADER_PATTERN = re.compile(
    r'^(?:Clause\s+|Section\s+)?(\d+\.\d+)(?!\.\d|\d)[\.\):]?\s*(.*)$',
    re.IGNORECASE,
)

# Catches numbering that does NOT cleanly match the X.Y pattern above
# (e.g. "2.3.1", "2.3a", "2-3"), so it can be preserved without being
# discarded or merged into a neighbouring clause.
AMBIGUOUS_HEADER_PATTERN = re.compile(
    r'^(?:Clause\s+|Section\s+)?(\d+(?:[\.\-]\d+){1,}[a-zA-Z]?|\d+[a-zA-Z])'
    r'[\.\):]?\s+(.+)$',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(input_path):
    """
    Skill: retrieve_policy

    Loads the .txt policy file at `input_path` and returns its content
    as structured numbered sections.

    Returns a dict:
        {
            "sections": {clause_id: clause_text, ...},
            "ambiguous": {best_guess_id: raw_text, ...},
            "preamble": "<any text before the first recognised clause>",
        }

    error_handling (skills.md):
      - Missing / non-.txt input -> raises FileNotFoundError / ValueError,
        caller must not proceed to summarize_policy.
      - Empty file or no identifiable numbered clauses -> raises ValueError.
      - Malformed/ambiguous clause numbering -> preserved under a
        best-guess identifier in "ambiguous", never discarded or merged.
      - The source text is never altered, paraphrased, or omitted during
        retrieval; this is a structural mapping only.
    """
    # error_handling: input file existence / type check
    if not os.path.isfile(input_path):
        raise FileNotFoundError(
            f"retrieve_policy error: input file not found: {input_path}"
        )
    if not input_path.lower().endswith(".txt"):
        raise ValueError(
            f"retrieve_policy error: input file is not a .txt file: "
            f"{input_path}"
        )

    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # error_handling: empty file
    if not raw_text.strip():
        raise ValueError(
            "retrieve_policy error: input file is empty; no sections "
            "could be extracted."
        )

    sections = {}
    ambiguous = {}
    preamble_lines = []

    current_clause = None
    current_lines = []
    ambiguous_counter = 0

    def flush_current():
        if current_clause is not None:
            text = "\n".join(current_lines).strip()
            if current_clause in sections:
                # Same clause id seen twice in the source: append rather
                # than overwrite, so nothing is lost or merged silently
                # into an unrelated clause.
                sections[current_clause] = (
                    sections[current_clause] + "\n" + text
                ).strip()
            else:
                sections[current_clause] = text

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()

        if not line:
            if current_clause is not None:
                current_lines.append("")
            continue

        clean_match = CLAUSE_HEADER_PATTERN.match(line)
        if clean_match:
            flush_current()
            current_clause = clean_match.group(1)
            remainder = clean_match.group(2).strip()
            current_lines = [remainder] if remainder else []
            continue

        ambig_match = AMBIGUOUS_HEADER_PATTERN.match(line)
        if ambig_match:
            # error_handling: malformed/ambiguous numbering -> preserve
            # raw text under a best-guess identifier, flagged separately.
            flush_current()
            current_clause = None
            current_lines = []
            ambiguous_counter += 1
            best_guess_id = ambig_match.group(1)
            ambiguous[best_guess_id] = line
            continue

        if current_clause is not None:
            current_lines.append(line)
        else:
            preamble_lines.append(line)

    flush_current()

    # error_handling: no identifiable numbered clauses at all
    if not sections:
        raise ValueError(
            "retrieve_policy error: no identifiable numbered clauses "
            "were found in the input file; cannot produce structured "
            "sections."
        )

    return {
        "sections": sections,
        "ambiguous": ambiguous,
        "preamble": "\n".join(preamble_lines).strip(),
    }


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------

def normalize_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text):
    """Lightweight sentence splitter, sufficient for policy clause text."""
    parts = re.split(r"(?<=[.;])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def compress_clause(clause_id, text):
    """
    Attempt a conservative compression of a clause: keep only sentences
    that carry a required binding verb / multi-condition term, or that
    contain a number (dates, day counts, hour limits, approver names,
    etc. tend to anchor the obligation). Always keep at least the first
    sentence.
    """
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        return text

    required_terms = []
    required_terms.extend(BINDING_VERBS.get(clause_id, []))
    required_terms.extend(MULTI_CONDITION_TERMS.get(clause_id, []))

    kept = []
    for sentence in sentences:
        lowered = sentence.lower()
        has_required_term = any(
            term.lower() in lowered for term in required_terms
        )
        has_number = bool(re.search(r"\d", sentence))
        if has_required_term or has_number or not kept:
            kept.append(sentence)

    return " ".join(kept)


def has_scope_bleed(text):
    lowered = text.lower()
    return any(phrase in lowered for phrase in SCOPE_BLEED_PHRASES)


def strip_scope_bleed(text):
    cleaned = text
    for phrase in SCOPE_BLEED_PHRASES:
        cleaned = re.sub(re.escape(phrase), "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r" {2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def verify_clause(clause_id, text):
    """
    Verification gate used before any compressed clause is allowed into
    the summary.

    Enforces:
      - Enforcement rule 4 / obligation softening: required binding-verb
        keyword(s) for this clause must still be present.
      - Enforcement rule 2: ALL multi-condition terms for this clause
        (e.g. clause 5.2's two approvers) must still be present.
      - Enforcement rule 3 / context: no scope-bleed phrasing.
    """
    lowered = text.lower()

    for verb in BINDING_VERBS.get(clause_id, []):
        if verb.lower() not in lowered:
            return False

    for term in MULTI_CONDITION_TERMS.get(clause_id, []):
        if term.lower() not in lowered:
            return False

    if has_scope_bleed(text):
        return False

    return True


def build_clause_entry(clause_id, clause_text):
    """
    Produce one "Clause X.Y: ..." line for the summary.

    If a verified compression is possible, use it. Otherwise (per
    enforcement rule 4 and the summarize_policy error_handling table),
    fall back to the verbatim source text, explicitly flagged as
    [VERBATIM].
    """
    normalized = normalize_whitespace(clause_text)

    candidate = normalize_whitespace(compress_clause(clause_id, normalized))

    if verify_clause(clause_id, candidate):
        return f"Clause {clause_id}: {candidate}"

    # error_handling: cannot condense without meaning loss -> verbatim,
    # explicitly flagged.
    return f"Clause {clause_id}: [VERBATIM] {normalized}"


def summarize_policy(retrieved):
    """
    Skill: summarize_policy

    Takes the structure returned by retrieve_policy and produces a
    compliant, clause-referenced plain-text summary.

    error_handling (skills.md):
      - Empty/malformed input -> raises ValueError; caller must run
        retrieve_policy successfully first.
      - Missing required clauses -> raises ValueError rather than
        emitting an incomplete summary (clause-omission guard).
      - Multi-condition / binding-verb integrity and scope-bleed
        avoidance are enforced per-clause via verify_clause(), with a
        verbatim fallback when compression cannot be verified safe.
    """
    if not retrieved or not retrieved.get("sections"):
        raise ValueError(
            "summarize_policy error: input structured sections are empty "
            "or malformed; retrieve_policy must be run successfully "
            "before summarize_policy."
        )

    sections = retrieved["sections"]
    ambiguous = retrieved.get("ambiguous", {})

    # Enforcement rule 1: every clause in the required inventory must be
    # present. If any is missing, do not emit an incomplete summary.
    missing = [c for c in REQUIRED_CLAUSES if c not in sections]
    if missing:
        raise ValueError(
            "summarize_policy error: the following required clauses are "
            f"missing from the retrieved sections and cannot be "
            f"summarised: {', '.join(missing)}"
        )

    def clause_sort_key(clause_id):
        try:
            return tuple(int(p) for p in clause_id.split("."))
        except ValueError:
            return (float("inf"),)

    lines = []
    lines.append("HR LEAVE POLICY SUMMARY")
    lines.append("=" * 40)
    lines.append("")
    lines.append(
        "This summary preserves the clause numbering, the core "
        "obligation, the binding-verb strength, and all multi-part "
        "conditions of the source policy document. No information "
        "beyond the source document has been added. Where a clause "
        "could not be condensed without risking a change in meaning, "
        "it is reproduced verbatim and marked [VERBATIM]."
    )
    lines.append("")

    for clause_id in sorted(sections.keys(), key=clause_sort_key):
        clause_text = sections[clause_id]
        if not clause_text.strip():
            # Nothing to summarise, but the clause reference must still
            # appear so it is not silently dropped.
            lines.append(
                f"Clause {clause_id}: [VERBATIM] "
                f"(no content was found under this clause heading)"
            )
            lines.append("")
            continue

        lines.append(build_clause_entry(clause_id, clause_text))
        lines.append("")

    if ambiguous:
        lines.append("AMBIGUOUS / UNPARSED CONTENT")
        lines.append("-" * 40)
        lines.append(
            "The following lines did not match the expected clause "
            "numbering and are reproduced verbatim rather than "
            "discarded or merged into another clause:"
        )
        lines.append("")
        for best_guess_id, raw_text in ambiguous.items():
            lines.append(f"[AMBIGUOUS {best_guess_id}] [VERBATIM] {raw_text}")
        lines.append("")

    summary_text = "\n".join(lines).rstrip() + "\n"

    # Final defensive pass: scope-bleed phrases must never appear in the
    # output, even if introduced by a bug in compression logic above.
    summary_text = strip_scope_bleed(summary_text)

    return summary_text


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "UC-0B: HR Leave Policy summarization agent. Reads a policy "
            ".txt file, structures it into numbered clauses "
            "(retrieve_policy), and writes a compliant clause-referenced "
            "summary (summarize_policy)."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        help=(
            "Path to the input policy .txt file, e.g. "
            "../data/policy-documents/policy_hr_leave.txt"
        ),
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the summary output file, e.g. "
             "summary_hr_leave.txt",
    )
    args = parser.parse_args()

    # Step 1: retrieve_policy (must succeed before summarize_policy runs)
    try:
        retrieved = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    # Step 2: summarize_policy
    try:
        summary_text = summarize_policy(retrieved)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    # Step 3: write output to the path specified by --output
    output_path = args.output
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"Summary written to: {output_path}")


if __name__ == "__main__":
    main()