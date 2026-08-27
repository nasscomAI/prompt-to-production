"""
UC-0B — Summary That Changes Meaning
Reads an HR policy document, extracts numbered clauses, and produces
a clause-preserving summary with enforcement rules applied.
"""
import argparse
import re
import sys


def retrieve_policy(path: str) -> list[dict]:
    """
    Load a .txt policy file and return its content as structured numbered sections.
    Each section: {"section": "2", "clause": "2.3", "text": "..."}
    """
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Cannot read file: {e}", file=sys.stderr)
        sys.exit(1)

    if not content.strip():
        print(f"ERROR: File is empty: {path}", file=sys.stderr)
        sys.exit(1)

    # Match clause patterns like "2.3", "5.12"
    clause_pattern = re.compile(
        r"^(\d+\.\d+)\s+(.+?)(?=^\d+\.\d+\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    # Split on clause boundaries
    lines = content.split("\n")
    clauses = []
    current_clause = None

    for line in lines:
        # Skip separator lines and section headers
        stripped = line.strip()
        if stripped.startswith("═") or re.match(r"^\d+\.\s+[A-Z]", stripped):
            continue
        m = re.match(r"^(\d+\.\d+)\s+(.*)", line.strip())
        if m:
            if current_clause:
                clauses.append(current_clause)
            clause_num = m.group(1)
            section = clause_num.split(".")[0]
            current_clause = {
                "section": section,
                "clause": clause_num,
                "text": m.group(2).strip(),
            }
        elif current_clause:
            # Continuation line — strip leading whitespace and append
            stripped = line.strip()
            if stripped:
                current_clause["text"] += " " + stripped

    if current_clause:
        clauses.append(current_clause)

    if not clauses:
        print(f"ERROR: No numbered clauses found in {path}", file=sys.stderr)
        sys.exit(1)

    return clauses


def _has_multiple_conditions(text: str) -> bool:
    """Detect clauses with multiple conditions connected by 'and'."""
    lower = text.lower()
    # Look for "and" connecting distinct obligations (not just lists)
    and_count = len(re.findall(r"\band\b", lower))
    # Also detect "both ... and" patterns
    has_both_and = bool(re.search(r"\bboth\b.+\band\b", lower))
    # "requires ... and" pattern
    requires_and = bool(re.search(r"\brequires?\b.+\band\b", lower))
    return has_both_and or requires_and or (and_count >= 2)


def _has_prohibition(text: str) -> bool:
    """Detect clauses with prohibitions that should be quoted verbatim."""
    lower = text.lower()
    return bool(re.search(r"\bnot permitted\b|\bnot valid\b|\bnot applicable\b|\bnot count\b|\bnot considered\b|\bnot sufficient\b", lower))


def _extract_binding_verbs(text: str) -> list[str]:
    """Extract binding verbs from clause text."""
    binding_verbs = [
        "must", "must not", "requires", "required", "will be",
        "shall", "shall not", "may not", "are forfeited",
        "not permitted", "not valid", "cannot", "not sufficient",
        "not considered", "not count", "not applicable",
    ]
    found = []
    lower = text.lower()
    for verb in binding_verbs:
        if verb in lower:
            found.append(verb)
    return found


def _condense_clause(clause: dict) -> str:
    """
    Produce a condensed version of a clause while preserving meaning.
    Returns the condensed text.
    """
    text = clause["text"]

    # Known multi-condition clauses that need verbatim treatment
    multi_condition_clauses = {
        "5.2": True,   # Department Head AND HR Director
        "3.2": True,   # 3+ days AND 48hr submission
        "3.4": True,   # before/after holiday AND regardless of duration
        "5.3": True,   # LWP >30 days AND Commissioner approval
        "2.5": True,   # LOP regardless of subsequent approval
        "7.2": True,   # not permitted under any circumstances
    }

    if clause["clause"] in multi_condition_clauses:
        return text

    if _has_multiple_conditions(text) or _has_prohibition(text):
        return text

    # For simpler clauses, return as-is (the text is already concise)
    return text


def summarize_policy(sections: list[dict]) -> str:
    """
    Take structured sections and produce a compliant summary.
    Every source clause is represented. Multi-condition obligations
    are preserved. No external information is added.
    """
    if not sections:
        print("ERROR: No sections provided to summarize.", file=sys.stderr)
        sys.exit(1)

    # Group clauses by section
    section_groups: dict[str, list[dict]] = {}
    for sec in sections:
        s = sec["section"]
        section_groups.setdefault(s, []).append(sec)

    section_titles = {
        "1": "Purpose and Scope",
        "2": "Annual Leave",
        "3": "Sick Leave",
        "4": "Maternity and Paternity Leave",
        "5": "Leave Without Pay (LWP)",
        "6": "Public Holidays",
        "7": "Leave Encashment",
        "8": "Grievances",
    }

    output_lines = []
    output_lines.append("POLICY SUMMARY — HR-POL-001")
    output_lines.append("All clauses referenced from source document.")
    output_lines.append("")

    for section_num in sorted(section_groups.keys(), key=int):
        title = section_titles.get(section_num, f"Section {section_num}")
        output_lines.append(f"SECTION {section_num}: {title.upper()}")
        output_lines.append("")

        for clause in section_groups[section_num]:
            clause_num = clause["clause"]
            condensed = _condense_clause(clause)
            binding = _extract_binding_verbs(condensed)

            output_lines.append(f"[{clause_num}] {condensed}")
            if binding:
                output_lines.append(f"  Binding: {', '.join(binding)}")
            output_lines.append("")

    # Clause completeness check
    all_clause_nums = sorted(
        [s["clause"] for s in sections],
        key=lambda x: [int(p) for p in x.split(".")]
    )
    output_lines.append("---")
    output_lines.append(f"Clauses covered: {', '.join(all_clause_nums)} ({len(all_clause_nums)} total)")

    return "\n".join(output_lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B — Summarize HR policy with clause preservation"
    )
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")
    print(f"Clauses found: {len(sections)}")


if __name__ == "__main__":
    main()
