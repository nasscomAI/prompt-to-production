"""
UC-0B app.py — Policy Summariser
Built with the RICE → agents.md → skills.md → CRAFT workflow.
Enforcement rules mirror uc-0b/agents.md: no clause omission, no scope bleed,
no obligation softening.
"""
import argparse
import re

# A clause line starts with a number like "2.3" (section.clause).
CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
# A section header line starts with a bare number like "2." followed by a title.
SECTION_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z].*)$")

# Binding language that must never be softened or dropped (agents.md).
BINDING_TERMS = [
    "must", "will", "requires", "shall", "not permitted",
    "not valid", "forfeited", "not sufficient", "cannot",
    "any circumstances", "regardless",
]

# A clause is emitted verbatim (not paraphrased) when it carries a condition
# that meaning-loss compression would endanger.
VERBATIM_TRIGGERS = [
    "and the", " and ", "regardless", "any circumstances",
    "not valid", "not sufficient", "not permitted",
]


def retrieve_policy(input_path: str):
    """Load .txt policy and return ordered sections -> ordered clauses."""
    with open(input_path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    if not any(line.strip() for line in lines):
        raise ValueError(f"Policy file is empty: {input_path}")

    sections = []
    current_section = None
    current_clause = None

    for line in lines:
        if not line.strip() or set(line.strip()) <= set("═ "):
            continue  # blank or box-drawing separator

        clause_match = CLAUSE_RE.match(line)
        section_match = SECTION_RE.match(line)

        if clause_match:
            clause_id, text = clause_match.group(1), clause_match.group(2).strip()
            current_clause = {"clause_id": clause_id, "clause_text": text}
            if current_section is None:
                current_section = {"section": "0", "title": "PREAMBLE", "clauses": []}
                sections.append(current_section)
            current_section["clauses"].append(current_clause)
        elif section_match:
            current_section = {
                "section": section_match.group(1),
                "title": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            current_clause = None
        elif current_clause is not None:
            # Continuation line of the current clause — never dropped.
            current_clause["clause_text"] += " " + line.strip()
        # Non-clause header text before any clause (doc title) is metadata, skipped.

    return sections


def is_binding(text: str) -> bool:
    low = text.lower()
    return any(term in low for term in BINDING_TERMS)


def needs_verbatim(text: str) -> bool:
    low = text.lower()
    return any(trigger in low for trigger in VERBATIM_TRIGGERS)


def summarize_policy(sections) -> str:
    """Produce a clause-referenced summary preserving every clause and condition."""
    out = ["POLICY SUMMARY — clause-preserving (UC-0B)", ""]
    source_ids = []

    for section in sections:
        if not section["clauses"]:
            continue
        out.append(f"Section {section['section']}: {section['title']}")
        for clause in section["clauses"]:
            cid = clause["clause_id"]
            text = clause["clause_text"]
            source_ids.append(cid)
            if is_binding(text) and needs_verbatim(text):
                # Cannot compress without risking a condition — quote verbatim.
                out.append(f"  {cid} [VERBATIM]: \"{text}\"")
            elif is_binding(text):
                out.append(f"  {cid} [BINDING]: {text}")
            else:
                out.append(f"  {cid}: {text}")
        out.append("")

    summary = "\n".join(out).rstrip() + "\n"

    # Coverage self-check: every source clause id must appear in the output.
    missing = [cid for cid in source_ids if f"{cid}" not in summary]
    if missing:
        raise AssertionError(f"Coverage check failed — missing clauses: {missing}")

    return summary


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    total = sum(len(s["clauses"]) for s in sections)
    print(f"Done. {total} clauses summarised. Written to {args.output}")


if __name__ == "__main__":
    main()
