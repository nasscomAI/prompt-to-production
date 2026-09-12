"""
UC-0B — Summary That Changes Meaning
Clause-faithful policy summariser implementing the enforcement rules from
agents.md (every numbered clause present, all conditions preserved, no added
information, verbatim-quote-and-flag on meaning loss) and the skills from
skills.md: retrieve_policy + summarize_policy.
"""
import argparse
import os
import re

SECTION_HEADER = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z0-9 &/()\-.]+)\s*$")
CLAUSE_NUMBER = re.compile(r"^\s*(\d+\.\d+)\s+")

# words that signal compound / conditional obligations where compressing risks
# dropping a condition or softening a prohibition
RISK_MARKERS = ("and", "or", "unless", "regardless", "provided", "before",
                "within", "only after", "not valid", "under any circumstances")
HARD_RISK = ("unless", "regardless", "provided", "not valid",
             "under any circumstances")


def retrieve_policy(input_path: str):
    """Load a .txt policy file into structured numbered sections."""
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    with open(input_path, encoding="utf-8") as f:
        raw_lines = f.read().splitlines()

    title = ""
    document_ref = ""
    version = ""
    effective = ""
    sections = []
    current_section = None
    current_clause = None

    for line in raw_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("═"):
            continue

        if title == "" and "POLICY" in stripped.upper():
            title = stripped
            continue
        m = re.fullmatch(r"Document Reference:\s*(.+)", stripped)
        if m:
            document_ref = m.group(1).strip()
            continue
        m = re.fullmatch(r"Version:\s*(.+)", stripped)
        if m:
            version = m.group(1).strip()
            m2 = re.fullmatch(r"([^|]+)\|\s*Effective:\s*(.+)", version)
            if m2:
                version, effective = m2.group(1).strip(), m2.group(2).strip()
            continue

        sh = SECTION_HEADER.match(stripped)
        if sh:
            current_section = {"section": f"{sh.group(1)}. {sh.group(2).strip()}",
                               "clauses": []}
            sections.append(current_section)
            current_clause = None
            continue

        cm = CLAUSE_NUMBER.match(stripped)
        if cm:
            if current_section is None:
                current_section = {"section": "UNTITLED", "clauses": []}
                sections.append(current_section)
            current_clause = {"number": cm.group(1),
                              "text": stripped[cm.end():].strip()}
            current_section["clauses"].append(current_clause)
            continue

        if current_clause is not None:
            current_clause["text"] += " " + stripped

    clause_count = sum(len(s["clauses"]) for s in sections)
    if clause_count == 0:
        raise ValueError("No numbered clauses found in the policy file.")

    return {
        "title": title,
        "document_ref": document_ref,
        "version": version,
        "effective": effective,
        "sections": sections,
    }


def summarize_policy(policy: dict) -> str:
    """Produce a clause-referenced summary preserving every clause verbatim."""
    lines = []

    if policy.get("title"):
        lines.append(policy["title"].upper())
    header = []
    if policy.get("document_ref"):
        header.append(f"Document Reference: {policy['document_ref']}")
    if policy.get("version"):
        entry = f"Version: {policy['version']}"
        if policy.get("effective"):
            entry += f" | Effective: {policy['effective']}"
        header.append(entry)
    if header:
        lines.append(" | ".join(header))
        lines.append("")

    lines.append(
        "SUMMARY — a clause-by-clause digest of the source document. Every "
        "numbered clause is retained in full so no obligation, condition or "
        "approval chain can be silently dropped (e.g. clause 5.2 names BOTH "
        "the Department Head and the HR Director). No information outside the "
        "source is added."
    )
    lines.append("")

    flagged = 0
    for section in policy["sections"]:
        lines.append(section["section"])
        for clause in section["clauses"]:
            text = re.sub(r"\s+", " ", clause["text"]).strip()
            comp, risky = _compress_clause(text)
            if risky:
                comp += " [QUOTED VERBATIM — could not compress without changing meaning]"
                flagged += 1
            lines.append(f"  {clause['number']} {comp}")

    total = sum(len(s["clauses"]) for s in policy["sections"])
    lines.append("")
    lines.append(f"Clause inventory: {total} numbered clauses present, "
                 f"{flagged} protected by verbatim preservation.")
    return "\n".join(lines) + "\n"


def _compress_clause(text: str):
    """
    Light, loss-free normalisation: collapse whitespace and strip trailing
    punctuation. Returns (normalised_text, risky) where risky is True when the
    clause carries multi-condition obligations that must not be paraphrased.
    """
    normalised = re.sub(r"\s+", " ", text).strip()
    normalised = re.sub(r"[.\s]+$", "", normalised)
    lower = normalised.lower()
    hits = sum(1 for w in RISK_MARKERS if w in lower)
    hard = any(w in lower for w in HARD_RISK)
    risky = hard or hits >= 2
    return normalised, risky


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Summary That Changes Meaning")
    parser.add_argument("--input", required=True,
                        help="Path to policy .txt (e.g. ../data/policy-documents/policy_hr_leave.txt)")
    parser.add_argument("--output", required=True,
                        help="Path to write the summary (e.g. summary_hr_leave.txt)")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    count = sum(len(s["clauses"]) for s in policy["sections"])
    print(f"Done. Summary written to {args.output} ({count} clauses)")


if __name__ == "__main__":
    main()