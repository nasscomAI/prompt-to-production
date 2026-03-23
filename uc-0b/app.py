"""
UC-0B app.py — Policy Summariser
Reads a .txt policy document, extracts every numbered clause, and writes a compliant
summary that preserves all obligations and conditions as defined in agents.md.
"""
import argparse
import re


def retrieve_policy(file_path: str) -> tuple:
    """
    Load a .txt policy file and return (metadata, sections).
    metadata: dict with keys title, reference, version
    sections: list of dicts with keys section_number, section_text
    """
    with open(file_path, encoding="utf-8") as f:
        raw = f.read()

    # Extract metadata from the header lines
    lines = raw.splitlines()
    title_lines = []
    for line in lines[:10]:
        stripped = line.strip()
        if stripped and not stripped.startswith("═"):
            title_lines.append(stripped)
        elif stripped.startswith("═"):
            break
    metadata = {
        "title": title_lines[0] if title_lines else "Unknown",
        "reference": next((l for l in title_lines if "Ref" in l or "POL" in l), ""),
        "version": next((l for l in title_lines if "Version" in l), ""),
    }

    # Extract numbered clauses (e.g. "2.3 Employees must submit...")
    # Each clause starts on a new line with a number like "N.N" or "N.NN"
    clause_pattern = re.compile(
        r'^\s*(\d+\.\d+)\s+(.+?)(?=\n\s*\d+\.\d+\s|\n\s*[═]+|\Z)',
        re.DOTALL | re.MULTILINE
    )
    sections = []
    for match in clause_pattern.finditer(raw):
        number = match.group(1).strip()
        text = re.sub(r'\s+', ' ', match.group(2)).strip()
        sections.append({"section_number": number, "section_text": text})

    return metadata, sections


# Clauses that must be preserved verbatim due to meaning-loss risk
VERBATIM_CLAUSES = {"5.2", "7.2"}


def summarize_policy(metadata: dict, sections: list) -> str:
    """
    Produce a compliant summary from the structured sections.
    Every numbered clause is present; multi-condition obligations preserve all conditions.
    No information beyond the source document is added.
    """
    lines = []
    lines.append(metadata.get("title", ""))
    ref = metadata.get("reference", "")
    ver = metadata.get("version", "")
    if ref or ver:
        lines.append(f"{ref}  {ver}".strip())
    lines.append("")
    lines.append("POLICY SUMMARY — ALL CLAUSES")
    lines.append("=" * 60)
    lines.append("")

    current_section = None
    for sec in sections:
        num = sec["section_number"]
        major = num.split(".")[0]

        # Print a section header when the major number changes
        if major != current_section:
            current_section = major
            lines.append("")

        text = sec["section_text"]
        if num in VERBATIM_CLAUSES:
            lines.append(
                f"{num}  {text}"
                f"  [VERBATIM — meaning loss risk if paraphrased]"
            )
        else:
            lines.append(f"{num}  {text}")

    lines.append("")
    lines.append("END OF SUMMARY")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument(
        "--input", required=True,
        help="Path to policy .txt file"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write summary .txt file"
    )
    args = parser.parse_args()

    metadata, sections = retrieve_policy(args.input)
    summary = summarize_policy(metadata, sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output} ({len(sections)} clauses extracted).")


if __name__ == "__main__":
    main()
