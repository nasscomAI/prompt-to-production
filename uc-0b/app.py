"""
UC-0B app.py — Policy summarization for clause-preserving intent.
Build this using RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import os
import re

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(input_path: str):
    """Load a policy text file and return structured numbered sections."""
    if not isinstance(input_path, str):
        raise TypeError("input_path must be a string")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy input file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    if not text.strip():
        return []

    clauses = []
    # find explicit clause lines first
    for clause in REQUIRED_CLAUSES:
        pattern = rf"(?mi)^\s*{re.escape(clause)}\b.*$"
        match = re.search(pattern, text)
        if match:
            clause_text = match.group(0).strip()
            clauses.append({"clause": clause, "text": clause_text})
        else:
            # fallback: locate clause by standalone token in text
            token_pattern = rf"(?mi)(?:\b{re.escape(clause)}\b).*"
            match2 = re.search(token_pattern, text)
            if match2:
                # line-based fallback
                line = match2.group(0).strip()
                clauses.append({"clause": clause, "text": line})

    # maybe there are other clauses in file; include them too, preserving all available context
    # Here we can parse each clause from lines to ensure no truncation
    # with fallback to matching all numbered clauses if needed.
    return clauses


def summarize_policy(clauses):
    """Produce a summary that includes all required clauses and preserves condition fidelity."""
    if not isinstance(clauses, list):
        raise TypeError("clauses must be a list of clause objects")

    clause_map = {c.get("clause"): c.get("text") for c in clauses if isinstance(c, dict) and "clause" in c}

    missing = [c for c in REQUIRED_CLAUSES if c not in clause_map]
    flags = []

    summary_lines = []
    summary_lines.append("Policy summary for `policy_hr_leave.txt`:")
    summary_lines.append("")

    for clause in REQUIRED_CLAUSES:
        if clause in clause_map:
            # preserve exact source text as required by enforcement
            original = clause_map[clause].strip()
            summary_lines.append(f"Clause {clause}: \"{original}\"")
            summary_lines.append("(Verbatim quote to prevent meaning loss and condition drop.)")
            summary_lines.append("")
        else:
            summary_lines.append(f"Clause {clause}: MISSING (required clause not found in source).")
            summary_lines.append("")

    if missing:
        flags.append(f"Missing clauses: {', '.join(missing)}")
        flags.append("NEEDS_REVIEW")

    # Clause condition check warnings (simple heuristic for multi-condition issues)
    if "5.2" in clause_map and not re.search(r"Department Head.*HR Director|HR Director.*Department Head", clause_map["5.2"], re.I):
        flags.append("Clause 5.2 may be missing the dual approver condition; verify exact phrasing.")

    if flags:
        summary_lines.append("Flags:")
        for f in flags:
            summary_lines.append(f"- {f}")

    summary_text = "\n".join(summary_lines).strip() + "\n"
    return {
        "summary": summary_text,
        "flags": flags
    }


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Clause Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    policy_clauses = retrieve_policy(args.input)
    summary_obj = summarize_policy(policy_clauses)

    output_dir = os.path.dirname(os.path.abspath(args.output))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8", newline="") as out_f:
        out_f.write(summary_obj["summary"])

    if summary_obj.get("flags"):
        print("Summary generated with flags:", "; ".join(summary_obj.get("flags")))
    else:
        print("Summary generated with no flags.")

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
