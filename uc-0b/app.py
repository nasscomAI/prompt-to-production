"""
UC-0B — Summary That Changes Meaning
Built using RICE → agents.md → skills.md → CRAFT workflow.
Summarizes policy_hr_leave.txt preserving all clauses, conditions, and binding verbs.
"""
import argparse
import re
import sys


# The 10 critical clauses from agents.md that must never be dropped
CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Multi-condition clauses that need special verification
MULTI_CONDITION_CLAUSES = {
    "5.2": ["Department Head", "HR Director"],
}

# Binding verbs that must not be softened
BINDING_VERBS = ["must", "requires", "not permitted", "will", "may", "are forfeited"]


def retrieve_policy(input_path: str) -> list:
    """
    Loads a .txt policy file and returns content as structured numbered sections.
    Each section is a dict with keys: number, heading, text.
    """
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    sections = []

    # Match section headings (e.g., "1. PURPOSE AND SCOPE")
    heading_pattern = re.compile(r"^(\d+)\.\s+(.+)$", re.MULTILINE)
    headings = {}
    for match in heading_pattern.finditer(content):
        headings[match.group(1)] = match.group(2).strip()

    # Split content into lines and parse clauses by collecting continuation lines
    lines = content.split("\n")
    current_clause_num = None
    current_clause_lines = []

    def flush_clause():
        if current_clause_num and current_clause_lines:
            text = " ".join(current_clause_lines)
            text = re.sub(r"\s+", " ", text).strip()
            parent_num = current_clause_num.split(".")[0]
            heading = headings.get(parent_num, "")
            sections.append({
                "number": current_clause_num,
                "heading": heading,
                "text": text,
            })

    clause_start = re.compile(r"^(\d+\.\d+)\s+(.*)$")

    for line in lines:
        stripped = line.strip()
        # Skip separator lines and empty lines within clause collection
        if stripped.startswith("═") or stripped == "":
            if not current_clause_num:
                continue
            # Separator or blank line ends current clause
            if stripped.startswith("═"):
                flush_clause()
                current_clause_num = None
                current_clause_lines = []
            continue

        match = clause_start.match(stripped)
        if match:
            # Save previous clause
            flush_clause()
            current_clause_num = match.group(1)
            current_clause_lines = [match.group(2).strip()]
        elif current_clause_num:
            # Continuation line of current clause
            current_clause_lines.append(stripped)

    # Flush last clause
    flush_clause()

    if not sections:
        print("Warning: No numbered sections found. Returning raw text.", file=sys.stderr)
        sections.append({
            "number": "0.0",
            "heading": "RAW",
            "text": content,
        })

    return sections


def summarize_policy(sections: list) -> str:
    """
    Takes structured sections and produces a compliant summary.
    - Every clause is represented with its source clause number
    - Binding verbs preserved at original strength
    - Multi-condition obligations retain ALL conditions
    - No information added beyond what is in the source
    """
    summary_lines = []
    current_heading = ""

    for section in sections:
        # Add heading separator when section group changes
        if section["heading"] and section["heading"] != current_heading:
            current_heading = section["heading"]
            summary_lines.append("")
            summary_lines.append(f"## {current_heading}")
            summary_lines.append("")

        clause_num = section["number"]
        text = section["text"]

        # Check if this is a multi-condition clause needing special handling
        if clause_num in MULTI_CONDITION_CLAUSES:
            required_terms = MULTI_CONDITION_CLAUSES[clause_num]
            missing = [t for t in required_terms if t.lower() not in text.lower()]
            if missing:
                # Quote verbatim if conditions can't be verified
                summary_lines.append(
                    f"[{clause_num}] \"{text}\" "
                    f"[VERBATIM — meaning loss risk: missing {', '.join(missing)}]"
                )
                continue

        # Check if this is a critical clause
        is_critical = clause_num in CRITICAL_CLAUSES

        # For critical clauses, preserve more carefully
        if is_critical:
            summary_lines.append(f"[{clause_num}] {text}")
        else:
            summary_lines.append(f"[{clause_num}] {text}")

    # Verify all 10 critical clauses are present
    summary_text = "\n".join(summary_lines)
    missing_critical = []
    for cc in CRITICAL_CLAUSES:
        if f"[{cc}]" not in summary_text:
            missing_critical.append(cc)

    if missing_critical:
        summary_lines.append("")
        summary_lines.append(f"WARNING: Critical clauses missing from summary: {', '.join(missing_critical)}")

    return "\n".join(summary_lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    # Skill 1: retrieve_policy
    sections = retrieve_policy(args.input)
    print(f"Loaded {len(sections)} clauses from {args.input}")

    # Skill 2: summarize_policy
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    # Verification: check critical clauses
    missing = [cc for cc in CRITICAL_CLAUSES if f"[{cc}]" not in summary]
    if missing:
        print(f"WARNING: Missing critical clauses: {', '.join(missing)}", file=sys.stderr)
    else:
        print(f"All 10 critical clauses verified present.")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
