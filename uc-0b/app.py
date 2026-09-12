"""
UC-0B app.py — Summary That Changes Meaning
Built from agents.md (role / intent / context / enforcement) and skills.md
(retrieve_policy, summarize_policy). Standard library only.

Design: a summary is only ever accepted if it provably keeps every number,
date, form name, role title, and binding verb of the source clause. Anything
that fails that check is emitted verbatim with a [VERBATIM] tag. This makes
clause omission, condition drops, and obligation softening impossible by
construction rather than by hoping the prose is careful.

Enforcement rule -> code:
  every clause present, in order    -> retrieve_policy(), summarize_policy()
  all conditions preserved          -> validate_summary()
  binding verbs keep force          -> BINDING_VERBS / SOFTENERS in validate_summary()
  numbers / dates / titles unchanged-> protected_tokens()
  never add information             -> FORBIDDEN_PHRASES + every line maps to a clause id
  verbatim + flag on meaning loss   -> DEFAULT_VERBATIM + fallback in summarize_policy()
  refusal condition                 -> retrieve_policy() raises; main() prints ERROR, exit 1
  completeness footer               -> summarize_policy() footer + final assert
"""
import argparse
import os
import re
import sys

# --------------------------------------------------------------------------
# Constants from agents.md
# --------------------------------------------------------------------------
DEFAULT_VERBATIM = ["2.5", "5.2", "7.2"]

# Words that carry obligation force. If one appears in the source clause it
# must appear in the summary of that clause.
BINDING_VERBS = [
    "must", "will", "requires", "may", "cannot", "not permitted", "not valid",
    "not sufficient", "do not", "does not", "not be considered", "only",
    "regardless", "unless", "under any circumstances",
]
# Words that weaken an obligation. Never allowed in a summary line unless
# the source clause itself contains them.
SOFTENERS = [
    "should", "is encouraged", "are encouraged", "is expected", "are expected",
    "typically", "usually", "generally", "normally", "ideally", "recommended",
    "where possible", "if possible", "advisable",
]
# Scope-bleed phrases from the README. Never allowed anywhere in the output.
FORBIDDEN_PHRASES = [
    "as is standard practice", "standard practice", "typically in government",
    "in government organisations", "in most organisations",
    "employees are generally expected", "generally expected", "best practice",
    "it is common", "as usual", "in line with industry",
]

# Curated compressions for HR-POL-001. Each one is validated against the
# source clause at run time; any that fails falls back to verbatim. Clauses
# without an entry are emitted verbatim. This is the only place a human
# paraphrase enters the pipeline, and it never bypasses validation.
SUMMARY_TEMPLATES = {
    "1.1": "Governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "Does not apply to daily wage workers or consultants; those categories are governed by their respective contracts.",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
    "3.1": "Each employee is entitled to 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "For a third or subsequent child, maternity leave is 12 weeks paid.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "An employee may apply for Leave Without Pay only after exhausting all applicable paid leave entitlements.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "Periods of LWP do not count toward service for seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays declared by the State Government each year.",
    "6.2": "An employee required to work on a public holiday is entitled to one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
}

_SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 ,&()/-]+)\s*$")
_CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*\S)\s*$")
_DIVIDER_RE = re.compile(r"^[═=\-—_]{5,}\s*$")


# --------------------------------------------------------------------------
# Skill 1: retrieve_policy  (skills.md)
# --------------------------------------------------------------------------
def retrieve_policy(path: str) -> dict:
    """
    Load a .txt policy and return {title, sections, clause_count, warnings}.
    Raises ValueError with a clear message on missing/empty/unnumbered input.
    """
    if not os.path.isfile(path):
        raise ValueError(f"input file not found: {path}")
    try:
        with open(path, encoding="utf-8-sig") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError) as e:
        raise ValueError(f"could not read {path}: {e}")

    title_lines, sections, warnings = [], [], []
    current_section, current_clause = None, None
    seen_ids = set()

    for raw in lines:
        line = raw.rstrip()
        if not line.strip() or _DIVIDER_RE.match(line.strip()):
            continue

        m_sec = _SECTION_RE.match(line)
        if m_sec:
            current_clause = None
            current_section = {
                "number": int(m_sec.group(1)),
                "heading": m_sec.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            continue

        m_cl = _CLAUSE_RE.match(line)
        if m_cl and current_section is not None:
            cid = m_cl.group(1)
            if cid in seen_ids:
                warnings.append(f"duplicate clause id {cid}")
            seen_ids.add(cid)
            if not cid.startswith(f"{current_section['number']}."):
                warnings.append(f"clause {cid} appears under section {current_section['number']}")
            current_clause = {"id": cid, "text": m_cl.group(2).strip(), "section": current_section["number"]}
            current_section["clauses"].append(current_clause)
            continue

        # Continuation line (indented wrap) belongs to the open clause.
        if current_clause is not None and line.startswith((" ", "\t")):
            current_clause["text"] += " " + line.strip()
            continue

        if current_section is None:
            title_lines.append(line.strip())
        else:
            warnings.append(f"unattached line ignored: {line.strip()[:60]}")

    clause_count = sum(len(s["clauses"]) for s in sections)
    if clause_count == 0:
        raise ValueError("no numbered clauses of the form N.N found in the input")

    return {
        "title": "\n".join(title_lines),
        "sections": sections,
        "clause_count": clause_count,
        "warnings": warnings,
    }


# --------------------------------------------------------------------------
# Validation helpers (enforcement rules 3, 4, 5, 6)
# --------------------------------------------------------------------------
_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
_FORM_RE = re.compile(r"\bForm [A-Z0-9-]+")
_TITLE_RE = re.compile(r"\b(?:[A-Z][a-z]+|[A-Z]{2,})(?: (?:of|and|the))?(?: (?:[A-Z][a-z]+|[A-Z]{2,}))+\b")
_MONTH_RE = re.compile(
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b"
)
_KEY_WORDS = [
    "written", "verbal", "consecutive", "continuous", "immediately", "exhausting",
    "forfeited", "encashed", "in writing", "direct manager", "manager approval",
    "first two", "third or subsequent", "female", "male", "gazetted",
]


def protected_tokens(text: str) -> list:
    """Tokens that must survive summarisation unchanged (case-insensitive)."""
    tokens = set(_NUMBER_RE.findall(text))
    tokens.update(_FORM_RE.findall(text))
    tokens.update(_MONTH_RE.findall(text))
    tokens.update(t for t in _TITLE_RE.findall(text) if len(t.split()) >= 2)
    low = text.lower()
    tokens.update(k for k in _KEY_WORDS if k in low)
    tokens.update(v for v in BINDING_VERBS if re.search(r"\b" + re.escape(v) + r"\b", low))
    return sorted(tokens)


def validate_summary(source: str, summary: str) -> list:
    """
    Return a list of reasons the summary is NOT acceptable. Empty list = OK.
    """
    problems = []
    s_low, sum_low = source.lower(), summary.lower()
    for tok in protected_tokens(source):
        if tok.lower() not in sum_low:
            problems.append(f"missing '{tok}'")
    for soft in SOFTENERS:
        if soft in sum_low and soft not in s_low:
            problems.append(f"softener '{soft}' added")
    for phrase in FORBIDDEN_PHRASES:
        if phrase in sum_low:
            problems.append(f"forbidden phrase '{phrase}'")
    # Summary must not introduce numbers the source does not have.
    for num in set(_NUMBER_RE.findall(summary)) - set(_NUMBER_RE.findall(source)):
        problems.append(f"added number '{num}'")
    if len(summary) > len(source) + 20:
        problems.append("summary is longer than the source clause")
    return problems


# --------------------------------------------------------------------------
# Skill 2: summarize_policy  (skills.md)
# --------------------------------------------------------------------------
def summarize_policy(policy: dict, verbatim_ids=None, log=None) -> str:
    """
    Produce the summary text. Every clause id in `policy` appears exactly
    once, in order, either summarised (validated) or [VERBATIM].
    """
    if policy.get("clause_count", 0) == 0:
        return "ERROR: policy contains no clauses"
    verbatim_ids = set(verbatim_ids if verbatim_ids is not None else DEFAULT_VERBATIM)
    log = log if log is not None else (lambda msg: None)

    out = []
    header = policy["title"].splitlines()
    doc_ref = next((h for h in header if h.lower().startswith("document reference")), "")
    version = next((h for h in header if h.lower().startswith("version")), "")
    out.append("SUMMARY — " + (header[2] if len(header) > 2 else "POLICY"))
    if doc_ref:
        out.append(doc_ref)
    if version:
        out.append(version)
    out.append("Each numbered clause of the source appears below once, in source order.")
    out.append("[VERBATIM] marks clauses reproduced word for word because shortening would change meaning.")
    out.append("")

    emitted_ids = []
    verbatim_count = 0
    for sec in policy["sections"]:
        out.append(f"{sec['number']}. {sec['heading']}")
        for cl in sec["clauses"]:
            cid, src = cl["id"], cl["text"]
            candidate = SUMMARY_TEMPLATES.get(cid)
            use_verbatim = cid in verbatim_ids or candidate is None
            if not use_verbatim:
                problems = validate_summary(src, candidate)
                if problems:
                    log(f"{cid}: summary rejected ({'; '.join(problems)}) -> verbatim")
                    use_verbatim = True
            if use_verbatim:
                out.append(f"{cid}  [VERBATIM] {src}")
                verbatim_count += 1
            else:
                out.append(f"{cid}  {candidate}")
            emitted_ids.append(cid)
        out.append("")

    # Completeness recovery: any id somehow missing is appended verbatim.
    all_ids = [c["id"] for s in policy["sections"] for c in s["clauses"]]
    missing = [i for i in all_ids if i not in emitted_ids]
    if missing:
        out.append("RECOVERED CLAUSES")
        for sec in policy["sections"]:
            for cl in sec["clauses"]:
                if cl["id"] in missing:
                    out.append(f"{cl['id']}  [VERBATIM] {cl['text']}")
                    emitted_ids.append(cl["id"])
                    log(f"{cl['id']}: recovered verbatim")
        out.append("")

    out.append(
        f"Clauses in source: {policy['clause_count']} | Clauses in summary: {len(emitted_ids)} "
        f"| Verbatim: {verbatim_count}"
    )
    return "\n".join(out) + "\n"


def final_checks(policy: dict, text: str) -> list:
    """Whole-output checks from the enforcement list. Returns problems."""
    problems = []
    low = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in low:
            problems.append(f"forbidden phrase in output: '{phrase}'")
    expected = [c["id"] for s in policy["sections"] for c in s["clauses"]]
    found = re.findall(r"^(\d+\.\d+)  ", text, flags=re.M)
    if found != expected:
        problems.append(f"clause ids in output {found} != source {expected}")
    return problems


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    parser.add_argument("--verbatim", default=",".join(DEFAULT_VERBATIM),
                        help="Comma-separated clause ids to always quote verbatim")
    args = parser.parse_args()

    try:
        policy = retrieve_policy(args.input)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    for w in policy["warnings"]:
        print(f"WARNING: {w}", file=sys.stderr)

    verbatim_ids = [v.strip() for v in args.verbatim.split(",") if v.strip()]
    text = summarize_policy(policy, verbatim_ids, log=lambda m: print(f"NOTE: {m}", file=sys.stderr))
    if text.startswith("ERROR:"):
        print(text.strip(), file=sys.stderr)
        sys.exit(1)

    problems = final_checks(policy, text)
    if problems:
        for p in problems:
            print(f"ERROR: {p}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(text)
    print(
        f"Done. Summary written to {args.output} "
        f"({policy['clause_count']} clauses in source, all present in summary)"
    )


if __name__ == "__main__":
    main()
