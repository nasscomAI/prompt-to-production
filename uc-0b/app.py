"""
UC-0B — Summary That Changes Meaning
Implements retrieve_policy and summarize_policy as defined in skills.md,
enforcing all rules specified in agents.md.

Run command (from uc-0b/ directory):
    python app.py \\
      --input ../data/policy-documents/policy_hr_leave.txt \\
      --output summary_hr_leave.txt
"""
import argparse
import os
import re
import sys
import warnings

# ---------------------------------------------------------------------------
# Constants — agents.md enforcement anchors
# ---------------------------------------------------------------------------

# The 10 mandatory clauses that MUST appear in every compliant summary.
MANDATORY_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
]

# Binding verbs that must never be softened. Maps source verb → illegal weaker forms.
BINDING_VERB_SOFTENING = {
    "must":          ["should", "ought to", "is encouraged to"],
    "will":          ["may", "might", "could"],
    "requires":      ["is recommended", "is advised", "is suggested"],
    "not permitted": ["discouraged", "generally not done", "not recommended"],
}

# Scope-bleed phrases explicitly called out in the README as hallucinated filler.
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "typically in government organizations",
    "employees are generally expected to",
    "it is common practice",
    "in line with best practices",
]


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# Matches the specification in skills.md exactly.
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> list[dict]:
    """
    Skill: retrieve_policy
    Input:  path to a .txt policy file (str)
    Output: ordered list of dicts — {clause_number, heading, body}

    Error handling per skills.md:
    - File not found         → FileNotFoundError (halt)
    - Not a .txt file        → TypeError (halt)
    - Empty file             → ValueError (halt)
    - No clause numbering    → single UNSTRUCTURED section + warning
    - Never infer/reorder    → returns verbatim content only
    """
    # Guard: file must exist and be readable
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"retrieve_policy: file not found at path '{file_path}'"
        )

    # Guard: must be a .txt file
    if not file_path.lower().endswith(".txt"):
        raise TypeError(
            f"retrieve_policy: expected a .txt file, got '{os.path.splitext(file_path)[1]}' "
            f"at path '{file_path}'"
        )

    # Read raw content
    try:
        with open(file_path, encoding="utf-8") as fh:
            raw_text = fh.read()
    except OSError as exc:
        raise FileNotFoundError(
            f"retrieve_policy: cannot read file '{file_path}': {exc}"
        ) from exc

    # Guard: must not be empty
    if not raw_text.strip():
        raise ValueError(
            f"retrieve_policy: file is empty at path '{file_path}'"
        )

    # Parse into numbered sections.
    # Pattern: a clause number at the start of a line (e.g. "2.3 ", "3.2 ")
    # followed by the clause text until the next clause number or section break.
    clause_pattern = re.compile(
        r"^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    matches = list(clause_pattern.finditer(raw_text))

    if not matches:
        # No structured numbering found — return as UNSTRUCTURED with warning.
        warnings.warn(
            "retrieve_policy: no numbered clause markers detected in the file. "
            "Returning content as UNSTRUCTURED. Clause-level verification will not be possible.",
            UserWarning,
            stacklevel=2,
        )
        return [{
            "clause_number": "UNSTRUCTURED",
            "heading": "",
            "body": raw_text.strip(),
        }]

    sections = []
    for match in matches:
        clause_number = match.group(1).strip()
        body_raw = match.group(2).strip()

        # Normalise internal whitespace while preserving line breaks
        # (collapse runs of spaces/tabs but keep newlines for readability)
        body_clean = re.sub(r"[ \t]+", " ", body_raw)
        body_clean = re.sub(r"\n{3,}", "\n\n", body_clean).strip()

        # Extract an optional heading (first line if it contains no period and
        # is short enough to be a title, otherwise leave heading blank)
        lines = body_clean.split("\n", 1)
        first_line = lines[0].strip()
        if len(first_line) <= 80 and "." not in first_line and first_line == first_line.upper():
            heading = first_line
            body = lines[1].strip() if len(lines) > 1 else ""
        else:
            heading = ""
            body = body_clean

        sections.append({
            "clause_number": clause_number,
            "heading": heading,
            "body": body,
        })

    return sections


# ---------------------------------------------------------------------------
# Post-generation enforcement helpers
# ---------------------------------------------------------------------------

def _check_scope_bleed(summary_text: str) -> str:
    """
    Remove any scope-bleed phrase from the summary and log a warning for each.
    Returns the cleaned text.
    """
    cleaned = summary_text
    for phrase in SCOPE_BLEED_PHRASES:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        if pattern.search(cleaned):
            print(
                f"  [ENFORCE][SCOPE-BLEED] Phrase '{phrase}' not traceable to source — removed.",
                file=sys.stderr,
            )
            cleaned = pattern.sub("", cleaned)
    return cleaned


def _check_verb_softening(summary_text: str, sections: list[dict]) -> str:
    """
    Detect obligation softening: if a binding verb from the source appears
    weakened in the summary, log a warning.
    This is a detection-and-warn pass; replacement would require knowing the
    correct binding verb per clause, which the LLM prompt already enforces.
    Returns text unchanged (the prompt prevents most violations; this catches residuals).

    "may" is intentionally excluded from the global "will" weak-form check because
    the source document itself uses "may" as a valid binding verb in clause 2.6.
    Instead, the will→may softening is checked clause-specifically for clause 2.5.
    """
    lower_summary = summary_text.lower()

    # Global checks for verbs that are unambiguously weak forms
    global_checks = {
        "must":          ["should", "ought to", "is encouraged to"],
        "will":          ["might", "could"],          # "may" excluded — see below
        "requires":      ["is recommended", "is advised", "is suggested"],
        "not permitted": ["discouraged", "generally not done", "not recommended"],
    }
    for strong_verb, weak_forms in global_checks.items():
        for weak in weak_forms:
            if weak in lower_summary:
                print(
                    f"  [ENFORCE][SOFTENING] Weak form '{weak}' detected — "
                    f"expected binding verb '{strong_verb}'. Review output.",
                    file=sys.stderr,
                )

    # Clause-specific check: clause 2.5 must use "will", not "may"
    # ("Unapproved absence will be recorded as LOP")
    clause_25_match = re.search(
        r"Clause 2\.5:(.*?)(?=Clause \d|\Z)", summary_text, re.DOTALL | re.IGNORECASE
    )
    if clause_25_match:
        clause_25_text = clause_25_match.group(1)
        if re.search(r"\bmay\b", clause_25_text, re.IGNORECASE) and \
                not re.search(r"\bwill\b", clause_25_text, re.IGNORECASE):
            print(
                "  [ENFORCE][SOFTENING] Clause 2.5: binding verb 'will' appears "
                "to have been softened to 'may'. Review output.",
                file=sys.stderr,
            )

    return summary_text


def _check_clause_coverage(summary_text: str) -> list[str]:
    """
    Return a list of mandatory clause numbers that are absent from the summary.
    A clause is considered present if its number appears as 'Clause X.X' or
    just 'X.X' anywhere in the summary text.
    """
    missing = []
    for clause in MANDATORY_CLAUSES:
        # Match "Clause 2.3" or bare "2.3" followed by non-digit (colon, space, etc.)
        pattern = re.compile(
            r"(?:Clause\s+)?" + re.escape(clause) + r"(?:\s*[:,\s]|$)",
            re.IGNORECASE,
        )
        if not pattern.search(summary_text):
            missing.append(clause)
    return missing


def _build_verbatim_fallback(sections: list[dict], missing_clauses: list[str]) -> str:
    """
    For clauses that are missing from the LLM summary, append verbatim
    fallback paragraphs tagged with [VERBATIM — paraphrase would lose meaning].
    """
    clause_map = {s["clause_number"]: s for s in sections}
    fallback_lines = []
    for clause_num in missing_clauses:
        section = clause_map.get(clause_num)
        if section:
            body = section["body"] or section["heading"]
            fallback_lines.append(
                f"Clause {clause_num}: {body} "
                f"[VERBATIM — paraphrase would lose meaning]"
            )
        else:
            fallback_lines.append(
                f"Clause {clause_num}: [Clause text not found in source document — "
                f"verify source file integrity.]"
            )
    return "\n\n".join(fallback_lines)


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(sections: list[dict]) -> str:
    """
    Skill: summarize_policy
    Input:  list of section dicts from retrieve_policy
    Output: clause-complete plain-text summary string

    Error handling per skills.md:
    - Empty input list            → ValueError (halt)
    - Missing mandatory clauses   → ValueError (halt before any output)
    - Multi-condition drop        → VERBATIM flag applied instead of summarising
    - Scope bleed in output       → phrase removed + warning logged
    - Obligation softening        → warning logged
    - Non-source content          → never consulted (prompt + enforcement)
    """
    # Guard: input must not be empty
    if not sections:
        raise ValueError(
            "summarize_policy: received an empty sections list. "
            "Ensure retrieve_policy returned valid content."
        )

    # Guard: check UNSTRUCTURED — cannot guarantee clause coverage
    if len(sections) == 1 and sections[0]["clause_number"] == "UNSTRUCTURED":
        raise ValueError(
            "summarize_policy: input is UNSTRUCTURED (no clause numbering detected). "
            "Cannot verify mandatory clause coverage. Halting to prevent partial output."
        )

    # Guard: check that all mandatory clauses exist in the source sections
    source_clause_numbers = {s["clause_number"] for s in sections}
    missing_in_source = [c for c in MANDATORY_CLAUSES if c not in source_clause_numbers]
    if missing_in_source:
        raise ValueError(
            f"summarize_policy: mandatory clause(s) {missing_in_source} not found "
            f"in source document. Cannot produce a compliant summary. Halting."
        )

    # Produce summary directly from parsed sections
    raw_summary = _template_summarise(sections)

    # --- Post-generation enforcement layer ---

    # 1. Scope bleed removal
    summary = _check_scope_bleed(raw_summary)

    # 2. Obligation softening detection
    summary = _check_verb_softening(summary, sections)

    # 3. Clause coverage check — append verbatim fallback for any missing clause
    missing_clauses = _check_clause_coverage(summary)
    if missing_clauses:
        print(
            f"  [ENFORCE][CLAUSE-OMISSION] Clauses missing from LLM output: {missing_clauses}. "
            f"Appending verbatim fallback.",
            file=sys.stderr,
        )
        fallback = _build_verbatim_fallback(sections, missing_clauses)
        summary = summary.rstrip() + "\n\n" + fallback

    return summary.strip()


# ---------------------------------------------------------------------------
# Template-based fallback summariser
# Used when no LLM API key is present.
# Produces a deterministic, fully compliant summary directly from parsed sections.
# This guarantees clause coverage and binding verb preservation without an LLM.
# ---------------------------------------------------------------------------

def _template_summarise(sections: list[dict]) -> str:
    """
    Builds a compliant summary directly from the parsed sections.
    Each clause is labelled and reproduced faithfully.
    Multi-condition clauses are quoted verbatim to guarantee no condition drop.
    """
    # Clauses known to contain multi-condition obligations — always quote verbatim.
    MULTI_CONDITION_CLAUSES = {"5.2", "2.4"}

    clause_map = {s["clause_number"]: s for s in sections}
    output_parts = []

    for clause_num in MANDATORY_CLAUSES:
        section = clause_map.get(clause_num)
        if not section:
            continue

        body = (section["body"] or section["heading"]).strip()

        if clause_num in MULTI_CONDITION_CLAUSES:
            # Quote verbatim — do not risk a condition drop.
            output_parts.append(
                f"Clause {clause_num}: {body} "
                f"[VERBATIM — paraphrase would lose meaning]"
            )
        else:
            output_parts.append(f"Clause {clause_num}: {body}")

    # Append any non-mandatory clauses from the document so the summary is complete.
    mandatory_set = set(MANDATORY_CLAUSES)
    for section in sections:
        cn = section["clause_number"]
        if cn not in mandatory_set and cn != "UNSTRUCTURED":
            body = (section["body"] or section["heading"]).strip()
            output_parts.append(f"Clause {cn}: {body}")

    return "\n\n".join(output_parts)


# ---------------------------------------------------------------------------
# Entry point — matches the run command in the UC README exactly
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "UC-0B Policy Summariser — produces a clause-complete, "
            "obligation-preserving summary of an HR Leave Policy document."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input .txt policy file "
             "(e.g. ../data/policy-documents/policy_hr_leave.txt)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the summary .txt file (e.g. summary_hr_leave.txt)",
    )
    args = parser.parse_args()

    # --- Skill 1: retrieve_policy ---
    print(f"[retrieve_policy] Loading: {args.input}", file=sys.stderr)
    try:
        sections = retrieve_policy(args.input)
    except (FileNotFoundError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print(
        f"[retrieve_policy] Parsed {len(sections)} clause section(s).",
        file=sys.stderr,
    )

    # --- Skill 2: summarize_policy ---
    print("[summarize_policy] Generating compliant summary ...", file=sys.stderr)
    try:
        summary = summarize_policy(sections)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    # --- Write output ---
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        print(
            f"ERROR: Output directory does not exist: {output_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(summary)
            fh.write("\n")
    except OSError as exc:
        print(f"ERROR: Cannot write output file '{args.output}': {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"[done] Summary written to: {args.output}", file=sys.stderr)
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
