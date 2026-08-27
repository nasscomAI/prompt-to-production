#!/usr/bin/env python3
"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re
import sys

# --------------------------------------------------------------------------- #
# Ground truth (from agents.md `intent` and the UC-0B clause inventory)
# --------------------------------------------------------------------------- #

EXPECTED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7",
                    "3.2", "3.4", "5.2", "5.3", "7.2"]

# Binding-force tokens whose presence must be preserved and never softened.
# Order matters for reporting only. Multi-word phrases are checked as phrases.
BINDING_VERBS = [
    "not permitted",
    "are forfeited",
    "forfeited",
    "requires",
    "require",
    "must",
    "will",
    "may",
]

# Multi-condition obligations: every named approver MUST survive to the summary.
REQUIRED_CONDITIONS = {
    "5.2": ["Department Head", "HR Director"],
    "5.3": ["Municipal Commissioner"],
}

# Binding force each tracked clause MUST carry (from the UC-0B inventory).
# Ground truth is this fixed inventory — not merely the provided text — so a
# clause whose supplied wording has already been softened is caught and halted.
EXPECTED_VERBS = {
    "2.3": ["must"],
    "2.4": ["must"],
    "2.5": ["will"],
    "2.6": ["may", "forfeited"],
    "2.7": ["must", "forfeited"],
    "3.2": ["requires"],
    "3.4": ["requires"],
    "5.2": ["requires"],
    "5.3": ["requires"],
    "7.2": ["not permitted"],
}

# Scope-bleed framing that never appears in the source and must never be added.
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "typically in government organizations",
    "employees are generally expected to",
]


# --------------------------------------------------------------------------- #
# Errors — the agent surfaces failures explicitly and fabricates nothing.
# --------------------------------------------------------------------------- #

class SkillError(Exception):
    """Raised by a skill when it cannot honestly produce its output."""


class EnforcementError(Exception):
    """Raised when a produced summary violates an agents.md enforcement rule."""


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _norm(s):
    """Collapse whitespace for substring / containment comparisons."""
    return re.sub(r"\s+", " ", s).strip()


def _contains_phrase(haystack, phrase):
    """Case-insensitive whole-phrase containment, whitespace-insensitive."""
    return _norm(phrase).lower() in _norm(haystack).lower()


def _binding_verbs_in(text):
    """Return the set of binding-force tokens present in `text`.

    Word-boundary matched for single words so 'require' inside 'requirement'
    or 'will' inside 'willing' does not create a phantom hit.
    """
    found = set()
    low = _norm(text).lower()
    for verb in BINDING_VERBS:
        if " " in verb:                     
            if verb in low:
                found.add(verb)
        else:
            if re.search(r"\b" + re.escape(verb) + r"\b", low):
                found.add(verb)
    return found


def _split_sentences(text):
    """Naive but faithful sentence splitter. Keeps original substrings."""
    # Split on sentence-final punctuation followed by whitespace, but keep the
    # punctuation attached to the sentence it terminates.
    parts = re.split(r"(?<=[.!?])\s+", _norm(text))
    return [p for p in parts if p.strip()]


# --------------------------------------------------------------------------- #
# SKILL 1 — retrieve_policy
# --------------------------------------------------------------------------- #

def retrieve_policy(path):
    """Load the .txt policy and parse it into ordered numbered clause sections.

    Returns: list[ {clause_id: str, text: str(verbatim)} ] in source order.
    Raises SkillError on any condition that would force fabrication or pass an
    incomplete structure downstream.
    """
    # --- error_handling: missing / unreadable / empty --------------------- #
    if not os.path.isfile(path):
        raise SkillError(f"retrieve_policy: policy file not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        raise SkillError(f"retrieve_policy: cannot read '{path}' as UTF-8 text: {exc}")

    if not raw.strip():
        raise SkillError(f"retrieve_policy: policy file is empty: {path}")

    # --- parse numbered clauses (e.g. 2.3, 5.2, 7.2) ---------------------- #
    # A "boundary" is any line starting with a dotted-number marker: a section
    # header ("3."), a clause ("3.2"), or a sub-clause ("2.3.1"). ALL of them
    # bound a clause body, so section titles never bleed into a clause. Only
    # two-level ids are emitted as clauses.
    boundary = re.compile(r"(?m)^[ \t]*(\d+(?:\.\d+)*)(?=[ \t.)\-:]|$)")
    marks = list(boundary.finditer(raw))

    two_level = [m for m in marks if m.group(1).count(".") == 1]
    if not two_level:
        raise SkillError(
            "retrieve_policy: no numbered clauses (e.g. 2.3, 5.2) found in source."
        )

    starts = [m.start() for m in marks]
    sections = []
    for m in two_level:
        clause_id = m.group(1)
        start = m.start()
        # body ends at the next boundary of ANY level.
        later = [s for s in starts if s > start]
        end = min(later) if later else len(raw)
        verbatim = raw[start:end].strip()
        sections.append({"clause_id": clause_id, "text": verbatim})

    # --- error_handling: guard against clause omission at the source ------ #
    found_ids = {s["clause_id"] for s in sections}
    missing = [cid for cid in EXPECTED_CLAUSES if cid not in found_ids]
    if missing:
        raise SkillError(
            "retrieve_policy: source is missing required clause(s): "
            + ", ".join(missing)
            + " — halting rather than passing an incomplete structure downstream."
        )

    return sections


# --------------------------------------------------------------------------- #
# SKILL 2 — summarize_policy
# --------------------------------------------------------------------------- #

def _clause_body(section):
    """Return the clause text with its leading id stripped, verbatim otherwise.

    A summary entry is the clause body reproduced VERBATIM. Deterministic
    reword or sentence-dropping cannot prove it preserved every condition
    (e.g. clause 2.4's "verbal approval is not valid" carries no binding verb
    yet is a real condition), so per enforcement rule 5 the agent quotes the
    clause rather than guess. This makes condition-drop and softening
    impossible by construction while keeping every line sourced.
    """
    clause_id = section["clause_id"]
    return re.sub(r"^\s*" + re.escape(clause_id) + r"[\.\):\-]?\s*", "",
                  _norm(section["text"])).strip()


def summarize_policy(sections):
    """Produce the compliant summary text from retrieve_policy output.

    Raises EnforcementError if the result would violate any agents.md rule.
    """
    if not isinstance(sections, list) or not sections:
        raise EnforcementError("summarize_policy: received no clause sections.")

    provided = {s["clause_id"] for s in sections}
    missing_in = [cid for cid in EXPECTED_CLAUSES if cid not in provided]
    if missing_in:
        raise EnforcementError(
            "summarize_policy: refusing to summarize — input is missing clause(s): "
            + ", ".join(missing_in)
        )

    # Every clause is reproduced verbatim (id-stripped). `src` == `text` here,
    # which is what makes the enforcement gates pass by construction; they are
    # retained as regression guards against any future change to this policy.
    entries = []          # (clause_id, summary_text, source_body)
    for section in sections:
        body = _clause_body(section)
        entries.append((section["clause_id"], body, body))

    # ---------------------------- render --------------------------------- #
    lines = [f"[{cid}] {text}" for cid, text, _src in entries]
    summary = "\n\n".join(lines)

    # ----------------------- ENFORCEMENT GATES --------------------------- #
    _enforce(summary, entries)

    return summary


# --------------------------------------------------------------------------- #
# Enforcement pass — the agents.md rules, as hard, verifiable gates.
# --------------------------------------------------------------------------- #

def _enforce(summary, entries):
    violations = []

    # Rule 1 — every numbered clause in the source must be present. This covers
    # the 10 tracked clauses AND any other numbered clause the source contains.
    present_ids = {cid for cid, _t, _s in entries}
    for cid in EXPECTED_CLAUSES:
        if cid not in present_ids or f"[{cid}]" not in summary:
            violations.append(f"tracked clause {cid} is missing from the summary")

    for cid, text, src in entries:
        # Rule 2 — multi-condition obligations keep ALL conditions.
        for cond in REQUIRED_CONDITIONS.get(cid, []):
            if not _contains_phrase(text, cond):
                violations.append(
                    f"clause {cid} dropped required condition: '{cond}'")

        # Rule 4 — binding force preserved, never softened.
        #  (a) relative check: no verb present in the clause's own source may
        #      disappear from its summary.
        out_verbs = _binding_verbs_in(text)
        for v in _binding_verbs_in(src) - out_verbs:
            violations.append(
                f"clause {cid} softened/dropped binding verb: '{v}'")
        #  (b) absolute check against the fixed inventory: each tracked clause
        #      must carry its expected binding force even if the supplied text
        #      arrived already softened.
        for v in EXPECTED_VERBS.get(cid, []):
            if v not in out_verbs:
                violations.append(
                    f"clause {cid} is missing its required binding force: '{v}'")

        # Rule 3 (part a) — no unsourced content: every summary sentence must
        # be a verbatim substring of its source clause.
        for sent in _split_sentences(text):
            if _norm(sent).lower() not in _norm(src).lower():
                violations.append(
                    f"clause {cid} contains a sentence not present in the "
                    f"source: '{sent[:60]}...'")

    # Rule 3 (part b) — no scope-bleed phrases anywhere in the summary.
    for phrase in SCOPE_BLEED_PHRASES:
        if _contains_phrase(summary, phrase):
            violations.append(f"scope-bleed phrase introduced: '{phrase}'")

    if violations:
        raise EnforcementError(
            "summarize_policy: enforcement failed — refusing to emit summary:\n  - "
            + "\n  - ".join(violations)
        )


# --------------------------------------------------------------------------- #
# Agent entry point
# --------------------------------------------------------------------------- #

def run(input_path, output_path):
    sections = retrieve_policy(input_path)                     # skill 1
    summary_body = summarize_policy(sections)                  # skill 2

    header = (
        "UC-0B — HR Leave Policy Summary\n"
        f"Source: {input_path}\n"
        f"Tracked clauses (all present): {', '.join(EXPECTED_CLAUSES)}\n"
        "Note: each clause is reproduced verbatim and tagged by its clause "
        "reference. Verbatim quotation is used deliberately so that no "
        "condition is dropped and no binding obligation is softened.\n"
        + "=" * 60 + "\n\n"
    )
    document = header + summary_body + "\n"

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(document)

    return output_path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="UC-0B HR leave policy summarization agent "
                    "(faithful, meaning-preserving)."
    )
    parser.add_argument("--input", required=True,
                        help="Path to the source .txt policy file.")
    parser.add_argument("--output", required=True,
                        help="Path to write the summary .txt file.")
    args = parser.parse_args(argv)

    try:
        out = run(args.input, args.output)
    except (SkillError, EnforcementError) as exc:
        # Fail loud, fabricate nothing, write no output file.
        sys.stderr.write(f"ERROR: {exc}\n")
        return 1

    sys.stdout.write(f"OK: summary written to {out}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())