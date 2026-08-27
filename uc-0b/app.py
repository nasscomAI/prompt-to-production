import os
import re
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "data", "policy-documents", "policy_hr_leave.txt")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "summary_hr_leave.txt")

def read_policy(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Policy file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def parse_sections(text):
    lines = text.splitlines()
    sections = []
    current_heading = "PREAMBLE"
    current_lines = []
    for line in lines:
        stripped = line.strip()
        is_heading = (stripped.isupper() and len(stripped) > 3) or re.match(r'^(\d+\.|[IVX]+\.)\s+[A-Z]', stripped)
        if is_heading and stripped:
            if current_lines:
                sections.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = stripped
            current_lines = []
        else:
            if stripped:
                current_lines.append(line)
    if current_lines:
        sections.append((current_heading, "\n".join(current_lines).strip()))
    return sections

def count_clauses(text):
    pattern = r'^\s*(\d+\.|[a-z]\.|[ivxlIVXL]+\.|\(\d+\)|\([a-z]\))'
    return len(re.findall(pattern, text, re.MULTILINE))

def summarise_section(heading, body):
    clauses = []
    current_clause = []
    for line in body.splitlines():
        stripped = line.strip()
        if re.match(r'^(\d+\.|[a-z]\.|[ivxlIVXL]+\.|\(\d+\)|\([a-z]\))\s', stripped):
            if current_clause:
                clauses.append(" ".join(current_clause))
            current_clause = [stripped]
        else:
            if stripped:
                current_clause.append(stripped)
    if current_clause:
        clauses.append(" ".join(current_clause))
    if not clauses:
        return body.strip()
    summary_lines = []
    for clause in clauses:
        if re.search(r'\bshall\s+be\s+determined\b|\bas\s+appropriate\b|\bat\s+discretion\b', clause, re.IGNORECASE):
            summary_lines.append(f"  [AMBIGUOUS] {clause}")
        else:
            summary_lines.append(f"  - {clause}")
    return "\n".join(summary_lines)

def main():
    print(f"Reading: {INPUT_FILE}")
    policy_text = read_policy(INPUT_FILE)
    sections = parse_sections(policy_text)
    total_clauses = count_clauses(policy_text)
    lines = [f"POLICY SUMMARY — HR LEAVE POLICY", f"Generated: {date.today().isoformat()}", "="*60, ""]
    summarised = 0
    for heading, body in sections:
        lines.append(f"SECTION: {heading}")
        lines.append("-"*40)
        lines.append(summarise_section(heading, body))
        summarised += count_clauses(body)
        lines.append("")
    lines += ["="*60, "CLAUSE COVERAGE CHECK", f"  Total clauses found      : {total_clauses}", f"  Total clauses summarised : {summarised}", f"  Missing clauses          : {'None' if total_clauses == summarised else str(total_clauses - summarised) + ' REVIEW REQUIRED'}"]
    summary = "\n".join(lines)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Done! Summary written to: {OUTPUT_FILE}")
    print(summary[:300])

main()
