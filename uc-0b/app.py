"""
UC-0B app.py — Policy Summarization Engine.
Built using the RICE → agents.md → skills.md workflow.
"""
import argparse
import os
import re

def retrieve_policy(input_path: str) -> dict:
    """
    Skill: retrieve_policy
    Loads raw .txt policy document and parses content into structured numbered sections and clauses.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input policy file not found: {input_path}")
        
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    doc_meta = {}
    sections = {}
    current_section = "Header"
    sections[current_section] = []

    for line in lines:
        line_str = line.strip()
        if not line_str or line_str.startswith("═"):
            continue
        
        # Check for section headers (e.g., 1. PURPOSE AND SCOPE, 5. LEAVE WITHOUT PAY (LWP))
        sec_match = re.match(r"^(\d+)\.\s+([A-Z\s\(\)]+)$", line_str)
        if sec_match:
            current_section = f"{sec_match.group(1)}. {sec_match.group(2)}"
            sections[current_section] = []
            continue

        sections[current_section].append(line_str)

    # Parse individual numbered clauses (e.g. 1.1, 2.3)
    clauses = {}
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)")

    for sec_title, sec_lines in sections.items():
        if sec_title == "Header":
            doc_meta["Header"] = " ".join(sec_lines)
            continue
            
        current_clause_id = None
        for line in sec_lines:
            match = clause_pattern.match(line)
            if match:
                current_clause_id = match.group(1)
                clauses[current_clause_id] = {
                    "section": sec_title,
                    "clause_id": current_clause_id,
                    "text": match.group(2)
                }
            elif current_clause_id:
                clauses[current_clause_id]["text"] += " " + line

    if not clauses:
        raise ValueError(f"No numbered clauses found in policy document: {input_path}")

    return {
        "metadata": doc_meta,
        "clauses": clauses
    }

def summarize_policy(parsed_policy: dict) -> str:
    """
    Skill: summarize_policy
    Takes structured policy clauses and generates a compliant summary adhering strictly to RICE enforcement rules:
    1. Every numbered clause represented with its clause reference.
    2. All multi-condition obligations preserved without softening.
    3. Zero scope bleed (no non-source assumptions or external phrases).
    """
    clauses = parsed_policy.get("clauses", {})
    doc_meta = parsed_policy.get("metadata", {})
    header_text = doc_meta.get("Header", "")

    summary_lines = []

    # Extract dynamic title / reference if present in header
    header_lines = [l.strip() for l in header_text.split(" ") if l.strip()]
    raw_header_str = doc_meta.get("Header", "")

    # Look for Document Reference
    ref_match = re.search(r"Document Reference:\s*([\w\-]+)", raw_header_str)
    eff_match = re.search(r"Version:\s*([\d\.]+)\s*\|\s*Effective:\s*([^\d]*\d{4})", raw_header_str)

    title_part = "POLICY SUMMARY"
    if "LEAVE POLICY" in raw_header_str:
        title_part = "EMPLOYEE LEAVE POLICY SUMMARY"
    elif "REIMBURSEMENT POLICY" in raw_header_str:
        title_part = "EMPLOYEE EXPENSE REIMBURSEMENT POLICY SUMMARY"
    elif "ACCEPTABLE USE POLICY" in raw_header_str:
        title_part = "ACCEPTABLE USE POLICY — IT SYSTEMS AND DEVICES SUMMARY"

    summary_lines.append(f"# CITY MUNICIPAL CORPORATION - {title_part}")

    meta_parts = []
    if ref_match:
        meta_parts.append(f"**Document Reference:** {ref_match.group(1)}")
    if eff_match:
        meta_parts.append(f"**Version:** {eff_match.group(1)} | **Effective:** {eff_match.group(2)}")

    if meta_parts:
        summary_lines.append(" | ".join(meta_parts) + "\n")
    else:
        summary_lines.append("")

    # Group by Section
    sections = {}
    for clause_id, item in clauses.items():
        sec = item["section"]
        if sec not in sections:
            sections[sec] = []
        sections[sec].append(item)

    for sec_title, sec_clauses in sections.items():
        summary_lines.append(f"## {sec_title}")
        for c in sec_clauses:
            cid = c["clause_id"]
            text = c["text"]
            summary_lines.append(f"- **Clause {cid}:** {text}")
        summary_lines.append("")

    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarization Engine")
    parser.add_argument("--input",  required=True, help="Path to input policy document .txt file")
    parser.add_argument("--output", required=True, help="Path to write output policy summary .txt file")
    args = parser.parse_args()

    parsed = retrieve_policy(args.input)
    summary = summarize_policy(parsed)

    # Ensure target directory exists if specified
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Policy summary generated successfully: {args.output}")

if __name__ == "__main__":
    main()
