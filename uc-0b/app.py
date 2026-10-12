"""
UC-0B app.py — Policy summariser that does not change meaning.
Built from uc-0b/agents.md (RICE enforcement) and uc-0b/skills.md.

Every numbered clause is kept. Each clause is shortened only with
meaning-neutral rewrites, then checked: if any number, binding verb,
absolute phrase or named approver was lost, the clause is quoted
verbatim and flagged [VERBATIM] instead.
"""
import argparse
import re
import sys
import textwrap

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 ()&/,\-–]+)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")

# Meaning-neutral rewrites only. None of these may delete a number, a binding
# verb, an absolute phrase or an approver — the checks below enforce that.
REWRITES = [
    (r"\bEach permanent employee is entitled to\b", "Permanent employees get"),
    (r"\bEach employee is entitled to\b", "Employees get"),
    (r"\b(?:is|are) entitled to\b", "get"),
    (r"\bfrom the date of joining\b", "from joining"),
    (r"\bthe employee's direct manager\b", "the direct manager"),
    (r"\bbefore the leave commences\b", "before leave starts"),
    (r"\bto the following calendar year\b", "to the next calendar year"),
    (r"\bof the following year\b", "of the next year"),
    (r"\bto the following year\b", "to the next year"),
    (r"\bwithin the first quarter \((January–March)\) of\b", r"within \1 of"),
    (r"\bfor the purposes of\b", "for"),
    (r"\bAn employee may apply for Leave Without Pay only after\b", "LWP may be applied for only after"),
    (r"\bPeriods of LWP do not count\b", "LWP periods do not count"),
    (r"\bLeave-related grievances\b", "Leave grievances"),
    (r"\s+", " "),
]

# Words and phrases whose loss would soften an obligation or drop a condition.
BINDING_TERMS = [
    "must", "will", "requires", "required", "may", "cannot", "not", "only", "both",
    "and", "or", "regardless", "under any circumstances", "not valid", "not sufficient",
    "maximum", "at least", "within", "before", "after", "unless", "alone",
]
APPROVERS = [
    "direct manager", "Department Head", "HR Director", "Municipal Commissioner",
    "HR Department", "State Government", "registered medical practitioner",
]

# Ground truth from the UC-0B README clause inventory: phrases each critical
# clause must still contain after summarising.
CRITICAL_CLAUSES = {
    "2.3": ["14 calendar days", "must"],
    "2.4": ["written approval", "direct manager", "Verbal approval is not valid"],
    "2.5": ["Loss of Pay", "regardless of subsequent approval"],
    "2.6": ["maximum of 5", "forfeited on 31 December"],
    "2.7": ["must be used", "January–March", "forfeited"],
    "3.2": ["3 or more consecutive days", "medical certificate", "48 hours"],
    "3.4": ["medical certificate", "regardless of duration"],
    "5.2": ["Department Head", "HR Director", "Manager approval alone is not sufficient"],
    "5.3": ["30 continuous days", "Municipal Commissioner"],
    "7.2": ["not permitted under any circumstances"],
}

SCOPE_BLEED = [
    "standard practice", "typically", "generally", "usually", "common practice",
    "in most organisations", "government organisations", "it is expected",
]


def retrieve_policy(path: str) -> dict:
    """Load a .txt policy file and return its numbered sections and clauses."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as exc:
        raise SystemExit(f"Error: cannot read policy file {path}: {exc}")

    title = ""
    reference = ""
    sections = []
    current_clause = None
    for raw in lines:
        line = raw.strip()
        if not line or set(line) <= {"═"}:
            current_clause = None
            continue
        if line.startswith("Document Reference:"):
            reference = line.split(":", 1)[1].strip()
            continue
        section = SECTION_RE.match(line)
        clause = CLAUSE_RE.match(line)
        if clause and sections:
            current_clause = {"id": clause.group(1), "text": clause.group(2)}
            sections[-1]["clauses"].append(current_clause)
        elif section:
            sections.append({"number": section.group(1), "heading": re.sub(r"\(Lwp\)", "(LWP)", section.group(2).title()), "clauses": []})
            current_clause = None
        elif current_clause is not None:
            # Continuation of a wrapped clause — join so no condition is lost.
            current_clause["text"] += " " + line
        elif not sections and not reference:
            title = f"{title} {line}".strip()

    if not any(s["clauses"] for s in sections):
        raise SystemExit(f"Error: no numbered clauses found in {path}")
    return {"document_title": title, "document_reference": reference, "sections": sections}


def _contains(text: str, term: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, re.IGNORECASE) is not None


def _lost_terms(original: str, summary: str, clause_id: str) -> list:
    """Return everything from the original that the summary line no longer carries."""
    lost = []
    for number in re.findall(r"\d+(?:[.,]\d+)?", original):
        if number not in summary:
            lost.append(number)
    for term in BINDING_TERMS + APPROVERS:
        if _contains(original, term) and not _contains(summary, term):
            lost.append(term)
    for phrase in CRITICAL_CLAUSES.get(clause_id, []):
        if phrase.lower() not in summary.lower():
            lost.append(phrase)
    return lost


def _shorten(text: str) -> str:
    for pattern, replacement in REWRITES:
        text = re.sub(pattern, replacement, text)
    return text.strip()


def summarize_policy(policy: dict) -> str:
    """Produce a clause-referenced summary that keeps every obligation and condition."""
    out = [
        f"SUMMARY — {policy['document_title']}",
        f"Source: policy_hr_leave.txt ({policy['document_reference']})",
        "Every numbered clause is listed. [VERBATIM] = quoted in full because it could not",
        "be shortened without losing a condition. Nothing here is added beyond the source.",
        "",
    ]
    source_ids = []
    summary_ids = []
    verbatim_ids = []

    for section in policy["sections"]:
        out.append(f"{section['number']}. {section['heading']}")
        for clause in section["clauses"]:
            source_ids.append(clause["id"])
            original = re.sub(r"\s+", " ", clause["text"]).strip()
            short = _shorten(original)
            if _lost_terms(original, short, clause["id"]):
                line = f'[{clause["id"]}] [VERBATIM] "{original}"'
                verbatim_ids.append(clause["id"])
            else:
                line = f"[{clause['id']}] {short}"
            # Final guard: the verbatim text itself must satisfy the critical checks.
            missing = [p for p in CRITICAL_CLAUSES.get(clause["id"], []) if p.lower() not in line.lower()]
            if missing:
                raise SystemExit(f"Error: clause {clause['id']} lost required condition(s): {missing}")
            summary_ids.append(clause["id"])
            out.append(textwrap.fill(line, width=88, subsequent_indent="      "))
        out.append("")

    all_present = source_ids == summary_ids
    out.append(f"Clauses in source: {len(source_ids)} | Clauses in summary: {len(summary_ids)} | "
               f"All present: {'YES' if all_present else 'NO'}")
    out.append(f"Critical clauses checked: {', '.join(CRITICAL_CLAUSES)}")
    out.append(f"Clauses quoted verbatim: {', '.join(verbatim_ids) if verbatim_ids else 'none'}")
    summary = "\n".join(out) + "\n"

    if not all_present:
        raise SystemExit("Error: clause omission — summary does not contain every source clause.")
    bleed = [p for p in SCOPE_BLEED if p in summary.lower()]
    if bleed:
        raise SystemExit(f"Error: scope bleed — summary contains phrases not in the source: {bleed}")
    return summary


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt file")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print(summary.splitlines()[-3])
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
