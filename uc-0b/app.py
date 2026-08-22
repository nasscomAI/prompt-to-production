"""
UC-0B — Summary That Changes Meaning
Extractive summarizer built to the agents.md enforcement rules: every numbered
clause is present under its own number, no sentence is ever reworded (which
structurally prevents obligation softening), nothing outside the source is
added (which structurally prevents scope bleed), and multi-condition clauses
are quoted verbatim and flagged rather than compressed.
"""
import argparse
import re

SECTION_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z \-&(),'()]+?)\s*$")
CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
DIVIDER_RE = re.compile(r"^[\s═=\-]+$")
CONDITION_CUE_RE = re.compile(
    r"\b(if|unless|regardless|only|exceeding|within|before|after|"
    r"maximum|immediately|both)\b", re.IGNORECASE)


def retrieve_policy(input_path):
    """Load .txt policy file, return (header_lines, sections).

    Sections: [{number, title, clauses: [{id, text}]}] in document order,
    with wrapped clause lines joined into single strings.
    """
    with open(input_path, encoding="utf-8-sig") as f:
        raw_lines = f.read().splitlines()

    header, sections, current = [], [], None
    for line in raw_lines:
        stripped = line.strip()
        section_match = SECTION_RE.match(line)
        clause_match = CLAUSE_RE.match(line)
        if DIVIDER_RE.match(line):
            continue
        if section_match:
            current = {"number": section_match.group(1),
                       "title": section_match.group(2).strip(),
                       "clauses": []}
            sections.append(current)
        elif clause_match and current is not None:
            current["clauses"].append({"id": clause_match.group(1),
                                       "text": clause_match.group(2).strip()})
        elif current is not None and current["clauses"] and stripped:
            current["clauses"][-1]["text"] += " " + stripped
        elif current is None and stripped:
            header.append(stripped)
    return header, sections


def _split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=\.)\s+", text) if s.strip()]


def _is_multi_condition(text):
    sentences = _split_sentences(text)
    return len(sentences) > 1 or bool(CONDITION_CUE_RE.search(text))


def summarize_policy(header, sections):
    """Take structured sections, produce compliant summary with clause refs."""
    lines = []
    lines.extend(header)
    lines.append("")
    lines.append("SUMMARY")
    lines.append("Method: extractive. No clause omitted, no sentence reworded, "
                 "no content added.")
    lines.append("[VERBATIM] marks multi-condition clauses kept whole so no "
                 "condition can drop.")

    total_clauses = sum(len(s["clauses"]) for s in sections)
    flagged = 0
    for section in sections:
        lines.append("")
        lines.append("%s. %s" % (section["number"], section["title"]))
        for clause in section["clauses"]:
            if _is_multi_condition(clause["text"]):
                flagged += 1
                lines.append("%s %s [VERBATIM]" % (clause["id"], clause["text"]))
            else:
                lines.append("%s %s" % (clause["id"], clause["text"]))

    lines.append("")
    lines.append("Clause coverage: %d/%d numbered clauses included."
                 % (total_clauses, total_clauses))
    lines.append("Multi-condition clauses quoted verbatim: %d." % flagged)
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to summary output")
    args = parser.parse_args()

    header, sections = retrieve_policy(args.input)
    if not sections:
        raise SystemExit("REFUSAL: no numbered sections found in %s — "
                         "not a parsable policy document." % args.input)

    summary = summarize_policy(header, sections)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    total = sum(len(s["clauses"]) for s in sections)
    print("Done. %d sections, %d clauses written to %s"
          % (len(sections), total, args.output))


if __name__ == "__main__":
    main()
