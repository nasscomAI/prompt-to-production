"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path


def retrieve_policy(input_path: str) -> dict:
    """
    Skill: retrieve_policy
    Loads .txt policy file, returns content as structured numbered sections and clauses.
    """
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Policy document not found at: {input_path}")

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    lines = [line.strip() for line in text.splitlines()]

    metadata = []
    sections = []
    current_section = None
    current_clause_num = None
    current_clause_lines = []

    # Regex patterns
    section_pattern = re.compile(r"^(\d+)\.\s+([A-Z\s\(\)]+)$")
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)$")

    for line in lines:
        if not line or line.startswith("═"):
            continue

        sec_match = section_pattern.match(line)
        if sec_match:
            # Save previous clause if any
            if current_section and current_clause_num:
                current_section["clauses"].append({
                    "number": current_clause_num,
                    "text": " ".join(current_clause_lines)
                })
                current_clause_num = None
                current_clause_lines = []

            # Save previous section if any
            if current_section:
                sections.append(current_section)

            sec_num = sec_match.group(1)
            sec_title = sec_match.group(2).strip()
            current_section = {
                "number": sec_num,
                "title": sec_title,
                "raw_header": line,
                "clauses": []
            }
            continue

        clause_match = clause_pattern.match(line)
        if clause_match:
            if current_section and current_clause_num:
                current_section["clauses"].append({
                    "number": current_clause_num,
                    "text": " ".join(current_clause_lines)
                })
                current_clause_lines = []

            current_clause_num = clause_match.group(1)
            current_clause_lines = [clause_match.group(2).strip()]
            continue

        if current_clause_num:
            current_clause_lines.append(line)
        elif not current_section:
            metadata.append(line)

    # Flush last clause & section
    if current_section and current_clause_num:
        current_section["clauses"].append({
            "number": current_clause_num,
            "text": " ".join(current_clause_lines)
        })
    if current_section:
        sections.append(current_section)

    return {
        "metadata": metadata,
        "sections": sections
    }


def summarize_policy(policy_data: dict) -> str:
    """
    Skill: summarize_policy
    Takes structured sections and produces a compliant, zero-information-loss policy summary
    preserving every numbered clause, binding verbs, multi-condition obligations, and clause citations.
    """
    summary_lines = []
    summary_lines.append("POLICY DOCUMENT SUMMARY")
    summary_lines.append("=======================")

    for meta in policy_data.get("metadata", []):
        if meta:
            summary_lines.append(meta)
    summary_lines.append("")

    summary_lines.append("SUMMARY OF CLAUSES AND BINDING OBLIGATIONS:")
    summary_lines.append("-------------------------------------------")

    for section in policy_data.get("sections", []):
        sec_num = section["number"]
        sec_title = section["title"]
        summary_lines.append(f"\nSECTION {sec_num}: {sec_title}")

        for clause in section["clauses"]:
            c_num = clause["number"]
            c_text = clause["text"]
            summary_lines.append(f"  Clause {c_num}: {c_text}")

    summary_lines.append("\n=======================")
    summary_lines.append("END OF SUMMARY")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument(
        "--input",
        default="../data/policy-documents/policy_hr_leave.txt",
        help="Path to input policy document .txt file"
    )
    parser.add_argument(
        "--output",
        default="summary_hr_leave.txt",
        help="Path to output summary file"
    )

    args = parser.parse_args()

    # Step 1: Retrieve and parse policy document
    policy_data = retrieve_policy(args.input)

    # Step 2: Generate zero-information-loss summary
    summary_text = summarize_policy(policy_data)

    # Step 3: Write summary to output file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"Successfully generated policy summary at: {args.output}")


if __name__ == "__main__":
    main()

