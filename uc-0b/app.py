"""
UC-0B — Policy Summariser: Summary That Changes Meaning
Reads a CMC HR Leave Policy text file (policy_hr_leave.txt) and produces a
clause-by-clause compliant summary.

Enforcement rules from agents.md:
1. All 10 critical clauses must appear in the summary.
2. Multi-condition obligations (e.g. Clause 5.2 — dual approver) are quoted verbatim.
3. No scope bleed: no phrases not present in the source document.
4. Binding verbs (must, will, requires, not permitted) are preserved.

Run command:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""
import argparse
import re
import sys

# --- Enforcement: these clauses MUST appear in the output ---
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# --- Clauses where verbatim quoting is required (risk of condition drop) ---
VERBATIM_CLAUSES = {"5.2", "5.3"}


def retrieve_policy(file_path: str) -> dict:
    """
    Load a .txt policy file and return structured sections keyed by clause number.
    Returns: {
        "document_title": str,
        "document_reference": str,
        "sections": { "2.3": "text...", "5.2": "text...", ... }
    }
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    if not content.strip():
        raise ValueError("Policy file is empty — cannot summarise.")

    lines = content.splitlines()
    sections = {}
    unparsed = []

    # Extract document metadata
    document_title = lines[0].strip() if lines else "Unknown"
    doc_ref_match = re.search(r"Document Reference:\s*(\S+)", content)
    doc_ref = doc_ref_match.group(1) if doc_ref_match else "Unknown"

    # Parse sections by looking for lines starting with a clause number pattern (e.g. "2.3 ")
    current_clause = None
    current_text_lines = []

    for line in lines:
        stripped = line.strip()
        clause_match = re.match(r'^(\d+\.\d+)\s+(.+)$', stripped)
        if clause_match:
            # Save previous
            if current_clause:
                sections[current_clause] = " ".join(current_text_lines).strip()
            current_clause = clause_match.group(1)
            current_text_lines = [clause_match.group(2)]
        elif current_clause and stripped and not stripped.startswith("═"):
            # Continuation of current clause
            current_text_lines.append(stripped)
        elif not current_clause and stripped and not stripped.startswith("═"):
            unparsed.append(stripped)

    # Save last clause
    if current_clause:
        sections[current_clause] = " ".join(current_text_lines).strip()

    if unparsed:
        print(f"[WARN] {len(unparsed)} unparsed lines found.", file=sys.stderr)

    return {
        "document_title": document_title,
        "document_reference": doc_ref,
        "sections": sections,
    }


def summarize_policy(policy_data: dict, required_clauses: list[str]) -> str:
    """
    Produce a clause-by-clause compliant summary.
    Verbatim-quotes multi-condition clauses to prevent condition drop.
    Raises ValueError if any required clause is missing.
    """
    sections = policy_data["sections"]
    doc_ref = policy_data["document_reference"]
    doc_title = policy_data["document_title"]

    lines = []
    lines.append(f"POLICY SUMMARY — {doc_title}")
    lines.append(f"Source: {doc_ref}")
    lines.append("=" * 60)
    lines.append("")
    lines.append("CRITICAL CLAUSES SUMMARY")
    lines.append("-" * 60)

    for clause_id in required_clauses:
        text = sections.get(clause_id)
        if not text:
            lines.append(f"  [{clause_id}] *** CLAUSE NOT FOUND IN DOCUMENT ***")
            continue

        if clause_id in VERBATIM_CLAUSES:
            lines.append(f"  [{clause_id}] [QUOTED VERBATIM — summarisation would drop a condition]")
            lines.append(f"         \"{text}\"")
        else:
            lines.append(f"  [{clause_id}] {text}")

    lines.append("")
    lines.append("ALL NUMBERED CLAUSES (complete reference)")
    lines.append("-" * 60)

    # Sort clause numbers numerically for complete reference
    all_clause_ids = sorted(
        sections.keys(),
        key=lambda x: [int(p) for p in x.split(".") if p.isdigit()]
    )
    for clause_id in all_clause_ids:
        text = sections[clause_id]
        if clause_id in VERBATIM_CLAUSES:
            lines.append(f"  [{clause_id}] [QUOTED VERBATIM] \"{text}\"")
        else:
            lines.append(f"  [{clause_id}] {text}")

    summary = "\n".join(lines)

    # --- Enforcement: verify all required clauses are present ---
    missing = [c for c in required_clauses if c not in sections]
    if missing:
        raise ValueError(
            f"Summary is INCOMPLETE. Missing required clauses: {', '.join(missing)}. "
            "These clauses were not found in the source document."
        )

    return summary


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    print(f"Loading policy: {args.input}")
    policy_data = retrieve_policy(args.input)

    num_sections = len(policy_data["sections"])
    print(f"Parsed {num_sections} numbered clauses from {policy_data['document_reference']}.")

    print(f"Generating summary (enforcing {len(REQUIRED_CLAUSES)} required clauses)...")
    try:
        summary = summarize_policy(policy_data, REQUIRED_CLAUSES)
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
