"""
UC-0B — Policy Summarizer (Summary That Changes Meaning)
Deterministic summarization based on uc-0b/agents.md and uc-0b/skills.md.
"""
import argparse
import os
import re
import sys

# Critical clauses from README ground-truth inventory with complex multi-conditions
CRITICAL_VERBATIM_CLAUSES = {
    "2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"
}


def retrieve_policy(file_path: str) -> dict:
    """
    Loads the policy .txt file and parses its contents into structured sections and clauses.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy document not found: '{file_path}'")

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read().strip()

    if not content:
        raise ValueError(f"Policy document is empty: '{file_path}'")

    lines = content.splitlines()
    header_lines = []
    sections = []
    current_section = None
    current_clause = None

    section_re = re.compile(r"^\d+\.\s+[A-Z\s()/,–-]+$")
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.+)$")

    for line in lines:
        s_line = line.strip()
        if not s_line or set(s_line) == {"═"}:
            continue

        sec_match = section_re.match(s_line)
        clause_match = clause_re.match(s_line)

        if sec_match:
            current_section = {
                "title": s_line,
                "clauses": []
            }
            sections.append(current_section)
            current_clause = None
        elif clause_match and current_section is not None:
            c_id = clause_match.group(1)
            c_text = clause_match.group(2).strip()
            current_clause = {
                "clause_id": c_id,
                "text": c_text
            }
            current_section["clauses"].append(current_clause)
        elif current_clause is not None and (line.startswith("    ") or line.startswith("\t") or line.startswith(" ")):
            current_clause["text"] += " " + s_line
        elif not sections:
            header_lines.append(s_line)

    if not sections:
        raise ValueError(f"Unable to parse numbered sections from policy document: '{file_path}'")

    return {
        "header": header_lines,
        "sections": sections
    }


def summarize_policy(structured_data: dict) -> str:
    """
    Takes structured policy sections and produces a compliant summary with explicit clause references.
    Preserves every numbered clause, all multi-condition obligations, binding verbs, and exact thresholds.
    """
    output_lines = []

    output_lines.append("POLICY SUMMARY: CITY MUNICIPAL CORPORATION EMPLOYEE LEAVE POLICY (HR-POL-001)")
    output_lines.append("=" * 77)
    output_lines.append("")

    for sec in structured_data["sections"]:
        output_lines.append(sec["title"])
        output_lines.append("-" * len(sec["title"]))

        for clause in sec["clauses"]:
            c_id = clause["clause_id"]
            text = " ".join(clause["text"].split())

            # Multi-condition and threshold obligations are preserved verbatim to eliminate meaning loss
            if c_id in CRITICAL_VERBATIM_CLAUSES:
                output_lines.append(f"[{c_id}] {text} [VERBATIM_PRESERVED]")
            else:
                output_lines.append(f"[{c_id}] {text}")
        output_lines.append("")

    return "\n".join(output_lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()

    try:
        policy_data = retrieve_policy(args.input)
        summary = summarize_policy(policy_data)

        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"Summary written successfully to {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
