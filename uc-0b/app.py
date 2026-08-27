"""
UC-0B app.py — Summary That Changes Meaning
Rule-based implementation. No API key required.
Implements retrieve_policy and summarize_policy skills
following all RICE enforcement rules from agents.md / skills.md.

Run:
    python app.py \
        --input ../data/policy-documents/policy_hr_leave.txt \
        --output summary_hr_leave.txt
"""

import argparse
import os
import re
import sys
from textwrap import wrap

# ---------------------------------------------------------------------------
# Ground-truth clause inventory (from README / agents.md)
# ---------------------------------------------------------------------------

REQUIRED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
]

SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "typically in government organizations",
    "employees are generally expected to",
    "as is common",
    "generally speaking",
    "in most organisations",
    "in most organizations",
]

BINDING_VERB_GUARDS = {
    "must":          ["should", "may wish to", "is encouraged to", "is expected to"],
    "will":          ["may", "might", "could"],
    "not permitted": ["discouraged", "not recommended", "generally avoided"],
    "requires":      ["recommends", "suggests", "encourages"],
    "are forfeited": ["may be lost", "could lapse", "might be forfeited"],
}

# Fragments matched against actual parsed source text (verified against file).
MULTI_CONDITION_REQUIREMENTS = {
    "5.2": ["HR Director"],
    "2.4": ["verbal"],
    "2.6": ["above 5", "31 December"],
    "2.7": ["January", "forfeited"],
    "5.3": ["Municipal Commissioner"],
    "3.2": ["48"],
    "3.4": ["medical certificate"],
}

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class PolicyFileNotFoundError(Exception):
    pass

class PolicyFormatError(Exception):
    pass

class PolicyContentError(Exception):
    pass

class ClauseInventoryError(Exception):
    pass

class ScopeBleedError(Exception):
    pass

class ConditionDropError(Exception):
    pass

class BindingVerbError(Exception):
    pass

# ---------------------------------------------------------------------------
# Skill 1 — retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path):
    """
    Load file_path and return a list of clause dicts:
        [{"clause": "2.3", "text": "<full normalised clause text>"}, ...]

    The parser captures the clause heading text AND all continuation lines.
    Section separator lines (===, ═══) are stripped from clause bodies.
    """
    if not os.path.exists(file_path):
        raise PolicyFileNotFoundError(
            "retrieve_policy: '{}' does not exist. "
            "Halting — no partial content returned.".format(file_path)
        )

    if not file_path.lower().endswith(".txt"):
        raise PolicyFormatError(
            "retrieve_policy: '{}' is not a .txt file. "
            "Only UTF-8 plain-text policy files are accepted.".format(file_path)
        )

    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except UnicodeDecodeError as exc:
        raise PolicyFormatError(
            "retrieve_policy: '{}' could not be decoded as UTF-8. "
            "Detail: {}".format(file_path, exc)
        )

    if not raw.strip():
        raise PolicyContentError(
            "retrieve_policy: '{}' is empty. No policy content found.".format(file_path)
        )

    # Capture clause number + heading text + all continuation lines,
    # stopping at the next clause number or end of file.
    pattern = re.compile(
        r"(?m)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s|\Z)",
        re.DOTALL,
    )
    matches = pattern.findall(raw)

    if not matches:
        print(
            "WARNING retrieve_policy: No numbered clause sections detected. "
            "Returning raw content as a single unstructured block. "
            "Clause-level validation will not be possible.",
            file=sys.stderr,
        )
        return [{"clause": "UNSTRUCTURED", "text": raw.strip()}]

    sections = []
    for clause_num, body in matches:
        # Strip embedded section separator blocks (lines of ═ or =)
        clean = re.sub(r"[═=]{5,}[^\n]*", "", body)
        # Collapse runs of whitespace / blank lines
        clean = re.sub(r"[ \t]+", " ", clean)
        clean = re.sub(r"\n\s*\n+", "\n", clean)
        clean = clean.strip()
        if clean:
            sections.append({"clause": clause_num, "text": clean})

    return sections


# ---------------------------------------------------------------------------
# Rule-based summarizer — no API key required
# ---------------------------------------------------------------------------

def _rule_based_summarize(clause_num, clause_text):
    """
    Produce a compliant summary using only rule-based text processing.

    Multi-condition clauses always return verbatim (compression is too
    risky when every condition fragment must survive).
    Single-obligation clauses: keep sentences that contain a binding verb
    or obligation keyword; fall back to verbatim if nothing useful remains.

    Returns (summary_text: str, flagged: bool)
    """
    # Normalise whitespace
    text = re.sub(r"\s+", " ", clause_text).strip()

    # Multi-condition clauses: always verbatim, never compress
    if clause_num in MULTI_CONDITION_REQUIREMENTS:
        return text, True

    sentence_splitter = re.compile(r"(?<=[.!?])\s+")
    sentences = [s.strip() for s in sentence_splitter.split(text) if s.strip()]

    if not sentences:
        return text, True

    if len(sentences) == 1:
        return sentences[0], False

    binding_pattern = re.compile(
        r"\b(must|will|shall|requires?|not permitted|are forfeited|forfeited|"
        r"written|verbal|approval|approved|certificate|encashment|"
        r"carry.?forward|LOP|LWP|permitted|days?|advance)\b",
        re.IGNORECASE,
    )
    core = [s for s in sentences if binding_pattern.search(s)]

    if not core:
        return text, True

    summary = " ".join(core)

    # If not meaningfully shorter, return verbatim
    if len(summary) > 0.90 * len(text) and len(sentences) > 2:
        return text, True

    return summary, False


# ---------------------------------------------------------------------------
# Enforcement helpers
# ---------------------------------------------------------------------------

def _check_scope_bleed(clause_num, summary):
    lower = summary.lower()
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase.lower() in lower:
            raise ScopeBleedError(
                "summarize_policy [clause {}]: Scope bleed detected. "
                "Forbidden phrase: '{}'. Output will not be written.".format(
                    clause_num, phrase)
            )


def _check_condition_drop(clause_num, clause_text, summary):
    if clause_num not in MULTI_CONDITION_REQUIREMENTS:
        return

    required = MULTI_CONDITION_REQUIREMENTS[clause_num]
    lower_summary = summary.lower()
    dropped = [frag for frag in required if frag.lower() not in lower_summary]

    if not dropped:
        return

    # Clause 2.4: "verbal" is acceptable if it appears as negated
    if clause_num == "2.4" and "verbal" in dropped:
        if "verbal" in lower_summary and (
            "not valid" in lower_summary or "invalid" in lower_summary
        ):
            dropped.remove("verbal")

    if dropped:
        raise ConditionDropError(
            "summarize_policy [clause {}]: Condition drop detected. "
            "Missing from summary: {}. Output will not be written.".format(
                clause_num, dropped)
        )


def _check_binding_verbs(clause_num, source_text, summary):
    lower_source  = source_text.lower()
    lower_summary = summary.lower()

    for strong_verb, weak_forms in BINDING_VERB_GUARDS.items():
        if strong_verb in lower_source:
            for weak in weak_forms:
                if weak in lower_summary:
                    raise BindingVerbError(
                        "summarize_policy [clause {}]: "
                        "Binding verb '{}' weakened to '{}' in summary. "
                        "Output will not be written.".format(
                            clause_num, strong_verb, weak)
                    )


# ---------------------------------------------------------------------------
# Skill 2 — summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(sections, output_path):
    """
    Produce a compliant summary from sections and write to output_path.
    All 10 required clauses must be present; all enforcement checks must pass.
    """
    if not sections:
        raise PolicyContentError(
            "summarize_policy: Input section list is empty or null. "
            "Cannot produce output file."
        )

    # Clause inventory check
    present = {s["clause"] for s in sections}
    missing = [c for c in REQUIRED_CLAUSES if c not in present]
    if missing:
        raise ClauseInventoryError(
            "summarize_policy: Required clause(s) missing from input: {}. "
            "Halting — no output file written.".format(", ".join(missing))
        )

    output_lines = [
        "HR LEAVE POLICY — COMPLIANT SUMMARY",
        "=" * 60,
        "Source  : policy_hr_leave.txt",
        "Method  : rule-based (no external API)",
        "Clauses : all 10 required clauses present and verified",
        "Checks  : binding verbs · multi-condition obligations · scope bleed",
        "",
    ]

    for clause_num in REQUIRED_CLAUSES:
        section = next(s for s in sections if s["clause"] == clause_num)
        clause_text = section["text"]

        summary, flagged = _rule_based_summarize(clause_num, clause_text)

        if flagged:
            summary = clause_text  # use full normalised source text

        # Enforcement checks
        _check_scope_bleed(clause_num, summary)
        _check_condition_drop(clause_num, clause_text, summary)
        _check_binding_verbs(clause_num, clause_text, summary)

        flag_label = (
            "  [FLAGGED — verbatim: could not compress without meaning loss]"
            if flagged else ""
        )
        output_lines.append("Clause {}:{}".format(clause_num, flag_label))
        wrapped = wrap(summary, width=76, initial_indent="  ", subsequent_indent="  ")
        output_lines.extend(wrapped if wrapped else ["  " + summary])
        output_lines.append("")

    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(output_lines))
        fh.write("\n")

    print("summarize_policy: Output written -> '{}'".format(output_path))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="UC-0B: Clause-faithful HR leave policy summary. No API key required."
    )
    parser.add_argument("--input",  required=True, metavar="FILE",
                        help="Path to the source HR leave policy .txt file.")
    parser.add_argument("--output", required=True, metavar="FILE",
                        help="Path for the compliant summary output .txt file.")
    return parser.parse_args()


def main():
    args = parse_args()

    print("UC-0B: Loading policy from '{}' ...".format(args.input))
    try:
        sections = retrieve_policy(args.input)
    except (PolicyFileNotFoundError, PolicyFormatError, PolicyContentError) as exc:
        print("ERROR [retrieve_policy]: {}".format(exc), file=sys.stderr)
        sys.exit(1)

    print("UC-0B: Parsed {} section(s). Running enforcement checks ...".format(
        len(sections)))

    try:
        summarize_policy(sections, args.output)
    except (PolicyContentError, ClauseInventoryError,
            ScopeBleedError, ConditionDropError, BindingVerbError) as exc:
        print("ERROR [summarize_policy]: {}".format(exc), file=sys.stderr)
        sys.exit(1)

    print("UC-0B: Done.")


if __name__ == "__main__":
    main()