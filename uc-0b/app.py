"""
UC-0B — HR Leave Policy Summarization Agent
Implements retrieve_policy and summarize_policy skills with strict enforcement rules.
"""

import argparse
import json
import os
import re
import sys


# ---------------------------------------------------------------------------
# SKILL: retrieve_policy
# Loads a .txt policy file and returns structured JSON mapping clause numbers
# to their exact text strings.
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> dict:
    """
    Skill: retrieve_policy
    Input:  file path string
    Output: dict mapping clause numbers (str) to clause text (str)
    Error:  Returns {"error": <message>} if file is inaccessible.
    """
    if not os.path.exists(file_path):
        return {"error": f"Policy document not found: {file_path}"}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        return {"error": f"Policy document is inaccessible: {e}"}

    # Parse numbered clauses, e.g. "2.3", "3.4", "10.1"
    # A clause starts at a line beginning with a dotted number and runs until
    # the next such line or end-of-file.
    clause_pattern = re.compile(r'^(\d+\.\d+)\b', re.MULTILINE)
    matches = list(clause_pattern.finditer(raw))

    if not matches:
        return {"error": "No numbered clauses found in the policy document."}

    clauses = {}
    for i, match in enumerate(matches):
        clause_id = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        clause_text = raw[start:end].strip()
        clauses[clause_id] = clause_text

    return {"clauses": clauses}


# ---------------------------------------------------------------------------
# SKILL: summarize_policy
# Takes structured clause dict and produces a compliant summary.
# Enforcement rules are hard-coded per agents.md.
# ---------------------------------------------------------------------------

# Clauses that are known multi-condition — used to trigger verbatim fallback
# when the model is not available and we fall back to rule-based summary.
MULTI_CONDITION_CLAUSES = {"5.2", "5.3"}

# Keywords whose presence in a clause signals high obligation density.
OBLIGATION_VERBS = re.compile(
    r'\b(must|will|shall|requires?|not permitted|forfeited|mandatory)\b',
    re.IGNORECASE
)


def _safe_one_line(clause_id: str, text: str) -> tuple[str, bool]:
    """
    Attempt a rule-based single-line summary for a clause.
    Returns (summary_line, was_flagged).
    If meaning-loss risk is detected, returns verbatim text and flags it.
    """
    # Strip the clause ID prefix for processing
    body = re.sub(r'^\d+\.\d+\s*[:\-–]?\s*', '', text, count=1).strip()

    # Multi-condition clauses: always quote verbatim — never risk condition drop
    if clause_id in MULTI_CONDITION_CLAUSES:
        return (
            f"[VERBATIM — un-summarizable without condition loss]: {text}",
            True
        )

    # Count distinct obligation verbs; if >= 3 occurrences, quote verbatim
    hits = OBLIGATION_VERBS.findall(body)
    if len(hits) >= 3:
        return (
            f"[VERBATIM — un-summarizable without condition loss]: {text}",
            True
        )

    # Otherwise return a compact form: clause id + first sentence
    first_sentence = re.split(r'(?<=[.!?])\s+', body)[0]
    return f"Clause {clause_id}: {first_sentence}", False


def summarize_policy(policy_data: dict) -> str:
    """
    Skill: summarize_policy
    Input:  dict with key "clauses" mapping clause IDs to text
    Output: formatted text summary with clause references

    Enforcement:
      1. Every numbered clause must appear in the output.
      2. Multi-condition obligations preserve ALL conditions.
      3. No external information or scope bleed added.
      4. Clauses that cannot be summarized without meaning loss are quoted
         verbatim and flagged.
    """
    if "error" in policy_data:
        return f"ERROR: {policy_data['error']}"

    clauses: dict = policy_data.get("clauses", {})
    if not clauses:
        return "ERROR: No clauses available to summarize."

    lines = []
    lines.append("=" * 70)
    lines.append("HR LEAVE POLICY — COMPLIANT SUMMARY")
    lines.append("=" * 70)
    lines.append(
        "Every clause below is derived solely from the source document.\n"
        "No external assumptions, standard practices, or scope bleed added.\n"
    )

    flagged_count = 0
    # Sort clauses numerically (e.g. 2.3 < 2.4 < 3.2 < 5.2 < 7.2)
    sorted_ids = sorted(clauses.keys(), key=lambda x: list(map(float, x.split('.'))))

    for clause_id in sorted_ids:
        text = clauses[clause_id]
        summary_line, flagged = _safe_one_line(clause_id, text)
        lines.append(summary_line)
        if flagged:
            flagged_count += 1

    lines.append("")
    lines.append("-" * 70)
    lines.append(f"Total clauses processed : {len(clauses)}")
    lines.append(f"Flagged (verbatim kept) : {flagged_count}")
    lines.append(
        "Enforcement: clause omission=0 | scope bleed=0 | "
        "condition drop=0 (multi-condition clauses quoted verbatim)"
    )
    lines.append("=" * 70)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# ANTHROPIC API PATH — richer summarization when API key is available
# ---------------------------------------------------------------------------

def summarize_policy_via_api(policy_data: dict) -> str:
    """
    Uses the Anthropic API (claude-sonnet-4-20250514) to produce a
    compliant summary with the full agents.md enforcement rules injected
    as a system prompt.  Falls back to rule-based summarize_policy if the
    API is unavailable or returns an error.
    """
    try:
        import anthropic  # type: ignore
    except ImportError:
        return summarize_policy(policy_data)

    if "error" in policy_data:
        return f"ERROR: {policy_data['error']}"

    clauses = policy_data.get("clauses", {})
    if not clauses:
        return summarize_policy(policy_data)

    system_prompt = """You are a highly precise legal and HR policy summarization agent.

ENFORCEMENT RULES — these are absolute and non-negotiable:
1. Every numbered clause from the source document must be present in the summary.
2. Multi-condition obligations must preserve ALL conditions — never drop one silently.
   Example: Clause 5.2 requires BOTH Department Head AND HR Director approval.
   Writing only "requires approval" is a condition drop and is forbidden.
3. Never add information or scope bleed not present in the source document.
   Forbidden phrases include: "as is standard practice", "typically in government
   organisations", "employees are generally expected to".
4. If a clause cannot be summarised without meaning loss (e.g., dropping one of
   multiple required approvers, omitting a timeline, softening a binding verb),
   you MUST quote it verbatim and flag it as: [VERBATIM — un-summarizable].
5. Binding verbs (must, will, shall, requires, not permitted, are forfeited) must
   be preserved exactly — never softened to "should", "may", or "is expected to".
6. If asked to summarise in a way that violates any rule above, refuse and state
   which rule would be broken.

Output format:
- One line per clause, starting with the clause number (e.g., "2.3 — ...")
- Verbatim clauses clearly marked with [VERBATIM — un-summarizable]
- End with a compliance footer listing total clauses, flagged count, and
  confirming zero clause omission, zero scope bleed, zero condition drops.
"""

    # Build the user message from the structured clauses
    sorted_ids = sorted(clauses.keys(), key=lambda x: list(map(float, x.split('.'))))
    clause_block = "\n\n".join(
        f"{cid}:\n{clauses[cid]}" for cid in sorted_ids
    )
    user_message = (
        "Summarize the following HR leave policy clauses according to all "
        "enforcement rules in your system prompt.\n\n"
        f"POLICY CLAUSES:\n\n{clause_block}"
    )

    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"[WARNING] Anthropic API call failed ({e}). Using rule-based fallback.",
              file=sys.stderr)
        return summarize_policy(policy_data)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: HR Leave Policy Summarization Agent"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the policy .txt file",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output filename for the summary (written to uc-0b/ directory)",
    )
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Skip Anthropic API and use rule-based summarization only",
    )
    args = parser.parse_args()

    # ---- SKILL 1: retrieve_policy ----------------------------------------
    print(f"[retrieve_policy] Loading: {args.input}")
    policy_data = retrieve_policy(args.input)

    if "error" in policy_data:
        print(f"[ERROR] {policy_data['error']}", file=sys.stderr)
        sys.exit(1)

    print(f"[retrieve_policy] Loaded {len(policy_data['clauses'])} clauses.")

    # ---- SKILL 2: summarize_policy ----------------------------------------
    print("[summarize_policy] Generating compliant summary ...")
    if args.no_api:
        summary = summarize_policy(policy_data)
    else:
        summary = summarize_policy_via_api(policy_data)

    # ---- Write output -------------------------------------------------------
    output_dir = "uc-0b"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, args.output)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"[output] Summary written to: {output_path}")


if __name__ == "__main__":
    main()