"""UC-0B policy summariser — deterministic, meaning-preserving.

Implements agents.md (faithful summarisation contract) and skills.md
(retrieve_policy + summarize_policy). Condenses only clauses whose
verified condensed form passes guard checks against the parsed source;
every other clause is quoted verbatim and flagged per the refusal rule.
"""
import argparse
import re
import sys

SEP_RE = re.compile(r"^\s*═+\s*$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
DOCREF_RE = re.compile(r"^Document Reference:\s*(.+)$", re.M)
VERSION_RE = re.compile(r"^Version:\s*(.+)$", re.M)

SCOPE_BLEED_PHRASES = [
    "standard practice",
    "typically",
    "generally expected",
]

STRONG_VERB_PATTERNS = [
    r"\bmust\b",
    r"\brequires?\b",
    r"\bwill\b",
    r"\bcannot\b",
    r"\bshall\b",
    r"\bmays?\b",
    r"\bentitled\b",
    r"not permitted",
    r"not valid",
    r"not sufficient",
    r"are forfeited",
    r"is forfeited",
]

CONDENSED = {
    "1.1": {
        "text": "Governs all leave entitlements for permanent and contractual CMC employees.",
        "guards": ["leave entitlements", "permanent", "contractual", "CMC"],
    },
    "1.2": {
        "text": "Does not apply to daily wage workers or consultants; those categories are governed by their respective contracts.",
        "guards": ["does not apply", "daily wage workers", "consultants", "respective contracts"],
    },
    "2.1": {
        "text": "Permanent employees are entitled to 18 days of paid annual leave per calendar year.",
        "guards": ["18", "paid annual leave", "calendar year", "entitled"],
    },
    "2.2": {
        "text": "Annual leave accrues at 1.5 days per month from the date of joining.",
        "guards": ["1.5", "per month", "date of joining"],
    },
    "2.3": {
        "text": "Leave application must be submitted at least 14 calendar days in advance, using Form HR-L1.",
        "guards": ["must", "14", "calendar days", "Form HR-L1"],
    },
    "2.4": {
        "text": "Leave applications must receive written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
        "guards": ["must", "written approval", "direct manager", "before the leave commences", "verbal approval", "not valid"],
    },
    "2.5": {
        "text": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "guards": ["will be recorded", "Loss of Pay", "LOP", "regardless of subsequent approval"],
    },
    "2.6": {
        "text": "A maximum of 5 unused annual leave days may be carried forward to the following calendar year; any days above 5 are forfeited on 31 December.",
        "guards": ["5", "may", ["carry forward", "carried forward"], "following calendar year", "above 5", "are forfeited", "31 December"],
    },
    "2.7": {
        "text": "Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited.",
        "guards": ["must", "first quarter", "January-March", "following year", "forfeited"],
    },
    "3.1": {
        "text": "Each employee is entitled to 12 days of paid sick leave per calendar year.",
        "guards": ["12", "paid sick leave", "calendar year", "entitled"],
    },
    "3.2": {
        "text": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
        "guards": ["3", "consecutive days", "requires", "medical certificate", "registered medical practitioner", "48 hours", "returning to work"],
    },
    "3.3": {
        "text": "Sick leave cannot be carried forward to the following year.",
        "guards": ["cannot", "carried forward", "following year"],
    },
    "3.4": {
        "text": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
        "guards": ["immediately before or after", "public holiday", "annual leave period", "requires", "medical certificate", "regardless of duration"],
    },
    "4.1": {
        "text": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
        "guards": ["female employees", "entitled", "26 weeks", "paid maternity leave", "first two live births"],
    },
    "4.2": {
        "text": "For a third or subsequent child, maternity leave is 12 weeks paid.",
        "guards": ["third or subsequent child", "12 weeks", "paid"],
    },
    "4.3": {
        "text": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
        "guards": ["male employees", "entitled", "5 days", "paid paternity leave", "30 days", "child's birth"],
    },
    "4.4": {
        "text": "Paternity leave cannot be split across multiple periods.",
        "guards": ["cannot", "split", "multiple periods"],
    },
    "5.1": {
        "text": "LWP may be applied for only after exhausting all applicable paid leave entitlements.",
        "guards": ["may", "only after", "exhausting", "paid leave entitlements"],
    },
    "5.2": {
        "text": "LWP requires approval from both the Department Head and the HR Director; manager approval alone is not sufficient.",
        "guards": ["requires", "department head", "hr director", "manager approval alone", "not sufficient"],
    },
    "5.3": {
        "text": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
        "guards": ["exceeding", "30 continuous days", "requires", "Municipal Commissioner"],
    },
    "5.4": {
        "text": "Periods of LWP do not count toward service for seniority, increments, or retirement benefits.",
        "guards": ["do not count toward service", "seniority", "increments", "retirement benefits"],
    },
    "6.1": {
        "text": "Employees are entitled to all gazetted public holidays as declared by the State Government each year.",
        "guards": ["entitled", "gazetted public holidays", "State Government", "each year"],
    },
    "6.2": {
        "text": "An employee required to work on a public holiday is entitled to one compensatory off day, to be taken within 60 days of the holiday worked.",
        "guards": ["required to work", "public holiday", "one compensatory off day", "60 days", "holiday worked"],
    },
    "6.3": {
        "text": "Compensatory off cannot be encashed.",
        "guards": ["cannot", "encashed"],
    },
    "7.1": {
        "text": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days.",
        "guards": ["may be encashed", "only", "retirement", "resignation", "maximum of 60 days"],
    },
    "7.2": {
        "text": "Leave encashment during service is not permitted under any circumstances.",
        "guards": ["not permitted", "under any circumstances", "during service"],
    },
    "7.3": {
        "text": "Sick leave and LWP cannot be encashed under any circumstances.",
        "guards": ["cannot", "encashed", "under any circumstances"],
    },
    "8.1": {
        "text": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
        "guards": ["must", "HR Department", "10 working days", "disputed decision"],
    },
    "8.2": {
        "text": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
        "guards": ["after 10 working days", "will not be considered", "exceptional circumstances", "in writing"],
    },
}

FLAG_MARK = "[FLAGGED: quoted verbatim]"


def _norm(text):
    text = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2019", "'")
    return re.sub(r"\s+", " ", text).strip().lower()


def _guard_present(guard, norm_text):
    guard_n = _norm(guard)
    if re.fullmatch(r"[\w\s/-]+", guard_n):
        pattern = r"(?<![a-z0-9])" + re.escape(guard_n).replace(r"\ ", r"\s+") + r"(?![a-z0-9])"
        return re.search(pattern, norm_text) is not None
    return guard_n in norm_text


def _concept_present(concept, norm_src, norm_cond):
    variants = concept if isinstance(concept, list) else [concept]
    return any(_guard_present(v, norm_src) for v in variants) and any(
        _guard_present(v, norm_cond) for v in variants
    )


def retrieve_policy(path):
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        sys.exit(f"error: cannot read input file '{path}': {exc}")

    sections = []
    pending_title = None
    current = None
    open_clause = None

    for raw in lines:
        line = raw.rstrip()
        if SEP_RE.match(line):
            continue
        stripped = line.strip()
        if not stripped:
            continue
        match = CLAUSE_RE.match(stripped)
        if match:
            num, first = match.group(1), match.group(2).strip()
            if pending_title is not None:
                current = {"title": pending_title, "clauses": {}}
                sections.append(current)
                pending_title = None
            if current is None:
                current = {"title": "", "clauses": {}}
                sections.append(current)
            current["clauses"][num] = first
            open_clause = num
        elif open_clause is not None:
            current["clauses"][open_clause] = current["clauses"][open_clause] + " " + stripped
            if pending_title is not None:
                pending_title = None
        else:
            pending_title = stripped

    total = sum(len(sec["clauses"]) for sec in sections)
    if total == 0:
        sys.exit(f"error: no numbered clauses recognised in '{path}' - aborting rather than emitting an empty summary")

    return sections


def _verbatim(num, text):
    flat = re.sub(r"\s+", " ", text).strip()
    return f"{num} {flat} {FLAG_MARK}"


def summarize_policy(sections):
    out = []
    condensed_count = 0
    flagged_count = 0
    for sec in sections:
        if sec["title"]:
            out.append("")
            out.append(sec["title"])
        for num, text in sec["clauses"].items():
            entry = CONDENSED.get(num)
            norm_src = _norm(text)
            usable = False
            if entry:
                norm_cond = _norm(entry["text"])
                guards_ok = all(_concept_present(g, norm_src, norm_cond) for g in entry["guards"])
                src_verbs = [p for p in STRONG_VERB_PATTERNS if re.search(p, norm_src)]
                verbs_ok = (
                    not src_verbs
                    or any(re.search(p, norm_cond) for p in src_verbs)
                )
                usable = guards_ok and verbs_ok
            if usable:
                out.append(f"{num} {entry['text']}")
                condensed_count += 1
            else:
                out.append(_verbatim(num, text))
                flagged_count += 1
    return "\n".join(out).lstrip("\n"), condensed_count, flagged_count


def _validate(summary, sections, condensed_count):
    parsed_nums = {num for sec in sections for num in sec["clauses"]}
    summary_nums = set(re.findall(r"^(\d+\.\d+)\s", summary, re.M))
    missing = parsed_nums - summary_nums
    if missing:
        sys.exit(f"error: clauses missing from summary: {sorted(missing)} - refusing to write output")
    extra = summary_nums - parsed_nums
    if extra:
        sys.exit(f"error: summary references unknown clauses: {sorted(extra)} - refusing to write output")
    norm_summary = _norm(summary)
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase in norm_summary:
            sys.exit(f"error: scope-bleed phrase '{phrase}' detected - refusing to write output")


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B deterministic policy summariser (meaning-preserving)."
    )
    parser.add_argument("--input", required=True, help="path to the plain-text policy document")
    parser.add_argument("--output", required=True, help="path to write the summary")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    body, condensed_count, flagged_count = summarize_policy(sections)
    _validate(body, sections, condensed_count)

    total = sum(len(sec["clauses"]) for sec in sections)
    header_lines = []
    try:
        with open(args.input, encoding="utf-8") as fh:
            head = fh.read(2048)
        ref = DOCREF_RE.search(head)
        ver = VERSION_RE.search(head)
        if ref:
            header_lines.append(f"Source: {ref.group(1).strip()}")
        if ver:
            header_lines.append(f"Version: {ver.group(1).strip()}")
    except OSError:
        pass

    parts = ["UC-0B Policy Summary"]
    parts.extend(header_lines)
    parts.append(
        f"Clauses: {total} total, {condensed_count} condensed, {flagged_count} "
        f"{FLAG_MARK}. Every clause retains its original obligations."
    )
    document = "\n".join(parts) + "\n\n" + body + "\n"

    try:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(document)
    except OSError as exc:
        sys.exit(f"error: cannot write output file '{args.output}': {exc}")

    print(f"Wrote {args.output}: {total} clauses ({condensed_count} condensed, {flagged_count} flagged verbatim)")


if __name__ == "__main__":
    main()
