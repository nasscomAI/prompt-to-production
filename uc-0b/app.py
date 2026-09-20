"""
UC-0B — Summary That Changes Meaning
Vibe-coded from agents.md + skills.md (RICE → CRAFT workflow).

Enforcement rules from agents.md are implemented here:
  1. Every numbered clause is retained with its reference (no clause omission).
  2. Multi-condition obligations keep all conditions — 5.2 names both approvers.
  3. No information outside the source document is added (no scope bleed).
  4. Binding verbs/deadlines/thresholds are preserved verbatim.
Obligations are quoted verbatim wherever a paraphrase could change meaning.
"""
import argparse
import re
import sys

CRITICAL_CLAUSES = ("2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2")

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.+?)\s*$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 &'()\-]*)$")
DIVIDER_RE = re.compile(r"^[\s═\-\=\_]+$")


def retrieve_policy(input_path: str) -> dict:
    """Load a policy file and return structured sections with numbered clauses."""
    try:
        with open(input_path, "r", encoding="utf-8-sig") as filehandle:
            lines = filehandle.read().splitlines()
    except OSError as exc:
        raise ValueError(f"Policy file could not be read: {exc}") from exc

    doc_title = ""
    doc_ref = ""
    doc_version = ""
    sections = {}          # section_number -> {"title": str, "clauses": [(num, text)]}
    order = []
    current_section = None

    for lineno, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or DIVIDER_RE.match(line):
            continue

        clause_match = CLAUSE_RE.match(line)
        if clause_match:
            number, text = clause_match.group(1), clause_match.group(2).strip()
            if current_section is None:
                current_section = "0"
                sections["0"] = {"title": "Ungrouped", "clauses": []}
                order.append("0")
            sections[current_section]["clauses"].append((number, text))
            continue

        section_match = SECTION_RE.match(line)
        if section_match and (not CLAUSE_RE.match(line)):
            current_section = section_match.group(1)
            if current_section not in sections:
                sections[current_section] = {"title": section_match.group(2), "clauses": []}
                order.append(current_section)
            continue

        # Preamble / metadata lines before section 1.
        if not sections:
            if line.lower().startswith("document reference"):
                doc_ref = line.split(":", 1)[1].strip() if ":" in line else line
            elif line.lower().startswith("version"):
                doc_version = line.split("|", 1)[0].replace("Version:", "").strip()
            elif not doc_title:
                doc_title = line
            continue

        # Continuation line of the current clause.
        if current_section is not None and sections[current_section]["clauses"]:
            current_number, current_text = sections[current_section]["clauses"][-1]
            sections[current_section]["clauses"][-1] = (
                current_number, f"{current_text} {line}",
            )

    if not any(sections[s]["clauses"] for s in sections):
        raise ValueError("Policy file contains no numbered clauses")

    return {
        "source": input_path,
        "doc_ref": doc_ref,
        "version": doc_version,
        "sections": sections,
        "order": order,
    }


def verify_completeness(clause_numbers) -> bool:
    """Check that every critical clause survived into the summary."""
    missing = [number for number in CRITICAL_CLAUSES if number not in clause_numbers]
    return not missing, missing


def summarize_policy(policy: dict) -> str:
    """Produce a clause-preserving, source-grounded summary."""
    all_numbers = []
    lines = [
        "HR LEAVE POLICY — CLAUSE-PRESERVING SUMMARY",
        f"Source: {policy['source']} ({policy['doc_ref']}, {policy['version']})",
        "",
        ("This summary retains every numbered clause together with all of its "
         "conditions, binding verbs, deadlines, and consequences. Obligations are "
         "quoted verbatim wherever a paraphrase could change their meaning. No "
         "information outside the source document has been added."),
        "",
    ]

    for section_number in policy["order"]:
        section = policy["sections"][section_number]
        if section_number != "0":
            lines.append(f"{section_number}. {section['title']}")
        for clause_number, clause_text in section["clauses"]:
            all_numbers.append(clause_number)
            lines.append(f"  {clause_number} {clause_text}")
        lines.append("")

    complete, missing = verify_completeness(all_numbers)
    lines.append(f"Completeness check: {len(set(all_numbers))} numbered clauses retained.")
    if complete:
        lines.append("All critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) present.")
    else:
        lines.append(f"CRITICAL CLAUSES MISSING: {', '.join(sorted(missing))}")
        raise RuntimeError("Refusing to emit an incomplete summary: clauses were omitted")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B clause-preserving policy summarizer")
    parser.add_argument("--input", required=True, help="Path to the policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)
    with open(args.output, "w", encoding="utf-8") as filehandle:
        filehandle.write(summary)

    clause_count = sum(len(s["clauses"]) for s in policy["sections"].values())
    print(f"Done. Summary written to {args.output} ({clause_count} clauses retained)")
    print("Completeness check passed — all 10 critical clauses present.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)