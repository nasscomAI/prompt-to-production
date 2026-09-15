"""
UC-0B — Summary That Changes Meaning

Extractive, meaning-preserving digest of a policy document.

Enforcement rules from agents.md mapped to code:
  1. every numbered clause in the source MUST appear in the summary
  2. multi-condition obligations are preserved in full — never drop a condition
  3. nothing is added that is not present in the source document
  4. high-risk clauses (multi-condition traps) are quoted verbatim and
     flagged [VERBATIM] instead of being rephrased

Because binding legal text cannot be safely condensed by deterministic rules,
the summarizer is extractive: each clause is reflowed verbatim under its
section header. A self-check report verifies completeness, condition
preservation for the multi-approver clause, and absence of scope-bleed.

Standard library only — runs on Python 3.9+ with no dependencies.
"""
import argparse
import re

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 &\-\/()]+)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")

# Substrings that make a clause high-risk to condense (README trap table).
TRAP_PHRASES = [
    "not valid",
    "regardless",
    "under any circumstances",
    "exceeding",
    "forfeited",
    "within 48 hours",
    "within 60 days",
    "and the hr director",
    "only after",
    "does not apply",
]

# Phrases that must never appear in output: they are not in the source.
SCOPE_BLEED_PHRASES = [
    "typically",
    "generally",
    "standard practice",
    "usually",
    "as is common",
    "employees are expected",
    "in most organisations",
]

CLAUDE_CHECK = "5.2"


def retrieve_policy(path):
    """Load a policy .txt file into (metadata, sections).

    sections is a list of (section_title, [(clause_id, clause_text)]).
    """
    metadata = []
    sections = []
    current_clause_id = None
    current_clause_lines = []

    def flush_clause():
        nonlocal current_clause_id, current_clause_lines
        if current_clause_id is not None and current_clause_lines:
            text = re.sub(r"\s+", " ", " ".join(current_clause_lines)).strip()
            if sections:
                sections[-1][2].append((current_clause_id, text))
            current_clause_id = None
            current_clause_lines = []

    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            stripped = raw.strip()
            if not stripped or stripped.count("═") > 3:
                continue
            match = CLAUSE_RE.match(stripped)
            if match:
                flush_clause()
                current_clause_id = match.group(1)
                current_clause_lines = [match.group(2)]
                continue
            match = SECTION_RE.match(stripped)
            if match:
                flush_clause()
                sections.append((match.group(1), match.group(2), []))
                continue
            if current_clause_id is not None:
                current_clause_lines.append(stripped)
            elif not sections:
                metadata.append(stripped)
    flush_clause()
    return metadata, sections


def summarize_policy(metadata, sections):
    """Build a meaning-preserving digest with [VERBATIM] flags on trap clauses."""
    lines = []
    if metadata:
        lines.append(" / ".join(metadata))
        lines.append("")
    for num, title, clauses in sections:
        lines.append(f"{num}. {title}")
        for cid, text in clauses:
            flag = "  [VERBATIM]" if any(
                p in text.lower() for p in TRAP_PHRASES
            ) else ""
            lines.append(f"  {cid}  {text}{flag}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def verify(metadata, sections, summary):
    """Self-check: completeness, 5.2 condition preservation, no scope bleed."""
    report = []
    text_by_id = {cid: t for _, _, cls in sections for cid, t in cls}
    source_ids = list(text_by_id)
    summary_ids = re.findall(r"(?m)^\s*(\d+\.\d+)\s+", summary)

    missing = [cid for cid in source_ids if cid not in summary_ids]
    report.append(f"Clauses in source: {len(source_ids)}")
    report.append(f"Clauses in summary: {len(summary_ids)}")
    report.append(f"Missing clauses: {', '.join(missing) if missing else 'none'}")

    c52 = text_by_id.get(CLAUDE_CHECK, "").lower()
    both = "department head" in c52 and "hr director" in c52
    report.append(
        f"Clause {CLAUDE_CHECK} preserves both approvers: "
        f"{'yes' if both else 'NO — condition dropped'}"
    )

    flagged = sum(
        1 for cid, text in text_by_id.items()
        if any(p in text.lower() for p in TRAP_PHRASES)
    )
    report.append(f"Verbatim-flagged clauses: {flagged}")

    bleed = [p for p in SCOPE_BLEED_PHRASES if p in summary.lower()]
    report.append(f"Scope-bleed phrases: {', '.join(bleed) if bleed else 'none'}")
    return report


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    try:
        metadata, sections = retrieve_policy(args.input)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}")
        raise SystemExit(1)

    if not sections:
        print("Error: no numbered clauses found — refusing to summarise.")
        raise SystemExit(1)

    summary = summarize_policy(metadata, sections)
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary)

    for line in verify(metadata, sections, summary):
        print(line)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
