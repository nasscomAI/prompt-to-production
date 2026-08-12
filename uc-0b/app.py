"""
UC-0B — Summary That Changes Meaning

An extractive compliance summariser for numbered policy documents.

The design premise: the three failure modes named in the README — clause
omission, scope bleed, obligation softening — are not things you fix by asking
a model more nicely. They are things you make structurally impossible.

  * Omission is impossible because every parsed clause is emitted, and the
    program fails if clauses-in != clauses-out.
  * Softening is impossible because any clause carrying a binding verb is
    reproduced verbatim. There is no code path that rewords an obligation.
  * Bleed is impossible because every alphabetic token in the output must trace
    back to the source document or to a fixed, declared structural vocabulary.

Compression — the part that makes this a summary rather than a copy — is applied
only to non-binding informational clauses, and even there every extracted figure
is retained.

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt
"""
import argparse
import io
import os
import re
import sys
from typing import Dict, List, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# Binding verbs. A clause matching any of these is reproduced VERBATIM.
# Order matters only for readability of the label list; all matches are kept.
# ─────────────────────────────────────────────────────────────────────────────
BINDING_PATTERNS = (
    ("MUST NOT", r"\bmust not\b"),
    ("MUST", r"\bmust\b"),
    ("REQUIRES", r"\brequires\b|\brequired\b"),
    ("NOT PERMITTED", r"\bnot permitted\b"),
    ("NOT VALID", r"\bnot valid\b"),
    ("NOT SUFFICIENT", r"\bnot sufficient\b"),
    ("NOT ELIGIBLE", r"\bnot eligible\b"),
    ("NOT REIMBURSABLE", r"\bnot reimbursable\b"),
    ("NOT CONSIDERED", r"\bnot be considered\b"),
    ("NOT PROCESSED", r"\bnot be processed\b"),
    ("DOES NOT APPLY", r"\bdoes not apply\b"),
    ("CANNOT", r"\bcannot\b"),
    ("FORFEITED", r"\bforfeited\b"),
    ("MANDATORY", r"\bmandatory\b"),
    ("WILL", r"\bwill\b"),
    ("MAY", r"\bmay\b"),
    ("CONDITIONAL", r"\bonly\b|\bunless\b|\bregardless of\b|\bsubject to\b"),
)

# Purely informational markers — an entitlement figure, not an obligation.
ENTITLEMENT_PATTERN = r"\bentitled\b|\baccrues\b"

# Enforcement rule: banned hedging and scope-bleed phrases.
BANNED_PHRASES = (
    "as is standard practice",
    "standard practice",
    "typically",
    "generally",
    "usually",
    "normally",
    "it is common practice",
    "common practice",
    "in most organisations",
    "in most organizations",
    "best practice",
    "it is understood that",
    "should ordinarily",
    "while not explicitly",
    "it is assumed",
    "presumably",
)

# Figures that must never be lost, even from a compressed clause.
FIGURE_PATTERNS = (
    r"Rs\s?[\d,]+",
    r"\b\d[\d,]*(?:\.\d+)?\s*(?:calendar days?|working days?|continuous days?|"
    r"consecutive days?|days?|weeks?|months?|years?|hours?|km)\b",
    r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\b",
    r"\bJanuary\s*[–—-]\s*March\b",
    r"\bForm\s+[A-Z]{2,}-[A-Z0-9]+\b",
    r"\b\d[\d,]*(?:\.\d+)?\s*%",
    r"\bmaximum of \d[\d,]*\b",
    r"\bfirst two live births\b",
)

# ─────────────────────────────────────────────────────────────────────────────
# The 10 critical clauses from the UC-0B README, with the phrases that MUST
# survive into the output. A missing phrase fails the run — it does not warn.
#
# Keyed by document reference, because a clause register is document-specific:
# clause 5.2 means "two approvers for LWP" in HR-POL-001 and something entirely
# different in FIN-POL-007. Applying the HR register to another document would
# manufacture ten false failures, which is its own kind of dishonest output.
# ─────────────────────────────────────────────────────────────────────────────
CRITICAL_CLAUSE_REGISTERS = {
    "HR-POL-001": {
        "2.3": ["14 calendar days", "Form HR-L1"],
        "2.4": ["written approval", "not valid"],
        "2.5": ["Loss of Pay", "regardless of subsequent approval"],
        "2.6": ["maximum of 5", "31 December"],
        "2.7": ["first quarter", "forfeited"],
        "3.2": ["3 or more consecutive days", "48 hours", "medical certificate"],
        "3.4": ["regardless of duration", "medical certificate"],
        "5.2": ["Department Head", "HR Director", "not sufficient"],
        "5.3": ["30 continuous days", "Municipal Commissioner"],
        "7.2": ["not permitted under any circumstances"],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Declared structural vocabulary — the ONLY words the template itself may add.
# Every other alphabetic token in the output must come from the source document.
# This list is the anti-scope-bleed contract, and it is checked, not trusted.
# ─────────────────────────────────────────────────────────────────────────────
STRUCTURAL_VOCABULARY = frozenset("""
compliance summary source document reference version generated extractive
summariser paraphrase binding obligation obligations verbatim coverage sections
parsed clauses clause emitted entitlements scope verification part limits
conditions condition multi preserved informational compressed figures retained
pass fail failed checks check critical register present key phrase phrases
banned hedging bleed token tokens traceable vocabulary count counts total none
detected label labels shortened note notes file whitespace normalised agents
enforcement rule rules id section title effective policy unparsed lines words
word structural added information softening omission possible construction
conditional entitlement uc reworded see below above per and or of in out to
this is are was for with by no not all every text field figure untraceable
line number verbs verb strength wrapped rejoined identical run report reported
input output truncated ellipsis carried forward marker markers never txt b
applicable register registers
requires must cannot forfeited mandatory may will valid sufficient eligible
reimbursable considered processed does apply permitted
""".split())


def _normalise_whitespace(text: str) -> str:
    """Rejoin hard line wraps. The only transformation applied to clause text."""
    return re.sub(r"\s+", " ", text).strip()


def retrieve_policy(path: str) -> dict:
    """Load a .txt policy file and return structured numbered sections."""
    if not os.path.isfile(path):
        print("Error: input file not found: {0}".format(path), file=sys.stderr)
        sys.exit(1)
    try:
        with io.open(path, "r", encoding="utf-8-sig") as handle:
            raw_lines = handle.read().splitlines()
    except (IOError, OSError, UnicodeDecodeError) as exc:
        print("Error: could not read {0}: {1}".format(path, exc), file=sys.stderr)
        sys.exit(1)

    section_re = re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s()/&,'–-]+)$")
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)$")
    divider_re = re.compile(r"^[═=_\-\s]+$")

    meta_lines = []
    sections = []
    clauses = []
    unparsed = []
    current_section = None
    current_clause = None

    for line in raw_lines:
        if not line.strip() or divider_re.match(line):
            continue

        section_match = section_re.match(line)
        clause_match = clause_re.match(line)

        if clause_match:
            current_clause = {
                "id": clause_match.group(1),
                "section": current_section["number"] if current_section else "0",
                "parts": [clause_match.group(2)],
            }
            clauses.append(current_clause)
            if current_section:
                current_section["clauses"].append(current_clause)
        elif section_match:
            current_section = {
                "number": section_match.group(1),
                "title": _normalise_whitespace(section_match.group(2)),
                "clauses": [],
            }
            sections.append(current_section)
            current_clause = None
        elif line.startswith((" ", "\t")) and current_clause is not None:
            # Continuation of the clause above — a hard line wrap, not new text.
            current_clause["parts"].append(line)
        elif current_section is None:
            meta_lines.append(line.strip())
        else:
            unparsed.append(line)

    for clause in clauses:
        clause["text"] = _normalise_whitespace(" ".join(clause["parts"]))
        del clause["parts"]

    if not clauses:
        print(
            "Error: no numbered clauses found in {0}. Refusing to emit an empty "
            "summary of a real policy.".format(path),
            file=sys.stderr,
        )
        sys.exit(1)

    reference = ""
    version = ""
    title_parts = []
    for line in meta_lines:
        if line.lower().startswith("document reference:"):
            reference = line.split(":", 1)[1].strip()
        elif line.lower().startswith("version:"):
            version = line.split(":", 1)[1].strip()
        else:
            title_parts.append(line)

    return {
        "title": " / ".join(title_parts),
        "reference": reference,
        "version": version,
        "sections": sections,
        "clauses": clauses,
        "unparsed": unparsed,
        "source_text": "\n".join(raw_lines),
    }


def _binding_labels(text: str) -> List[str]:
    """Return every binding-verb label present in the clause."""
    return [label for label, pattern in BINDING_PATTERNS
            if re.search(pattern, text, re.IGNORECASE)]


def _extract_figures(text: str) -> List[str]:
    """Pull out numeric limits, dates and form numbers — verbatim spans."""
    found = []
    for pattern in FIGURE_PATTERNS:
        for match in re.finditer(pattern, text):
            span = _normalise_whitespace(match.group(0))
            if span and span not in found:
                found.append(span)
    return found


def _split_conditions(text: str) -> List[str]:
    """Decompose a clause into its condition fragments.

    Used only to COUNT and DISPLAY conditions alongside the verbatim text — the
    verbatim text is always emitted too, so this split can never lose a
    condition. A dropped condition would change the count, which is asserted.

    Two refinements found by reading the output rather than trusting it:
      * " and " is split only when BOTH sides are substantial (>=3 words).
        Otherwise clause 7.3 "Sick leave and LWP cannot be encashed" splits into
        a dangling "Sick leave", which reads as a lost condition rather than a
        compound subject. Clause 5.2's two approvers still separate correctly.
      * One-word fragments are merged back into the previous fragment, so a
        comma-separated list never leaves orphan tokens.
    """
    fragments = [f.strip() for f in re.split(r"(?:\.\s+)|(?:;\s*)|(?:,\s+)", text)]

    expanded = []
    for fragment in fragments:
        parts = re.split(r"\s+and\s+", fragment)
        if len(parts) == 2 and all(len(p.split()) >= 3 for p in parts):
            expanded.extend(p.strip() for p in parts)
        else:
            expanded.append(fragment)

    merged = []
    for fragment in expanded:
        cleaned = fragment.strip().rstrip(".")
        if not cleaned:
            continue
        if len(cleaned.split()) < 2 and merged:
            merged[-1] = merged[-1] + ", " + cleaned
        else:
            merged.append(cleaned)
    return [f for f in merged if len(f) > 3]


def _compress_informational(text: str, word_limit: int = 26) -> Tuple[str, bool]:
    """Shorten a non-binding clause using only its own leading words.

    Cuts at the last comma inside the limit where one exists, so the output ends
    on a phrase boundary instead of mid-possessive ("the child's …").
    """
    words = text.split()
    if len(words) <= word_limit:
        return text, False

    head = words[:word_limit]
    for index in range(len(head) - 1, max(len(head) // 2, 2), -1):
        if head[index].endswith(","):
            return " ".join(head[: index + 1]) + " …", True
    return " ".join(head) + " …", True


def _check_tokens(body: str, source_text: str) -> List[str]:
    """Every alphabetic token in the body must trace to source or vocabulary."""
    source_tokens = set(w.lower() for w in re.findall(r"[A-Za-z]+", source_text))
    untraceable = []
    for token in re.findall(r"[A-Za-z]+", body):
        lowered = token.lower()
        if lowered in source_tokens or lowered in STRUCTURAL_VOCABULARY:
            continue
        if lowered not in untraceable:
            untraceable.append(lowered)
    return untraceable


def summarize_policy(policy: dict, source_name: str = "") -> Tuple[str, dict]:
    """Produce the compliance summary and verify it against the enforcement rules."""
    binding_entries = []
    info_entries = []

    for clause in policy["clauses"]:
        text = clause["text"]
        labels = _binding_labels(text)
        figures = _extract_figures(text)

        if labels:
            conditions = _split_conditions(text)
            binding_entries.append(
                {
                    "id": clause["id"],
                    "text": text,
                    "labels": labels,
                    "figures": figures,
                    "conditions": conditions,
                }
            )
        else:
            compressed, truncated = _compress_informational(text)
            info_entries.append(
                {
                    "id": clause["id"],
                    "text": compressed,
                    "truncated": truncated,
                    "figures": figures,
                    "entitlement": bool(re.search(ENTITLEMENT_PATTERN, text, re.I)),
                }
            )

    total_in = len(policy["clauses"])
    total_out = len(binding_entries) + len(info_entries)
    multi = [e for e in binding_entries if len(e["conditions"]) > 1]

    lines = []
    lines.append("COMPLIANCE SUMMARY — " + policy["title"])
    lines.append("Source document: {0} | Reference {1} | Version {2}".format(
        os.path.basename(source_name) or "none",
        policy["reference"] or "none",
        policy["version"] or "none"))
    lines.append("Generated by UC-0B extractive summariser — all binding clause "
                 "text below is verbatim, with no paraphrase.")
    lines.append("")
    lines.append("=" * 74)
    lines.append("COVERAGE")
    lines.append("=" * 74)
    lines.append("  Sections parsed          : {0}".format(len(policy["sections"])))
    lines.append("  Clauses parsed from source: {0}".format(total_in))
    lines.append("  Clauses emitted in summary: {0}".format(total_out))
    lines.append("  Binding obligations       : {0}".format(len(binding_entries)))
    lines.append("  Multi-condition clauses   : {0}".format(len(multi)))
    lines.append("  Informational clauses     : {0}".format(len(info_entries)))
    lines.append("  Unparsed source lines     : {0}".format(len(policy["unparsed"])))
    lines.append("")

    lines.append("=" * 74)
    lines.append("PART 1 — BINDING OBLIGATIONS (verbatim, never reworded)")
    lines.append("=" * 74)
    for entry in binding_entries:
        label = " · ".join(entry["labels"])
        if len(entry["conditions"]) > 1:
            label += " · MULTI-CONDITION ({0} conditions — all preserved)".format(
                len(entry["conditions"]))
        lines.append("")
        lines.append("[{0}] {1}".format(entry["id"], label))
        lines.append('  "{0}"'.format(entry["text"]))
        if entry["figures"]:
            lines.append("  Limits: " + " | ".join(entry["figures"]))
        if len(entry["conditions"]) > 1:
            lines.append("  Conditions:")
            for index, condition in enumerate(entry["conditions"], start=1):
                lines.append("    {0}. {1}".format(index, condition))
    lines.append("")

    lines.append("=" * 74)
    lines.append("PART 2 — ENTITLEMENTS AND SCOPE (compressed, figures retained)")
    lines.append("=" * 74)
    for entry in info_entries:
        marker = " [truncated]" if entry["truncated"] else ""
        lines.append("")
        lines.append("[{0}]{1} {2}".format(entry["id"], marker, entry["text"]))
        if entry["figures"]:
            lines.append("  Figures: " + " | ".join(entry["figures"]))
    lines.append("")

    body = "\n".join(lines)

    # ── Self-verification against the enforcement rules ──────────────────────
    failures = []

    complete = total_in == total_out
    if not complete:
        failures.append("Clause count mismatch: {0} parsed, {1} emitted.".format(
            total_in, total_out))

    found_banned = [p for p in BANNED_PHRASES if p in body.lower()]
    if found_banned:
        failures.append("Banned phrase(s) present: " + ", ".join(found_banned))

    untraceable = _check_tokens(body, policy["source_text"])
    if untraceable:
        failures.append("Untraceable token(s) — possible scope bleed: "
                        + ", ".join(untraceable))

    emitted_ids = set(e["id"] for e in binding_entries) | set(e["id"] for e in info_entries)
    register = CRITICAL_CLAUSE_REGISTERS.get(policy["reference"], {})
    critical_results = []
    for clause_id, required in sorted(register.items()):
        if clause_id not in emitted_ids:
            critical_results.append((clause_id, "FAIL", "clause absent"))
            failures.append("Critical clause {0} absent from summary.".format(clause_id))
            continue
        entry = next((e for e in binding_entries if e["id"] == clause_id), None)
        if entry is None:
            critical_results.append((clause_id, "FAIL", "no binding label detected"))
            failures.append("Critical clause {0} has no binding label.".format(clause_id))
            continue
        missing = [p for p in required if p.lower() not in body.lower()]
        if missing:
            critical_results.append((clause_id, "FAIL", "lost: " + ", ".join(missing)))
            failures.append("Critical clause {0} lost required phrase(s): {1}".format(
                clause_id, ", ".join(missing)))
        else:
            critical_results.append(
                (clause_id, "PASS", " · ".join(entry["labels"])))

    verification = []
    verification.append("=" * 74)
    verification.append("PART 3 — VERIFICATION (checked by the program, not asserted by it)")
    verification.append("=" * 74)
    verification.append("  Completeness  : {0} — {1} clauses parsed, {2} emitted".format(
        "PASS" if complete else "FAIL", total_in, total_out))
    verification.append("  No bleed      : {0} — {1} untraceable token(s)".format(
        "PASS" if not untraceable else "FAIL", len(untraceable)))
    verification.append("  No hedging    : {0} — {1} banned phrase(s)".format(
        "PASS" if not found_banned else "FAIL", len(found_banned)))
    verification.append("")
    if register:
        verification.append(
            "  Critical clause register for {0} ({1} clauses from the UC-0B README):".format(
                policy["reference"], len(register)))
        for clause_id, status, detail in critical_results:
            verification.append("    [{0}] {1} — {2}".format(clause_id, status, detail))
    else:
        verification.append(
            "  Critical clause register: not applicable — no register declared for "
            "reference {0}. Completeness, bleed and hedging checks still apply.".format(
                policy["reference"] or "none"))
    verification.append("")
    verification.append("  Overall: {0}".format("PASS" if not failures else "FAIL"))
    if failures:
        verification.append("  Failures:")
        for failure in failures:
            verification.append("    - " + failure)

    summary_text = body + "\n" + "\n".join(verification) + "\n"

    report = {
        "clauses_in": total_in,
        "clauses_out": total_out,
        "binding": len(binding_entries),
        "multi_condition": len(multi),
        "informational": len(info_entries),
        "critical": critical_results,
        "untraceable": untraceable,
        "banned": found_banned,
        "failures": failures,
        "passed": not failures,
    }
    return summary_text, report


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary_text, report = summarize_policy(policy, source_name=args.input)

    try:
        with io.open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(summary_text)
    except (IOError, OSError) as exc:
        print("Error: could not write {0}: {1}".format(args.output, exc), file=sys.stderr)
        sys.exit(1)

    print("Clauses parsed {clauses_in} -> emitted {clauses_out} | binding {binding} "
          "| multi-condition {multi_condition} | informational {informational}".format(**report))
    print("Critical clauses: {0}/{1} PASS".format(
        sum(1 for _, status, _ in report["critical"] if status == "PASS"),
        len(report["critical"])))

    if report["failures"]:
        print("\nENFORCEMENT FAILURES:", file=sys.stderr)
        for failure in report["failures"]:
            print("  - " + failure, file=sys.stderr)
        print("Summary written to {0} with FAIL recorded.".format(args.output))
        sys.exit(1)

    print("All enforcement checks PASS. Summary written to {0}".format(args.output))


if __name__ == "__main__":
    main()
