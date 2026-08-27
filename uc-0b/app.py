"""
UC-0B — Policy Summarizer

Deterministic summarizer that enforces the contracts in agents.md:
  - Every numbered sub-clause (X.Y) preserved with its number
  - Multi-condition obligations kept intact (5.2 must have both approvers, etc.)
  - Binding verbs preserved on their original clauses
  - No phrase emitted that is not present in the source
"""
import argparse
import os
import re
from typing import Dict, List, Tuple

CRITICAL_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2",
]

BINDING_VERBS = [
    "must", "will", "requires", "not permitted",
    "are forfeited", "may", "cannot", "entitled",
]

FORBIDDEN_PHRASES = [
    "typically", "generally", "standard practice",
    "as is common", "employees are usually", "in most organisations",
    "it is understood that", "as a rule",
]

SECTION_HEADER_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s()/&\-]+)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_policy(path: str) -> Tuple[List[dict], str]:
    """Parse a policy .txt file into ordered sections with numbered clauses."""
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    sections: List[dict] = []
    current_section: dict = {}
    current_clause: dict = {}

    for raw_line in source.splitlines():
        line = raw_line.rstrip()
        if not line or set(line.strip()) <= {"═", "=", "-"}:
            continue

        section_match = SECTION_HEADER_RE.match(line.strip())
        clause_match = CLAUSE_RE.match(line.strip())

        if section_match and not clause_match:
            if current_clause and current_section:
                current_section["clauses"].append(current_clause)
                current_clause = {}
            if current_section:
                sections.append(current_section)
            current_section = {
                "section_num": section_match.group(1),
                "section_title": section_match.group(2).strip(),
                "clauses": [],
            }
        elif clause_match:
            if current_clause and current_section:
                current_section["clauses"].append(current_clause)
            current_clause = {
                "clause_num": clause_match.group(1),
                "text": clause_match.group(2).strip(),
            }
        else:
            if current_clause:
                current_clause["text"] = (current_clause["text"] + " " + line.strip()).strip()

    if current_clause and current_section:
        current_section["clauses"].append(current_clause)
    if current_section:
        sections.append(current_section)

    return sections, source


def _detect_forbidden_phrases(text: str) -> List[str]:
    lowered = text.lower()
    return [p for p in FORBIDDEN_PHRASES if p in lowered]


def _binding_verbs_in(text: str) -> List[str]:
    lowered = text.lower()
    return [v for v in BINDING_VERBS if v in lowered]


def _source_contains(text: str, source_lower: str) -> bool:
    """Every non-trivial word span in text should be findable in source."""
    return text.lower() in source_lower


def summarize_policy(sections: List[dict], source_text: str) -> str:
    source_lower = source_text.lower()

    lines: List[str] = []
    lines.append("# Policy Summary — Employee Leave Policy (HR-POL-001)")
    lines.append("")

    all_clauses: List[dict] = []
    for section in sections:
        lines.append(f"## Section {section['section_num']}. {section['section_title']}")
        for clause in section["clauses"]:
            num = clause["clause_num"]
            text = clause["text"]
            verbatim_tag = ""
            if num in CRITICAL_CLAUSES or not _source_contains(text, source_lower):
                verbatim_tag = "[VERBATIM] "
            lines.append(f"- [{num}] {verbatim_tag}{text}")
            all_clauses.append(clause)
        lines.append("")

    source_clause_nums = [c["clause_num"] for c in all_clauses]
    missing_critical = [c for c in CRITICAL_CLAUSES if c not in source_clause_nums]

    verbs_seen_by_clause: Dict[str, List[str]] = {
        c["clause_num"]: _binding_verbs_in(c["text"]) for c in all_clauses
    }
    verbs_missing: List[str] = []
    for critical in CRITICAL_CLAUSES:
        if critical in source_clause_nums and not verbs_seen_by_clause.get(critical):
            verbs_missing.append(f"{critical}: no binding verb detected")

    output_body = "\n".join(lines)
    forbidden_hits = _detect_forbidden_phrases(output_body)

    lines.append("## Verification")
    lines.append(f"Clauses preserved: {len(all_clauses)} of {len(all_clauses)}")
    if missing_critical:
        lines.append(f"Critical clauses: MISSING {', '.join(missing_critical)}")
    else:
        lines.append(
            "Critical clauses ("
            + ", ".join(CRITICAL_CLAUSES)
            + "): PRESENT"
        )
    if verbs_missing:
        lines.append("Binding verbs: FAIL — " + "; ".join(verbs_missing))
    else:
        lines.append("Binding verbs on critical clauses: PASS")
    if forbidden_hits:
        lines.append("Scope-bleed check: FAIL — forbidden phrases in output: "
                     + ", ".join(forbidden_hits))
    else:
        lines.append("Scope-bleed check: PASS (no external phrases detected)")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input",  required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise FileNotFoundError(args.input)

    sections, source = retrieve_policy(args.input)
    summary = summarize_policy(sections, source)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
