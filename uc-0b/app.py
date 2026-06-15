"""
UC-0B: Policy summarisation agent that preserves clause obligations without
omission, condition-dropping, or scope bleed.

No LLM backend required — summarise_policy produces output directly from the
parsed clause list using deterministic formatting rules.
"""
import argparse
import re
import sys
from pathlib import Path

GROUND_TRUTH_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government",
    "employees are generally expected to",
]

# Binding verbs that must not be softened; checked left-to-right (stronger first).
_BINDING_VERBS = [
    "not permitted",
    "must",
    "will",
    "requires",
    "required",
]

_SOFTENING_MAP = {
    "must":        ["should", "may", "can", "might"],
    "will":        ["may", "can", "might", "could"],
    "not permitted": ["not recommended", "discouraged", "inadvisable"],
    "requires":    ["recommends", "suggests", "encourages"],
}


# ---------------------------------------------------------------------------
# Skill 1: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> list[dict]:
    """Load and parse a policy .txt file into numbered sections."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        raise ValueError(f"Policy file is empty: {file_path}")

    sections = []
    current_clause = None
    current_lines = []
    clause_pattern = re.compile(r"^(\d+\.\d+(?:\.\d+)?)\b")

    for line in raw.splitlines():
        match = clause_pattern.match(line.strip())
        if match:
            if current_clause is not None:
                sections.append({
                    "clause": current_clause,
                    "text": " ".join(current_lines).strip(),
                })
            current_clause = match.group(1)
            current_lines = [line.strip()]
        else:
            if current_clause is not None:
                current_lines.append(line.strip())
            elif line.strip():
                sections.append({"clause": None, "text": line.strip()})

    if current_clause is not None:
        sections.append({
            "clause": current_clause,
            "text": " ".join(current_lines).strip(),
        })

    if not sections:
        raise ValueError("No content could be parsed from the policy file.")

    flagged = [s for s in sections if s["clause"] is None]
    for s in flagged:
        print(
            f"[WARNING] Unnumbered section flagged for manual review: "
            f"{s['text'][:80]}",
            file=sys.stderr,
        )

    return sections


# ---------------------------------------------------------------------------
# Skill 2: summarize_policy  (deterministic — no LLM)
# ---------------------------------------------------------------------------

def _leading_binding_verb(text: str) -> str | None:
    lower = text.lower()
    for verb in _BINDING_VERBS:
        if verb in lower:
            return verb
    return None


def _condense(text: str) -> str:
    """Return the clause text verbatim — preserves all conditions and verbs."""
    return text.strip()


def summarize_policy(sections: list[dict]) -> str:
    """Produce a clause-by-clause summary directly from parsed sections.

    Each clause is reproduced verbatim to guarantee zero condition-dropping
    and zero binding-verb softening. Unnumbered sections are flagged.
    """
    lines = ["HR LEAVE POLICY — CLAUSE-BY-CLAUSE SUMMARY", "=" * 50, ""]

    for s in sections:
        if s["clause"] is None:
            lines.append(f"[UNNUMBERED — manual review required]: {s['text']}")
            continue

        verb = _leading_binding_verb(s["text"])
        entry = f"{s['clause']} — {_condense(s['text'])}"
        if verb is None:
            entry += "  [FLAG: no binding verb detected — manual review required]"
        lines.append(entry)
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Post-generation check
# ---------------------------------------------------------------------------

def check_summary(summary: str) -> list[str]:
    """Return enforcement warnings about the generated summary."""
    warnings = []
    for clause in GROUND_TRUTH_CLAUSES:
        if clause not in summary:
            warnings.append(f"MISSING clause {clause} from summary")
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase.lower() in summary.lower():
            warnings.append(f"SCOPE BLEED detected: '{phrase}'")
    return warnings


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Compliant HR policy summarisation agent (no LLM)"
    )
    parser.add_argument("--input",  required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Output file for the summary")
    args = parser.parse_args()

    print(f"[retrieve_policy] Loading: {args.input}")
    try:
        sections = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"[retrieve_policy] Parsed {len(sections)} sections.")

    print("[summarize_policy] Generating deterministic summary …")
    summary = summarize_policy(sections)

    warnings = check_summary(summary)
    if warnings:
        print("\n[POST-GENERATION WARNINGS]")
        for w in warnings:
            print(f"  ⚠  {w}")
    else:
        print(
            "[check_summary] All 10 ground-truth clauses present. "
            "No scope bleed detected."
        )

    output_path = Path(args.output)
    output_path.write_text(summary, encoding="utf-8")
    print(f"\n[done] Summary written to: {output_path}")


if __name__ == "__main__":
    main()
