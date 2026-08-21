"""
UC-0B — Summary That Changes Meaning

Summarises a numbered policy document without rewriting any binding sentence.

The design decision this file is built around: compression by *selection*, not
by *paraphrase*. Structure, ordering and labelling are the summariser's to
change. The wording of an obligation is not. A clause that carries a mandatory
verb, a prohibition, a conditional qualifier or a number is reproduced
character for character and flagged with the marker that made it unsafe to
touch.

Two modes:
    --mode naive      the Control step. An unconstrained "summarise this"
                      baseline — section headings plus the opening sentence of
                      each section, capped at a readable length. It runs no
                      audit. Its clause loss is measured and printed.
    --mode enforced   the default. Full clause coverage, verbatim binding text,
                      obligation and multi-condition indexes, and a
                      self-audit that must pass before anything is written.

Run:
    python app.py \
      --input ../data/policy-documents/policy_hr_leave.txt \
      --output summary_hr_leave.txt
"""
import argparse
import re
import sys

# --- Enforcement rule 2: what makes a clause unsafe to compress ---------------
# Each entry is (label, pattern). The label lands in the output next to the
# clause so a reviewer can audit why it was left verbatim rather than trust it.
MANDATORY_MARKERS = [
    ("MANDATORY(must)", r"\bmust\b"),
    ("MANDATORY(requires)", r"\brequire[sd]?\b"),
    ("MANDATORY(shall)", r"\bshall\b"),
]

PROHIBITION_MARKERS = [
    ("PROHIBITION(cannot)", r"\bcannot\b"),
    ("PROHIBITION(not permitted)", r"\bnot permitted\b"),
    ("PROHIBITION(not valid)", r"\bnot valid\b"),
    ("PROHIBITION(not eligible)", r"\bnot eligible\b"),
    ("PROHIBITION(not reimbursable)", r"\bnot reimbursable\b"),
    ("PROHIBITION(does not apply)", r"\bdoes not apply\b"),
    ("PROHIBITION(do not count)", r"\bdo not count\b"),
    ("PROHIBITION(will not)", r"\bwill not\b"),
    ("PROHIBITION(forfeited)", r"\bforfeit\w*"),
    ("PROHIBITION(not sufficient)", r"\bnot sufficient\b"),
    ("PROHIBITION(not be)", r"\bnot be\b"),
]

CONDITIONAL_MARKERS = [
    ("CONDITIONAL(only)", r"\bonly\b"),
    ("CONDITIONAL(unless)", r"\bunless\b"),
    ("CONDITIONAL(regardless)", r"\bregardless\b"),
    ("CONDITIONAL(before)", r"\bbefore\b"),
    ("CONDITIONAL(after)", r"\bafter\b"),
    ("CONDITIONAL(within)", r"\bwithin\b"),
    ("CONDITIONAL(subject to)", r"\bsubject to\b"),
    ("CONDITIONAL(if)", r"\bif\b"),
]

ENTITLEMENT_MARKERS = [
    ("ENTITLEMENT(entitled)", r"\bentitled\b"),
    ("ENTITLEMENT(accrues)", r"\baccrue\w*"),
    ("ENTITLEMENT(may)", r"\bmay\b"),
]

NUMERIC_MARKER = ("NUMERIC", r"\d")

# --- Enforcement rule 3: scope bleed is banned outright -----------------------
# Asserted absent from the finished text before it is allowed to reach disk.
BANNED_PHRASES = [
    "as is standard practice",
    "typically in government",
    "typically",
    "generally expected",
    "generally understood",
    "it is understood that",
    "it is common practice",
    "as a rule of thumb",
    "best practice",
    "in most organisations",
    "in most organizations",
    "usually",
]

# Conjunctions that join two separate requirements. Clause 5.2 is the reason
# this list exists: "the Department Head and the HR Director" is two approvers,
# and a summary that keeps only "requires approval" has silently dropped one.
CONJUNCTION_PATTERNS = [
    r"\band\b",
    r"\bboth\b",
    r"\bas well as\b",
]

# The 10 clauses the UC README names as the compliance-critical set for this
# document. Reported explicitly so their presence is proven, not assumed.
CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

BANNER = re.compile(r"^[═=─-]{5,}\s*$")
SECTION_RE = re.compile(r"^(\d+)\.\s+(\S.*)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(\S.*)$")


def _normalise(text: str) -> str:
    """Collapse line-wrap whitespace. Nothing else about the text changes."""
    return re.sub(r"\s+", " ", text).strip()


def retrieve_policy(path: str) -> dict:
    """
    Load a .txt policy file and return it as structured numbered sections.

    Returns {header: [str], sections: [{number, title, clauses: [{ref, text}]}]}
    """
    try:
        with open(path, encoding="utf-8") as handle:
            raw = handle.read()
    except OSError as exc:
        raise SystemExit("Cannot read policy file %s: %s" % (path, exc))

    lines = raw.splitlines()

    header = []
    sections = []
    current_section = None
    current_clause = None
    seen_first_section = False

    def close_clause():
        if current_clause is not None:
            current_clause["text"] = _normalise(current_clause["text"])

    for line in lines:
        if BANNER.match(line):
            continue

        section_match = SECTION_RE.match(line.strip())
        clause_match = CLAUSE_RE.match(line.strip())

        if clause_match:
            close_clause()
            if current_section is None:
                # A clause before any header: keep it rather than lose it.
                current_section = {"number": "0", "title": "(UNSECTIONED)", "clauses": []}
                sections.append(current_section)
            current_clause = {"ref": clause_match.group(1), "text": clause_match.group(2)}
            current_section["clauses"].append(current_clause)
            continue

        if section_match:
            close_clause()
            current_clause = None
            seen_first_section = True
            current_section = {
                "number": section_match.group(1),
                "title": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            continue

        if not line.strip():
            continue

        if current_clause is not None:
            current_clause["text"] += " " + line.strip()
        elif not seen_first_section:
            header.append(line.strip())

    close_clause()

    clause_count = sum(len(s["clauses"]) for s in sections)
    if clause_count == 0:
        # Refusal: completeness cannot be verified on an unstructured document,
        # so the system declines rather than producing unverifiable prose.
        raise SystemExit(
            "Refusing to summarise %s: no numbered clauses found. This system "
            "only summarises documents whose clause coverage it can verify." % path
        )

    # The raw text travels with the parsed structure so the audit can check the
    # summary against the *source*, not against the parser's opinion of it.
    return {"header": header, "sections": sections, "raw": raw}


def source_clause_refs(raw: str):
    """
    Every clause reference in the source, read straight off the file.

    Deliberately independent of the parser. The completeness audit was
    originally written against the parsed clause list and was circular: drop a
    clause in retrieve_policy and the audit compared the summary to a structure
    that no longer contained it, so it passed. A clause-omission check that
    cannot detect clause omission is decoration.
    """
    return sorted(set(re.findall(r"^\s*(\d+\.\d+)\s", raw, flags=re.MULTILINE)))


def _all_clauses(policy: dict):
    return [c for section in policy["sections"] for c in section["clauses"]]


def _markers_for(text: str):
    """Return the labels explaining why this clause is compression-unsafe."""
    found = []
    for group in (MANDATORY_MARKERS, PROHIBITION_MARKERS, CONDITIONAL_MARKERS):
        for label, pattern in group:
            if re.search(pattern, text, flags=re.IGNORECASE):
                found.append(label)
    label, pattern = NUMERIC_MARKER
    if re.search(pattern, text):
        found.append(label)
    return found


def _entitlements_for(text: str):
    return [
        label
        for label, pattern in ENTITLEMENT_MARKERS
        if re.search(pattern, text, flags=re.IGNORECASE)
    ]


def _is_binding(sentence: str) -> bool:
    """Does this sentence carry a mandatory verb or a prohibition?"""
    return any(
        re.search(pattern, sentence, flags=re.IGNORECASE)
        for _label, pattern in MANDATORY_MARKERS + PROHIBITION_MARKERS
    )


def _condition_profile(text: str) -> dict:
    """
    Break a clause into the separate things that must hold, and say why.

    Counting bare conjunctions was the first attempt and it was wrong in both
    directions: it flagged 1.1 ("permanent and contractual employees" — one
    scope statement, not two requirements) and it missed 2.4, whose two
    obligations sit in two sentences with no conjunction between them.

    A "part" is therefore counted only where it can carry an obligation:
      - each sentence that carries a mandatory verb or prohibition
      - each conjunction that appears *inside* such a sentence — this is the
        clause 5.2 case, "the Department Head and the HR Director"
      - each conditional qualifier inside such a sentence (before, within, only)
      - each distinct numeric threshold in the clause
    """
    sentences = [s.strip() for s in re.split(r"(?<=\.)\s+", text) if s.strip()]
    binding = [s for s in sentences if _is_binding(s)]

    conjunctions = 0
    conjunctive_fragment = ""
    for sentence in binding:
        hits = sum(len(re.findall(p, sentence, flags=re.IGNORECASE)) for p in CONJUNCTION_PATTERNS)
        if hits and not conjunctive_fragment:
            conjunctive_fragment = sentence
        conjunctions += hits

    qualifiers = 0
    for sentence in binding:
        for _label, pattern in CONDITIONAL_MARKERS:
            if re.search(pattern, sentence, flags=re.IGNORECASE):
                qualifiers += 1

    numbers = len(set(re.findall(r"\d+(?:\.\d+)?", text)))

    reasons = []
    if len(binding) > 1:
        reasons.append("MULTI-SENTENCE")
    if conjunctions:
        reasons.append("CONJUNCTIVE")
    if qualifiers:
        reasons.append("QUALIFIED")
    if numbers > 1:
        reasons.append("NUMERIC-THRESHOLDS")

    return {
        "parts": len(binding) + conjunctions + qualifiers + numbers,
        "reasons": reasons,
        # Extracted verbatim, never composed — the index must not paraphrase
        # the very text it exists to protect.
        "fragment": conjunctive_fragment or (binding[0] if binding else text),
    }


def _content_words(text: str):
    """Lowercased words of 4+ characters — used to measure content retention."""
    return {w for w in re.findall(r"[a-z]{4,}", text.lower())}


def _condense(text: str) -> str:
    """
    Mechanical head-trim for a clause with no binding content. This is the only
    transformation applied to any clause text anywhere in this program, and it
    removes a leading determiner phrase — it does not reword.
    """
    trimmed = re.sub(r"^This (policy|section|document)\s+", "", text)
    return trimmed[0].upper() + trimmed[1:] if trimmed and trimmed != text else text


def naive_summary(policy: dict) -> str:
    """
    The Control step — an unconstrained summariser.

    This is what "Summarize the policy document." produces: section headings and
    the opening sentence of each, trimmed to a comfortable reading length. It
    reads well. It is also missing most of the document's obligations, and
    nothing in it can tell you that. No audit runs here by design.
    """
    parts = ["SUMMARY OF THE EMPLOYEE LEAVE POLICY", ""]
    for section in policy["sections"]:
        if not section["clauses"]:
            continue
        opening = re.split(r"(?<=\.)\s+", section["clauses"][0]["text"])[0]
        parts.append("%s. %s" % (section["number"], section["title"].title()))
        parts.append("    %s" % opening)
        parts.append("")
    return "\n".join(parts)


def summarize_policy(policy: dict, mode: str = "enforced"):
    """
    Produce the summary. In enforced mode, audit it before handing it back.

    Returns (summary_text, audit_dict).
    """
    clauses = _all_clauses(policy)

    if mode == "naive":
        text = naive_summary(policy)
        # Retention is measured by content, not by clause reference. Scoring a
        # prose summary on whether it prints the string "2.3" would be rigging
        # the control — it never cites references, and that is not the failure
        # being demonstrated. A clause counts as retained if 60% of its content
        # words survive somewhere in the summary.
        summary_words = _content_words(text)
        present = []
        for clause in clauses:
            words = _content_words(clause["text"])
            if words and len(words & summary_words) / len(words) >= 0.6:
                present.append(clause["ref"])
        return text, {
            "mode": "naive",
            "clauses_total": len(clauses),
            "clauses_present": len(present),
            "missing": [c["ref"] for c in clauses if c["ref"] not in present],
            "critical_missing": [r for r in CRITICAL_CLAUSES if r not in present],
        }

    verbatim_count = 0
    condensed_count = 0
    obligations = []
    multi_condition = []
    lines = []

    for line in policy["header"]:
        lines.append(line)
    lines.append("")
    lines.append("COMPLIANCE SUMMARY — generated by uc-0b/app.py")
    lines.append("Binding clauses are reproduced verbatim from the source. No obligation")
    lines.append("in this document has been reworded, softened, or merged.")
    lines.append("")

    body = []
    for section in policy["sections"]:
        body.append("")
        body.append("%s. %s" % (section["number"], section["title"]))
        body.append("-" * 59)
        for clause in section["clauses"]:
            text = clause["text"]
            markers = _markers_for(text)
            profile = _condition_profile(text)

            if markers:
                verbatim_count += 1
                body.append("  %s  [VERBATIM · %s]" % (clause["ref"], " ".join(markers)))
                body.append('      "%s"' % text)
                if any(m.startswith(("MANDATORY", "PROHIBITION")) for m in markers):
                    obligations.append((clause["ref"], markers[0]))
            else:
                condensed_count += 1
                body.append("  %s  [CONDENSED]" % clause["ref"])
                body.append("      %s" % _condense(text))

            entitlements = _entitlements_for(text)
            if entitlements:
                body.append("      · %s" % " ".join(entitlements))
            if profile["parts"] > 1 and profile["reasons"]:
                body.append(
                    "      · %d PARTS (%s) — all preserved verbatim above"
                    % (profile["parts"], ", ".join(profile["reasons"]))
                )
                multi_condition.append((clause["ref"], profile))

    # Indexes are built from the clause pass above, then placed before the body
    # so the reader meets the obligations first.
    lines.append("COVERAGE")
    lines.append("  Sections: %d" % len(policy["sections"]))
    lines.append("  Clauses in source: %d" % len(clauses))
    lines.append("  Reproduced verbatim: %d" % verbatim_count)
    lines.append("  Condensed: %d" % condensed_count)
    lines.append("  Omitted: 0 — every numbered clause appears below")
    lines.append("")

    lines.append("CRITICAL CLAUSE CHECK")
    refs = {c["ref"] for c in clauses}
    for ref in CRITICAL_CLAUSES:
        lines.append("  %-5s %s" % (ref, "present" if ref in refs else "MISSING"))
    lines.append("")

    lines.append("HARD OBLIGATIONS — clauses carrying a mandatory verb or prohibition")
    for ref, marker in obligations:
        lines.append("  %-5s %s" % (ref, marker))
    lines.append("")

    lines.append("MULTI-PART OBLIGATIONS — every part preserved, none dropped")
    lines.append("  The fragment shown is the source sentence, unaltered.")
    for ref, profile in multi_condition:
        lines.append("  %-5s %d parts (%s)" % (ref, profile["parts"], ", ".join(profile["reasons"])))
        lines.append('        "%s"' % profile["fragment"])
    lines.append("")

    text = "\n".join(lines + body) + "\n"

    audit = _audit(text, policy, clauses, verbatim_count, condensed_count, multi_condition)
    return text, audit


def _audit(text: str, policy: dict, clauses, verbatim_count: int, condensed_count: int, multi_condition):
    """
    Enforcement made executable. Raises rather than returning a bad summary.
    """
    # Completeness is measured against the source file, never against the
    # parsed structure — otherwise a clause lost during parsing is invisible to
    # the very check meant to catch it.
    source_refs = source_clause_refs(policy.get("raw", ""))
    parsed_refs = {c["ref"] for c in clauses}

    dropped_by_parser = [r for r in source_refs if r not in parsed_refs]
    if dropped_by_parser:
        raise AssertionError(
            "Parser lost clauses present in the source: %s" % ", ".join(dropped_by_parser)
        )

    missing = [r for r in source_refs if not re.search(r"\b%s\b" % re.escape(r), text)]
    if missing:
        raise AssertionError("Clause omission — absent from summary: %s" % ", ".join(missing))

    for clause in clauses:
        if _markers_for(clause["text"]) and clause["text"] not in text:
            raise AssertionError(
                "Verbatim fidelity failed for clause %s — binding text was altered." % clause["ref"]
            )

    lowered = text.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            raise AssertionError("Scope bleed — banned phrase %r present in summary." % phrase)

    critical_missing = [
        r for r in CRITICAL_CLAUSES if not re.search(r"\b%s\b" % re.escape(r), text)
    ]
    if critical_missing:
        raise AssertionError("Critical clauses missing: %s" % ", ".join(critical_missing))

    return {
        "mode": "enforced",
        "clauses_total": len(clauses),
        "clauses_present": len(clauses),
        "missing": [],
        "verbatim_count": verbatim_count,
        "condensed_count": condensed_count,
        "multi_condition": [(ref, profile["parts"]) for ref, profile in multi_condition],
        "critical_missing": [],
    }


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    parser.add_argument(
        "--mode",
        choices=["enforced", "naive"],
        default="enforced",
        help="enforced (default) applies agents.md rules; naive is the Control baseline",
    )
    args = parser.parse_args()

    policy = retrieve_policy(args.input)

    try:
        summary, audit = summarize_policy(policy, mode=args.mode)
    except AssertionError as exc:
        # Refusal: a summary that failed its own audit must not reach disk.
        sys.exit("Refusing to write %s — %s" % (args.output, exc))

    with open(args.output, "w", encoding="utf-8") as out:
        out.write(summary)

    print("Done. Summary written to %s" % args.output)
    print("  mode              : %s" % audit["mode"])
    print("  clauses in source : %d" % audit["clauses_total"])
    print("  clauses in summary: %d" % audit["clauses_present"])
    if audit["missing"]:
        print("  CLAUSES DROPPED   : %s" % ", ".join(audit["missing"]))
    if audit["critical_missing"]:
        print("  CRITICAL DROPPED  : %s" % ", ".join(audit["critical_missing"]))
    if audit["mode"] == "enforced":
        print("  verbatim          : %d" % audit["verbatim_count"])
        print("  condensed         : %d" % audit["condensed_count"])
        print(
            "  multi-condition   : %s"
            % ", ".join("%s(%d)" % (r, c) for r, c in audit["multi_condition"])
        )


if __name__ == "__main__":
    main()
