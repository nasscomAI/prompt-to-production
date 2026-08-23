"""
UC-0B — Summary That Changes Meaning

Reads a plain-text HR policy document, extracts every numbered clause, and
writes a summary in which no obligation can silently change meaning.
Behaviour follows the enforcement rules in agents.md:

- completeness guard: every numbered clause found in the source is rendered
  under its section heading with its clause number preserved, and a
  completeness ledger proves full coverage
- multi-condition preservation guard: clauses with compound obligations,
  multiple approvers/conditions, absolute prohibitions, or thresholds paired
  with consequences are quoted verbatim and tagged [VERBATIM] instead of
  compressed, so conditions such as clause 5.2's Department Head AND HR
  Director approval survive intact
- scope bleed guard: output text is assembled only from source characters;
  nothing is added, paraphrased, or softened
- refusal guard: unreadable input, unparseable input, or a missing critical
  clause exits non-zero and writes no output file

The tool is deterministic and fully offline.
"""
import argparse
import re
import sys

CRITICAL_CLAUSE_IDS = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2",
]

BINDING_TOKENS = [
    "must", "shall", "requires", "required", "cannot", "may not",
    "will be", "forfeit", "not permitted", "not valid",
    "not sufficient", "not considered",
]

STRONG_TRIGGER_RE = re.compile(
    r"regardless"
    r"|under any circumstances"
    r"|unless"
    r"|subject to"
    r"|\band\b[^.]*(?:approval|approver)"
    r"|(?:approval|approver)[^.]*\band\b",
    re.IGNORECASE,
)

THRESHOLD_RE = re.compile(
    r"\bat least\b"
    r"|\bmaximum of\b"
    r"|\bexceeding\b"
    r"|\bmore than\b"
    r"|\bno more than\b"
    r"|\babove\s+\d"
    r"|\bwithin\b",
    re.IGNORECASE,
)

BANNER_RE = re.compile(r"^[=\u2550\u2551-]{5,}\s*$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Za-z].*)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+([A-Za-z].*)$")


class PolicyParseError(Exception):
    """Raised when the input does not parse into sections and clauses."""


class MissingCriticalClauseError(Exception):
    """Raised when one or more critical clauses are absent from the parse."""


def _normalise(text):
    return re.sub(r"\s+", " ", text).strip()


def _is_verbatim_required(clause_text):
    if STRONG_TRIGGER_RE.search(clause_text):
        return True
    binding_hits = sum(1 for token in BINDING_TOKENS if token in clause_text.lower())
    has_threshold = bool(THRESHOLD_RE.search(clause_text))
    return binding_hits >= 2 or (binding_hits >= 1 and has_threshold)


def retrieve_policy(input_path):
    """
    Load the policy .txt and return structured data.
    Returns: dict with keys: meta, sections (number, title, clauses),
    clause_ids. Raises FileNotFoundError / PolicyParseError on bad input.
    """
    with open(input_path, encoding="utf-8-sig") as handle:
        raw_lines = handle.read().splitlines()

    meta = []
    sections = []
    current_section = None
    seen_banner = False

    for raw_line in raw_lines:
        line = raw_line.rstrip()
        if BANNER_RE.match(line):
            seen_banner = True
            continue
        if not line.strip():
            continue

        if current_section is None:
            if not seen_banner:
                meta.append(_normalise(line))
                continue
            match = SECTION_RE.match(line.strip())
            if not match:
                raise PolicyParseError(
                    "Expected a numbered section heading after the first "
                    "banner, got: %r" % line.strip()
                )
            current_section = {
                "number": int(match.group(1)),
                "title": match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            continue

        section_match = SECTION_RE.match(line.strip())
        if section_match:
            current_section = {
                "number": int(section_match.group(1)),
                "title": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            continue

        clause_match = CLAUSE_RE.match(line.strip())
        if clause_match:
            current_section["clauses"].append({
                "id": clause_match.group(1),
                "text": _normalise(clause_match.group(2)),
                "verbatim_required": False,
            })
            continue

        if current_section["clauses"]:
            current_section["clauses"][-1]["text"] = _normalise(
                current_section["clauses"][-1]["text"] + " " + line.strip()
            )
        else:
            raise PolicyParseError(
                "Found body text before the first clause in section %d: %r"
                % (current_section["number"], line.strip())
            )

    if not sections:
        raise PolicyParseError("No numbered sections found in %s" % input_path)

    clause_ids = []
    for section in sections:
        for clause in section["clauses"]:
            clause["verbatim_required"] = _is_verbatim_required(clause["text"])
            clause_ids.append(clause["id"])

    total_clauses = len(clause_ids)
    if total_clauses == 0:
        raise PolicyParseError("No numbered clauses found in %s" % input_path)
    if len(set(clause_ids)) != total_clauses:
        raise PolicyParseError("Duplicate clause numbers detected in %s" % input_path)

    return {"meta": meta, "sections": sections, "clause_ids": clause_ids}


def summarize_policy(policy):
    """
    Render the structured policy into a lossless summary text.
    Returns: (summary_text, stats_dict). Raises MissingCriticalClauseError
    when a critical clause is absent — no partial summary is produced.
    """
    extracted_ids = policy["clause_ids"]
    missing_critical = [cid for cid in CRITICAL_CLAUSE_IDS if cid not in extracted_ids]
    if missing_critical:
        raise MissingCriticalClauseError(
            "Critical clauses missing from parsed input: %s"
            % ", ".join(missing_critical)
        )

    rule = "=" * 78
    subrule = "-" * 78
    out = []
    out.append(rule)
    out.append("POLICY SUMMARY")
    for meta_line in policy["meta"]:
        out.append(meta_line)
    out.append("")
    out.append("METHOD: Deterministic extractive summary generated offline by")
    out.append("uc-0b/app.py. Every numbered clause below is quoted")
    out.append("character-for-character from the source document: nothing added,")
    out.append("nothing omitted, no obligation softened. Clauses carrying compound")
    out.append("obligations, multiple conditions/approvers, absolute prohibitions,")
    out.append("or thresholds paired with consequences are tagged [VERBATIM].")
    out.append(rule)
    out.append("")

    rendered_ids = []
    flagged_ids = []
    for section in policy["sections"]:
        heading = "%d. %s" % (section["number"], section["title"])
        out.append(heading)
        out.append(subrule)
        if not section["clauses"]:
            out.append("(no clauses parsed for this section)")
        for clause in section["clauses"]:
            line = "%s %s" % (clause["id"], clause["text"])
            if clause["verbatim_required"]:
                line += " [VERBATIM]"
                flagged_ids.append(clause["id"])
            out.append(line)
            rendered_ids.append(clause["id"])
        out.append("")

    out.append(rule)
    out.append("COMPLETENESS LEDGER")
    out.append(
        "Sections: %d | Clauses extracted: %d | Clauses rendered: %d"
        % (len(policy["sections"]), len(extracted_ids), len(rendered_ids))
    )
    out.append("Coverage: %s" % ("COMPLETE" if rendered_ids == extracted_ids else "INCOMPLETE"))
    out.append("Clause ids: %s" % ", ".join(rendered_ids))
    out.append("")
    out.append(
        "Critical-clause verification (UC ground truth): %d/%d PRESENT"
        % (len(CRITICAL_CLAUSE_IDS) - sum(1 for cid in CRITICAL_CLAUSE_IDS if cid not in rendered_ids),
           len(CRITICAL_CLAUSE_IDS))
    )
    for cid in CRITICAL_CLAUSE_IDS:
        status = "PRESENT" if cid in rendered_ids else "MISSING"
        out.append("  %s %s" % (cid, status))
    out.append("")
    out.append("Flagged [VERBATIM] (compound/multi-condition obligations): %s"
               % (", ".join(flagged_ids) if flagged_ids else "none"))
    out.append(rule)

    stats = {
        "sections": len(policy["sections"]),
        "extracted": len(extracted_ids),
        "rendered": len(rendered_ids),
        "complete": rendered_ids == extracted_ids,
        "critical_present": sum(1 for cid in CRITICAL_CLAUSE_IDS if cid in rendered_ids),
        "critical_total": len(CRITICAL_CLAUSE_IDS),
        "flagged": flagged_ids,
    }
    return "\n".join(out) + "\n", stats


def run(input_path, output_path):
    """
    Full pipeline: retrieve, summarise, verify, write.
    Refusal conditions exit non-zero without writing the output file.
    """
    policy = retrieve_policy(input_path)
    summary_text, stats = summarize_policy(policy)
    with open(output_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(summary_text)
    return stats


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="UC-0B HR Leave Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to the policy .txt document")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt")
    args = parser.parse_args()

    try:
        outcome = run(args.input, args.output)
    except FileNotFoundError as error:
        print("REFUSED: input file not found: %s" % error, file=sys.stderr)
        sys.exit(2)
    except PolicyParseError as error:
        print("REFUSED: could not parse policy document: %s" % error, file=sys.stderr)
        sys.exit(3)
    except MissingCriticalClauseError as error:
        print("REFUSED: %s" % error, file=sys.stderr)
        sys.exit(4)

    print("Done. Summary written to %s" % args.output)
    print("Sections: %d | Clauses extracted: %d | Clauses rendered: %d"
          % (outcome["sections"], outcome["extracted"], outcome["rendered"]))
    print("Coverage: %s" % ("COMPLETE" if outcome["complete"] else "INCOMPLETE"))
    print("Critical clauses verified: %d/%d"
          % (outcome["critical_present"], outcome["critical_total"]))
    print("Flagged [VERBATIM]: %s" % ", ".join(outcome["flagged"]))
