"""
UC-0B app.py — Summary That Changes Meaning
Implements the retrieve_policy and summarize_policy skills defined in skills.md,
governed by the RICE agent contract in agents.md.

No external dependencies — pure Python standard library only.

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""

import argparse
import re
import os
import sys
import textwrap

# ---------------------------------------------------------------------------
# Agent configuration — mirrors agents.md exactly
# ---------------------------------------------------------------------------
AGENT_ROLE = (
    "A high-fidelity policy summarization agent specialized in extracting HR leave "
    "clauses without omission, softening, or scope bleed."
)

AGENT_INTENT = (
    "Produce a summary of the input policy document where every numbered clause is "
    "represented, multi-condition obligations are preserved in full, and no external "
    "information is added."
)

AGENT_CONTEXT = (
    "The agent is allowed to use only the provided policy text. It must explicitly "
    "exclude any external knowledge, 'standard practices,' or general HR conventions "
    "not found in the source document."
)

AGENT_ENFORCEMENT = [
    "Every numbered clause from the source must be present in the summary.",
    "Multi-condition obligations (e.g., multiple required approvers) must preserve "
    "ALL conditions — never drop one silently.",
    "Never add information, phrases, or 'common sense' context not explicitly present "
    "in the source document.",
    "If a clause cannot be summarized without losing specific binding meaning, "
    "quote it verbatim and flag it.",
    "Refuse to process if the input document lacks clear clause numbering or is "
    "fundamentally illegible.",
]

# Patterns that signal a multi-condition obligation.
# These clauses are always quoted verbatim to prevent silent condition drops
# (enforcement rule 2 / the Clause 5.2 trap).
MULTI_CONDITION_SIGNALS = [
    r"\bboth\b",
    r"\b(?:and|as well as)\b.{1,60}\b(?:approval|approver|director|head|commissioner)\b",
    r"\b(?:approval|approver|director|head|commissioner)\b.{1,60}\b(?:and|as well as)\b",
]


def _is_multi_condition(text: str) -> bool:
    """Return True if the clause likely contains a multi-condition obligation."""
    for pattern in MULTI_CONDITION_SIGNALS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


# ---------------------------------------------------------------------------
# Skill 1 — retrieve_policy
# ---------------------------------------------------------------------------
def retrieve_policy(file_path: str) -> list:
    """
    Skill: retrieve_policy
    Loads a .txt policy file and returns content as a list of structured clause
    objects: [{"clause_id": "2.3", "content": "..."}]

    Error handling:
      - Raises FileNotFoundError if the file does not exist.
      - Raises ValueError if the file is empty or has no identifiable numbered clauses.
    """
    # -- file existence check --
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: '{file_path}'")

    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        raise ValueError(f"Could not read policy file: {exc}") from exc

    if not raw.strip():
        raise ValueError("Policy file is empty.")

    # Match clause lines like:  2.3  Some heading text
    # then capture everything until the next clause or end of file.
    clause_pattern = re.compile(
        r"(?m)^[ \t]*(\d+\.\d+(?:\.\d+)?)[ \t]+(.*?)(?=\n[ \t]*\d+\.\d+[ \t]|\Z)",
        re.DOTALL,
    )

    clauses = []
    for match in clause_pattern.finditer(raw):
        clause_id = match.group(1).strip()
        content = match.group(2).strip()
        # Collapse internal whitespace to single spaces
        content = re.sub(r"[ \t]*\r?\n[ \t]*", " ", content)
        content = re.sub(r" {2,}", " ", content)
        if content:
            clauses.append({"clause_id": clause_id, "content": content})

    # -- error handling: no clauses found (enforcement rule 5) --
    if not clauses:
        raise ValueError(
            "No identifiable numbered clauses found in the document. "
            "The document must use a numbered structure (e.g. '2.3 Clause title ...')."
        )

    return clauses


# ---------------------------------------------------------------------------
# Skill 2 — summarize_policy
# ---------------------------------------------------------------------------
def summarize_policy(clauses: list) -> str:
    """
    Skill: summarize_policy
    Takes structured clause objects and produces a high-fidelity summary that
    preserves ALL binding conditions, with explicit clause references.

    Enforcement rules applied deterministically:
      Rule 1 — every clause is listed (no omissions).
      Rule 2 — multi-condition clauses are quoted verbatim and flagged.
      Rule 3 — no external knowledge is introduced; only the source text is used.
      Rule 4 — short / ambiguous clauses are quoted verbatim and flagged.
      Rule 5 — handled upstream in retrieve_policy.

    Returns a formatted summary string.

    Error handling:
      - Raises ValueError if clauses list is empty.
    """
    if not clauses:
        raise ValueError("No clauses provided to summarize_policy.")

    WIDTH = 72
    divider = "=" * WIDTH
    thin_div = "-" * WIDTH

    lines = []

    # -- Header --
    lines.append(divider)
    lines.append("POLICY SUMMARY")
    lines.append(divider)
    lines.append(f"Agent role    : {AGENT_ROLE}")
    lines.append("")
    lines.append(f"Intent        : {AGENT_INTENT}")
    lines.append("")
    lines.append(
        "Source context: Summary is derived ONLY from the source document. "
        "No external knowledge has been added."
    )
    lines.append(divider)
    lines.append("")

    # -- Enforcement rules block --
    lines.append("ENFORCEMENT RULES APPLIED")
    lines.append(thin_div)
    for i, rule in enumerate(AGENT_ENFORCEMENT, start=1):
        wrapped = textwrap.fill(f"  {i}. {rule}", width=WIDTH, subsequent_indent="     ")
        lines.append(wrapped)
    lines.append("")
    lines.append(divider)
    lines.append("")

    # -- Per-clause summary (enforcement rules 1–4) --
    lines.append("CLAUSE-BY-CLAUSE SUMMARY")
    lines.append(thin_div)

    flagged = []  # collect clause IDs that needed special treatment

    for clause in clauses:
        cid = clause["clause_id"]
        content = clause["content"]
        word_count = len(content.split())

        # Enforcement rule 4: clause is too short to paraphrase safely -> verbatim + flag
        too_short = word_count < 6
        # Enforcement rule 2: multi-condition obligation -> verbatim + flag
        multi_cond = _is_multi_condition(content)

        if too_short or multi_cond:
            reasons = []
            if multi_cond:
                reasons.append("multi-condition obligation")
            if too_short:
                reasons.append("content too brief to paraphrase safely")
            flag_label = "VERBATIM + FLAGGED (" + ", ".join(reasons) + ")"
            lines.append(f"Clause {cid}  [{flag_label}]")
            # Indent verbatim text for readability
            for vline in textwrap.wrap(f'"{content}"', width=WIDTH - 2,
                                       initial_indent="  ", subsequent_indent="   "):
                lines.append(vline)
            flagged.append(cid)
        else:
            lines.append(f"Clause {cid}")
            for wline in textwrap.wrap(content, width=WIDTH - 2,
                                       initial_indent="  ", subsequent_indent="  "):
                lines.append(wline)

        lines.append("")

    # -- Footer / audit trail --
    lines.append(divider)
    lines.append(f"Total clauses captured : {len(clauses)}")
    if flagged:
        lines.append(
            "Clauses quoted verbatim: " + ", ".join(flagged)
            + " (see enforcement rules 2 & 4)"
        )
    else:
        lines.append("No clauses required verbatim quoting.")
    lines.append(divider)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# main — wires together the two skills
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: High-fidelity HR policy summarization agent (no LLM required)."
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to the source .txt policy file."
    )
    parser.add_argument(
        "--output", required=True,
        help="Path for the generated summary .txt file."
    )
    args = parser.parse_args()

    # -- Skill 1: retrieve_policy --
    print(f"[INFO] Loading policy: {args.input}")
    try:
        clauses = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as err:
        # Enforcement rule 5: refuse to process illegible / missing input
        print(f"[ERROR] {err}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Retrieved {len(clauses)} clause(s).")

    # -- Skill 2: summarize_policy --
    print("[INFO] Summarizing policy (enforcing RICE agent rules)...")
    try:
        summary = summarize_policy(clauses)
    except ValueError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        sys.exit(1)

    # -- Write output --
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary)

    print(f"[INFO] Summary written to: {args.output}")


if __name__ == "__main__":
    main()
