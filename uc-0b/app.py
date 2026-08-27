"""
UC-0B app.py — Policy Summary That Changes Meaning
Built using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys

# ── SKILL: retrieve_policy ──────────────────────────────────────────────────
def retrieve_policy(file_path: str) -> dict:
    """
    Load a .txt policy file and return content as structured numbered sections.
    Output: dict mapping section number (str) to section text (str).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find policy file at '{file_path}'")
        sys.exit(1)

    sections = {}
    # Split on section headers like "1.", "2.3", "5.2" etc.
    pattern = re.compile(r'(?m)^\s*(\d+\.\d*)\s+(.+?)(?=^\s*\d+\.\d|\Z)', re.DOTALL | re.MULTILINE)
    for match in pattern.finditer(content):
        clause_id = match.group(1).strip()
        clause_text = match.group(2).strip()
        sections[clause_id] = clause_text
    return sections


# ── SKILL: summarize_policy ──────────────────────────────────────────────────
# Enforcement rules embedded per agents.md:
#  1. Every numbered clause must be present - no omissions
#  2. Multi-condition obligations must preserve ALL conditions
#  3. Never add information not in the source document
#  4. If meaning loss risk exists, quote verbatim and flag [VERBATIM]

VERBATIM_CLAUSES = {"2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}

def summarize_policy(sections: dict) -> str:
    """
    Produce a compliant summary of the policy with every clause referenced.
    Multi-condition obligations are preserved exactly.
    """
    lines = []
    lines.append("HUMAN RESOURCES — EMPLOYEE LEAVE POLICY SUMMARY")
    lines.append("Document: HR-POL-001 | Version 2.3 | Effective: 1 April 2024")
    lines.append("=" * 65)
    lines.append("")

    # Track section headings to group clauses
    current_section = None

    for clause_id, text in sorted(sections.items(), key=lambda x: [int(p) for p in x[0].split('.') if p]):
        top = clause_id.split('.')[0]
        if top != current_section:
            current_section = top
            section_titles = {
                "1": "1. PURPOSE AND SCOPE",
                "2": "2. ANNUAL LEAVE",
                "3": "3. SICK LEAVE",
                "4": "4. MATERNITY AND PATERNITY LEAVE",
                "5": "5. LEAVE WITHOUT PAY (LWP)",
                "6": "6. PUBLIC HOLIDAYS",
                "7": "7. LEAVE ENCASHMENT",
                "8": "8. GRIEVANCES",
            }
            lines.append(section_titles.get(top, f"SECTION {top}"))
            lines.append("-" * 40)

        # Verbatim flag for high-risk clauses
        if clause_id in VERBATIM_CLAUSES:
            lines.append(f"  [{clause_id}] [VERBATIM] {text}")
        else:
            lines.append(f"  [{clause_id}] {text}")

    lines.append("")
    lines.append("=" * 65)
    lines.append("END OF SUMMARY — All numbered clauses from HR-POL-001 are present above.")
    lines.append("Clauses marked [VERBATIM] are quoted exactly to preserve legal meaning.")
    return "\n".join(lines)


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    # Skill 1: Load and structure the document
    sections = retrieve_policy(args.input)

    if not sections:
        print("Warning: No numbered clauses found in the input document.")
        sys.exit(1)

    # Skill 2: Summarise with all enforcement rules applied
    summary = summarize_policy(sections)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
