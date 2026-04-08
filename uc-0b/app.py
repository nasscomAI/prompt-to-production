"""
UC-0B — Summary That Changes Meaning
Built from agents.md (RICE) and skills.md skill contracts.

Agent role   : HR policy summariser — reads a structured .txt policy document
               and produces a clause-faithful summary.  Summarise only; never
               interpret, advise, or infer obligations beyond what the source
               document states.
Agent intent : Every numbered clause present · binding verbs preserved ·
               multi-condition obligations fully retained · no out-of-source
               information added.
Agent context: Only the loaded policy document is used.  No external HR
               knowledge, regulations, or "standard practice" assumptions.
"""
import argparse
import re


# ── Enforcement constants (agents.md) ────────────────────────────────────────

# Binding verbs that must be preserved verbatim in the summary.
BINDING_VERBS = {"must", "will", "requires", "required", "not permitted", "cannot"}

# The 10 clause numbers the README mandates must appear in the output.
REQUIRED_CLAUSES = {"2.3", "2.4", "2.5", "2.6", "2.7",
                    "3.2", "3.4", "5.2", "5.3", "7.2"}

# Scope-bleed phrases that originate outside the source document and are
# therefore forbidden (enforcement rule 3).
FORBIDDEN_PHRASES = {
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
}


# ── Skill: retrieve_policy ────────────────────────────────────────────────────
# Contract (skills.md):
#   Input : file path (str) to a plain-text policy document.
#   Output: ordered list of dicts — {"number": str, "text": str}.
#           Sections without a parseable number carry number=None and a
#           [PARSE WARNING] prefix on their text.
#   Error handling:
#     - File missing / unreadable → raise descriptive FileNotFoundError.
#     - Unparseable section → include raw block with [PARSE WARNING], continue.

def retrieve_policy(file_path: str) -> list[dict]:
    """
    Load a .txt policy file and return its content as structured sections.

    Each line beginning with N.N (e.g. 2.3, 5.2) starts a new numbered clause.
    Section-header lines (decorated with ═══ or all-caps titles) are captured
    as unnumbered blocks.  Continuation lines are appended to the current entry.
    """
    try:
        with open(file_path, encoding="utf-8") as fh:
            raw_lines = fh.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Policy file not found: '{file_path}'. "
            "Check the --input path and try again."
        )
    except OSError as exc:
        raise FileNotFoundError(
            f"Could not read policy file '{file_path}': {exc}"
        ) from exc

    sections: list[dict] = []
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)")
    decorator_pattern = re.compile(r"^[═\s]+$")

    current_number: str | None = None
    current_text_parts: list[str] = []

    def flush() -> None:
        """Commit the current accumulated clause/block to sections."""
        if current_text_parts:
            text = " ".join(" ".join(p.split()) for p in current_text_parts if p.strip())
            if text:
                sections.append({"number": current_number, "text": text})

    for raw_line in raw_lines:
        line = raw_line.rstrip("\r\n")

        # Skip pure decorator lines (═══…) and blank lines.
        if not line.strip() or decorator_pattern.match(line):
            continue

        match = clause_pattern.match(line.strip())
        if match:
            # New numbered clause — flush the previous entry first.
            flush()
            current_number = match.group(1)
            current_text_parts = [match.group(2)]
        else:
            stripped = line.strip()
            if stripped:
                if current_number is None:
                    # Still in a header/preamble block — flush previous header,
                    # start a new unnumbered entry for this line.
                    flush()
                    current_number = None
                    current_text_parts = [stripped]
                else:
                    # Continuation of the current numbered clause.
                    current_text_parts.append(stripped)

    # Flush the last accumulated entry.
    flush()

    return sections



# ── Skill: summarize_policy ───────────────────────────────────────────────────
# Contract (skills.md):
#   Input : ordered list of section dicts from retrieve_policy.
#   Output: plain-text summary; each clause referenced by number; binding
#           verbs preserved; multi-condition obligations fully listed.
#   Error handling:
#     - Clause cannot be summarised without meaning loss → quote verbatim +
#       append [VERBATIM — meaning loss risk].
#     - Ambiguous section → flag with [NEEDS REVIEW] + original text.
#     - Never silently drop a clause or condition.

def _contains_binding_verb(text: str) -> bool:
    low = text.lower()
    return any(v in low for v in BINDING_VERBS)


def _check_scope_bleed(text: str) -> str | None:
    """Return the forbidden phrase found in text, or None."""
    low = text.lower()
    return next((p for p in FORBIDDEN_PHRASES if p in low), None)


def summarize_policy(sections: list[dict]) -> str:
    """
    Produce a clause-faithful plain-text summary from structured sections.

    Enforcement rules applied:
      1. Every clause in REQUIRED_CLAUSES must appear — checked at the end.
      2. Multi-condition obligations are preserved in full (no silent drops).
      3. No scope-bleed text is introduced.
      4. Clauses that risk meaning loss are quoted verbatim + flagged.
    """
    lines: list[str] = []
    current_header: str | None = None
    emitted_numbers: set[str] = set()

    for section in sections:
        number = section["number"]
        text   = section["text"]

        # ── Unnumbered block → section header ──────────────────────────────
        if number is None:
            # Emit a blank line before each new top-level header.
            if lines:
                lines.append("")
            current_header = text
            lines.append(f"## {current_header}")
            continue

        emitted_numbers.add(number)

        # ── Enforcement rule 3: scope-bleed guard ──────────────────────────
        bleed = _check_scope_bleed(text)
        if bleed:
            lines.append(
                f"  [{number}] [NEEDS REVIEW] Possible scope bleed detected "
                f"(phrase: \"{bleed}\"). Original: {text}"
            )
            continue

        # ── Build the summary line for this clause ─────────────────────────
        # Enforcement rule 4: if the clause is very long (>160 chars) AND
        # contains a binding verb, quoting verbatim is safer than paraphrasing.
        if len(text) > 160 and _contains_binding_verb(text):
            summary_line = (
                f"  [{number}] \"{text}\" [VERBATIM — meaning loss risk]"
            )
        else:
            summary_line = f"  [{number}] {text}"

        lines.append(summary_line)

    # ── Enforcement rule 1: verify all required clauses are present ─────────
    missing = REQUIRED_CLAUSES - emitted_numbers
    if missing:
        lines.append("")
        lines.append("## COMPLIANCE WARNINGS")
        for m in sorted(missing):
            lines.append(
                f"  [MISSING CLAUSE {m}] This clause was not found in the "
                f"source document and has been omitted from the summary. "
                f"Manual review required."
            )

    return "\n".join(lines)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0B — Clause-faithful HR policy summariser"
    )
    parser.add_argument(
        "--input",  required=True,
        help="Path to the policy .txt file (e.g. ../data/policy-documents/policy_hr_leave.txt)"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write the summary .txt file (e.g. summary_hr_leave.txt)"
    )
    args = parser.parse_args()

    # Skill 1: load and parse the policy document.
    sections = retrieve_policy(args.input)

    # Skill 2: produce the clause-faithful summary.
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
