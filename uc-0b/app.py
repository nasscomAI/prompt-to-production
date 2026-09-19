"""
UC-0B — Summary That Changes Meaning

Clause-preserving policy summariser. Every numbered clause in the source is carried into
the summary in its own line with its clause number. Each clause is condensed with a small
set of meaning-neutral rewrites, then checked against a "meaning guard": if condensing
lost any number, binding verb, strength qualifier or named approver, the clause is quoted
verbatim and marked [VERBATIM] instead. Nothing is ever added that is not in the source.
"""
import argparse
import re
import sys

# The 10 clauses from the README clause inventory, with the facts each must keep.
CRITICAL_CLAUSES = {
    "2.3": ["14", "must"],
    "2.4": ["written approval", "before", "verbal approval is not valid"],
    "2.5": ["loss of pay", "regardless of subsequent approval"],
    "2.6": ["5", "forfeited", "31 december"],
    "2.7": ["first quarter", "forfeited"],
    "3.2": ["3 or more", "medical certificate", "48 hours"],
    "3.4": ["before or after", "medical certificate", "regardless of duration"],
    "5.2": ["department head", "hr director", "not sufficient"],
    "5.3": ["30", "municipal commissioner"],
    "7.2": ["not permitted under any circumstances"],
}

# Words/phrases whose loss changes an obligation. If a condensed clause drops one that the
# original had, the condensed version is rejected.
BINDING_TERMS = [
    "must not", "must", "will", "requires", "required", "may", "cannot", "not permitted",
    "not valid", "not sufficient", "not apply", "only", "regardless", "under any circumstances",
    "forfeited", "maximum", "at least", "within", "before", "after", "and", "or",
]
ROLE_TERMS = [
    "direct manager", "department head", "hr director", "municipal commissioner",
    "hr department", "state government", "registered medical practitioner",
]

# Phrases the summary must never contain unless the source does (scope bleed).
SCOPE_BLEED_PHRASES = [
    "standard practice", "typically", "generally", "usually", "as is common",
    "in most organisations", "in government organisations", "employees are expected to",
]

# Meaning-neutral condensations. Each one only shortens wording; none changes a verb of
# obligation, a number, or who is responsible.
CONDENSE_RULES = [
    (r"\bThis policy governs\b", "Governs"),
    (r"\bThis policy does not apply to\b", "Does not apply to"),
    (r"\bEach permanent employee is entitled to\b", "Permanent employees get"),
    (r"\bEach employee is entitled to\b", "Employees get"),
    (r"\bFemale employees are entitled to\b", "Female employees get"),
    (r"\bMale employees are entitled to\b", "Male employees get"),
    (r"\bEmployees are entitled to\b", "Employees get"),
    (r"\bthey are entitled to\b", "they get"),
    (r"\bLeave Without Pay\b", "LWP"),
    (r"\bLoss of Pay \(LOP\)", "Loss of Pay (LOP)"),
    (r"\ba leave application\b", "leave applications"),
    (r"\bthe following calendar year\b", "the next calendar year"),
    (r"\bthe following year\b", "the next year"),
    (r"\bfor the purposes of\b", "for"),
    (r"\bthe employee's direct manager\b", "the direct manager"),
    (r"\bAn employee may apply for LWP only after\b", "LWP may be applied for only after"),
    (r"\.\s*Those categories are governed by their respective contracts\.", " (governed by their own contracts)."),
    (r"\bIf an employee is required to work on a public holiday, they get\b",
     "Working a public holiday earns"),
]


def retrieve_policy(path):
    """Load a policy .txt and return (title_lines, sections).

    sections = [{"number": "2", "heading": "ANNUAL LEAVE",
                 "clauses": [{"id": "2.3", "text": "..."}]}]
    """
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        sys.exit(f"Refusing: policy file not found: {path}")

    title, sections, current, clause = [], [], None, None
    heading_re = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z ()&/,-]+)$")
    clause_re = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
    for raw in lines:
        line = raw.strip()
        if not line or set(line) <= {"═", "="}:
            continue
        m_head = heading_re.match(line)
        m_clause = clause_re.match(line)
        if m_head and not m_clause:
            current = {"number": m_head.group(1), "heading": m_head.group(2).strip(), "clauses": []}
            sections.append(current)
            clause = None
        elif m_clause and current is not None:
            clause = {"id": m_clause.group(1), "text": m_clause.group(2).strip()}
            current["clauses"].append(clause)
        elif clause is not None:
            clause["text"] += " " + line          # continuation line of the current clause
        elif current is None:
            title.append(line)

    if not any(s["clauses"] for s in sections):
        sys.exit(f"Refusing: no numbered clauses found in {path} — cannot summarise safely.")
    return title, sections


def _terms_present(text, terms):
    low = text.lower()
    return {t for t in terms if re.search(r"\b" + re.escape(t) + r"\b", low)}


def _numbers(text):
    return set(re.findall(r"\d+(?:[.,]\d+)?", text))


def _heading(text):
    """Title-case a section heading but keep acronyms in brackets, e.g. '(LWP)'."""
    return re.sub(r"\((\w+)\)", lambda m: f"({m.group(1).upper()})", text.title())


def _condense(text):
    out = text
    for pat, repl in CONDENSE_RULES:
        out = re.sub(pat, repl, out)
    return re.sub(r"\s{2,}", " ", out).strip()


def _meaning_lost(original, condensed):
    """Return the list of facts present in original but missing from condensed."""
    lost = []
    lost += sorted(_numbers(original) - _numbers(condensed))
    lost += sorted(_terms_present(original, BINDING_TERMS) - _terms_present(condensed, BINDING_TERMS))
    lost += sorted(_terms_present(original, ROLE_TERMS) - _terms_present(condensed, ROLE_TERMS))
    return lost


def summarize_policy(title, sections):
    """Produce summary lines (one per clause, clause number kept) plus a check report."""
    out, report = [], []
    doc_ref = next((t for t in title if t.lower().startswith("document reference")), "")
    heading = next((t for t in title if "POLICY" in t.upper()), "Policy")
    out.append(f"SUMMARY — {heading.title()}")
    if doc_ref:
        out.append(f"Source: {doc_ref}. Every numbered clause is listed; nothing has been added.")
    out.append("[VERBATIM] marks a clause quoted word-for-word because condensing it would drop a condition.")
    out.append("")

    seen = {}
    for sec in sections:
        if not sec["clauses"]:
            continue
        out.append(f"{sec['number']}. {_heading(sec['heading'])}")
        for cl in sec["clauses"]:
            original = cl["text"]
            condensed = _condense(original)
            lost = _meaning_lost(original, condensed)
            if lost:
                line = f"  [{cl['id']}] [VERBATIM] {original}"
                report.append(f"{cl['id']}: condensing would drop {lost} → quoted verbatim")
            else:
                line = f"  [{cl['id']}] {condensed}"
            out.append(line)
            seen[cl["id"]] = line
        out.append("")

    # --- verification against the clause inventory ---------------------------
    for cid, facts in CRITICAL_CLAUSES.items():
        if cid not in seen:
            report.append(f"{cid}: MISSING from summary")
            continue
        missing = [f for f in facts if f not in seen[cid].lower()]
        if missing:
            report.append(f"{cid}: required facts missing {missing}")
    body = "\n".join(out).lower()
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase in body:
            report.append(f"scope bleed: summary contains '{phrase}'")
    return out, report


def main():
    parser = argparse.ArgumentParser(description="UC-0B clause-preserving policy summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt")
    args = parser.parse_args()

    title, sections = retrieve_policy(args.input)
    lines, report = summarize_policy(title, sections)

    failures = [r for r in report if "MISSING" in r or "required facts" in r or "scope bleed" in r]
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")

    total = sum(len(s["clauses"]) for s in sections)
    print(f"Summarised {total} clauses from {args.input} → {args.output}")
    for r in report:
        print("  " + r)
    if failures:
        print(f"FAILED: {len(failures)} critical check(s) failed — do not use this summary.")
        sys.exit(1)
    print(f"All {len(CRITICAL_CLAUSES)} critical clauses present with their conditions; no scope bleed.")


if __name__ == "__main__":
    main()
