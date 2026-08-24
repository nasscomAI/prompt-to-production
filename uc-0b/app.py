"""
UC-0B — Summary That Changes Meaning

The failure this file is built against is not "the summary was too long". It is that a
summary can read perfectly while having quietly dropped one of two required approvers.

So the compressor here is deletion-only: it can remove filler, but it has no mechanism
for substituting a word. A softening ("must" -> "should") requires substitution, and an
invented norm ("as is standard practice") requires insertion. Neither operation exists
in this program, which is why those two failure modes cannot occur — and the run
verifies that claim token-by-token before it writes anything to disk.

Run:
    python3 app.py --input ../data/policy-documents/policy_hr_leave.txt \
                   --output summary_hr_leave.txt
"""
import argparse
import re
import sys

# The 10 clauses the UC-0B README names as ground truth. Presence is asserted, and each
# is forced verbatim regardless of how compressible it looks.
GROUND_TRUTH_CLAUSES = {
    "2.3": "14-day advance notice required",
    "2.4": "written approval required before leave commences; verbal not valid",
    "2.5": "unapproved absence = LOP regardless of subsequent approval",
    "2.6": "max 5 days carry-forward; above 5 forfeited on 31 Dec",
    "2.7": "carry-forward days must be used Jan-Mar or forfeited",
    "3.2": "3+ consecutive sick days requires medical certificate within 48hrs",
    "3.4": "sick leave before/after holiday requires certificate regardless of duration",
    "5.2": "LWP requires Department Head AND HR Director approval",
    "5.3": "LWP >30 days requires Municipal Commissioner approval",
    "7.2": "leave encashment during service not permitted under any circumstances",
}

# Enforcement: binding verbs must survive at original strength. Any of these present in
# a source clause must still be present in that clause's summary entry.
BINDING_VERBS = [
    r"must not", r"must", r"will be recorded", r"will", r"requires", r"required",
    r"is not permitted", r"not permitted", r"cannot", r"are forfeited",
    r"is forfeited", r"forfeited", r"shall", r"is entitled", r"are entitled",
    r"may not", r"may", r"is mandatory", r"not valid", r"not sufficient",
    r"do not count", r"will not be considered",
]

# Enforcement: scope-bleed phrases. If any appears in the output, the run fails.
BANNED_PHRASES = [
    "as is standard practice", "standard practice", "typically",
    "in government organisations", "generally expected", "generally understood",
    "usually", "normally", "in most cases", "it is common practice",
    "as a rule", "best practice", "industry norm", "commonly",
    "should ideally", "is advisable", "it is recommended",
]

# Tokens that mark a clause meaning-critical — never compressed.
CRITICAL_MARKERS = [
    r"\d",                                        # any number, deadline or amount
    r"\bRs\b", r"₹",
    r"\bwithin\b", r"\bbefore\b", r"\bafter\b", r"\bby\b",
    r"\bDepartment Head\b", r"\bHR Director\b", r"\bMunicipal Commissioner\b",
    r"\bmanager\b", r"\bIT Department\b",
    r"\bnot permitted\b", r"\bcannot\b", r"\bmust not\b", r"\bnot valid\b",
    r"\bnot sufficient\b", r"\bforfeit\w*\b", r"\bonly\b",
]

# Roles, so a multi-approver condition can be enumerated rather than summarised away.
ROLE_PATTERNS = [
    r"\bDepartment Head\b", r"\bHR Director\b", r"\bMunicipal Commissioner\b",
    r"\bHR Department\b", r"\bIT Department\b", r"\bdirect manager\b",
    r"\bmanager\b", r"\bregistered medical practitioner\b", r"\bState Government\b",
]

# Deletion-only filler. Nothing here carries an obligation, a number or a condition.
DELETABLE_FILLER = [
    r"\bfor the purposes of\b", r"\bas the case may be\b",
    r"\bit is noted that\b", r"\bplease note that\b",
]

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z \-—&/()]+)$")
BANNER_RE = re.compile(r"^[═=]{5,}$")


def retrieve_policy(path: str) -> dict:
    """
    Load a .txt policy file and return it as addressable numbered clauses.

    Continuation lines are joined into their owning clause and whitespace-normalised.
    No word is added and none is removed.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except FileNotFoundError:
        sys.exit(f"ERROR: policy file not found: {path}")

    title, sections, clauses = [], [], []
    current_section = None
    current_clause = None
    seen_first_structure = False

    def close_clause():
        nonlocal current_clause
        if current_clause is not None:
            current_clause["text"] = re.sub(r"\s+", " ", current_clause["text"]).strip()
            clauses.append(current_clause)
            if current_section is not None:
                current_section["clauses"].append(current_clause)
            current_clause = None

    for raw in lines:
        line = raw.rstrip()
        if not line or BANNER_RE.match(line.strip()):
            continue

        section_match = SECTION_RE.match(line.strip())
        clause_match = CLAUSE_RE.match(line.strip())

        if clause_match:
            close_clause()
            seen_first_structure = True
            if current_section is None:
                # A clause before any heading is kept, not discarded.
                current_section = {"number": "0", "heading": "PREAMBLE", "clauses": []}
                sections.append(current_section)
            current_clause = {
                "ref": clause_match.group(1),
                "text": clause_match.group(2),
                "section": current_section["heading"],
            }
        elif section_match:
            close_clause()
            seen_first_structure = True
            current_section = {
                "number": section_match.group(1),
                "heading": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
        elif current_clause is not None:
            current_clause["text"] += " " + line.strip()
        elif not seen_first_structure:
            title.append(line.strip())

    close_clause()

    if not clauses:
        sys.exit(f"ERROR: no numbered clauses (N.M) found in {path} — refusing to "
                 f"write an empty summary")

    return {
        "title": title,
        "sections": sections,
        "clauses": clauses,
        "clause_count": len(clauses),
    }


def _found(patterns, text):
    """Literal matched strings for every pattern present in text."""
    hits = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            if match.group(0) not in hits:
                hits.append(match.group(0))
    return hits


def _is_critical(clause: dict) -> bool:
    if clause["ref"] in GROUND_TRUTH_CLAUSES:
        return True
    return bool(_found(CRITICAL_MARKERS, clause["text"]))


# A role named in one of these sentences is explicitly NOT a sufficient approver.
# Listing it as a required approver would invert the obligation, which is the exact
# failure mode this UC exists to catch.
INSUFFICIENCY_MARKERS = [
    r"\bnot sufficient\b", r"\balone is not\b", r"\bnot valid\b",
    r"\bis not enough\b", r"\bnot by itself\b",
]


def _sentences(text: str):
    return [s.strip() for s in re.split(r"(?<=[.;])\s+", text) if s.strip()]


def _conditions(text: str):
    """
    Enumerate the conditions attached to an obligation, extracted verbatim.

    This exists for clause 5.2: 'Department Head and the HR Director' must survive as
    TWO required approvers, not as the single phrase 'requires approval' — and
    'Manager approval alone is not sufficient' must survive as an EXCLUSION, never as
    a third required approver.
    """
    conditions = []

    # Roles, scoped per sentence so negation is not lost.
    for sentence in _sentences(text):
        negated = bool(_found(INSUFFICIENCY_MARKERS, sentence))
        roles = _found(ROLE_PATTERNS, sentence)
        # 'manager' is redundant when the more specific 'direct manager' already matched.
        if any(r.lower() == "direct manager" for r in roles):
            roles = [r for r in roles if r.lower() != "manager"]
        for role in roles:
            if negated:
                conditions.append(f"NOT sufficient alone: {role}")
            else:
                conditions.append(f"required approver: {role}")

    # Qualifiers, cut at a sentence or clause boundary and never mid-word.
    for match in re.finditer(
        r"\b(?:within|exceeding|at least|up to|maximum of|more than|not exceed)\b"
        r"[^,.;]*", text, re.IGNORECASE
    ):
        # No length cap: the character class already stops at the clause boundary, and
        # a cap here would clip "...to the following calendar year" off clause 2.6 —
        # a truncated condition is a dropped condition.
        phrase = " ".join(match.group(0).split()).strip()
        if phrase:
            conditions.append(f"qualifier: {phrase}")

    for match in re.finditer(r"\b\d[\d,.]*\s*(?:calendar days|working days|days?|"
                             r"weeks?|hours?|months?)\b", text, re.IGNORECASE):
        conditions.append(f"quantity: {match.group(0).strip()}")

    for match in re.finditer(r"\b(?:not permitted|not valid|not sufficient|cannot|"
                             r"must not|will not be considered|are forfeited|"
                             r"is forfeited|not reimbursable)\b", text, re.IGNORECASE):
        conditions.append(f"prohibition: {match.group(0).strip()}")

    # De-duplicate, preserving order.
    seen, unique = set(), []
    for condition in conditions:
        key = condition.lower()
        if key not in seen:
            seen.add(key)
            unique.append(condition)
    return unique


def _compress(text: str) -> str:
    """
    Deletion-only compression. Removes whitelisted filler and nothing else.

    There is deliberately no substitution path in this function: substitution is how
    'must' becomes 'should'. If a clause is meaning-critical, this is never called.
    """
    out = text
    for pattern in DELETABLE_FILLER:
        out = re.sub(pattern, "", out, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", out).strip()


def _tokens(text: str):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def summarize_policy(policy: dict) -> tuple:
    """
    Build the summary. Returns (summary_text, report_dict).

    Raises before returning if coverage, binding-verb preservation, scope-bleed or
    token-containment checks fail — a defective summary never reaches disk.
    """
    lines = []
    lines.append("SUMMARY — CLAUSE-PRESERVING")
    for header in policy["title"]:
        lines.append(header)
    lines.append("")
    lines.append("Method: every numbered clause below is represented and cited by its")
    lines.append("own number. Meaning-critical clauses are quoted verbatim and marked")
    lines.append("[VERBATIM]. Multi-condition obligations are marked [MULTI-CONDITION]")
    lines.append("with each condition listed separately, so a dropped approver is")
    lines.append("visible rather than invisible. No clause is paraphrased, because")
    lines.append("paraphrase is what changes meaning.")
    lines.append("")

    verbatim_count = 0
    multi_count = 0
    entries = {}

    for section in policy["sections"]:
        if not section["clauses"]:
            continue
        lines.append("=" * 66)
        lines.append(f"SECTION {section['number']} — {section['heading']}")
        lines.append("=" * 66)
        for clause in section["clauses"]:
            critical = _is_critical(clause)
            conditions = _conditions(clause["text"])
            multi = len(conditions) >= 2
            tags = []
            if critical:
                tags.append("[VERBATIM]")
                verbatim_count += 1
            if multi:
                tags.append("[MULTI-CONDITION]")
                multi_count += 1
            if clause["ref"] in GROUND_TRUTH_CLAUSES:
                tags.append("[CRITICAL]")

            body = clause["text"] if critical else _compress(clause["text"])
            tag_str = (" " + " ".join(tags)) if tags else ""
            lines.append(f"{clause['ref']}{tag_str}")
            lines.append(f'    "{body}"')
            if multi:
                lines.append("    conditions preserved (every one below is stated in "
                             "the clause):")
                for condition in conditions:
                    lines.append(f"      - {condition}")
            lines.append("")
            entries[clause["ref"]] = body

    # ---- Verification. These run before the caller is allowed to write the file. ----
    missing = [c["ref"] for c in policy["clauses"] if c["ref"] not in entries]
    if missing:
        raise AssertionError(f"coverage failure — clauses unrepresented: {missing}")

    missing_ground_truth = [ref for ref in GROUND_TRUTH_CLAUSES if ref not in entries]
    if missing_ground_truth:
        raise AssertionError(
            f"ground-truth clause missing from summary: {missing_ground_truth}")

    softened = []
    for clause in policy["clauses"]:
        source_verbs = _found(BINDING_VERBS, clause["text"])
        summary_text = entries[clause["ref"]]
        for verb in source_verbs:
            if not re.search(re.escape(verb), summary_text, re.IGNORECASE):
                softened.append(f"{clause['ref']}: lost binding verb '{verb}'")
    if softened:
        raise AssertionError("binding-verb softening detected: " + "; ".join(softened))

    added = []
    for clause in policy["clauses"]:
        extra = _tokens(entries[clause["ref"]]) - _tokens(clause["text"])
        if extra:
            added.append(f"{clause['ref']}: {sorted(extra)}")
    if added:
        raise AssertionError("scope bleed — tokens not in source clause: "
                             + "; ".join(added))

    summary = "\n".join(lines)
    bleed = [phrase for phrase in BANNED_PHRASES
             if re.search(r"\b" + re.escape(phrase) + r"\b", summary, re.IGNORECASE)]
    if bleed:
        raise AssertionError(f"scope-bleed phrase present in output: {bleed}")

    report = {
        "clauses_in_source": policy["clause_count"],
        "clauses_represented": len(entries),
        "verbatim": verbatim_count,
        "multi_condition": multi_count,
        "ground_truth_present": len(GROUND_TRUTH_CLAUSES) - len(missing_ground_truth),
        "ground_truth_total": len(GROUND_TRUTH_CLAUSES),
        "banned_phrases_found": bleed,
        "softened_verbs": softened,
    }

    verification = [
        "=" * 66,
        "COVERAGE AND VERIFICATION",
        "=" * 66,
        f"Clauses in source document      : {report['clauses_in_source']}",
        f"Clauses represented in summary   : {report['clauses_represented']}",
        f"Coverage                         : "
        f"{report['clauses_represented']}/{report['clauses_in_source']} "
        f"({100 * report['clauses_represented'] // report['clauses_in_source']}%)",
        f"Quoted verbatim (meaning-critical): {report['verbatim']}",
        f"Multi-condition clauses enumerated: {report['multi_condition']}",
        f"README ground-truth clauses present: "
        f"{report['ground_truth_present']}/{report['ground_truth_total']}",
        "",
        "Checks run before this file was written:",
        "  [PASS] every numbered clause in the source is present, cited by number",
        "  [PASS] no binding verb was softened (must/will/requires/not permitted)",
        "  [PASS] no token appears in any entry that is absent from its source clause",
        "  [PASS] no scope-bleed phrase present in this output",
        "",
        "Ground-truth clause check:",
    ]
    for ref, obligation in GROUND_TRUTH_CLAUSES.items():
        state = "present" if ref in entries else "MISSING"
        verification.append(f"  {ref:<5} {state:<8} — {obligation}")

    return summary + "\n" + "\n".join(verification) + "\n", report


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B clause-preserving policy summariser")
    parser.add_argument("--input", required=True, help="path to policy .txt")
    parser.add_argument("--output", required=True, help="path to summary .txt")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    try:
        summary, report = summarize_policy(policy)
    except AssertionError as exc:
        sys.exit(f"REFUSED to write summary — {exc}")

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary)

    print(f"Wrote {args.output}")
    print(f"  clauses in source / represented : "
          f"{report['clauses_in_source']} / {report['clauses_represented']}")
    print(f"  quoted verbatim                 : {report['verbatim']}")
    print(f"  multi-condition enumerated      : {report['multi_condition']}")
    print(f"  README ground-truth clauses     : "
          f"{report['ground_truth_present']}/{report['ground_truth_total']}")
    print("  scope-bleed phrases             : "
          f"{report['banned_phrases_found'] or 'none'}")
    print("  softened binding verbs          : "
          f"{report['softened_verbs'] or 'none'}")


if __name__ == "__main__":
    main()
