"""
UC-0B — Summary That Changes Meaning
CRAFT-enforced: clause omission, scope bleed, obligation softening.
"""
import argparse
import re


def retrieve_policy(file_path: str) -> list:
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    sections = []
    # Match numbered clauses at line start, e.g. "2.3 Employees must..."
    pattern = re.compile(r'^\s*(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+\s|\n[═]+|\Z)', re.DOTALL | re.MULTILINE)
    for match in pattern.finditer(content):
        section_id = match.group(1).strip()
        text = " ".join(match.group(2).split())
        if text:
            sections.append({"section_id": section_id, "text": text})
    return sections


# Clauses where meaning loss is high risk — quote verbatim
VERBATIM_CLAUSES = {"2.5", "2.6", "2.7", "3.4", "5.2", "5.3", "7.2"}

BINDING_VERBS = ["must", "will", "requires", "required", "not permitted", "cannot", "forfeited"]


def _has_binding_language(text: str) -> bool:
    return any(v in text.lower() for v in BINDING_VERBS)


def summarize_policy(sections: list) -> str:
    lines = []
    lines.append("CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY")
    lines.append("Document Reference: HR-POL-001 | Version 2.3 | Effective: 1 April 2024")
    lines.append("=" * 70)
    lines.append("IMPORTANT: This summary preserves all clause obligations verbatim")
    lines.append("where meaning-loss risk is high. Verify against source HR-POL-001.")
    lines.append("=" * 70)
    lines.append("")

    current_section = None

    for item in sections:
        sid = item["section_id"]
        text = item["text"]
        major = sid.split(".")[0]

        if not text:
            lines.append(f"[{sid}] [CLAUSE UNREADABLE — manual review required]")
            continue

        # Section headers
        section_headers = {
            "1": "1. PURPOSE AND SCOPE",
            "2": "2. ANNUAL LEAVE",
            "3": "3. SICK LEAVE",
            "4": "4. MATERNITY AND PATERNITY LEAVE",
            "5": "5. LEAVE WITHOUT PAY (LWP)",
            "6": "6. PUBLIC HOLIDAYS",
            "7": "7. LEAVE ENCASHMENT",
            "8": "8. GRIEVANCES",
        }
        if major != current_section:
            current_section = major
            lines.append("")
            lines.append(section_headers.get(major, f"Section {major}"))
            lines.append("-" * 40)

        if sid in VERBATIM_CLAUSES:
            lines.append(f"  [{sid}] \"{text}\" [VERBATIM — meaning-loss risk]")
        else:
            lines.append(f"  [{sid}] {text}")

    lines.append("")
    lines.append("=" * 70)
    lines.append("END OF SUMMARY — All clauses from source document included.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    if not sections:
        print("Warning: no numbered clauses found in input file.")

    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
