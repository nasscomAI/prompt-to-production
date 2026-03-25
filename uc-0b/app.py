"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re


CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+(.+)$")


def retrieve_policy(input_path: str) -> list:
    """
    Load policy text and return structured numbered clauses.
    Output format: list of dicts with keys section, clause, text.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    clauses = []
    current_section = ""
    current_clause = None

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue
        if set(line) == {"═"}:
            continue

        section_match = SECTION_RE.match(line)
        if section_match and CLAUSE_RE.match(line) is None:
            current_section = f"{section_match.group(1)}. {section_match.group(2)}"
            continue

        clause_match = CLAUSE_RE.match(line)
        if clause_match:
            if current_clause is not None:
                clauses.append(current_clause)
            current_clause = {
                "section": current_section,
                "clause": clause_match.group(1),
                "text": clause_match.group(2).strip(),
            }
            continue

        # Wrapped line that continues current clause text.
        if current_clause is not None:
            current_clause["text"] = f"{current_clause['text']} {line}".strip()

    if current_clause is not None:
        clauses.append(current_clause)

    if not clauses:
        raise ValueError("No numbered clauses found in policy file")

    return clauses


def _needs_verbatim(text: str) -> bool:
    risky_markers = [
        " and ",
        " or ",
        "regardless",
        "not valid",
        "not sufficient",
        "under any circumstances",
        "must",
        "requires",
    ]
    lowered = f" {text.lower()} "
    return any(marker in lowered for marker in risky_markers)


def summarize_policy(structured_sections: list) -> str:
    """
    Produce a compliant summary that preserves every numbered clause.
    Risky clauses are quoted verbatim and flagged.
    """
    if not structured_sections:
        raise ValueError("No structured sections provided")

    output_lines = [
        "HR Leave Policy Summary (Clause-Complete)",
        "",
    ]

    for item in structured_sections:
        clause_id = item["clause"]
        clause_text = " ".join(item["text"].split())

        if _needs_verbatim(clause_text):
            output_lines.append(f"{clause_id}: \"{clause_text}\" [VERBATIM]")
        else:
            output_lines.append(f"{clause_id}: {clause_text}")

    source_clause_ids = {item["clause"] for item in structured_sections}
    summary_clause_ids = {
        line.split(":", 1)[0]
        for line in output_lines
        if re.match(r"^\d+\.\d+:", line)
    }
    missing = sorted(source_clause_ids - summary_clause_ids)
    if missing:
        raise ValueError(f"Summary missing clauses: {', '.join(missing)}")

    return "\n".join(output_lines) + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt")
    parser.add_argument("--output", required=True, help="Path to output summary .txt")
    args = parser.parse_args()

    structured = retrieve_policy(args.input)
    summary = summarize_policy(structured)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
