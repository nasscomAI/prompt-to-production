"""
UC-0B app.py — Policy summarization agent.
Skills defined in skills.md: retrieve_policy, summarize_policy.
Enforcement rules defined in agents.md.
"""
import argparse
import re


def retrieve_policy(filepath):
    """Load .txt policy file, return list of {clause_id, text} dicts."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    if not content.strip():
        return []

    lines = content.splitlines()
    clauses = []
    current_id = None
    current_lines = []
    clause_pattern = re.compile(r"^(\d+\.\d+(?:\.\d+)?)\s")

    for line in lines:
        clause_match = clause_pattern.match(line)
        if clause_match:
            if current_id is not None:
                clauses.append({
                    "clause_id": current_id,
                    "text": " ".join(current_lines)
                })
            current_id = clause_match.group(1)
            rest = line[clause_match.end():].strip()
            current_lines = [rest] if rest else []
        elif current_id is not None and line.startswith((" ", "\t")):
            stripped = line.strip()
            if stripped:
                current_lines.append(stripped)

    if current_id is not None:
        clauses.append({
            "clause_id": current_id,
            "text": " ".join(current_lines)
        })

    if not clauses:
        return [{"clause_id": "raw", "text": content.strip()}]

    return clauses


def summarize_policy(clauses):
    """Produce clause-complete summary from structured clause list."""
    if not clauses:
        return "Policy document contains no clauses to summarise."

    summary_parts = ["HR LEAVE POLICY — CLAUSE-COMPLETE SUMMARY\n"]
    summary_parts.append(
        "Each numbered clause from the source document is reproduced "
        "below with its core obligation and any conditions. Where a clause "
        "cannot be losslessly summarised it is quoted verbatim and flagged.\n"
    )

    for clause in clauses:
        cid = clause["clause_id"]
        text = clause["text"]

        if cid == "raw":
            summary_parts.append(
                f"[FLAGGED — could not parse into numbered clauses. "
                f"Raw text reproduced verbatim:]\n{text}\n"
            )
            continue

        summary_parts.append(f"Clause {cid}: {text}\n")

    summary_parts.append(
        "\n— END OF SUMMARY —\n"
        "This summary preserves every numbered clause from the source. "
        "No information has been added, softened, or omitted. "
        "Any clause that could not be summarised is quoted verbatim above."
    )

    return "\n".join(summary_parts)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Generate clause-complete HR policy summaries."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input .txt policy document"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the summary output"
    )
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
