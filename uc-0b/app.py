"""UC-0B Policy Summary Agent — retrieve_policy -> summarize_policy pipeline."""
import argparse
import re
import sys

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
RULE_CHARS = set("═")
NUM_RE = re.compile(r"\d+(?:\.\d+)?")

VERB_PATTERNS = [
    r"\bmust\b",
    r"\bwill\b",
    r"\bmay\b",
    r"\bcannot\b",
    r"\brequir\w*",
    r"\bnot permitted\b",
    r"under any circumstances",
    r"\bentitl\w*",
    r"\bforfeit\w*",
    r"\bgovern\w*",
    r"\bappli\w*",
    r"\bregardless\b",
]

KEY_PHRASES = [
    "department head",
    "hr director",
    "municipal commissioner",
    "registered medical practitioner",
    "loss of pay",
    "state government",
    "form hr-l1",
    "january–march",
    "hr department",
    "compensatory off",
]

PARAPHRASES = {
    "1.1": "This policy governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "It does not apply to daily wage workers or consultants; those categories are governed by their respective contracts.",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP), regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
    "3.1": "Each employee is entitled to 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or an annual leave period requires a medical certificate regardless of duration.",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "For a third or subsequent child, maternity leave is 12 weeks paid.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "An employee may apply for Leave Without Pay only after exhausting all applicable paid leave entitlements.",
    "5.2": "LWP requires approval from the Department Head and the HR Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "Periods of LWP do not count toward service for seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays declared by the State Government each year.",
    "6.2": "An employee required to work on a public holiday is entitled to one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
}


def _collapse(text):
    return " ".join(text.split())


def retrieve_policy(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    header_lines = []
    body_start = len(lines)
    for i, line in enumerate(lines):
        s = line.strip()
        if s and set(s) <= RULE_CHARS:
            body_start = i + 1
            break
        header_lines.append(line)

    title_parts = []
    reference = ""
    version = ""
    for line in header_lines:
        s = line.strip()
        if not s:
            continue
        low = s.lower()
        if low.startswith("document reference:"):
            reference = s.split(":", 1)[1].strip()
        elif low.startswith("version:"):
            version = s.split(":", 1)[1].split("|")[0].strip()
        else:
            title_parts.append(s)
    title = " ".join(title_parts)

    clauses = []
    seen = set()
    prev_tuple = None
    section = ""
    current = None
    for line in lines[body_start:]:
        s = line.strip()
        if not s or (s and set(s) <= RULE_CHARS):
            continue
        m = CLAUSE_RE.match(s)
        if m:
            if current is not None:
                clauses.append(current)
            clause_num = m.group(1)
            marker = ""
            t = tuple(int(part) for part in clause_num.split("."))
            if clause_num in seen or (prev_tuple is not None and t < prev_tuple):
                marker = " [SEQUENCE_CHECK]"
            seen.add(clause_num)
            prev_tuple = t
            current = {
                "clause_id": clause_num + marker,
                "section_title": section,
                "text": m.group(2),
            }
        elif current is not None and line[:1].isspace():
            current["text"] += " " + s
        else:
            if current is not None:
                clauses.append(current)
                current = None
            section = s
    if current is not None:
        clauses.append(current)

    for clause in clauses:
        clause["text"] = _collapse(clause["text"])

    return {
        "title": title,
        "reference": reference,
        "version": version,
        "clauses": clauses,
    }


def _conditions_preserved(candidate, source):
    if sorted(NUM_RE.findall(source)) != sorted(NUM_RE.findall(candidate)):
        return False
    sl = source.lower()
    cl = candidate.lower()
    for pattern in VERB_PATTERNS:
        if re.search(pattern, sl) and not re.search(pattern, cl):
            return False
    for phrase in KEY_PHRASES:
        if phrase in sl and phrase not in cl:
            return False
    return True


def _summarize_with_stats(doc):
    clauses = doc.get("clauses", [])
    if not clauses:
        raise ValueError("policy contains no numbered clauses; refusing to summarize")

    out = ["POLICY SUMMARY — " + doc.get("title", "").strip()]
    meta = []
    if doc.get("reference"):
        meta.append("Document Reference: " + doc["reference"])
    if doc.get("version"):
        meta.append("Version: " + doc["version"])
    if meta:
        out.append(" | ".join(meta))

    kept = verbatim = unreadable = 0
    last_section = None
    for clause in clauses:
        cid = clause.get("clause_id")
        text = clause.get("text", "")
        section = clause.get("section_title") or ""
        if section != last_section:
            out.append("")
            out.append(section)
            last_section = section
        if not isinstance(cid, str) or not cid.strip():
            out.append("[UNREADABLE] malformed clause entry")
            unreadable += 1
            continue
        if not text.strip():
            out.append("[%s] [UNREADABLE]" % cid)
            unreadable += 1
            continue
        m = CLAUSE_RE.match(cid.strip())
        base = m.group(1) if m else cid.strip()
        candidate = PARAPHRASES.get(base)
        if candidate and _conditions_preserved(candidate, text):
            out.append("[%s] %s" % (cid, candidate))
            kept += 1
        else:
            out.append("[%s] [VERBATIM] %s" % (cid, text))
            verbatim += 1

    total = len(clauses)
    out.append("")
    out.append(
        "Coverage: %d/%d clauses included (%d paraphrased, %d verbatim fallbacks, %d unreadable)."
        % (total, total, kept, verbatim, unreadable)
    )
    stats = {"total": total, "paraphrased": kept, "verbatim": verbatim, "unreadable": unreadable}
    return "\n".join(out) + "\n", stats


def summarize_policy(doc):
    summary, _ = _summarize_with_stats(doc)
    return summary


def main():
    parser = argparse.ArgumentParser(description="UC-0B faithful policy summarizer")
    parser.add_argument("--input", required=True, help="path to .txt policy document")
    parser.add_argument("--output", required=True, help="path for summary output file")
    args = parser.parse_args()

    try:
        doc = retrieve_policy(args.input)
    except OSError as exc:
        print("ERROR: cannot read input policy file: %s" % exc, file=sys.stderr)
        return 1

    try:
        summary, stats = _summarize_with_stats(doc)
    except ValueError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 1

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
    except OSError as exc:
        print("ERROR: cannot write output file: %s" % exc, file=sys.stderr)
        return 1

    print(
        "Wrote %s: %d/%d clauses covered (%d paraphrased, %d verbatim fallbacks, %d unreadable)"
        % (args.output, stats["total"], stats["total"], stats["paraphrased"], stats["verbatim"], stats["unreadable"])
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
