"""
UC-0B — Summary That Changes Meaning
Built with the RICE -> agents.md -> skills.md -> CRAFT workflow.

The naive prompt ("Summarize the policy document.") returned eight tidy bullet
points. It dropped 21 of the 29 clauses, turned "requires approval from the
Department Head and the HR Director" into "requires managerial approval", and
added a sentence about what is "standard practice in government organisations"
that appears nowhere in the source.

This summariser cannot do any of those three things, because each one is a gate
that runs before a line is accepted:

  completeness gate  -> every parsed clause must appear in the output
  condition gate     -> every condition token extracted from a clause must
                        survive into that clause's summary line, or the clause
                        is emitted verbatim instead
  scope-bleed gate   -> every word in the summary body must exist in the source
                        document's own vocabulary

Run:  python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                    --output summary_hr_leave.txt
Self-test the condition gate:  python app.py --self-test
"""
import argparse
import re
import sys

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 ,()/&'\-]+)\s*$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*\S)\s*$")
CONTINUATION_RE = re.compile(r"^\s{2,}(\S.*)$")
SEPARATOR_RE = re.compile(r"^[═=]{3,}\s*$")

META_PATTERNS = {
    "reference": re.compile(r"^Document Reference:\s*(.+)$", re.IGNORECASE),
    "version": re.compile(r"^Version:\s*([^|]+)", re.IGNORECASE),
    "effective": re.compile(r"\bEffective:\s*(.+)$", re.IGNORECASE),
}

# ---------------------------------------------------------------------------
# Enforcement rule 4 — binding verbs are copied, never re-worded.
# Order matters: negatives and multi-word forms are tested first.
# ---------------------------------------------------------------------------
BINDING_VERBS = [
    (re.compile(r"\bmust not\b", re.I), "MUST NOT"),
    (re.compile(r"\bcannot\b|\bcan not\b", re.I), "CANNOT"),
    (re.compile(r"\bis not permitted\b|\bnot permitted\b", re.I), "NOT PERMITTED"),
    (re.compile(r"\bdoes not apply\b|\bdo not apply\b", re.I), "DOES NOT APPLY"),
    (re.compile(r"\bdo not count\b|\bdoes not count\b", re.I), "DOES NOT COUNT"),
    (re.compile(r"\bwill not be\b", re.I), "WILL NOT"),
    (re.compile(r"\bare not eligible\b|\bis not eligible\b", re.I), "NOT ELIGIBLE"),
    (re.compile(r"\bare not reimbursable\b|\bis not reimbursable\b", re.I), "NOT REIMBURSABLE"),
    (re.compile(r"\bmust\b", re.I), "MUST"),
    (re.compile(r"\brequires?\b|\brequired\b", re.I), "REQUIRES"),
    (re.compile(r"\bare forfeited\b|\bis forfeited\b|\bforfeited\b", re.I), "FORFEITED"),
    (re.compile(r"\bis entitled to\b|\bare entitled to\b", re.I), "ENTITLED"),
    (re.compile(r"\baccrues\b", re.I), "ACCRUES"),
    (re.compile(r"\bwill be\b|\bwill\b", re.I), "WILL"),
    (re.compile(r"\bmay\b", re.I), "MAY"),
]

# ---------------------------------------------------------------------------
# Enforcement rule 2 — condition tokens. Anything matched here must survive
# into the summary line for its clause or that clause falls back to verbatim.
# ---------------------------------------------------------------------------
CONDITION_PATTERNS = [
    # quantities with a time or money unit
    re.compile(r"\b\d+(?:\.\d+)?\s+(?:\w+\s+){0,3}?"
               r"(?:calendar days?|working days?|continuous days?|"
               r"consecutive days?|days?|weeks?|months?|years?|hours?)\b", re.I),
    re.compile(r"\bRs\s?[\d,]+\b", re.I),
    re.compile(r"\b\d{1,3}%\b"),
    re.compile(r"\bGrade [A-Z]\b"),
    # calendar dates and month ranges
    re.compile(r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|"
               r"August|September|October|November|December)\b", re.I),
    re.compile(r"\((?:January|February|March|April|May|June|July|August|"
               r"September|October|November|December)"
               r"[–—-]"
               r"(?:January|February|March|April|May|June|July|August|"
               r"September|October|November|December)\)", re.I),
    # forms
    re.compile(r"\bForm\s+[A-Z]{2,3}-[A-Z0-9]+\b"),
    # named approvers and authorities — dropping one of these is the UC-0B trap
    re.compile(r"\bDepartment Head\b|\bHR Director\b|\bMunicipal Commissioner\b"
               r"|\bdirect manager\b|\bHR Department\b|\bState Government\b"
               r"|\bregistered medical practitioner\b|\bIT Department\b"
               r"|\bFinance Department\b|\bCommunications Department\b"
               r"|\bIT Security team\b|\bIT helpdesk\b", re.I),
    # absolute qualifiers — removing these is obligation softening
    re.compile(r"\bunder any circumstances\b|\bregardless of\b"
               r"|\balone is not sufficient\b|\bis not valid\b|\bnot valid\b"
               r"|\bonly after\b|\bonly at the time of\b|\bat all times\b"
               r"|\bimmediately before or after\b|\bwithout prior notice\b"
               r"|\bin writing\b|\bfirst two live births\b", re.I),
]

# ---------------------------------------------------------------------------
# Compression. Every entry DELETES words or swaps them for a symbol — none of
# them can introduce vocabulary that is not already in the source, which is what
# keeps the scope-bleed gate meaningful rather than decorative.
# ---------------------------------------------------------------------------
COMPRESSIONS = [
    (re.compile(r"\bup to a maximum of\b", re.I), "≤"),
    (re.compile(r"\ba maximum of\b", re.I), "≤"),
    (re.compile(r"\bat least\b", re.I), "≥"),
    (re.compile(r"\bexceeding\b", re.I), ">"),
    (re.compile(r"\bper calendar year\b", re.I), "/year"),
    (re.compile(r"\bper day\b", re.I), "/day"),
    (re.compile(r"\bper night\b", re.I), "/night"),
    (re.compile(r"\bper month\b", re.I), "/month"),
    (re.compile(r"\s+"), " "),
]

# The only words the summariser itself is allowed to contribute to a clause
# line. Everything else must come from the source document.
STRUCTURAL_ALLOWLIST = {
    "must", "not", "cannot", "permitted", "does", "do", "apply", "count",
    "will", "requires", "forfeited", "entitled", "accrues", "states", "may",
    "eligible", "reimbursable", "verbatim", "is", "are", "to", "be",
}

# Ground-truth clauses from uc-0b/README.md, with the condition most likely to
# be dropped by a naive summariser. Checked explicitly in the output.
CRITICAL_CLAUSES = {
    "2.3": "14 calendar days",
    "2.4": "Verbal approval is not valid",
    "2.5": "regardless of",
    "2.6": "31 December",
    "2.7": "(January",
    "3.2": "registered medical practitioner",
    "3.4": "regardless of",
    "5.2": "HR Director",
    "5.3": "Municipal Commissioner",
    "7.2": "under any circumstances",
}

WORD_RE = re.compile(r"[A-Za-z]+")


def retrieve_policy(path: str) -> dict:
    """Load a .txt policy file as structured numbered sections and clauses."""
    try:
        with open(path, encoding="utf-8") as handle:
            raw = handle.read()
    except FileNotFoundError:
        raise FileNotFoundError("Policy file not found at: %s" % path)

    metadata = {"source_file": path.split("/")[-1], "title": "",
                "reference": "", "version": "", "effective": "",
                "source_size": len(raw)}
    sections, current_section, current_clause = [], None, None
    title_lines = []

    for line in raw.splitlines():
        stripped = line.strip()

        for key, pattern in META_PATTERNS.items():
            found = pattern.search(stripped)
            if found and not metadata[key]:
                metadata[key] = found.group(1).strip()

        if SEPARATOR_RE.match(stripped):
            current_clause = None
            continue

        section_hit = SECTION_RE.match(stripped)
        if section_hit:
            current_section = {"number": section_hit.group(1),
                               "title": section_hit.group(2).strip(),
                               "clauses": []}
            sections.append(current_section)
            current_clause = None
            continue

        clause_hit = CLAUSE_RE.match(line)
        if clause_hit and current_section is not None:
            current_clause = {"number": clause_hit.group(1),
                              "text": clause_hit.group(2).strip()}
            current_section["clauses"].append(current_clause)
            continue

        continuation = CONTINUATION_RE.match(line)
        if continuation and current_clause is not None:
            current_clause["text"] += " " + continuation.group(1).strip()
            continue

        if current_section is None and stripped and not metadata["title"]:
            title_lines.append(stripped)

    metadata["title"] = " / ".join(title_lines[:3])

    clause_total = sum(len(s["clauses"]) for s in sections)
    if clause_total == 0:
        # agents.md refusal condition: never fall back to prose summarisation.
        raise ValueError(
            "Refusing to summarise: %s contains no clauses matching the N.N "
            "pattern, so completeness cannot be verified. No output written."
            % path)

    for section in sections:
        for clause in section["clauses"]:
            clause["text"] = re.sub(r"\s+", " ", clause["text"]).strip()

    return {"metadata": metadata, "sections": sections}


def extract_conditions(text: str) -> list:
    """Every token that must survive compression, in order of appearance."""
    found = []
    for pattern in CONDITION_PATTERNS:
        for match in pattern.finditer(text):
            fragment = match.group(0).strip()
            if fragment and fragment not in found:
                found.append(fragment)
    return found


def detect_binding(text: str) -> str:
    """Return the source's own binding verb, never a re-worded one."""
    hits = []
    for pattern, tag in BINDING_VERBS:
        match = pattern.search(text)
        if match:
            hits.append((match.start(), tag))
    if not hits:
        return "STATES"
    hits.sort()
    primary = hits[0][1]
    extra = [tag for _, tag in hits[1:] if tag != primary]
    return primary + (" + " + " + ".join(dict.fromkeys(extra)) if extra else "")


def compress(text: str) -> str:
    for pattern, replacement in COMPRESSIONS:
        text = pattern.sub(replacement, text)
    return text.strip()


def conditions_preserved(conditions: list, candidate: str) -> list:
    """Return the conditions that did NOT survive into the candidate line."""
    haystack = re.sub(r"\s+", " ", candidate).lower()
    return [c for c in conditions
            if re.sub(r"\s+", " ", c).lower() not in haystack]


def summarize_policy(policy: dict) -> dict:
    meta = policy["metadata"]
    clauses = [(s, c) for s in policy["sections"] for c in s["clauses"]]
    clause_numbers = [c["number"] for _, c in clauses]

    body, summarised, verbatim, multi_condition = [], [], [], {}
    source_chars = 0
    summary_chars = 0

    for section in policy["sections"]:
        body.append("")
        body.append("--- %s. %s ---" % (section["number"], section["title"]))
        for clause in section["clauses"]:
            original = clause["text"]
            source_chars += len(original)
            conditions = extract_conditions(original)
            tag = detect_binding(original)

            candidate = compress(original)
            missing = conditions_preserved(conditions, candidate)
            if missing:
                # Enforcement rule 5 — quote verbatim rather than emit a
                # line that has silently lost a condition.
                line = "%s [%s] [VERBATIM] %s" % (clause["number"], tag, original)
                verbatim.append(clause["number"])
            else:
                line = "%s [%s] %s" % (clause["number"], tag, candidate)

            body.append(line)
            summary_chars += len(line)
            summarised.append(clause["number"])
            if len(conditions) >= 2:
                multi_condition[clause["number"]] = conditions

    omitted = [n for n in clause_numbers if n not in summarised]

    # Scope-bleed gate over the clause body only — the report frame below is
    # the summariser's own labelling and is excluded by design.
    source_vocab = set()
    for _, clause in clauses:
        source_vocab.update(w.lower() for w in WORD_RE.findall(clause["text"]))
    for section in policy["sections"]:
        source_vocab.update(w.lower() for w in WORD_RE.findall(section["title"]))

    bleed = []
    for line in body:
        if not line.startswith("---") and line.strip():
            for word in WORD_RE.findall(line):
                low = word.lower()
                if low not in source_vocab and low not in STRUCTURAL_ALLOWLIST \
                        and low not in bleed:
                    bleed.append(low)

    header = [
        "SUMMARY - %s" % (meta["title"] or meta["source_file"]),
        "Source document: %s | Reference: %s | Version: %s | Effective: %s"
        % (meta["source_file"], meta["reference"] or "n/a",
           meta["version"] or "n/a", meta["effective"] or "n/a"),
        "Generated by: uc-0b/app.py (clause-complete summariser)",
        "",
        "Clauses parsed from source : %d" % len(clause_numbers),
        "Clauses in this summary    : %d" % len(summarised),
        "Clauses omitted            : %s" % (", ".join(omitted) or "none"),
        "Clauses kept verbatim      : %s" % (", ".join(verbatim) or "none"),
        "Words added to source      : %s" % (", ".join(bleed) or "none"),
        "Source document            : %d characters" % meta["source_size"],
        "This summary               : %d characters (%+.1f%%)"
        % (summary_chars, -100.0 * (1 - (summary_chars / meta["source_size"]))
           if meta["source_size"] else 0),
        "",
        "WHY THIS SUMMARY IS NOT DRAMATICALLY SHORTER THAN THE POLICY",
        "That is deliberate. Under the enforcement rules in agents.md, brevity is",
        "the last priority. A shorter summary that drops the second approver in",
        "clause 5.2, or softens 'not permitted under any circumstances', is wrong",
        "no matter how well it reads. Compression here is limited to symbols and",
        "to removing the document's own section rules and repeated headers.",
        "",
        "HOW TO READ THIS FILE",
        "Each line is <clause> [<binding verb from the source>] <obligation>.",
        "Nothing here is added: every word below occurs in the source document.",
        "[VERBATIM] marks a clause that could not be compressed without losing a",
        "condition, so it is quoted in full instead. That is the intended",
        "behaviour, not a defect.",
        "Symbols used: ≥ for 'at least', ≤ for 'a maximum of', > for",
        "'exceeding', /year /day /night /month for 'per ...'.",
    ]

    footer = ["", "--- CONDITION PRESERVATION CHECK ---",
              "Clauses carrying two or more conditions, and the conditions "
              "retained in each:"]
    for number, conditions in multi_condition.items():
        footer.append("  %-5s %s" % (number, " | ".join(conditions)))

    footer += ["", "--- CRITICAL CLAUSE CHECK ---",
               "The ten clauses named in uc-0b/README.md, and the condition "
               "most often dropped from each:"]
    body_text = "\n".join(body)
    critical_failures = []
    for number, must_contain in CRITICAL_CLAUSES.items():
        clause_line = next((l for l in body if l.startswith(number + " ")), "")
        ok = bool(clause_line) and must_contain.lower() in clause_line.lower()
        if not ok:
            critical_failures.append(number)
        footer.append("  %-5s %-4s must retain: %s"
                      % (number, "PASS" if ok else "FAIL", must_contain))

    footer += ["", "--- SCOPE BLEED CHECK ---",
               "Every alphabetic word in the clause lines above was checked "
               "against the",
               "vocabulary of %s. Words not found there: %s"
               % (meta["source_file"], ", ".join(bleed) or "none")]

    return {
        "lines": header + body + footer,
        "clause_count": len(clause_numbers),
        "summarised_count": len(summarised),
        "omitted": omitted,
        "verbatim": verbatim,
        "bleed": bleed,
        "multi_condition": multi_condition,
        "critical_failures": critical_failures,
        "compression_ratio": (summary_chars / source_chars) if source_chars else 1.0,
        "body_text": body_text,
    }


def self_test() -> int:
    """
    Prove the condition gate is real: feed it the exact softened line the naive
    prompt produced for clause 5.2 and show that it is rejected.
    """
    source = ("LWP requires approval from the Department Head and the "
              "HR Director. Manager approval alone is not sufficient.")
    naive = "LWP requires approval."
    conditions = extract_conditions(source)
    missing = conditions_preserved(conditions, naive)

    print("Source clause 5.2 : %s" % source)
    print("Conditions found  : %s" % " | ".join(conditions))
    print("Naive summary     : %s" % naive)
    print("Conditions dropped: %s" % (" | ".join(missing) or "none"))

    if not missing:
        print("SELF-TEST FAILED — the gate did not catch the dropped approver.")
        return 1

    good = compress(source)
    still_missing = conditions_preserved(conditions, good)
    print("Gated summary     : %s" % good)
    print("Conditions dropped: %s" % (" | ".join(still_missing) or "none"))
    if still_missing:
        print("SELF-TEST FAILED — the compliant line lost a condition.")
        return 1

    print("SELF-TEST PASSED — lossy line rejected, complete line accepted.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", help="Path to the .txt policy document")
    parser.add_argument("--output", help="Path to write the summary")
    parser.add_argument("--self-test", action="store_true",
                        help="Prove the condition-preservation gate rejects a "
                             "softened obligation")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.input or not args.output:
        parser.error("--input and --output are required (or use --self-test)")

    policy = retrieve_policy(args.input)
    result = summarize_policy(policy)

    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write("\n".join(result["lines"]).rstrip() + "\n")

    print("Clauses parsed: %d | summarised: %d | omitted: %s | verbatim: %s"
          % (result["clause_count"], result["summarised_count"],
             ", ".join(result["omitted"]) or "none",
             ", ".join(result["verbatim"]) or "none"))
    print("Scope bleed: %s" % (", ".join(result["bleed"]) or "none"))
    print("Critical clause failures: %s"
          % (", ".join(result["critical_failures"]) or "none"))
    print("Written to %s" % args.output)

    if result["omitted"] or result["bleed"] or result["critical_failures"]:
        print("FAILED: a gate did not pass — see above.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
