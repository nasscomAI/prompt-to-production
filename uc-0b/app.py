"""
UC-0B — Summary That Changes Meaning
=====================================
Implements the policy-summarisation agent defined in agents.md using the
two skills defined in skills.md:

  retrieve_policy   — loads and structures the .txt policy document
  summarize_policy  — produces a clause-faithful summary via an LLM

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt

Requirements:
    pip install google-generativeai
    GEMINI_API_KEY environment variable must be set.
"""

import argparse
import os
import sys
import re
import textwrap

# ---------------------------------------------------------------------------
# Optional LLM import — fail gracefully with a clear message
# ---------------------------------------------------------------------------
try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants derived from agents.md clause inventory
# ---------------------------------------------------------------------------
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7",
                    "3.2", "3.4", "5.2", "5.3", "7.2"]

SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government",
    "employees are generally expected",
    "as per usual",
    "common practice",
    "industry norm",
]

# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> str:
    """
    Skill: retrieve_policy
    Loads the HR Leave Policy .txt file and returns its full content as a
    structured string, preserving original clause numbering.

    Raises:
        FileNotFoundError  – if the path does not exist
        ValueError         – if the file is empty or unreadable
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Policy document not found: {file_path!r}\n"
            "Source document could not be loaded. Summarisation aborted."
        )

    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        raise ValueError(
            f"Policy document could not be read: {exc}\n"
            "Source document could not be loaded. Summarisation aborted."
        ) from exc

    if not content.strip():
        raise ValueError(
            "Policy document is empty.\n"
            "Source document could not be loaded. Summarisation aborted."
        )

    return content


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(structured_content: str, model_name: str = "gemini-2.0-flash") -> str:
    """
    Skill: summarize_policy
    Sends the structured policy content to the LLM with a strict system
    prompt that enforces all rules from agents.md, then validates the
    response before returning it.

    Raises:
        ValueError  – if input is empty, missing required clauses, or the
                      LLM response fails post-generation validation
        RuntimeError – if the google-generativeai package is not installed
    """
    if not structured_content.strip():
        raise ValueError(
            "summarize_policy received empty content. "
            "Re-invoke retrieve_policy or abort."
        )

    # Pre-flight: verify all required clauses exist in the source
    missing = _check_clauses_in_source(structured_content)
    if missing:
        raise ValueError(
            f"Input is missing required clauses: {missing}. "
            "Cannot produce a compliant summary. Aborting."
        )

    if not _GENAI_AVAILABLE:
        raise RuntimeError(
            "google-generativeai is not installed.\n"
            "Run: pip install google-generativeai"
        )

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set. "
            "Cannot call the LLM."
        )

    genai.configure(api_key=api_key)

    system_prompt = textwrap.dedent(f"""
        You are a policy summarisation agent with a strict operational boundary.

        INPUT
        -----
        You will receive the full text of an HR Leave Policy document. Your
        ONLY allowed source is this document — nothing else.

        REQUIRED CLAUSES
        ----------------
        Your summary MUST explicitly reference ALL of the following clause
        numbers and faithfully describe their content:
        {", ".join(REQUIRED_CLAUSES)}

        BINDING VERBS
        -------------
        Preserve every binding verb verbatim or with equivalently strong
        language. Never soften:
          - "must"         → never replace with "should" or "may"
          - "will"         → never replace with "might" or "is expected to"
          - "requires"     → never replace with "is recommended"
          - "not permitted"→ never replace with "is discouraged"

        MULTI-CONDITION OBLIGATIONS
        ---------------------------
        Retain ALL conditions in multi-condition clauses. In particular:
          - Clause 5.2: name BOTH "Department Head" AND "HR Director" as
            required approvers. Dropping even one is a hard failure.
          - Clause 5.3: name "Municipal Commissioner" as the additional
            approver for LWP exceeding 30 continuous days.

        SCOPE BLEED — PROHIBITED PHRASES
        ---------------------------------
        Do NOT include any of these phrases or anything similar:
          "as is standard practice", "typically in government",
          "employees are generally expected", "as per usual",
          "common practice", "industry norm"
        Do not add information not present in the source document.

        VERBATIM FLAG
        -------------
        If any clause cannot be summarised without meaning loss, quote it
        verbatim and prepend: [VERBATIM — meaning-loss risk]

        OUTPUT FORMAT
        -------------
        Produce a structured written summary. Group clauses by section
        (Annual Leave, Sick Leave, Leave Without Pay, Leave Encashment).
        Reference each clause number explicitly (e.g. "Clause 2.3 states…").
    """).strip()

    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
    )

    response = model.generate_content(structured_content)
    summary = response.text.strip()

    # Post-generation validation
    _validate_summary(summary)

    return summary


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _check_clauses_in_source(text: str) -> list[str]:
    """Return list of REQUIRED_CLAUSES not found in text."""
    return [c for c in REQUIRED_CLAUSES if c not in text]


def _validate_summary(summary: str) -> None:
    """
    Enforce agents.md rules on the generated summary.
    Raises ValueError describing every violation found.
    """
    errors = []

    # Rule 1: every required clause number must appear in the summary
    missing_clauses = [c for c in REQUIRED_CLAUSES if c not in summary]
    if missing_clauses:
        errors.append(
            f"Summary is missing required clause references: {missing_clauses}"
        )

    # Rule 2: check for softened binding verbs (heuristic — common patterns)
    softening_patterns = [
        (r"\bshould submit\b",   "2.3 — 'must submit' softened to 'should submit'"),
        (r"\bshould receive\b",  "2.4 — binding approval softened"),
        (r"\bmay be recorded\b", "2.5 — 'will be recorded' softened to 'may be recorded'"),
        (r"\bis encouraged\b",   "general — obligation softened to encouragement"),
        (r"\bis recommended\b",  "general — 'requires' softened to 'is recommended'"),
    ]
    for pattern, label in softening_patterns:
        if re.search(pattern, summary, re.IGNORECASE):
            errors.append(f"Binding-verb softening detected: {label}")

    # Rule 3: scope bleed detection
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase.lower() in summary.lower():
            errors.append(f"Scope bleed detected — prohibited phrase: '{phrase}'")

    # Rule 4: clause 5.2 must name BOTH approvers
    if "5.2" in summary:
        has_dept_head = bool(re.search(r"department head", summary, re.IGNORECASE))
        has_hr_dir    = bool(re.search(r"hr director", summary, re.IGNORECASE))
        if not (has_dept_head and has_hr_dir):
            missing = []
            if not has_dept_head: missing.append("Department Head")
            if not has_hr_dir:    missing.append("HR Director")
            errors.append(
                f"Clause 5.2 condition drop — missing approver(s): {missing}"
            )

    if errors:
        raise ValueError(
            "Summary failed compliance validation:\n" +
            "\n".join(f"  • {e}" for e in errors)
        )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B — HR Leave Policy Summarisation Agent"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to policy_hr_leave.txt"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write the compliant summary"
    )
    parser.add_argument(
        "--model", default="gemini-2.0-flash",
        help="Gemini model name (default: gemini-2.0-flash)"
    )
    args = parser.parse_args()

    # ── Skill 1: retrieve_policy ──────────────────────────────────────────
    print(f"[retrieve_policy] Loading: {args.input}")
    try:
        policy_content = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"[retrieve_policy] Loaded {len(policy_content)} characters.")

    # ── Skill 2: summarize_policy ─────────────────────────────────────────
    print(f"[summarize_policy] Generating summary via {args.model} …")
    try:
        summary = summarize_policy(policy_content, model_name=args.model)
    except (ValueError, RuntimeError) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    print("[summarize_policy] Summary generated and validated.")

    # ── Write output ──────────────────────────────────────────────────────
    try:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(summary)
    except OSError as exc:
        print(f"\nERROR writing output: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"\nDone. Summary written to: {args.output}")


if __name__ == "__main__":
    main()
