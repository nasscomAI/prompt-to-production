"""
UC-0B — Summary That Changes Meaning

CRAFT cycle 1 fix: clause omission.

The baseline dropped 13 of 29 clauses because nothing in the prompt said the
summary had to contain them. Enforcement rule COMPLETENESS now says so, and
this file makes the rule testable: the summariser emits every clause under its
own clause ID, and validate_summary fails the run if the output clause-ID set
is not identical to the source clause-ID set.

    --mode naive      the baseline, kept so the failure stays reproducible
    --mode enforced   the clause register (default)

Usage:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt
"""

import argparse
import os
import re
import sys


# agents.md / COMPLETENESS — the ten clauses the UC-0B ground truth asserts.
CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Binding verbs, longest first so "must not" is matched before "must".
BINDING_VERBS = [
    "must not", "must", "shall not", "shall", "will not", "will",
    "may not", "may", "cannot", "can not", "not permitted", "is not permitted",
    "requires", "required", "are forfeited", "is forfeited", "are entitled",
    "is entitled", "does not apply", "do not count", "will not be considered",
    "are not eligible", "is not valid", "not sufficient",
]


class PolicyError(Exception):
    """Raised when the source document cannot be read or parsed into clauses."""


class SummaryError(Exception):
    """Raised when a produced summary fails validation under strict mode."""


CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(\S.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 \-&/(),']+)$")
SEPARATOR_RE = re.compile(r"^[═─\-=_\s]+$")
# A clause reference only counts when it sits in marker position at the start
# of a line — "[2.3]  ..." or "   - 2.3 ..." — never mid-sentence.
CLAUSE_MARKER_RE = re.compile(r"^[\s\-\*>]*\[?(\d+\.\d+)\]?[\s:\]]", re.M)


def _split_sentences(text):
    """Split on sentence boundaries without breaking decimals like '1.5 days'."""
    if not text:
        return []
    parts = re.split(r"(?<=[.:])\s+(?=[A-Z(])", text.strip())
    return [p.strip() for p in parts if p.strip()]


def retrieve_policy(path):
    """Load one .txt policy and return {'meta': [...], 'sections': [...]}."""
    if not os.path.isfile(path):
        raise PolicyError("Policy file not found: {}".format(path))
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw_lines = handle.read().splitlines()
    except OSError as exc:
        raise PolicyError("Could not read {}: {}".format(path, exc))

    meta = []
    sections = []
    current_section = None
    current_clause = None
    seen_first_section = False

    for line in raw_lines:
        stripped = line.strip()

        if not stripped or SEPARATOR_RE.match(stripped):
            continue

        section_match = SECTION_RE.match(stripped)
        if section_match:
            seen_first_section = True
            current_clause = None
            current_section = {
                "number": section_match.group(1),
                "title": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            continue

        clause_match = CLAUSE_RE.match(stripped)
        if clause_match and current_section is not None:
            current_clause = {"id": clause_match.group(1), "text": clause_match.group(2).strip()}
            current_section["clauses"].append(current_clause)
            continue

        if not seen_first_section:
            meta.append(stripped)
            continue

        # Continuation of the clause above — line-wrap artefact, not new content.
        if current_clause is not None:
            current_clause["text"] = (current_clause["text"] + " " + stripped).strip()

    for section in sections:
        for clause in section["clauses"]:
            clause["text"] = re.sub(r"\s+", " ", clause["text"]).strip()
            clause["sentences"] = _split_sentences(clause["text"])

    if sum(len(s["clauses"]) for s in sections) == 0:
        # An empty parse would sail through every downstream check.
        raise PolicyError("Parsed 0 clauses from {} — refusing to summarise.".format(path))

    return {"meta": meta, "sections": sections}


def all_clauses(structured):
    """Flatten to [(section, clause), ...] in document order."""
    out = []
    for section in structured["sections"]:
        for clause in section["clauses"]:
            out.append((section, clause))
    return out


def binding_verb_of(text):
    lowered = text.lower()
    for verb in BINDING_VERBS:
        if verb in lowered:
            return verb.upper()
    return "STATEMENT"


def _render_clause(clause):
    """Render one clause as a register block under its own clause ID."""
    sentences = clause["sentences"] or [clause["text"]]
    lines = [
        "[{}]  binding verb: {}".format(clause["id"], binding_verb_of(clause["text"])),
        "      obligation : {}".format(sentences[0]),
    ]
    for extra in sentences[1:]:
        lines.append("      condition  : {}".format(extra))
    return "\n".join(lines)


def summarize_policy(structured, strict=True):
    """Produce the clause register plus its validation report."""
    out = ["COMPLIANCE SUMMARY — CLAUSE REGISTER"]
    out.extend(structured["meta"])
    out.append("")
    out.append("Every numbered clause in the source appears below under its own clause ID.")
    out.append("")

    for section in structured["sections"]:
        out.append("=" * 70)
        out.append("SECTION {} — {}".format(section["number"], section["title"]))
        out.append("=" * 70)
        for clause in section["clauses"]:
            out.append(_render_clause(clause))
            out.append("")

    summary_text = "\n".join(out).rstrip() + "\n"
    report = validate_summary(structured, summary_text)
    summary_text = summary_text + "\n" + _render_report(report)

    if strict and not report["ok"]:
        raise SummaryError("Summary failed validation: {}".format(report))

    return summary_text, report


def naive_summarize(structured):
    """
    What an unenforced "Summarize the policy document." prompt produces:
      - keeps only the headline clauses of each section
      - keeps only the first sentence of each clause it keeps
      - closes with a plausible-sounding generalisation that is not in the source
    """
    out = ["SUMMARY OF THE POLICY DOCUMENT", ""]
    for section in structured["sections"]:
        out.append("{}. {}".format(section["number"], section["title"].title()))
        for clause in section["clauses"][:2]:
            first = (clause["sentences"] or [clause["text"]])[0]
            out.append("   - {} {}".format(clause["id"], first))
        out.append("")
    out.append(
        "Overall, employees are generally expected to plan leave in advance and "
        "seek approval from their manager, as is standard practice in government "
        "organisations."
    )
    return "\n".join(out) + "\n"


def validate_summary(structured, candidate_text):
    """Completeness check: does every source clause ID appear in the candidate?"""
    source_ids = [clause["id"] for _, clause in all_clauses(structured)]
    present_ids = set(CLAUSE_MARKER_RE.findall(candidate_text))

    missing_ids = [cid for cid in source_ids if cid not in present_ids]
    extra_ids = sorted(present_ids - set(source_ids))
    critical_missing = [cid for cid in CRITICAL_CLAUSES if cid in missing_ids]

    report = {
        "clauses_source": len(source_ids),
        "clauses_summary": len(source_ids) - len(missing_ids),
        "missing_ids": missing_ids,
        "extra_ids": extra_ids,
        "critical_gate_missing": critical_missing,
    }
    report["ok"] = not missing_ids and not extra_ids and not critical_missing
    return report


def _render_report(report):
    lines = [
        "=" * 70,
        "COMPLIANCE CHECK (generated by validate_summary, not by hand)",
        "=" * 70,
        "Clauses in source          : {}".format(report["clauses_source"]),
        "Clauses in summary         : {}".format(report["clauses_summary"]),
        "Missing clause IDs         : {}".format(report["missing_ids"] or "none"),
        "Unsourced clause IDs       : {}".format(report["extra_ids"] or "none"),
        "Critical 10 gate           : {}".format(
            "PASS" if not report["critical_gate_missing"] else "FAIL"
        ),
        "RESULT                     : {}".format("PASS" if report["ok"] else "FAIL"),
    ]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to the .txt policy document")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    parser.add_argument("--mode", choices=["enforced", "naive"], default="enforced")
    args = parser.parse_args()

    try:
        structured = retrieve_policy(args.input)
    except PolicyError as exc:
        print("REFUSED: {}".format(exc), file=sys.stderr)
        return 2

    if args.mode == "naive":
        text = naive_summarize(structured)
        report = validate_summary(structured, text)
        text = text + "\n" + _render_report(report)
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
        print(_render_report(report))
        print("Naive mode is expected to FAIL. That failure is the point of UC-0B.")
        return 0

    try:
        text, report = summarize_policy(structured, strict=True)
    except SummaryError as exc:
        print("REFUSED: {}".format(exc), file=sys.stderr)
        return 3

    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(text)
    print("Summary written to {}".format(args.output))
    print(_render_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
