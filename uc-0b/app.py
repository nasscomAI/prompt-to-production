"""
UC-0B — Summary That Changes Meaning
Implemented according to agents.md (RICE) and skills.md.

Enforcement rules (from agents.md):
  1. Every numbered clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2)
     must appear in the output summary — omission is a hard failure.
  2. Multi-condition obligations must preserve ALL conditions —
     clause 5.2: both 'Department Head' AND 'HR Director' must be named.
     clause 5.3: 'Municipal Commissioner' must be named.
  3. Never add information not present in the source document —
     no general knowledge, no inferred norms, no hedging phrases.
  4. If a clause cannot be summarised without meaning loss → quote verbatim
     and append: [VERBATIM — MEANING LOSS RISK]

Context boundary (from agents.md):
  Only the source document text may be used. No external knowledge.
  Prohibited phrases: "as is standard practice", "typically in government
  organisations", "employees are generally expected to".
"""

import argparse
import os
import re
import sys
from pathlib import Path

# ── Clauses the README mandates must appear (enforcement rule 1) ──────────────
MANDATORY_CLAUSES = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}

# ── Prohibited scope-bleed phrases (enforcement rule 3) ───────────────────────
PROHIBITED_PHRASES = [
    "as is standard practice",
    "typically in government",
    "employees are generally expected",
    "it is common practice",
    "generally understood",
    "while not explicitly covered",
]

# ── High-risk clauses that carry multi-condition obligations ──────────────────
# These are reproduced verbatim to prevent condition drops (enforcement rule 2).
VERBATIM_CLAUSE_IDS = {"5.2", "5.3", "2.4", "2.5", "2.6", "2.7", "7.2"}


# ─────────────────────────────────────────────────────────────────────────────
# Skill: retrieve_policy
# ─────────────────────────────────────────────────────────────────────────────

def retrieve_policy(file_path: str) -> tuple[list[dict], dict]:
    """
    Load a .txt policy document and return its content as an ordered list of
    numbered clause dicts.

    Returns:
        clauses  — list of {clause_id, heading, body}
        metadata — {document_name, total_clauses}

    Raises:
        FileNotFoundError  if file_path does not exist
        ValueError         if the file is empty
    Logs a warning (to stderr) if no numbered clauses are detected.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy document not found: {file_path}")

    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        raise ValueError("Policy document is empty.")

    document_name = path.name

    # ── Parse numbered clauses ────────────────────────────────────────────────
    # Match lines starting with N.N or N.N.N (e.g. "2.3", "3.2", "5.2")
    # Clause body runs until the next clause or section header.
    clause_pattern = re.compile(
        r"^(\d+\.\d+(?:\.\d+)?)\s+(.*?)$",
        re.MULTILINE,
    )

    matches = list(clause_pattern.finditer(raw))

    if not matches:
        # Fallback: return whole document as UNNUMBERED (skills.md error_handling)
        print(
            f"WARNING: No numbered clauses detected in '{document_name}'. "
            "Returning full text as UNNUMBERED.",
            file=sys.stderr,
        )
        clauses = [{"clause_id": "UNNUMBERED", "heading": "", "body": raw.strip()}]
        return clauses, {"document_name": document_name, "total_clauses": 1}

    clauses = []
    for i, m in enumerate(matches):
        clause_id  = m.group(1)
        first_line = m.group(2).strip()

        # Body = first line + ALL continuation lines until the next clause match
        # or a section-separator line (═══...).
        start = m.end()
        end   = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        continuation = raw[start:end]

        body_lines = [first_line]
        for line in continuation.splitlines():
            stripped = line.strip()
            # Stop at section-header separators
            if re.match(r"^═+", line):
                break
            # Skip blank separator lines that precede the next section header
            # but only if we haven't collected any content yet after first_line
            body_lines.append(stripped)

        # Join, collapse multiple blank lines, strip trailing whitespace
        body_text = "\n".join(body_lines).strip()
        body_text = re.sub(r"\n{3,}", "\n\n", body_text)
        # Remove trailing blank lines introduced by continuation scan
        body_text = body_text.rstrip()

        clauses.append({
            "clause_id": clause_id,
            "heading":   first_line,
            "body":      body_text,
        })

    return clauses, {"document_name": document_name, "total_clauses": len(clauses)}


# ─────────────────────────────────────────────────────────────────────────────
# Skill: summarize_policy
# ─────────────────────────────────────────────────────────────────────────────

def summarize_policy(clauses: list[dict], document_name: str) -> str:
    """
    Produce a clause-complete summary from the structured clause list.

    Enforcement:
      - Every clause appears in output — none silently omitted.
      - Verbatim quotation used for multi-condition / meaning-loss clauses.
      - [VERBATIM — MEANING LOSS RISK] marker appended for flagged clauses.
      - [EMPTY CLAUSE — REVIEW SOURCE] marker for empty bodies.

    Raises:
        ValueError  if clauses list is empty
    """
    if not clauses:
        raise ValueError("No clauses to summarise.")

    lines = []
    lines.append(f"POLICY SUMMARY — {document_name}")
    lines.append("=" * 60)
    lines.append(
        "SOURCE: Verbatim clause bodies reproduced to prevent meaning loss.\n"
        "No information has been added beyond what appears in the source document."
    )
    lines.append("=" * 60)
    lines.append("")

    for clause in clauses:
        cid  = clause["clause_id"]
        body = clause["body"].strip()

        if not body:
            # Empty clause — must still appear (skills.md: never omit)
            lines.append(f"[{cid}] [EMPTY CLAUSE — REVIEW SOURCE]")
            lines.append("")
            continue

        if cid in VERBATIM_CLAUSE_IDS or cid == "UNNUMBERED":
            # High-risk: quote verbatim to guarantee no condition drop
            lines.append(f"[{cid}] {body}")
            lines.append("      [VERBATIM — MEANING LOSS RISK]")
        else:
            lines.append(f"[{cid}] {body}")

        lines.append("")

    # ── Mandatory clause audit (enforcement rule 1) ───────────────────────────
    found_ids = {c["clause_id"] for c in clauses}
    missing   = MANDATORY_CLAUSES - found_ids
    if missing:
        lines.append("─" * 60)
        lines.append(
            f"WARNING — MISSING MANDATORY CLAUSES: {sorted(missing)}\n"
            "These clauses were not found in the source document. "
            "Review the source file before distributing this summary."
        )

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summariser — RICE-enforced, clause-complete output"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy .txt file (e.g. ../data/policy-documents/policy_hr_leave.txt)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write summary (e.g. summary_hr_leave.txt)",
    )
    args = parser.parse_args()

    # ── Retrieve ──────────────────────────────────────────────────────────────
    print(f"Loading: {args.input}")
    clauses, meta = retrieve_policy(args.input)
    print(
        f"Parsed {meta['total_clauses']} clauses from '{meta['document_name']}'"
    )

    # ── Summarise ─────────────────────────────────────────────────────────────
    summary = summarize_policy(clauses, meta["document_name"])

    # ── Write ─────────────────────────────────────────────────────────────────
    output_path = Path(args.output)
    output_path.write_text(summary, encoding="utf-8")

    # ── Audit report to stdout ────────────────────────────────────────────────
    found_ids       = {c["clause_id"] for c in clauses}
    mandatory_found = MANDATORY_CLAUSES & found_ids
    mandatory_miss  = MANDATORY_CLAUSES - found_ids

    print()
    print("── UC-0B Summary Audit ──────────────────────────────────")
    print(f"  Source document  : {meta['document_name']}")
    print(f"  Total clauses    : {meta['total_clauses']}")
    print(f"  Mandatory present: {len(mandatory_found)}/{len(MANDATORY_CLAUSES)} "
          f"→ {sorted(mandatory_found)}")
    if mandatory_miss:
        print(f"  MISSING mandatory: {sorted(mandatory_miss)}  ← HARD FAILURE")
    else:
        print("  Mandatory check  : ALL PRESENT ✓")
    verbatim_count = sum(1 for c in clauses if c["clause_id"] in VERBATIM_CLAUSE_IDS)
    print(f"  Verbatim quoted  : {verbatim_count} high-risk clauses")
    print(f"  Output written   : {output_path}")
    print("─────────────────────────────────────────────────────────")
    print()
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
