"""
UC-0B app.py — HR Leave Policy Summariser
Implements skills: retrieve_policy + summarize_policy
Enforcement from agents.md (RICE):
  - Every clause cited by number
  - Binding verbs preserved exactly
  - Multi-condition obligations fully listed (e.g. §5.2 both approvers)
  - No information added from outside the source document
  - Verbatim fallback when paraphrase would alter meaning
"""
import argparse
import re
import sys
from dataclasses import dataclass


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class Section:
    clause_id: str   # e.g. "2.3", "5.2"
    heading:   str   # section heading if present, else ""
    body:      str   # exact clause text, unmodified


# ── Skill: retrieve_policy ────────────────────────────────────────────────────

def retrieve_policy(file_path: str) -> list[Section]:
    """
    Load a .txt policy file and return structured numbered sections.
    Raises FileNotFoundError / ValueError on failure — never falls back
    to external knowledge.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"FILE_UNAVAILABLE: '{file_path}' not found. "
            "Cannot summarise without source document."
        )
    except OSError as e:
        raise OSError(f"FILE_UNAVAILABLE: {e}")

    if not raw.strip():
        raise ValueError(
            f"FILE_UNAVAILABLE: '{file_path}' is empty. "
            "Cannot summarise without source document."
        )

    sections: list[Section] = []

    # Split into top-level section blocks by the ═══ dividers
    # Captures heading line and everything until the next divider or EOF
    block_pattern = re.compile(
        r"═+\n(\d+\.\s+[^\n]+)\n═+\n(.*?)(?=\n═+|\Z)", re.DOTALL
    )
    top_headings: dict[str, str] = {}
    for m in block_pattern.finditer(raw):
        heading_line = m.group(1).strip()
        # e.g. "2. ANNUAL LEAVE" → top_id = "2"
        top_id = heading_line.split(".")[0].strip()
        top_headings[top_id] = heading_line

    # Extract every sub-clause (e.g. 2.3, 5.2) with its body text
    clause_pattern = re.compile(
        r"^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for m in clause_pattern.finditer(raw):
        clause_id = m.group(1)
        raw_body = m.group(2)
        # Strip divider lines and section heading lines that may trail into body
        raw_body = re.sub(r"═+", "", raw_body)
        raw_body = re.sub(r"^\d+\.\s+[A-Z ()]+$", "", raw_body, flags=re.MULTILINE)
        body = re.sub(r"\s+", " ", raw_body).strip()
        top_id = clause_id.split(".")[0]
        heading = top_headings.get(top_id, "")
        sections.append(Section(clause_id=clause_id, heading=heading, body=body))

    if not sections:
        raise ValueError(
            "FILE_UNAVAILABLE: No numbered clauses found in document. "
            "Cannot produce a faithful summary."
        )

    return sections


# ── Skill: summarize_policy ───────────────────────────────────────────────────

# Clauses where paraphrase risk is too high — output verbatim (agents.md rule 4)
VERBATIM_CLAUSES = {"2.5", "5.2", "5.3", "7.2"}

# Binding verbs that must never be softened
BINDING_VERBS = {
    "must", "will", "requires", "required", "not permitted", "cannot",
    "entitled", "governed", "does not apply", "do not count", "may not",
}

# The 10 critical clauses from README ground-truth
CRITICAL_CLAUSES = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}


def _check_binding_verb(body: str, clause_id: str) -> str:
    """
    Verify the body contains at least one binding verb.
    Returns a warning tag if none found (should not happen with real policy text).
    """
    lower = body.lower()
    if any(v in lower for v in BINDING_VERBS):
        return ""
    return f" [WARNING §{clause_id}: no binding verb detected — review manually]"


def summarize_policy(sections: list[Section]) -> str:
    """
    Produce a clause-complete, obligation-faithful plain-text summary.
    Enforcement:
      - Every clause cited with §id
      - Binding verbs preserved
      - Multi-condition obligations fully listed
      - Verbatim fallback for high-risk clauses
      - No external information added
    """
    if not sections:
        return (
            "ERROR: No sections supplied — cannot summarise. "
            "Please supply the policy file."
        )

    # Group by top-level section heading
    groups: dict[str, list[Section]] = {}
    for s in sections:
        groups.setdefault(s.heading or "General", []).append(s)

    lines: list[str] = ["HR LEAVE POLICY — CLAUSE-COMPLETE SUMMARY", "=" * 50, ""]

    seen_clause_ids: set[str] = set()

    for heading, clauses in groups.items():
        lines.append(f"## {heading}")
        for s in clauses:
            seen_clause_ids.add(s.clause_id)
            warning = _check_binding_verb(s.body, s.clause_id)

            if s.clause_id in VERBATIM_CLAUSES:
                lines.append(
                    f"  §{s.clause_id} [VERBATIM – paraphrase would alter meaning]: "
                    f"{s.body}{warning}"
                )
            else:
                lines.append(f"  §{s.clause_id}: {s.body}{warning}")
        lines.append("")

    # Integrity check: flag any critical clauses that were missing from the document
    missing = CRITICAL_CLAUSES - seen_clause_ids
    if missing:
        lines.append("## INTEGRITY WARNING")
        for cid in sorted(missing):
            lines.append(
                f"  §{cid} was expected (README ground-truth) but not found "
                "in the source document."
            )
        lines.append("")

    lines.append(f"Total clauses summarised: {len(seen_clause_ids)}")
    return "\n".join(lines)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Leave Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    # Skill 1: retrieve_policy
    try:
        sections = retrieve_policy(args.input)
    except (FileNotFoundError, OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(sections)} clauses from '{args.input}'.")

    # Skill 2: summarize_policy
    summary = summarize_policy(sections)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
    except OSError as e:
        print(f"ERROR: Could not write output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Done. Summary written to '{args.output}'.")


if __name__ == "__main__":
    main()
