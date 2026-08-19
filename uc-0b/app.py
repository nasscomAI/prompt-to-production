"""
UC-0B — Policy Summarizer (Lossless Clause-Preserving Summarizer)

Implements the enforcement rules from agents.md and skills from skills.md:
- retrieve_policy: loads a .txt policy file and parses header + sections + clauses.
- summarize_policy: renders a structured, lossless summary that preserves every
  numbered clause and every multi-condition obligation verbatim — no clause
  omission, no condition drop, no obligation softening, no scope bleed.

Classification only: never edits the source, never adds external information,
and only renders what the document actually says.
"""
import argparse
import re
from pathlib import Path

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Za-z&()\s\-]+)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SEPARATOR_RE = re.compile(r"^[=\u2550\u2500\u2501\-\s]+$")


def _collapse(text: str) -> str:
    """Collapse runs of whitespace into a single space."""
    return re.sub(r"\s+", " ", text).strip()


def retrieve_policy(input_path: str) -> dict:
    """Load text policy file and return header plus structured sections/clauses."""
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input policy file not found: {input_path}")

    text = path.read_text(encoding="utf-8")

    header = []
    sections = []
    current_section = None
    current_clause = None

    def flush_clause():
        nonlocal current_clause
        if current_clause is None:
            return
        current_clause["text"] = _collapse(current_clause["text"])
        if current_clause["text"]:
            current_section["clauses"].append(current_clause)
        current_clause = None

    def flush_section():
        nonlocal current_section
        if current_section is None:
            return
        flush_clause()
        if current_section["clauses"]:
            sections.append(current_section)
        current_section = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or SEPARATOR_RE.match(stripped):
            continue

        if SECTION_RE.match(stripped) and not CLAUSE_RE.match(stripped):
            flush_section()
            current_section = {
                "title": f"{SECTION_RE.match(stripped).group(1)}. {SECTION_RE.match(stripped).group(2).strip()}",
                "clauses": [],
            }
            continue

        clause_match = CLAUSE_RE.match(stripped)
        if clause_match:
            flush_clause()
            current_clause = {"num": clause_match.group(1), "text": clause_match.group(2)}
        elif current_clause is not None:
            current_clause["text"] += " " + stripped
        elif current_section is None and not sections:
            header.append(stripped)

    flush_section()

    return {
        "raw_text": text,
        "header": header,
        "sections": sections,
        "clause_count": sum(len(s["clauses"]) for s in sections),
    }


def summarize_policy(policy_data: dict) -> str:
    """Render a lossless, clause-by-clause summary of the policy."""
    header = policy_data.get("header", [])
    sections = policy_data.get("sections", [])

    title = header[2] if len(header) > 2 else "POLICY SUMMARY"
    doc_ref = next(
        (l.split(":", 1)[1].strip() for l in header if "Document Reference" in l),
        "N/A",
    )
    version_line = next((l for l in header if l.lower().startswith("version")), "")

    lines = [
        "=" * 60,
        f"SUMMARY: {title}",
        f"Document Reference: {doc_ref}",
    ]
    if version_line:
        lines.append(version_line)
    lines.append("=" * 60)
    lines.append("")

    for section in sections:
        lines.append(section["title"])
        for clause in section["clauses"]:
            lines.append(f"- Clause {clause['num']}: {clause['text']}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    data = retrieve_policy(args.input)
    summary = summarize_policy(data)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")
    print(
        f"Done. Summary written to {args.output} "
        f"({data['clause_count']} clauses preserved)"
    )


if __name__ == "__main__":
    main()
