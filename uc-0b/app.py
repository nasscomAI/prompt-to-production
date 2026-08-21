"""
UC-0B — Summary That Changes Meaning

Summarises a single CMC policy document into a clause register that provably
preserves every numbered clause and every condition inside it, and that cannot
contain language the source document does not contain.

CRAFT cycle 3 fix: scope bleed.

Two paths are implemented so the CRAFT loop is reproducible from the CLI:

    --mode naive      what "Summarize the policy document." gets you: a generic
                      extractive summary. Keeps the headline clause of each
                      section, drops the rest, and closes with a generalisation
                      that is nowhere in the source. Fails validation.

    --mode enforced   the agents.md rules applied: every clause, every condition,
                      binding verb named, banned language blocked, verbatim
                      fallback when a clause cannot be condensed losslessly.

Both paths are scored by the same validator, so the difference is measured,
not asserted.

Usage:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_naive.txt --mode naive
"""

import argparse
import os
import re
import sys


# --------------------------------------------------------------------------
# Enforcement constants — these come straight from agents.md. Changing a rule
# means changing it here, which is what makes the rules testable rather than
# decorative.
# --------------------------------------------------------------------------

# agents.md / COMPLETENESS — the ten clauses the UC-0B ground truth asserts.
CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# agents.md / NO ADDED INFORMATION — scope-bleed and hedging language.
BANNED_PHRASES = [
    "as is standard practice",
    "standard practice",
    "typically",
    "generally",
    "usually",
    "commonly",
    "it is common practice",
    "in most organisations",
    "in most organizations",
    "in government organisations",
    "in government organizations",
    "employees are generally expected",
    "best practice",
    "industry norm",
    "while not explicitly",
    "it is understood that",
]

# agents.md / TOKEN SURVIVAL — binding verbs, longest first so "must not"
# is matched before "must".
BINDING_VERBS = [
    "must not", "must", "shall not", "shall", "will not", "will",
    "may not", "may", "cannot", "can not", "not permitted", "is not permitted",
    "requires", "required", "are forfeited", "is forfeited", "are entitled",
    "is entitled", "does not apply", "do not count", "will not be considered",
    "are not eligible", "is not valid", "not sufficient",
]

# agents.md / CONDITION PRESERVATION — named approvers and bodies.
NAMED_ROLES = [
    "Department Head", "HR Director", "Municipal Commissioner", "direct manager",
    "HR Department", "IT Department", "Finance Department",
    "Communications Department", "State Government", "IT Security",
    "registered medical practitioner",
]

# agents.md / TOKEN SURVIVAL — absolute qualifiers that carry obligation weight.
QUALIFIERS = [
    "only", "regardless", "unless", "not valid", "not sufficient",
    "under any circumstances", "before", "after", "within", "at least",
    "maximum", "minimum", "provided", "subject to",
]


class PolicyError(Exception):
    """Raised when the source document cannot be read or parsed into clauses."""


class SummaryError(Exception):
    """Raised when a produced summary fails validation under strict mode."""


# --------------------------------------------------------------------------
# skills.md :: retrieve_policy
# --------------------------------------------------------------------------

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

    total = sum(len(s["clauses"]) for s in sections)
    if total == 0:
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


# --------------------------------------------------------------------------
# Critical-token extraction — the machinery behind TOKEN SURVIVAL
# --------------------------------------------------------------------------

def critical_tokens(text):
    """Every token whose loss would change what the clause obliges."""
    tokens = set()

    for number in re.findall(r"\d[\d,]*(?:\.\d+)?", text):
        tokens.add(number)

    for form in re.findall(r"Form\s+[A-Z0-9\-]+", text):
        tokens.add(form)

    lowered = text.lower()
    for role in NAMED_ROLES:
        if role.lower() in lowered:
            tokens.add(role)
    for verb in BINDING_VERBS:
        if verb in lowered:
            tokens.add(verb)
    for qualifier in QUALIFIERS:
        if qualifier in lowered:
            tokens.add(qualifier)

    for acronym in re.findall(r"\b[A-Z]{2,}\b", text):
        tokens.add(acronym)

    return tokens


def binding_verb_of(text):
    lowered = text.lower()
    for verb in BINDING_VERBS:
        if verb in lowered:
            return verb.upper()
    return "STATEMENT"


def approvers_in(text):
    lowered = text.lower()
    return [role for role in NAMED_ROLES if role.lower() in lowered]


def tokens_present(tokens, block):
    """Which critical tokens failed to survive into the rendered block."""
    lowered = block.lower()
    missing = []
    for token in tokens:
        if token.lower() not in lowered:
            missing.append(token)
    return sorted(missing)


# --------------------------------------------------------------------------
# skills.md :: summarize_policy  (enforced path)
# --------------------------------------------------------------------------

def _render_clause(clause):
    """
    Render one clause as a register block.

    Compression is structural only: clause ID, named binding verb, conditions
    enumerated one per line. Obligation wording is not paraphrased, because
    CONDITION PRESERVATION cannot be mechanically verified across a paraphrase.
    If the rendered block loses a critical token anyway, the clause falls back
    to verbatim and is flagged.
    """
    sentences = clause["sentences"] or [clause["text"]]
    verb = binding_verb_of(clause["text"])
    approvers = approvers_in(clause["text"])

    lines = []
    lines.append("[{}]  binding verb: {}".format(clause["id"], verb))
    lines.append("      obligation : {}".format(sentences[0]))
    for extra in sentences[1:]:
        lines.append("      condition  : {}".format(extra))

    if len(approvers) > 1:
        lines.append(
            "      >> MULTI-APPROVER — ALL {} REQUIRED: {}".format(
                len(approvers), "; ".join(approvers)
            )
        )

    lowered = clause["text"].lower()
    hits = [q for q in QUALIFIERS if q in lowered]
    if hits:
        lines.append("      qualifiers : {}".format(", ".join(sorted(set(hits)))))

    block = "\n".join(lines)

    missing = tokens_present(critical_tokens(clause["text"]), block)
    if missing:
        # Refusal path: do not paraphrase, quote and flag.
        block = "\n".join([
            "[{}]  binding verb: {}".format(clause["id"], verb),
            "      [FLAG: VERBATIM-REQUIRED — condensing this clause would drop "
            "a binding condition ({})]".format(", ".join(missing)),
            "      verbatim   : {}".format(clause["text"]),
        ])

    return block


def summarize_policy(structured, strict=True):
    """Produce the compliant clause register plus its validation report."""
    flat = all_clauses(structured)

    out = []
    out.append("COMPLIANCE SUMMARY — CLAUSE REGISTER")
    for line in structured["meta"]:
        out.append(line)
    out.append("")
    out.append("Scope: this register restates the obligations in the source document above.")
    out.append("It adds nothing. Where the source is silent, this register is silent.")
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
    summary_text = summary_text + "\n" + _render_report(report, len(flat))

    if strict and not report["ok"]:
        raise SummaryError("Summary failed validation: {}".format(report))

    return summary_text, report


# --------------------------------------------------------------------------
# The naive path — reproduces the failure the UC is about
# --------------------------------------------------------------------------

def naive_summarize(structured):
    """
    A generic extractive summary, which is what an unenforced
    "Summarize the policy document." prompt produces:
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


# --------------------------------------------------------------------------
# skills.md :: validate_summary
# --------------------------------------------------------------------------

def validate_summary(structured, candidate_text):
    flat = all_clauses(structured)
    source_ids = [clause["id"] for _, clause in flat]

    # A clause counts as present only if its ID appears in clause-marker
    # position at the start of a line. This is what stops "1.5 days per month"
    # inside clause 2.2 from being counted as a clause called 1.5.
    present_ids = set(CLAUSE_MARKER_RE.findall(candidate_text))

    missing_ids = [cid for cid in source_ids if cid not in present_ids]
    extra_ids = sorted(present_ids - set(source_ids))

    token_failures = {}
    for _, clause in flat:
        if clause["id"] in missing_ids:
            continue
        block = _extract_block(candidate_text, clause["id"])
        missing = tokens_present(critical_tokens(clause["text"]), block)
        if missing:
            token_failures[clause["id"]] = missing

    lowered = candidate_text.lower()
    banned_hits = [phrase for phrase in BANNED_PHRASES if phrase in lowered]

    critical_missing = [cid for cid in CRITICAL_CLAUSES if cid in missing_ids]
    critical_token_drop = {
        cid: token_failures[cid] for cid in CRITICAL_CLAUSES if cid in token_failures
    }

    flagged = re.findall(r"\[(\d+\.\d+)\][^\n]*\n\s*\[FLAG: VERBATIM-REQUIRED", candidate_text)

    report = {
        "clauses_source": len(source_ids),
        "clauses_summary": len(source_ids) - len(missing_ids),
        "missing_ids": missing_ids,
        "extra_ids": extra_ids,
        "token_failures": token_failures,
        "banned_phrases": banned_hits,
        "critical_gate_missing": critical_missing,
        "critical_gate_token_drop": critical_token_drop,
        "flagged_verbatim": flagged,
    }
    report["ok"] = (
        not missing_ids
        and not extra_ids
        and not token_failures
        and not banned_hits
        and not critical_missing
    )
    return report


def _extract_block(text, clause_id):
    """The chunk of the candidate summary that belongs to one clause ID."""
    markers = list(CLAUSE_MARKER_RE.finditer(text))
    chunks = []
    for index, marker in enumerate(markers):
        if marker.group(1) != clause_id:
            continue
        start = marker.end()
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        chunks.append(text[start:end])
    return " ".join(chunks)


def _render_report(report, total):
    lines = [
        "=" * 70,
        "COMPLIANCE CHECK (generated by validate_summary, not by hand)",
        "=" * 70,
        "Clauses in source          : {}".format(report["clauses_source"]),
        "Clauses in summary         : {}".format(report["clauses_summary"]),
        "Missing clause IDs         : {}".format(report["missing_ids"] or "none"),
        "Unsourced clause IDs       : {}".format(report["extra_ids"] or "none"),
        "Clauses losing a condition : {}".format(report["token_failures"] or "none"),
        "Banned / scope-bleed phrases: {}".format(report["banned_phrases"] or "none"),
        "Critical 10 gate           : {}".format(
            "PASS" if not report["critical_gate_missing"]
            and not report["critical_gate_token_drop"] else "FAIL"
        ),
        "Flagged verbatim           : {}".format(report["flagged_verbatim"] or "none"),
        "RESULT                     : {}".format("PASS" if report["ok"] else "FAIL"),
    ]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to the .txt policy document")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    parser.add_argument(
        "--mode",
        choices=["enforced", "naive"],
        default="enforced",
        help="enforced = agents.md rules applied; naive = reproduce the failure",
    )
    args = parser.parse_args()

    try:
        structured = retrieve_policy(args.input)
    except PolicyError as exc:
        print("REFUSED: {}".format(exc), file=sys.stderr)
        return 2

    if args.mode == "naive":
        text = naive_summarize(structured)
        report = validate_summary(structured, text)
        text = text + "\n" + _render_report(report, report["clauses_source"])
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
        print("Naive summary written to {}".format(args.output))
        print(_render_report(report, report["clauses_source"]))
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
    print(_render_report(report, report["clauses_source"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
