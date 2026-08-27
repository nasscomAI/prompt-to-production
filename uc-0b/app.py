"""
UC-0B — Summary That Changes Meaning
app.py: Policy summarization agent with clause-complete, obligation-faithful output.

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt
"""

import argparse
import os
import re
import sys
import json

# ---------------------------------------------------------------------------
# Constants — enforcement ground truth
# ---------------------------------------------------------------------------

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Multi-condition checks: clause -> list of required strings (case-insensitive)
MULTI_CONDITION_CHECKS = {
    "5.2": ["department head", "hr director"],
    "5.3": ["municipal commissioner"],
}

# Scope-bleed phrases that must never appear in output
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "typically in government organizations",
    "employees are generally expected to",
    "as is customary",
    "in line with standard",
]

# Softening substitutions: (weak_pattern, strong_original)
SOFTENING_MAP = [
    (r"\bshould\b",        "must"),
    (r"\bmay wish to\b",   "requires"),
    (r"\bis expected to\b","must"),
    (r"\badvised to\b",    "must"),
    (r"\bencouraged to\b", "must"),
]

# Binding verbs expected per clause (for verb-preservation audit)
BINDING_VERBS = {
    "2.3": ["must"],
    "2.4": ["must"],
    "2.5": ["will"],
    "2.6": ["forfeited"],
    "2.7": ["must", "forfeited"],
    "3.2": ["requires"],
    "3.4": ["requires"],
    "5.2": ["requires"],
    "5.3": ["requires"],
    "7.2": ["not permitted"],
}

OUTPUT_DIR = "uc-0b"

# ---------------------------------------------------------------------------
# Anthropic client (lazy import so unit tests can mock)
# ---------------------------------------------------------------------------

def get_anthropic_client():
    try:
        import anthropic
    except ImportError:
        sys.exit(
            "ERROR: 'anthropic' package not installed. "
            "Run: pip install anthropic"
        )

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print(
            "[INFO] ANTHROPIC_API_KEY environment variable not set.",
            file=sys.stderr,
        )
        try:
            api_key = input("Enter your Anthropic API key: ").strip()
        except (EOFError, KeyboardInterrupt):
            sys.exit(
                "\nERROR: No API key provided. "
                "Set ANTHROPIC_API_KEY or enter it when prompted."
            )
    if not api_key:
        sys.exit(
            "ERROR: API key is empty. "
            "Get your key at https://console.anthropic.com/settings/keys"
        )

    return anthropic.Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# Skill 1 — retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> list[dict]:
    """
    Load a .txt policy file and return an ordered list of clause objects:
        { clause_number: str, clause_text: str, binding_verb: str }

    Error codes raised as RuntimeError:
        FILE_NOT_FOUND | UNSUPPORTED_FORMAT | NO_CLAUSES_DETECTED | PARTIAL_PARSE
    """
    # --- file existence ---
    if not os.path.exists(file_path):
        raise RuntimeError(
            f"FILE_NOT_FOUND: '{file_path}' does not exist. "
            "Check the --input path and retry."
        )

    # --- format check ---
    if not file_path.lower().endswith(".txt"):
        raise RuntimeError(
            f"UNSUPPORTED_FORMAT: '{file_path}' is not a .txt file. "
            "Only plain-text policy documents are supported."
        )

    # --- read ---
    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        raise RuntimeError(
            f"UNSUPPORTED_FORMAT: Could not read '{file_path}' as UTF-8 text. "
            f"Detail: {exc}"
        )

    # --- parse numbered clauses (e.g. "2.3", "3.4", "10.1") ---
    # Pattern: a decimal clause number at the start of a line, followed by text.
    clause_pattern = re.compile(
        r"^(\d+\.\d+)\s+(.+?)(?=^\d+\.\d+\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    matches = clause_pattern.findall(raw)

    if not matches:
        raise RuntimeError(
            "NO_CLAUSES_DETECTED: No numbered clauses found in the document. "
            "Structured parsing failed. Raw content returned for manual inspection.\n\n"
            + raw
        )

    clauses = []
    unparsed_warnings = []

    for number, text in matches:
        text = text.strip()
        binding_verb = _extract_binding_verb(text)
        clauses.append({
            "clause_number": number,
            "clause_text": text,
            "binding_verb": binding_verb,
        })

    # --- check for expected clauses; warn if some are absent (PARTIAL_PARSE) ---
    found_numbers = {c["clause_number"] for c in clauses}
    missing = [cn for cn in REQUIRED_CLAUSES if cn not in found_numbers]
    if missing:
        unparsed_warnings.append(
            f"PARTIAL_PARSE: The following required clauses were not found during "
            f"parsing: {missing}. The document may use non-standard numbering. "
            "Manual inspection recommended before proceeding."
        )
        for w in unparsed_warnings:
            print(f"[WARNING] {w}", file=sys.stderr)

    return clauses


def _extract_binding_verb(text: str) -> str:
    """Return the first recognised binding verb found in clause text."""
    verbs = [
        "not permitted", "must", "will", "requires", "require",
        "forfeited", "may not", "shall",
    ]
    lower = text.lower()
    for v in verbs:
        if v in lower:
            return v
    return "unknown"


# ---------------------------------------------------------------------------
# Skill 2 — summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(clauses: list[dict], output_path: str) -> str:
    """
    Call the Anthropic API to produce a clause-complete summary, then run all
    enforcement checks before writing to output_path.

    Error codes printed to stderr:
        INCOMPLETE_CLAUSE_LIST | CONDITION_DROP | SCOPE_BLEED |
        OBLIGATION_SOFTENING | CLAUSE_MISSING_FROM_OUTPUT
    """
    # --- pre-flight: all required clauses present in input ---
    found = {c["clause_number"] for c in clauses}
    missing = [cn for cn in REQUIRED_CLAUSES if cn not in found]
    if missing:
        raise RuntimeError(
            f"INCOMPLETE_CLAUSE_LIST: The following required clauses are absent "
            f"from the structured input and cannot be summarised: {missing}. "
            "Re-run retrieve_policy on a complete document."
        )

    # --- build structured input for the prompt ---
    clause_block = "\n\n".join(
        f"[{c['clause_number']}] {c['clause_text']}"
        for c in clauses
    )

    system_prompt = (
        "You are a policy summarization agent. "
        "Your only permitted information source is the clause text provided by the user. "
        "You must not add, infer, or generalise beyond what is explicitly stated in the clauses. "
        "Do not use phrases such as 'as is standard practice', "
        "'typically in government organisations', or 'employees are generally expected to'. "
        "Preserve all binding verbs (must, will, requires, not permitted, are forfeited) verbatim. "
        "Never drop conditions from multi-condition obligations. "
        "For clause 5.2 you must name BOTH the Department Head AND the HR Director. "
        "For clause 5.3 you must name the Municipal Commissioner. "
        "If you cannot condense a clause without losing meaning, reproduce it verbatim "
        "and append the flag: [VERBATIM - meaning-loss risk]. "
        "Return ONLY a JSON object with this schema and nothing else — no markdown fences, "
        "no preamble:\n"
        '{"clauses": [{"number": "<clause_number>", "summary": "<summary text>"}]}'
    )

    user_prompt = (
        "Summarise each of the following HR leave policy clauses. "
        "Reference every clause by its number. "
        "Preserve all binding verbs and multi-condition obligations exactly.\n\n"
        "CLAUSES:\n"
        + clause_block
    )

    client = get_anthropic_client()

    print("[INFO] Calling Anthropic API for policy summarization ...", file=sys.stderr)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw_response = "".join(
        block.text for block in response.content if hasattr(block, "text")
    )

    # --- parse JSON response ---
    try:
        clean = raw_response.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        parsed = json.loads(clean)
        summaries: list[dict] = parsed["clauses"]
    except (json.JSONDecodeError, KeyError) as exc:
        raise RuntimeError(
            f"API_PARSE_ERROR: Could not parse the model's JSON response. "
            f"Detail: {exc}\nRaw response:\n{raw_response}"
        )

    # --- build summary dict keyed by clause number ---
    summary_map: dict[str, str] = {
        item["number"]: item["summary"] for item in summaries
    }

    # -----------------------------------------------------------------------
    # Enforcement checks
    # -----------------------------------------------------------------------

    errors: list[str] = []
    warnings: list[str] = []

    # 1. Clause-presence check
    for cn in REQUIRED_CLAUSES:
        if cn not in summary_map:
            errors.append(
                f"CLAUSE_MISSING_FROM_OUTPUT: Clause {cn} is absent from the "
                "model's summary. Cannot write output."
            )

    # 2. Multi-condition checks (5.2, 5.3)
    for cn, required_strings in MULTI_CONDITION_CHECKS.items():
        if cn in summary_map:
            text_lower = summary_map[cn].lower()
            dropped = [s for s in required_strings if s not in text_lower]
            if dropped:
                errors.append(
                    f"CONDITION_DROP: Clause {cn} is missing required condition(s): "
                    f"{dropped}. This is a critical failure."
                )

    # 3. Scope-bleed check
    full_output = "\n".join(summary_map.values())
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase.lower() in full_output.lower():
            errors.append(
                f"SCOPE_BLEED: Prohibited phrase detected in output: '{phrase}'. "
                "Remove all language not traceable to the source document."
            )

    # 4. Obligation-softening check
    for cn, text in summary_map.items():
        for pattern, original in SOFTENING_MAP:
            if re.search(pattern, text, re.IGNORECASE):
                warnings.append(
                    f"OBLIGATION_SOFTENING: Clause {cn} contains a weakened modal "
                    f"(matched /{pattern}/). Expected binding verb: '{original}'. "
                    "Output flagged for review."
                )

    # 5. Binding-verb audit
    for cn, expected_verbs in BINDING_VERBS.items():
        if cn in summary_map:
            text_lower = summary_map[cn].lower()
            missing_verbs = [v for v in expected_verbs if v not in text_lower]
            if missing_verbs:
                warnings.append(
                    f"BINDING_VERB_MISSING: Clause {cn} — expected verb(s) "
                    f"{missing_verbs} not found in summary text."
                )

    # --- emit warnings ---
    for w in warnings:
        print(f"[WARNING] {w}", file=sys.stderr)

    # --- halt on errors ---
    if errors:
        for e in errors:
            print(f"[ERROR] {e}", file=sys.stderr)
        raise RuntimeError(
            f"Enforcement failure: {len(errors)} error(s) detected. "
            "Output file was NOT written. See stderr for details."
        )

    # -----------------------------------------------------------------------
    # Assemble final output text
    # -----------------------------------------------------------------------

    lines = ["HR LEAVE POLICY — CLAUSE-COMPLETE SUMMARY", "=" * 60, ""]
    for cn in REQUIRED_CLAUSES:
        lines.append(f"[{cn}] {summary_map[cn]}")
        lines.append("")

    lines.append("=" * 60)
    lines.append(
        "Enforcement: All 10 required clauses verified present. "
        "Multi-condition obligations checked. Scope-bleed scan passed."
    )

    output_text = "\n".join(lines)

    # -----------------------------------------------------------------------
    # Write output — enforced path only
    # -----------------------------------------------------------------------

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    enforced_path = os.path.join(OUTPUT_DIR, os.path.basename(output_path))

    with open(enforced_path, "w", encoding="utf-8") as fh:
        fh.write(output_text)

    print(f"[INFO] Summary written to: {enforced_path}", file=sys.stderr)
    return output_text


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="UC-0B: Clause-complete HR policy summarization agent."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the source .txt policy document.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output filename (written inside uc-0b/ directory).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # --- Skill 1: retrieve_policy ---
    print(f"[INFO] Loading policy from: {args.input}", file=sys.stderr)
    try:
        clauses = retrieve_policy(args.input)
    except RuntimeError as exc:
        sys.exit(str(exc))

    print(f"[INFO] Parsed {len(clauses)} clause(s) from source document.", file=sys.stderr)

    # --- Skill 2: summarize_policy ---
    try:
        summarize_policy(clauses, args.output)
    except RuntimeError as exc:
        sys.exit(str(exc))


if __name__ == "__main__":
    main()

# Quick offline test — paste at bottom and run: python app.py --test
if "--test" in sys.argv:
    clauses = retrieve_policy("../data/policy-documents/policy_hr_leave.txt")
    for c in clauses:
        print(f"[{c['clause_number']}] verb={c['binding_verb']} | {c['clause_text'][:80]}")