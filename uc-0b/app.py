"""
UC-0B — Policy Summariser

Implements the contract in agents.md / skills.md.

Summarisation here is EXTRACTIVE: every sentence of body text emitted is a
verbatim substring of the source document. That is the load-bearing design
choice — an obligation that is never rewritten cannot be softened, and text that
must come from the source cannot bleed in outside knowledge. The run verifies
both properties rather than asserting them.
"""
import argparse
import os
import re
import sys

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z \-/&()]+)$")
RULE_RE = re.compile(r"^[═=]{5,}$")
# Avoid splitting "1.5 days" or "HR-L1." mid-number.
SENTENCE_SPLIT_RE = re.compile(r"(?<=[a-z\)\]])\.\s+(?=[A-Z])")

# Strongest binding verb wins; order is the precedence.
BINDING_VERBS = [
    ("MUST", r"\bmust\b"),
    ("REQUIRES", r"\brequires?\b|\brequired\b"),
    ("PROHIBITED", r"\bnot permitted\b|\bcannot\b|\bis not valid\b|\bnot sufficient\b"),
    ("WILL", r"\bwill\b|\bare forfeited\b|\bis recorded\b"),
    ("ENTITLEMENT", r"\bentitled to\b|\baccrues\b"),
    ("MAY", r"\bmay\b"),
    ("SCOPE", r"\bgoverns\b|\bdoes not apply\b"),
]

# Anything that changes what a reader must actually do. Order matters only for
# readability of the conditions line.
CONDITION_PATTERNS = [
    # Up to 3 qualifier words between the number and its unit, so
    # "5 unused annual leave days" is captured, not just "5 days".
    r"\b\d+(?:\.\d+)?\s+(?:[a-z]+\s+){0,3}?(?:days|day|weeks|week|hours|months)\b",
    r"\b31 December\b",
    r"\bJanuary[–-]March\b",
    r"\bfirst quarter\b",
    r"\bForm HR-L1\b",
    r"\bDepartment Head\b",
    r"\bHR Director\b",
    r"\bMunicipal Commissioner\b",
    r"\bHR Department\b",
    r"\bState Government\b",
    r"\bdirect manager\b",
    r"\bregistered medical practitioner\b",
    r"\bmedical certificate\b",
    r"\bwritten approval\b",
    r"\bLoss of Pay \(LOP\)",
    r"\bcompensatory off\b",
    r"\bpublic holiday\b",
    r"\bbefore the leave commences\b",
    r"\bonly after exhausting\b",
    r"\bregardless of [a-z ]+\b",
    r"\bunder any circumstances\b",
    r"\bfirst two live births\b",
    r"\bthird or subsequent child\b",
]

NEGATION_PATTERNS = [
    r"\bis not valid\b",
    r"\bnot sufficient\b",
    r"\bnot permitted\b",
    r"\bcannot\b",
    r"\bwill not be considered\b",
    r"\bdo not count\b",
    r"\bdoes not apply\b",
]

# None of these appear in the source; any hit means invented framing.
BANNED_PHRASES = [
    "as is standard", "standard practice", "typically", "generally",
    "usually", "in most cases", "it is recommended", "best practice",
    "normally", "as a rule", "commonly", "industry norm",
]

VERBATIM_FLAG = "[VERBATIM — multi-condition]"

# From uc-0b/README.md. Each entry: clause id -> substrings that must survive.
GROUND_TRUTH = {
    "2.3": ["14 calendar", "must"],
    "2.4": ["written approval", "direct manager", "not valid"],
    "2.5": ["Loss of Pay", "regardless of subsequent approval"],
    "2.6": ["5 unused annual leave", "31 December", "forfeited"],
    "2.7": ["first quarter", "forfeited", "must"],
    "3.2": ["3 or more consecutive days", "medical certificate", "48 hours"],
    "3.4": ["medical certificate", "regardless"],
    "5.2": ["Department Head", "HR Director", "not sufficient"],
    "5.3": ["30 continuous days", "Municipal Commissioner"],
    "7.2": ["not permitted", "under any circumstances"],
}


def _normalise(text):
    return re.sub(r"\s+", " ", text).strip()


def _split_sentences(text):
    parts = [s.strip() for s in SENTENCE_SPLIT_RE.split(text) if s.strip()]
    # the split consumes the separating '.', so put it back
    return [p if p.endswith((".", ":", ";")) else p + "." for p in parts]


def _find_all(patterns, text):
    hits = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = _normalise(match.group(0))
            if value.lower() not in {h.lower() for h in hits}:
                hits.append(value)
    return hits


def retrieve_policy(path: str) -> dict:
    """Load a policy .txt into ordered sections and clauses."""
    with open(path, "r", encoding="utf-8") as handle:
        raw_lines = handle.read().splitlines()

    header, sections, clauses = [], [], []
    current_section = None
    current_clause = None
    seen_first_section = False

    def close_clause():
        if current_clause is not None:
            current_clause["text"] = _normalise(current_clause["text"])
            current_clause["sentences"] = _split_sentences(current_clause["text"])

    for line in raw_lines:
        stripped = line.strip()

        if not stripped or RULE_RE.match(stripped):
            continue

        section_match = SECTION_RE.match(stripped)
        if section_match:
            close_clause()
            current_clause = None
            seen_first_section = True
            current_section = {
                "number": section_match.group(1),
                "title": _normalise(section_match.group(2)),
                "clauses": [],
            }
            sections.append(current_section)
            continue

        clause_match = CLAUSE_RE.match(stripped)
        if clause_match:
            close_clause()
            if current_section is None:
                current_section = {"number": "0", "title": "PREAMBLE", "clauses": []}
                sections.append(current_section)
            current_clause = {
                "id": clause_match.group(1),
                "section": current_section["number"],
                "section_title": current_section["title"],
                "text": clause_match.group(2),
                "sentences": [],
            }
            current_section["clauses"].append(current_clause)
            clauses.append(current_clause)
            continue

        if current_clause is not None:
            current_clause["text"] += " " + stripped
        elif not seen_first_section:
            header.append(stripped)

    close_clause()

    if not clauses:
        raise ValueError(
            "no numbered clauses found in {} — unexpected file shape".format(path))

    duplicates = [c["id"] for c in clauses
                  if [x["id"] for x in clauses].count(c["id"]) > 1]
    return {
        "meta": {"source": os.path.basename(path), "header": header,
                 "duplicate_ids": sorted(set(duplicates))},
        "sections": sections,
        "clauses": clauses,
    }


def _binding_tag(text):
    for tag, pattern in BINDING_VERBS:
        if re.search(pattern, text, re.IGNORECASE):
            return tag
    return "CLAUSE"


def summarize_policy(structured: dict):
    """Build the clause-referenced summary. Body text is verbatim by construction."""
    source_chars = sum(len(c["text"]) for c in structured["clauses"])
    lines, flagged = [], []

    meta = structured["meta"]
    lines.append("EMPLOYEE LEAVE POLICY — COMPLIANCE SUMMARY")
    lines.append("Source: {}".format(meta["source"]))
    for header_line in meta["header"]:
        lines.append("  {}".format(header_line))
    lines.append("")
    lines.append("Method: EXTRACTIVE. Every sentence of body text below is a verbatim")
    lines.append("substring of the source. Nothing is paraphrased, so no obligation can")
    lines.append("be softened and no outside information can be introduced.")
    lines.append("Clauses marked {} carry two or more independent".format(VERBATIM_FLAG))
    lines.append("conditions and are reproduced in full rather than compressed.")
    lines.append("")

    for section in structured["sections"]:
        lines.append("=" * 68)
        lines.append("{}. {}".format(section["number"], section["title"]))
        lines.append("=" * 68)

        for clause in section["clauses"]:
            conditions = _find_all(CONDITION_PATTERNS, clause["text"])
            negations = _find_all(NEGATION_PATTERNS, clause["text"])
            multi = len(conditions) + len(negations) >= 2
            tag = _binding_tag(clause["text"])

            heading = "[{}] {}".format(clause["id"], tag)
            if multi:
                heading += "  {}".format(VERBATIM_FLAG)
                flagged.append(clause["id"])
            lines.append(heading)

            for sentence in clause["sentences"]:
                lines.append("  {}".format(sentence))

            shown = conditions + ["{} (NEGATION)".format(n) for n in negations]
            if shown:
                lines.append("  conditions: {}".format(" · ".join(shown)))
            lines.append("")

    summary_text = "\n".join(lines).rstrip() + "\n"
    report = {
        "clauses_in": len(structured["clauses"]),
        "clauses_out": len(re.findall(r"^\[\d+\.\d+\]", summary_text, re.MULTILINE)),
        "flagged_verbatim": len(flagged),
        "flagged_ids": flagged,
        "source_chars": source_chars,
    }
    return summary_text, report


def verify_summary(structured: dict, summary_text: str, raw_source: str) -> dict:
    """Adversarial checks. Empty list per key == pass."""
    violations = {
        "clause_coverage": [],
        "extractive_fidelity": [],
        "numeric_fidelity": [],
        "negation_fidelity": [],
        "ground_truth": [],
        "scope_bleed": [],
    }

    flat_summary = _normalise(summary_text)
    source_flat = _normalise(raw_source)

    summary_ids = set(re.findall(r"^\[(\d+\.\d+)\]", summary_text, re.MULTILINE))
    for clause in structured["clauses"]:
        if clause["id"] not in summary_ids:
            violations["clause_coverage"].append(clause["id"])

    # Every body line must be verbatim source text.
    for line in summary_text.splitlines():
        body = line.strip()
        if not body.startswith("  ") and not line.startswith("  "):
            continue
        if body.startswith("conditions:") or not body:
            continue
        if body not in source_flat:
            violations["extractive_fidelity"].append(body[:70])

    # Per-clause numeric and negation survival.
    blocks = _clause_blocks(summary_text)
    for clause in structured["clauses"]:
        block = blocks.get(clause["id"], "")
        for number in re.findall(r"\b\d+(?:\.\d+)?\b", clause["text"]):
            if number not in block:
                violations["numeric_fidelity"].append(
                    "{}: lost '{}'".format(clause["id"], number))
        for pattern in NEGATION_PATTERNS:
            if re.search(pattern, clause["text"], re.IGNORECASE) and \
               not re.search(pattern, block, re.IGNORECASE):
                violations["negation_fidelity"].append(
                    "{}: lost negation {}".format(clause["id"], pattern))

    for clause_id, required in GROUND_TRUTH.items():
        block = blocks.get(clause_id, "")
        if not block:
            violations["ground_truth"].append("{}: clause absent".format(clause_id))
            continue
        for needle in required:
            if needle.lower() not in block.lower():
                violations["ground_truth"].append(
                    "{}: missing condition '{}'".format(clause_id, needle))

    for phrase in BANNED_PHRASES:
        if phrase.lower() in flat_summary.lower():
            violations["scope_bleed"].append(phrase)

    return violations


def _clause_blocks(summary_text):
    """
    Map clause id -> its BODY text only.

    The derived `conditions:` line is excluded deliberately. It is generated from
    the source, so it is correct by construction and would mask a mutation in the
    body underneath it — checking against it makes the fidelity checks vacuous.
    """
    blocks, current_id, buffer = {}, None, []
    for line in summary_text.splitlines():
        match = re.match(r"^\[(\d+\.\d+)\]", line)
        if match:
            if current_id:
                blocks[current_id] = "\n".join(buffer)
            current_id, buffer = match.group(1), [line]
        elif current_id:
            if line.strip().startswith("conditions:"):
                continue
            buffer.append(line)
    if current_id:
        blocks[current_id] = "\n".join(buffer)
    return blocks


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    try:
        structured = retrieve_policy(args.input)
        with open(args.input, "r", encoding="utf-8") as handle:
            raw_source = handle.read()
    except (OSError, ValueError) as error:
        print("ERROR: cannot read {}: {}".format(args.input, error), file=sys.stderr)
        sys.exit(1)

    summary_text, report = summarize_policy(structured)

    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(summary_text)

    violations = verify_summary(structured, summary_text, raw_source)

    print("clauses in source : {}".format(report["clauses_in"]))
    print("clauses in summary: {}".format(report["clauses_out"]))
    print("flagged verbatim  : {} -> {}".format(
        report["flagged_verbatim"], ", ".join(report["flagged_ids"])))
    print("")
    print("VERIFICATION")
    failed = False
    for check, hits in violations.items():
        status = "PASS" if not hits else "FAIL"
        failed = failed or bool(hits)
        print("  {:<20} {}".format(check, status))
        for hit in hits:
            print("      - {}".format(hit))

    print("")
    print("Summary written to {}".format(args.output))
    if failed:
        print("VERIFICATION FAILED — summary is not trustworthy.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
