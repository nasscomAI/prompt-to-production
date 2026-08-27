"""
UC-0B app.py — Clause-faithful policy summariser.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import os
import sys

CRITICAL_CLAUSES = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}

SECTION_TITLES = {
    "1": "Purpose and Scope",
    "2": "Annual Leave",
    "3": "Sick Leave",
    "4": "Maternity and Paternity Leave",
    "5": "Leave Without Pay (LWP)",
    "6": "Public Holidays",
    "7": "Leave Encashment",
    "8": "Grievances",
}

FORBIDDEN_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
    "common practice",
    "industry standard",
]


def extract_binding_verb(text):
    text_lower = text.lower()
    for phrase in ["is not permitted", "are forfeited", "cannot",
                    "must", "requires", "will", "shall", "may"]:
        if phrase in text_lower:
            return phrase
    return ""


def retrieve_policy(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Policy file not found: {filepath}")
    if not filepath.lower().endswith(".txt"):
        raise ValueError(f"Input must be a .txt file: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError(f"Policy file is empty: {filepath}")

    lines = content.split("\n")
    sections = {}
    clause_pattern = re.compile(r"^(\d+)\.(\d+)\s+(.*)")
    section_header_pattern = re.compile(r"^(\d+)\.\s+(.+)")
    continuation_pattern = re.compile(r"^\s{4}(.+)")

    current_clause = None

    for line in lines:
        stripped = line.rstrip()

        if section_header_pattern.match(stripped):
            current_clause = None
            continue

        clause_match = clause_pattern.match(stripped)
        if clause_match:
            sec = clause_match.group(1)
            clause_num = f"{sec}.{clause_match.group(2)}"
            text = clause_match.group(3)
            verb = extract_binding_verb(text)
            current_clause = {
                "number": clause_num,
                "text": text,
                "binding_verb": verb,
            }
            sections.setdefault(sec, []).append(current_clause)
            continue

        cont_match = continuation_pattern.match(stripped)
        if cont_match and current_clause is not None:
            current_clause["text"] += " " + cont_match.group(1).strip()
            current_verb = extract_binding_verb(
                current_clause["text"]
            )
            if current_verb:
                current_clause["binding_verb"] = current_verb

    if not sections:
        raise ValueError("No numbered clauses found in the policy file.")

    return sections


def summarize_policy(sections):
    lines = []

    for sec_num in sorted(sections.keys(), key=int):
        title = SECTION_TITLES.get(sec_num, f"Section {sec_num}")
        lines.append(f"\n{sec_num}. {title}")

        for clause in sections[sec_num]:
            num = clause["number"]
            text = clause["text"]
            verb = clause["binding_verb"]

            is_critical = num in CRITICAL_CLAUSES
            has_multi_condition = any(
                c in text.lower()
                for c in [" and ", " or ", "regardless", "within",
                          "except", "unless", "provided that"]
            )
            use_verbatim = is_critical or has_multi_condition

            if verb:
                label = f"[{verb}]"
            else:
                label = ""

            if use_verbatim:
                lines.append(f"    {num} {text} [VERBATIM] {label}".strip())
            else:
                lines.append(f"    {num} {text} {label}".strip())

    body = "\n".join(lines).strip()

    for phrase in FORBIDDEN_PHRASES:
        if phrase in body.lower():
            raise ValueError(
                f"Scope bleed detected — phrase not in source: '{phrase}'"
            )

    all_numbers = set()
    for clauses in sections.values():
        for c in clauses:
            all_numbers.add(c["number"])

    found_numbers = set(re.findall(r"\b\d+\.\d+\b", body))
    missing = all_numbers - found_numbers
    if missing:
        raise ValueError(
            f"Clauses missing from output: {', '.join(sorted(missing))}"
        )

    return body


def main():
    parser = argparse.ArgumentParser(
        description="Clause-faithful policy summariser"
    )
    parser.add_argument("--input", required=True,
                        help="Path to input .txt policy file")
    parser.add_argument("--output", required=True,
                        help="Path to output summary file")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        output_path = os.path.abspath(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)
            f.write("\n")
        print(f"Summary written to {output_path}")
    except (FileNotFoundError, ValueError, TypeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
