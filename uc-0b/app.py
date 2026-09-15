"""
UC-0B - Summary That Changes Meaning

Implements the enforcement rules declared in uc-0b/agents.md:

  CLAUSE INVENTORY COMPLETENESS   every source clause id is cited; omissions are reported
  MULTI-CONDITION PRESERVATION    every condition of a multi-condition clause is enumerated
  NO NEW INFORMATION              summary vocabulary is diffed against the source, mechanically
  NO PARAPHRASE OF BINDING LANG.  clause text is reproduced verbatim; verbs are classified, not rewritten
  REFUSAL BY FLAGGING             uncompressible clauses are marked [VERBATIM-REQUIRED], not guessed at

Standard library only. Deterministic: the same input file always produces the same
output file.

Usage:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt
"""

import argparse
import re
import sys
from typing import Dict, List

# --------------------------------------------------------------------------
# Ground truth from the UC-0B README clause inventory. These ten clauses carry
# the obligations a dropped condition would invert, so they are never compressed.
# --------------------------------------------------------------------------

CRITICAL_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
]

# --------------------------------------------------------------------------
# Binding verb classification. All matching classes are kept, not just the
# strongest - clause 2.6 is both a permission (may carry forward) and a
# forfeiture (days above 5 are forfeited), and dropping either changes it.
# --------------------------------------------------------------------------

VERB_PATTERNS = [
    ("PROHIBITION", re.compile(
        r"\b(?:not permitted|cannot|is not valid|not sufficient|"
        r"will not be considered|does not apply|do not count)\b", re.I)),
    ("MUST", re.compile(r"\bmust\b", re.I)),
    ("REQUIRES", re.compile(r"\brequires?\b", re.I)),
    ("WILL", re.compile(r"\bwill\b", re.I)),
    ("FORFEIT", re.compile(r"\bforfeit(?:ed|s|ure)?\b", re.I)),
    ("MAY", re.compile(r"\bmay\b", re.I)),
    ("ENTITLEMENT", re.compile(r"\b(?:entitled to|accrues)\b", re.I)),
]

# --------------------------------------------------------------------------
# Condition extraction. Each pattern captures an exact substring of the clause -
# nothing is reworded. Conjoined approvers, time limits, preconditions, negated
# alternatives and scope qualifiers all count as conditions, because dropping
# any one of them changes what the clause permits.
# --------------------------------------------------------------------------

CONDITION_PATTERNS = [
    # conjoined approvers - the clause 5.2 trap
    ("approver", re.compile(
        r"approval from (?:the )?[A-Z][\w\s]*? and (?:the )?[A-Z][\w\s]*?(?=[,.])", re.I)),
    ("approver", re.compile(r"approval from (?:the )?(?:Municipal Commissioner|"
                            r"employee's direct manager)", re.I)),
    ("time limit", re.compile(r"within \d+ [\w\s]*?(?=[,.]|$)", re.I)),
    ("time limit", re.compile(r"at least \d+ [\w\s]*?(?= using|[,.]|$)", re.I)),
    ("time limit", re.compile(r"before the leave commences", re.I)),
    ("time limit", re.compile(r"within the first quarter \([^)]*\)", re.I)),
    ("threshold", re.compile(r"\d+ or more consecutive days", re.I)),
    ("threshold", re.compile(r"exceeding \d+ continuous days", re.I)),
    ("threshold", re.compile(r"maximum of \d+ [\w\s]*?(?=[,.]|$)", re.I)),
    ("precondition", re.compile(r"only after [^.]*", re.I)),
    ("precondition", re.compile(r"only at [^.,]*", re.I)),
    ("forfeiture", re.compile(r"forfeited on \d+ \w+", re.I)),
    ("forfeiture", re.compile(r"or they are forfeited", re.I)),
    ("precondition", re.compile(r"immediately before or after [^.]*?(?= requires)", re.I)),
    ("precondition", re.compile(r"subject to [^.]*", re.I)),
    ("precondition", re.compile(r"unless [^.]*", re.I)),
    ("scope qualifier", re.compile(r"regardless of [^.]*", re.I)),
    ("scope qualifier", re.compile(r"under any circumstances", re.I)),
    ("negated alternative", re.compile(r"[A-Z][^.]*?\bis not valid", re.I)),
    ("negated alternative", re.compile(r"[A-Z][^.]*?\bis not sufficient", re.I)),
    ("form", re.compile(r"using Form [\w-]+", re.I)),
]

ABSOLUTE_QUALIFIERS = re.compile(
    r"\b(?:under any circumstances|regardless of|is not valid|"
    r"not sufficient|not permitted)\b", re.I)

QUANTITY_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s+(?:calendar |working |continuous |consecutive |unused |paid )*"
    r"(?:days?|weeks?|hours?|months?)\b", re.I)

# --------------------------------------------------------------------------
# NO NEW INFORMATION
# The only words the summariser is allowed to add. Every other word in the
# output body must come from the source. Adding to this list is a visible code
# change a reviewer can object to - that is the point of it being a constant.
# --------------------------------------------------------------------------

TEMPLATE_VOCAB = {
    "policy", "summary", "source", "generated", "deterministic", "paraphrase",
    "clause", "clauses", "section", "sections", "index", "record", "register",
    "verification", "glance", "key", "figures", "binding", "obligations",
    "obligation", "absolute", "prohibitions", "multi", "condition", "conditions",
    "enumerated", "full", "verbatim", "required", "reason", "critical", "present",
    "missing", "omitted", "cited", "parsed", "total", "count", "counts", "none",
    "scope", "bleed", "unsourced", "words", "check", "checks", "all", "and",
    "the", "from", "with", "each", "per", "see", "ref", "verb", "type", "file",
    "document", "reference", "version", "effective", "title", "compressed",
    "prohibition", "must", "requires", "will", "forfeit", "may", "entitlement",
    "statement", "approver", "time", "limit", "threshold", "precondition",
    "negated", "alternative", "qualifier", "form", "app", "txt", "not", "this",
    "was", "because", "carries", "carry", "one", "two", "three", "or", "more",
    "of", "in", "no", "is", "are", "any", "that", "it", "by", "for", "a", "an",
    "at", "to", "on", "as", "sourced", "added", "body", "vocabulary", "declared",
    "template", "structural", "below", "above", "run", "input", "output",
}


# --------------------------------------------------------------------------
# Skill: retrieve_policy
# --------------------------------------------------------------------------

def retrieve_policy(path: str) -> dict:
    """Load the policy file and return it as structured numbered clauses.

    Clause text is reproduced verbatim; only line-wrap whitespace is collapsed.
    Source order is preserved and clause ids are never renumbered.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = handle.read()
    except FileNotFoundError:
        sys.stderr.write("ERROR: policy file not found: {}\n".format(path))
        sys.exit(1)
    except (OSError, UnicodeDecodeError) as exc:
        sys.stderr.write("ERROR: could not read {}: {}\n".format(path, exc))
        sys.exit(1)

    lines = raw.replace("\r\n", "\n").split("\n")

    meta = {"header_lines": [], "reference": "", "version": "", "effective": ""}
    sections: List[dict] = []
    clauses: List[dict] = []

    current_section = None
    current_clause = None
    seen_first_section = False

    section_re = re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s\-()/]+)\s*$")
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)$")
    separator_re = re.compile(r"^[\u2550\u2500=\-_]{5,}\s*$")

    def close_clause():
        if current_clause is not None:
            current_clause["text"] = re.sub(r"\s+", " ", current_clause["text"]).strip()
            clauses.append(current_clause)
            if current_section is not None:
                current_section["clauses"].append(current_clause["id"])

    for line in lines:
        stripped = line.strip()

        if not stripped or separator_re.match(stripped):
            continue

        section_match = section_re.match(stripped)
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

        clause_match = clause_re.match(stripped)
        if clause_match:
            close_clause()
            current_clause = {
                "id": clause_match.group(1),
                "section": current_section["number"] if current_section else "",
                "text": clause_match.group(2),
            }
            continue

        if current_clause is not None:
            # continuation of a wrapped clause line
            current_clause["text"] += " " + stripped
        elif not seen_first_section:
            meta["header_lines"].append(stripped)

    close_clause()

    for header in meta["header_lines"]:
        if header.lower().startswith("document reference:"):
            meta["reference"] = header.split(":", 1)[1].strip()
        elif "version:" in header.lower():
            parts = header.split("|")
            for part in parts:
                if "version:" in part.lower():
                    meta["version"] = part.split(":", 1)[1].strip()
                elif "effective:" in part.lower():
                    meta["effective"] = part.split(":", 1)[1].strip()

    if not clauses:
        sys.stderr.write(
            "ERROR: no numbered clauses parsed from {}. Refusing to write a summary.\n"
            .format(path))
        sys.exit(1)

    return {
        "meta": meta,
        "sections": sections,
        "clauses": clauses,
        "clause_ids": [c["id"] for c in clauses],
        "raw": raw,
    }


# --------------------------------------------------------------------------
# Skill: classify_clause
# --------------------------------------------------------------------------

def classify_clause(clause: dict) -> dict:
    """Label a clause with verb classes, extracted conditions, and verbatim status."""
    text = clause["text"]

    verb_classes = [name for name, pattern in VERB_PATTERNS if pattern.search(text)]
    if not verb_classes:
        verb_classes = ["STATEMENT"]

    raw_conditions: List[tuple] = []
    seen = set()
    for label, pattern in CONDITION_PATTERNS:
        for match in pattern.finditer(text):
            found = match.group(0).strip().rstrip(",.")
            if not found:
                continue
            # Conjoined approvers become separate conditions. Clause 5.2 names two
            # approvers; listing them on one line is how "and the HR Director"
            # goes missing downstream.
            if label == "approver" and re.search(r"\band\b", found, re.I):
                head = re.match(r"(approval from )", found, re.I)
                prefix = head.group(1) if head else ""
                body = found[len(prefix):]
                parts = [p.strip() for p in re.split(r"\band\b", body, flags=re.I)]
                pieces = [prefix + p for p in parts if p]
            else:
                pieces = [found]

            for piece in pieces:
                key = piece.lower()
                if key not in seen:
                    seen.add(key)
                    raw_conditions.append((label, piece))

    # Drop any condition wholly contained in another - nested captures are
    # duplicates, and the longer capture always preserves more of the source.
    conditions: List[str] = []
    for label, piece in raw_conditions:
        if any(piece.lower() in other.lower() and piece.lower() != other.lower()
               for _, other in raw_conditions):
            continue
        conditions.append("{}: {}".format(label, piece))

    reasons = []
    if clause["id"] in CRITICAL_CLAUSES:
        reasons.append("critical clause")
    if len(conditions) >= 2:
        reasons.append("carries {} conditions".format(len(conditions)))
    if ABSOLUTE_QUALIFIERS.search(text):
        reasons.append("absolute qualifier present")

    return {
        "verb_classes": verb_classes,
        "conditions": conditions,
        "verbatim_required": bool(reasons),
        "verbatim_reason": "; ".join(reasons),
    }


# --------------------------------------------------------------------------
# Skill: check_scope_bleed
# --------------------------------------------------------------------------

def _tokens(text: str) -> List[str]:
    return [t.lower() for t in re.findall(r"[A-Za-z]{3,}", text)]


CLAIM_LINE = re.compile(r"\[\d+\.\d+\]")


def check_scope_bleed(summary_text: str, source_text: str) -> List[str]:
    """Return words present in the summary's claim lines but absent from the source.

    This is the testable form of "do not add information". Phrases like
    "as is standard practice" introduce words the source never used, and are
    caught here rather than trusted away.

    Only lines that cite a clause id are audited. A section heading asserts
    nothing about the policy; a line reading "[5.2] LWP requires approval from..."
    does. Auditing the claim lines is what keeps the check meaningful instead of
    forcing every heading word into the allowlist until the allowlist is the
    whole language.
    """
    source_vocab = set(_tokens(source_text))
    added = []
    for line in summary_text.split("\n"):
        if not CLAIM_LINE.search(line):
            continue
        for token in _tokens(line):
            if token in source_vocab or token in TEMPLATE_VOCAB:
                continue
            if token not in added:
                added.append(token)
    return added


# --------------------------------------------------------------------------
# Skill: summarize_policy
# --------------------------------------------------------------------------

def _rule(char: str = "-", width: int = 74) -> str:
    return char * width


def summarize_policy(policy: dict) -> str:
    """Build the summary text. Clause text is never rewritten."""
    clauses = policy["clauses"]
    analysis: Dict[str, dict] = {c["id"]: classify_clause(c) for c in clauses}
    by_id = {c["id"]: c for c in clauses}

    out: List[str] = []
    meta = policy["meta"]

    out.append(_rule("="))
    out.append("POLICY SUMMARY - {} | version {} | effective {}".format(
        meta["reference"] or "n/a", meta["version"] or "n/a", meta["effective"] or "n/a"))
    out.append("Generated by uc-0b/app.py - structural index, no paraphrase of clause text.")
    out.append(_rule("="))
    out.append("")

    # ---------------- 1. AT A GLANCE ----------------
    out.append("1. AT A GLANCE - KEY FIGURES")
    out.append(_rule())
    out.append("   Each figure below is reproduced from the clause cited beside it.")
    out.append("")
    for clause in clauses:
        quantities = QUANTITY_PATTERN.findall(clause["text"])
        found = [m.group(0) for m in QUANTITY_PATTERN.finditer(clause["text"])]
        if found:
            out.append("   [{}] {}".format(clause["id"], "  |  ".join(found)))
    out.append("")

    # ---------------- 2. BINDING OBLIGATIONS INDEX ----------------
    out.append("2. BINDING OBLIGATIONS INDEX")
    out.append(_rule())
    out.append("   Verb classes are classified from the source, never substituted.")
    out.append("")
    binding = [c for c in clauses
               if set(analysis[c["id"]]["verb_classes"]) &
               {"MUST", "REQUIRES", "WILL", "PROHIBITION", "FORFEIT"}]
    for clause in binding:
        info = analysis[clause["id"]]
        out.append("   [{}] {}".format(clause["id"], " + ".join(info["verb_classes"])))
        out.append("        {}".format(clause["text"]))
    out.append("")
    out.append("   Binding clauses: {} of {}.".format(len(binding), len(clauses)))
    out.append("")

    # ---------------- 3. MULTI-CONDITION OBLIGATIONS ----------------
    out.append("3. MULTI-CONDITION OBLIGATIONS - ALL CONDITIONS ENUMERATED")
    out.append(_rule())
    out.append("   A clause below is satisfied only when every condition listed under it")
    out.append("   is satisfied. Dropping one is the failure this section exists to prevent.")
    out.append("")
    multi = [c for c in clauses if len(analysis[c["id"]]["conditions"]) >= 2]
    for clause in multi:
        info = analysis[clause["id"]]
        out.append("   [{}] {}".format(clause["id"], clause["text"]))
        for index, condition in enumerate(info["conditions"], start=1):
            out.append("        ({}) {}".format(index, condition))
        out.append("")
    out.append("   Multi-condition clauses: {}.".format(len(multi)))
    out.append("")

    # ---------------- 4. ABSOLUTE PROHIBITIONS ----------------
    out.append("4. ABSOLUTE PROHIBITIONS")
    out.append(_rule())
    out.append("")
    prohibitions = [c for c in clauses
                    if "PROHIBITION" in analysis[c["id"]]["verb_classes"]]
    for clause in prohibitions:
        out.append("   [{}] {}".format(clause["id"], clause["text"]))
    out.append("")
    out.append("   Prohibition clauses: {}.".format(len(prohibitions)))
    out.append("")

    # ---------------- 5. FULL CLAUSE RECORD ----------------
    out.append("5. FULL CLAUSE RECORD - VERBATIM, SOURCE ORDER")
    out.append(_rule())
    out.append("")
    for section in policy["sections"]:
        out.append("   SECTION {} - {}".format(section["number"], section["title"]))
        for clause_id in section["clauses"]:
            clause = by_id[clause_id]
            info = analysis[clause_id]
            marker = ""
            if info["verbatim_required"]:
                marker = "  [VERBATIM-REQUIRED: {}]".format(info["verbatim_reason"])
            out.append("     [{}] {}{}".format(clause_id, clause["text"], marker))
        out.append("")

    # ---------------- 6. VERIFICATION ----------------
    body = "\n".join(out)
    cited = set(re.findall(r"\[(\d+\.\d+)\]", body))
    source_ids = set(policy["clause_ids"])
    omitted = sorted(source_ids - cited, key=lambda s: [int(p) for p in s.split(".")])
    bleed = check_scope_bleed(body, policy["raw"])

    out.append("6. VERIFICATION")
    out.append(_rule())
    out.append("   Clauses parsed from source:   {}".format(len(source_ids)))
    out.append("   Clauses cited in summary:     {}".format(len(cited & source_ids)))
    out.append("   Clauses omitted:              {} {}".format(
        len(omitted), omitted if omitted else ""))
    out.append("")
    out.append("   Critical clause checklist:")
    for clause_id in CRITICAL_CLAUSES:
        status = "PRESENT" if clause_id in cited else "MISSING"
        out.append("     [{}] {}".format(clause_id, status))
    out.append("")
    out.append("   Scope bleed check - words in summary not sourced from the document")
    out.append("   or the declared template vocabulary:")
    out.append("     {}".format(bleed if bleed else "none"))
    out.append("")
    out.append(_rule("="))

    return "\n".join(out) + "\n", omitted, bleed


# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    sys.stderr.write("Parsed {} clauses across {} sections from {}\n".format(
        len(policy["clauses"]), len(policy["sections"]), args.input))

    summary_text, omitted, bleed = summarize_policy(policy)

    # REFUSAL: an incomplete summary is not written at all.
    if omitted:
        sys.stderr.write(
            "ERROR: {} clause(s) missing from summary: {}. Refusing to write.\n"
            .format(len(omitted), omitted))
        sys.exit(1)

    try:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(summary_text)
    except OSError as exc:
        sys.stderr.write("ERROR: could not write {}: {}\n".format(args.output, exc))
        sys.exit(1)

    sys.stderr.write("Clause completeness: {}/{} cited, 0 omitted\n".format(
        len(policy["clause_ids"]), len(policy["clause_ids"])))
    sys.stderr.write("Scope bleed: {}\n".format(bleed if bleed else "none"))
    print("Done. Summary written to {}".format(args.output))


if __name__ == "__main__":
    main()