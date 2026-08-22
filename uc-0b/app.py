"""
UC-0B app.py — Summary That Changes Meaning
Deterministic extractive summariser implementing the RICE enforcement in
agents.md and the skill contracts in skills.md.
"""
import argparse
import re
import sys

CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

CONDITION_MARKERS = [
    "regardless",
    "under any circumstances",
    "unless",
    "not valid",
    "not sufficient",
    "are forfeited",
]

FORBIDDEN_SCOPE_BLEED = [
    "as is standard practice",
    "standard practice",
    "typically",
    "generally expected",
    "generally accepted",
]


def retrieve_policy(input_path: str) -> dict:
    """
    Load a plain-text policy file and return structured numbered clauses.

    Returns: {"header": list[str], "clauses": [{"section_number": str,
    "clause_id": str, "text": str}, ...]} in source order, wording preserved.
    """
    try:
        with open(input_path, encoding="utf-8-sig") as f:
            lines = f.read().splitlines()
    except OSError as exc:
        print(f"Error: cannot read input file '{input_path}': {exc}")
        sys.exit(1)

    header = []
    clauses = []
    current_section = ""
    current_clause_id = None
    current_parts = []

    def flush_clause():
        nonlocal current_clause_id, current_parts
        if current_clause_id is not None and current_parts:
            clauses.append({
                "section_number": current_section,
                "clause_id": current_clause_id,
                "text": " ".join(" ".join(current_parts).split()),
            })
        current_clause_id = None
        current_parts = []

    for line in lines:
        stripped = line.strip()
        if not stripped or re.fullmatch(r"═+", stripped):
            continue

        clause_match = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
        section_match = None if clause_match else re.match(r"^(\d+)\.\s+(\S.*)$", stripped)

        if clause_match:
            flush_clause()
            current_clause_id = clause_match.group(1)
            current_section = current_clause_id.split(".")[0]
            current_parts = [clause_match.group(2)]
        elif section_match:
            flush_clause()
            current_section = section_match.group(1)
            header.append(stripped)
        elif current_clause_id is not None:
            current_parts.append(stripped)
        else:
            header.append(stripped)

    flush_clause()

    if not clauses:
        print(f"Error: no numbered clauses found in '{input_path}'.")
        sys.exit(1)

    return {"header": header, "clauses": clauses}


def _split_sentences(text: str) -> list:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _needs_verbatim(text: str) -> bool:
    lowered = text.lower()
    return len(_split_sentences(text)) > 1 or any(m in lowered for m in CONDITION_MARKERS)


def _check_scope_bleed(entries: list):
    """Enforcement self-check: the summary must never add outside framing."""
    joined = " ".join(e["text"].lower() for e in entries)
    violations = [p for p in FORBIDDEN_SCOPE_BLEED if p in joined]
    if violations:
        print(f"Error: scope bleed detected ({violations}); refusing to write output.")
        sys.exit(1)


def summarize_policy(policy: dict, output_path: str):
    """
    Produce a compliant clause-referenced summary and write it to output_path.

    Contract (skills.md): one entry per clause in source order, each starting
    with its clause number, binding verbs intact, every condition preserved.
    Multi-condition clauses are quoted verbatim and marked [QUOTE-VERBATIM];
    critical clauses missing from the parsed input are flagged, never skipped.
    """
    entries = []
    for clause in policy["clauses"]:
        if _needs_verbatim(clause["text"]):
            entries.append({
                "clause_id": clause["clause_id"],
                "text": f"{clause['text']} [QUOTE-VERBATIM]",
                "quoted": True,
            })
        else:
            entries.append({
                "clause_id": clause["clause_id"],
                "text": clause["text"],
                "quoted": False,
            })

    present = {c["clause_id"] for c in policy["clauses"]}
    missing_flags = [
        {"clause_id": cid, "text": f"[MISSING CLAUSE] {cid} not found in source parse.", "quoted": False}
        for cid in CRITICAL_CLAUSES
        if cid not in present
    ]
    entries.extend(missing_flags)

    _check_scope_bleed(entries)

    out_lines = []
    title_lines = [h for h in policy["header"][:3]]
    meta_lines = [h for h in policy["header"] if re.match(r"^(Document Reference|Version)", h)]
    out_lines.extend(title_lines)
    out_lines.append(" | ".join(meta_lines))
    out_lines.append("")

    current_section = None
    for e in entries:
        section = e["clause_id"].split(".")[0]
        if section != current_section:
            current_section = section
            heading = next(
                (h for h in policy["header"] if re.match(rf"^{re.escape(section)}\.\s", h)),
                f"{section}.",
            )
            out_lines.append(heading)
        out_lines.append(f"  {e['clause_id']} {e['text']}")

    quoted = sum(1 for e in entries if e["quoted"])
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines) + "\n")

    print(
        f"Done. Summarised {len(policy['clauses'])} clauses "
        f"({quoted} quoted verbatim, {len(missing_flags)} missing-critical flags). "
        f"Summary written to {output_path}"
    )


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()
    policy = retrieve_policy(args.input)
    summarize_policy(policy, args.output)


if __name__ == "__main__":
    main()
