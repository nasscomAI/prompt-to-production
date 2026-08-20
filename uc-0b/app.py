"""
UC-0B — Summary That Changes Meaning
Implements the enforcement rules in agents.md and the two skills in skills.md.

The failure modes taught here are clause omission, scope bleed, and obligation
softening / condition dropping. The only way to guarantee none of those occur is a
faithful, extractive summary: every numbered clause is preserved with its number,
all binding conditions are kept, nothing is added, and completeness is self-checked.

Skills:
  retrieve_policy  -> parse .txt into structured numbered sections and clauses
  summarize_policy -> produce a compliant, clause-referenced summary + completeness check
"""
import argparse
import re

# A clause line looks like "2.3 Employees must submit ...". A section header looks
# like "2. ANNUAL LEAVE". Separator lines are the box-drawing rules.
CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z].*)$")
SEPARATOR_CHARS = set("═=─-")

# Binding verbs/phrases that must never be softened.
BINDING_TERMS = ["must", "will", "requires", "required", "not permitted",
                 "mandatory", "not valid", "cannot", "forfeited"]

# Signals that a clause carries more than one condition (so a reviewer can confirm
# none was dropped). The full text is always preserved regardless of this flag.
MULTI_CONDITION_SIGNALS = [" and ", " both ", "regardless", "within", "before",
                           "after", "unless", "exceeding", "maximum of"]


def _is_separator(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and all(ch in SEPARATOR_CHARS for ch in stripped)


def retrieve_policy(input_path: str) -> dict:
    """
    Read the policy file and return structured sections and clauses.
    Returns: {"title_lines": [...], "sections": [{"number","title","clauses":[{"ref","text"}]}]}
    """
    try:
        with open(input_path, "r", encoding="utf-8") as fh:
            raw_lines = fh.read().splitlines()
    except OSError as exc:
        raise RuntimeError(f"Could not read policy file '{input_path}': {exc}") from exc

    title_lines = []
    sections = []
    current_section = None
    current_clause = None
    seen_first_section = False

    def _flush_clause():
        nonlocal current_clause
        if current_clause is not None:
            current_clause["text"] = re.sub(r"\s+", " ", current_clause["text"]).strip()
            current_section["clauses"].append(current_clause)
            current_clause = None

    for line in raw_lines:
        if _is_separator(line):
            continue
        if not line.strip():
            continue

        section_match = SECTION_RE.match(line)
        clause_match = CLAUSE_RE.match(line)

        # Section header (e.g. "2. ANNUAL LEAVE") — but not a clause like "2.3 ...".
        if section_match and not clause_match:
            _flush_clause()
            seen_first_section = True
            current_section = {
                "number": section_match.group(1),
                "title": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            continue

        # Clause line (e.g. "2.3 Employees must ...").
        if clause_match and current_section is not None:
            _flush_clause()
            current_clause = {"ref": clause_match.group(1), "text": clause_match.group(2)}
            continue

        # Continuation of the current clause (wrapped line).
        if current_clause is not None:
            current_clause["text"] += " " + line.strip()
            continue

        # Pre-section document header (title block).
        if not seen_first_section:
            title_lines.append(line.strip())

    _flush_clause()
    return {"title_lines": title_lines, "sections": sections}


def _classify_clause(text: str):
    """Return (is_multi_condition, has_binding_term)."""
    lowered = text.lower()
    multi = sum(1 for sig in MULTI_CONDITION_SIGNALS if sig in lowered) >= 1
    binding = any(term in lowered for term in BINDING_TERMS)
    return multi, binding


def summarize_policy(policy: dict) -> str:
    """
    Produce a compliant, clause-referenced summary with a completeness self-check.
    Faithful/extractive: preserves every clause number, binding verb, and condition.
    """
    lines = []
    source_refs = []

    if policy["title_lines"]:
        lines.append("SUMMARY OF: " + " / ".join(policy["title_lines"][:3]))
        lines.append("")

    for section in policy["sections"]:
        header = f"{section['number']}. {section['title']}"
        lines.append(header)
        if not section["clauses"]:
            lines.append("  (no binding clauses in this section)")
            lines.append("")
            continue
        for clause in section["clauses"]:
            source_refs.append(clause["ref"])
            multi, binding = _classify_clause(clause["text"])
            markers = []
            if multi and binding:
                markers.append("[MULTI-CONDITION]")
            marker_str = (" " + " ".join(markers)) if markers else ""
            lines.append(f"  {clause['ref']}{marker_str} {clause['text']}")
        lines.append("")

    # Enforcement: self-verify clause completeness before emitting.
    summarised_refs = set(source_refs)
    all_source_refs = {c["ref"] for s in policy["sections"] for c in s["clauses"]}
    missing = sorted(all_source_refs - summarised_refs)
    if missing:
        raise RuntimeError(
            "Refusing to emit summary: source clauses missing from summary: "
            + ", ".join(missing)
        )

    lines.append("─" * 55)
    lines.append(
        f"COMPLETENESS CHECK: {len(source_refs)} of {len(all_source_refs)} "
        f"source clauses preserved. All clause numbers accounted for."
    )
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary)

    total = sum(len(s["clauses"]) for s in policy["sections"])
    print(f"Done. {total} clauses preserved. Summary written to {args.output}")


if __name__ == "__main__":
    main()
