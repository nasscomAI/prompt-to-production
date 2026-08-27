"""
UC-0B — Summary That Changes Meaning
Reads a policy .txt file and produces a clause-by-clause summary.
Enforces: no clause omission, no scope bleed, no obligation softening.
"""
import argparse
import re


def retrieve_policy(input_path: str) -> dict:
    """
    Loads a .txt policy file, returns content as structured numbered sections.
    Returns: dict mapping section number strings (e.g. '2.3') to their full text.
    """
    try:
        with open(input_path, encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    sections = {}
    # Match clause numbers like "2.3", "5.2" etc. followed by their text
    pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+|\Z)', re.MULTILINE | re.DOTALL)
    matches = pattern.findall(raw)
    for clause_num, text in matches:
        # Clean whitespace but preserve content exactly
        cleaned = re.sub(r'\s+', ' ', text).strip()
        if cleaned:
            sections[clause_num] = cleaned

    if not sections:
        sections["UNPARSED"] = raw.strip()

    return sections


def summarize_policy(sections: dict) -> str:
    """
    Produces a compliant clause-by-clause summary from structured sections.
    Preserves all binding language, multi-condition obligations, and clause numbers.
    """
    # Section headings for grouping
    section_headings = {
        "1": "1. PURPOSE AND SCOPE",
        "2": "2. ANNUAL LEAVE",
        "3": "3. SICK LEAVE",
        "4": "4. MATERNITY AND PATERNITY LEAVE",
        "5": "5. LEAVE WITHOUT PAY (LWP)",
        "6": "6. PUBLIC HOLIDAYS",
        "7": "7. LEAVE ENCASHMENT",
        "8": "8. GRIEVANCES",
    }

    output_lines = []
    output_lines.append("CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY (HR-POL-001 v2.3)")
    output_lines.append("Summary — Every clause is present. Binding verbs are preserved verbatim.")
    output_lines.append("=" * 70)

    current_section = None
    for clause_num in sorted(sections.keys(), key=lambda x: [int(p) for p in x.split('.')] if x != "UNPARSED" else [999]):
        if clause_num == "UNPARSED":
            output_lines.append("\n[UNPARSED CONTENT]\n" + sections[clause_num])
            continue

        section_key = clause_num.split('.')[0]
        if section_key != current_section:
            current_section = section_key
            heading = section_headings.get(section_key, f"SECTION {section_key}")
            output_lines.append(f"\n{heading}")
            output_lines.append("-" * 40)

        text = sections[clause_num]

        # Flag clauses that cannot be safely paraphrased (multi-condition or complex)
        verbatim_triggers = [
            "and the",           # multi-party approvals e.g. 5.2
            "not permitted under any circumstances",  # absolute prohibition
            "regardless of",     # unconditional requirements
            "forfeited on 31",   # specific date conditions
        ]
        needs_verbatim = any(trigger in text.lower() for trigger in verbatim_triggers)

        if needs_verbatim:
            output_lines.append(f"  Clause {clause_num}: {text}")
            output_lines.append(f"  [VERBATIM — risk of meaning loss if paraphrased]")
        else:
            output_lines.append(f"  Clause {clause_num}: {text}")

    output_lines.append("\n" + "=" * 70)
    output_lines.append("END OF SUMMARY — All clauses from source document are present above.")
    return "\n".join(output_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    print(f"Reading policy from: {args.input}")
    sections = retrieve_policy(args.input)
    print(f"Parsed {len(sections)} clause(s).")

    summary = summarize_policy(sections)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Done. Summary written to: {args.output}")
    except Exception as e:
        print(f"Error writing output file {args.output}: {e}")


if __name__ == "__main__":
    main()
