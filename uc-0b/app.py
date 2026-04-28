import argparse
import re
import sys
from pathlib import Path

CLAUSE_INVENTORY = {
    "2.3": {"core": "14-day advance notice required", "verb": "must"},
    "2.4": {"core": "Written approval required before leave commences. Verbal not valid.", "verb": "must"},
    "2.5": {"core": "Unapproved absence = LOP regardless of subsequent approval", "verb": "will"},
    "2.6": {"core": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.", "verb": "may / are forfeited"},
    "2.7": {"core": "Carry-forward days must be used Jan–Mar or forfeited", "verb": "must"},
    "3.2": {"core": "3+ consecutive sick days requires medical cert within 48hrs", "verb": "requires"},
    "3.4": {"core": "Sick leave before/after holiday requires cert regardless of duration", "verb": "requires"},
    "5.2": {"core": "LWP requires Department Head AND HR Director approval", "verb": "requires"},
    "5.3": {"core": "LWP >30 days requires Municipal Commissioner approval", "verb": "requires"},
    "7.2": {"core": "Leave encashment during service not permitted under any circumstances", "verb": "not permitted"},
}

SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
    "it is common practice",
    "in most cases",
]


def retrieve_policy(input_file: str) -> dict:
    path = Path(input_file)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {input_file}")
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        raise IOError(f"Cannot read policy file: {e}")

    sections = {}
    lines = content.split("\n")
    current_clause = None
    current_text = []

    for line in lines:
        if line.strip().startswith("═"):
            continue
        clause_match = re.match(r"^(\d+\.\d+)\s+(.+)$", line)
        section_match = re.match(r"^\d+\.\s+[A-Z]", line)
        if section_match:
            continue
        if clause_match:
            if current_clause:
                sections[current_clause] = " ".join(current_text)
            current_clause = clause_match.group(1)
            current_text = [clause_match.group(2)]
        elif current_clause and line.strip():
            current_text.append(line.strip())

    if current_clause:
        sections[current_clause] = " ".join(current_text)

    for clause_num in CLAUSE_INVENTORY:
        if clause_num not in sections:
            print(f"WARNING: Clause {clause_num} missing from policy document", file=sys.stderr)

    return sections


def summarize_policy(sections: dict, inventory: dict) -> str:
    missing_clauses = [c for c in inventory if c not in sections]
    if missing_clauses:
        raise ValueError(f"Summary violates enforcement rule: missing clauses {missing_clauses}")

    summary_lines = ["HR LEAVE POLICY SUMMARY", "=" * 50, ""]

    for clause_num in sorted(inventory.keys()):
        if clause_num not in sections:
            continue
        clause_text = sections[clause_num]
        info = inventory[clause_num]
        verb = info["verb"]
        core = info["core"]

        for phrase in SCOPE_BLEED_PHRASES:
            if phrase.lower() in clause_text.lower():
                raise ValueError(f"Scope bleed detected in clause {clause_num}: '{phrase}'")

        needs_verbatim = False
        multi_condition_core = "and" in core.lower() and ("department head" in core.lower() or "hr director" in core.lower() or "municipal commissioner" in core.lower())
        if multi_condition_core:
            required_entities = []
            if "department head" in core.lower():
                required_entities.append("department head")
            if "hr director" in core.lower():
                required_entities.append("hr director")
            if "municipal commissioner" in core.lower():
                required_entities.append("municipal commissioner")
            clause_lower = clause_text.lower()
            for entity in required_entities:
                if entity not in clause_lower:
                    needs_verbatim = True
                    break

        if needs_verbatim or len(clause_text) < 20:
            summary_lines.append(f"Clause {clause_num}: [VERBATIM - meaning loss if summarized]")
            summary_lines.append(f"  \"{clause_text}\"")
        else:
            summary_lines.append(f"Clause {clause_num}:")
            summary_lines.append(f"  Obligation: {core}")
            summary_lines.append(f"  Binding verb: {verb}")
            summary_lines.append(f"  Summary: {clause_text}")

        summary_lines.append("")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="HR Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections, CLAUSE_INVENTORY)

    output_path = Path(args.output)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
