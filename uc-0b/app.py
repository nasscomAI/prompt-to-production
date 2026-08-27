"""
UC-0B — Summary That Changes Meaning

Built with the RICE -> agents.md -> skills.md -> CRAFT workflow.

The premise of this UC is that a fluent summary can quietly change what a
policy requires. So this summariser does not trust itself: it compresses a
clause only when every material token survives, quotes the clause verbatim
when they do not, and then audits its own output against the source before
declaring the result usable.

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt

Compare against the unguarded baseline:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output naive_summary.txt --mode naive
"""
import argparse
import os
import re
import sys

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 ,\-/&()]+)\s*$")
CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
RULE_RE = re.compile(r"^[═=\-_]{5,}\s*$")

# --- Enforcement rule 4: binding verbs carry the modal force of the clause ---
BINDING_VERBS = [
    "must not", "must", "will not", "will", "requires", "required", "shall",
    "cannot", "not permitted", "not valid", "not sufficient", "not eligible",
    "not reimbursable", "are forfeited", "forfeited", "may", "entitled",
    "not apply", "not considered", "not processed", "not accepted",
]

# --- Enforcement rule 3: scope-bleed phrases, checked by exact match --------
BANNED_PHRASES = [
    "as is standard practice", "typically", "generally", "usually",
    "in most cases", "it is common practice", "employees are generally expected to",
    "industry standard", "best practice", "normally", "as a rule of thumb",
    "it is understood", "commonly", "in practice", "as expected",
    "standard procedure",
]

# Words the renderer itself is allowed to introduce. Anything outside this set
# and outside the source vocabulary counts as scope bleed (enforcement rule 3).
STRUCTURAL_WORDS = set("""
summary source document mode generated clause clauses section sections
inventory fidelity audit at a glance full verbatim compressed critical
obligations obligation result passed failed check checks total in of the
and or for not no yes none tokens token dropped missing banned phrase phrases
binding verb verbs softened line lines number numbers count counts
all present absent this file was by uc app py enforced naive baseline
every rendered material preserved reason compression risk meaning loss
policy summariser run output see below above n a numbered
""".split())


def retrieve_policy(path):
    """Load a .txt policy file into ordered sections and numbered clauses."""
    if not os.path.isfile(path):
        raise SystemExit("ERROR: policy file not found: %s" % path)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw_lines = handle.read().splitlines()
    except OSError as exc:
        raise SystemExit("ERROR: cannot read %s (%s)" % (path, exc))

    title_lines = []
    sections = []
    clauses = []
    current_section = None
    current_clause = None

    def close_clause():
        if current_clause is not None:
            text = re.sub(r"\s+", " ", " ".join(current_clause["parts"])).strip()
            current_clause["text"] = text or "(no text parsed)"
            del current_clause["parts"]
            clauses.append(current_clause)
            if current_section is not None:
                current_section["clauses"].append(current_clause)

    for line in raw_lines:
        if RULE_RE.match(line):
            continue
        if not line.strip():
            continue

        section_match = SECTION_RE.match(line.strip())
        clause_match = CLAUSE_RE.match(line)

        if clause_match:
            close_clause()
            current_clause = {
                "number": clause_match.group(1),
                "section": current_section["number"] if current_section else "0",
                "parts": [clause_match.group(2)],
            }
        elif section_match:
            close_clause()
            current_clause = None
            current_section = {
                "number": section_match.group(1),
                "heading": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
        elif current_clause is not None and line.startswith(" "):
            current_clause["parts"].append(line.strip())
        elif current_section is None:
            title_lines.append(line.strip())

    close_clause()

    if not clauses:
        raise SystemExit(
            "ERROR: no numbered clauses (N.N) parsed from %s — refusing to "
            "render an empty summary that would pass a completeness check "
            "trivially." % path
        )

    seen = {}
    duplicates = []
    for clause in clauses:
        seen[clause["number"]] = seen.get(clause["number"], 0) + 1
        if seen[clause["number"]] > 1:
            duplicates.append(clause["number"])

    return {
        "title": title_lines,
        "sections": sections,
        "clauses": clauses,
        "clause_count": len(clauses),
        "duplicates": duplicates,
    }


def material_tokens(text):
    """Tokens whose loss would change what the clause requires.

    Digit groups (14, 5, 31, 48), acronyms (LOP, LWP, HR), capitalised role
    and form names (Department Head, HR Director, Form HR-L1, December), and
    binding verbs. Enforcement rule 2 turns on this set.
    """
    tokens = set()
    tokens.update(re.findall(r"\d+", text))
    tokens.update(re.findall(r"\b[A-Z]{2,}(?:-[A-Z0-9]+)*\b", text))
    # Capitalised words that are not merely the first word of a sentence.
    for match in re.finditer(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-z]{2,})\b", text):
        tokens.add(match.group(1))
    for verb in BINDING_VERBS:
        if re.search(r"(?<!\w)" + re.escape(verb) + r"(?!\w)", text, re.I):
            tokens.add(verb.lower())
    return tokens


def binding_verbs_in(text):
    found = []
    for verb in BINDING_VERBS:
        if re.search(r"(?<!\w)" + re.escape(verb) + r"(?!\w)", text, re.I):
            found.append(verb)
    return found


def compress_clause(text):
    """Attempt a shorter rendering by dropping the leading subject phrase.

    Compression stops at the first binding verb, so the obligation and every
    condition after it are retained. The caller still verifies the result and
    discards it if any material token was lost.
    """
    best = None
    for verb in sorted(BINDING_VERBS, key=len, reverse=True):
        match = re.search(r"(?<!\w)" + re.escape(verb) + r"(?!\w)", text, re.I)
        if match and (best is None or match.start() < best):
            best = match.start()
    if best is None or best == 0:
        return text
    candidate = text[best:].strip()
    # Only worth it if it actually saves something meaningful.
    if len(candidate) < len(text) * 0.55:
        return text
    return candidate


def render_clause(clause):
    """Return (line, tag, dropped_tokens) for one clause."""
    source = clause["text"]
    candidate = compress_clause(source)
    dropped = material_tokens(source) - material_tokens(candidate)
    if candidate == source:
        return source, "VERBATIM", set()
    if dropped:
        # Enforcement rule 5: refuse to compress, quote instead.
        return source, "VERBATIM", dropped
    return candidate, "compressed", set()


def naive_summarize(policy):
    """The unguarded baseline: one line per section, binding verbs softened.

    This is a real naive summarisation strategy -- take the first clause of
    each section and smooth the language -- not a mock of one. It exists so
    the failure modes in the UC-0B README can be observed and measured rather
    than assumed.
    """
    lines = []
    for section in policy["sections"]:
        if not section["clauses"]:
            continue
        first = section["clauses"][0]["text"]
        softened = first
        for hard, soft in (("must not", "should avoid"), ("must", "should"),
                           ("requires", "may require"),
                           ("cannot", "is not usually able to"),
                           ("will be recorded", "is generally recorded"),
                           ("is not permitted", "is generally discouraged")):
            softened = re.sub(r"(?<!\w)" + hard + r"(?!\w)", soft, softened,
                              flags=re.I)
        lines.append("- %s: %s" % (section["heading"].title(), softened))
    lines.append("")
    lines.append("Employees are generally expected to follow these rules as is "
                 "standard practice in most cases.")
    return "\n".join(lines)


CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4",
                    "5.2", "5.3", "7.2"]


def summarize_policy(policy, mode="enforced"):
    """Produce the summary text and the audit dict."""
    audit = {
        "mode": mode,
        "source_clause_count": policy["clause_count"],
        "rendered_clause_count": 0,
        "missing_clauses": [],
        "missing_critical": [],
        "condition_drops": {},
        "banned_phrases": [],
        "softened_verbs": [],
        "scope_bleed_words": [],
        "duplicates": policy["duplicates"],
        "passed": True,
    }

    source_text = " ".join(c["text"] for c in policy["clauses"])
    source_vocab = set(w.lower() for w in re.findall(r"[A-Za-z]+", source_text))
    source_vocab.update(w.lower() for line in policy["title"]
                        for w in re.findall(r"[A-Za-z]+", line))
    # Section headings are source content too. Omitting them made the audit
    # report the document's own words ("PURPOSE", "SCOPE") as scope bleed.
    source_vocab.update(w.lower() for section in policy["sections"]
                        for w in re.findall(r"[A-Za-z]+", section["heading"]))

    if mode == "naive":
        body = naive_summarize(policy)
        rendered_numbers = set()
    else:
        out = []
        out.append("AT A GLANCE — CRITICAL OBLIGATIONS")
        out.append("")
        by_number = {c["number"]: c for c in policy["clauses"]}
        for number in CRITICAL_CLAUSES:
            clause = by_number.get(number)
            if clause is None:
                continue
            line, tag, _ = render_clause(clause)
            out.append("  %s  %s" % (number, line))
        out.append("")
        out.append("FULL CLAUSE INVENTORY — every numbered clause in the source")
        out.append("")
        rendered_numbers = set()
        for section in policy["sections"]:
            out.append("SECTION %s — %s" % (section["number"],
                                            section["heading"]))
            for clause in section["clauses"]:
                line, tag, dropped = render_clause(clause)
                rendered_numbers.add(clause["number"])
                if dropped:
                    audit["condition_drops"][clause["number"]] = sorted(dropped)
                out.append("  %-5s [%s] %s" % (clause["number"], tag, line))
                # Enforcement rule 4: binding verbs must survive.
                src_verbs = set(v.lower() for v in
                                binding_verbs_in(clause["text"]))
                out_verbs = set(v.lower() for v in binding_verbs_in(line))
                lost = src_verbs - out_verbs
                if lost:
                    audit["softened_verbs"].append(
                        "%s lost %s" % (clause["number"], sorted(lost)))
            out.append("")
        body = "\n".join(out)

    audit["rendered_clause_count"] = len(rendered_numbers)
    all_numbers = set(c["number"] for c in policy["clauses"])
    audit["missing_clauses"] = sorted(all_numbers - rendered_numbers,
                                      key=lambda n: [int(p) for p in n.split(".")])
    audit["missing_critical"] = [n for n in CRITICAL_CLAUSES
                                 if n in all_numbers and n not in rendered_numbers]

    lowered = body.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            audit["banned_phrases"].append(phrase)

    for word in set(w.lower() for w in re.findall(r"[A-Za-z]+", body)):
        if word not in source_vocab and word not in STRUCTURAL_WORDS:
            audit["scope_bleed_words"].append(word)
    audit["scope_bleed_words"].sort()

    # condition_drops records compressions that WOULD have lost a material
    # token and were therefore discarded in favour of the verbatim clause
    # (enforcement rule 5). That is the refusal rule succeeding, so it is
    # reported but must not fail the run -- only a drop that survived into the
    # output would, and by construction none can.
    audit["passed"] = not (audit["missing_clauses"] or audit["missing_critical"]
                           or audit["banned_phrases"]
                           or audit["softened_verbs"]
                           or audit["scope_bleed_words"])

    header = []
    header.append("=" * 72)
    for line in policy["title"]:
        header.append(line)
    header.append("=" * 72)
    header.append("SUMMARY MODE : %s" % mode)
    header.append("SOURCE       : %s" % policy.get("path", "(see --input)"))
    header.append("")

    footer = []
    footer.append("")
    footer.append("=" * 72)
    footer.append("FIDELITY AUDIT")
    footer.append("=" * 72)
    footer.append("  clauses in source        : %d" % audit["source_clause_count"])
    footer.append("  clauses in summary       : %d" % audit["rendered_clause_count"])
    footer.append("  missing clauses          : %s"
                  % (", ".join(audit["missing_clauses"]) or "none"))
    footer.append("  missing critical clauses : %s"
                  % (", ".join(audit["missing_critical"]) or "none"))
    if audit["condition_drops"]:
        footer.append("  condition drops caught   : %d clause(s) re-emitted "
                      "verbatim rather than compressed"
                      % len(audit["condition_drops"]))
        for number in sorted(audit["condition_drops"],
                             key=lambda n: [int(p) for p in n.split(".")]):
            footer.append("      %s would have lost: %s"
                          % (number, ", ".join(audit["condition_drops"][number])))
    else:
        footer.append("  condition drops caught   : none")
    footer.append("  banned hedge phrases     : %s"
                  % (", ".join(audit["banned_phrases"]) or "none"))
    footer.append("  softened binding verbs   : %s"
                  % ("; ".join(audit["softened_verbs"]) or "none"))
    footer.append("  scope-bleed words        : %s"
                  % (", ".join(audit["scope_bleed_words"]) or "none"))
    footer.append("  duplicate clause numbers : %s"
                  % (", ".join(audit["duplicates"]) or "none"))
    footer.append("")
    footer.append("  RESULT: %s" % ("PASS — every clause present, every "
                                    "material condition preserved."
                                    if audit["passed"] else
                                    "FAIL — see the discrepancies listed above. "
                                    "Do not rely on this summary."))
    footer.append("=" * 72)

    return "\n".join(header) + body + "\n".join(footer) + "\n", audit


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    parser.add_argument("--mode", default="enforced",
                        choices=["enforced", "naive"],
                        help="enforced applies agents.md rules; naive "
                             "reproduces the unguarded baseline for comparison")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    policy["path"] = args.input
    summary, audit = summarize_policy(policy, mode=args.mode)

    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(summary)

    print("Mode              : %s" % audit["mode"])
    print("Clauses in source : %d" % audit["source_clause_count"])
    print("Clauses in summary: %d" % audit["rendered_clause_count"])
    print("Missing clauses   : %s"
          % (", ".join(audit["missing_clauses"]) or "none"))
    print("Missing critical  : %s"
          % (", ".join(audit["missing_critical"]) or "none"))
    print("Condition drops   : %d caught and re-emitted verbatim"
          % len(audit["condition_drops"]))
    print("Banned phrases    : %s"
          % (", ".join(audit["banned_phrases"]) or "none"))
    print("Softened verbs    : %s"
          % ("; ".join(audit["softened_verbs"]) or "none"))
    print("Scope-bleed words : %s"
          % (", ".join(audit["scope_bleed_words"]) or "none"))
    print("RESULT            : %s" % ("PASS" if audit["passed"] else "FAIL"))
    print("Written to        : %s" % args.output)

    # Enforcement rule 6: a defective summary must not exit clean.
    if not audit["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
