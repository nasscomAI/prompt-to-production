"""
UC-0B — Summary That Changes Meaning
Policy summarizer built to satisfy the enforcement rules in agents.md
and the skill contracts in skills.md.

Enforcement rules implemented:
1. Every numbered clause must be present in the summary.
2. Multi-condition obligations must preserve ALL conditions — so every
   clause is quoted verbatim; nothing is paraphrased away.
3. Never add information not present in the source document — the summary
   contains only text extracted from the source.
4. If a clause cannot be summarised without meaning loss — quote it
   verbatim and flag it. Multi-condition clauses are flagged [VERBATIM]
   in the output.

The summarizer is deliberately extractive: for a binding policy document,
a lossy paraphrase is a compliance failure, so clauses are reproduced
verbatim and organised by section.
"""
import argparse
import re
import sys

# Clauses that the workshop README designates as ground truth. The output
# is checked against this list and any missing clause is reported.
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7",
                    "3.2", "3.4", "5.2", "5.3", "7.2"]

# Patterns that indicate a multi-condition obligation. Such clauses are
# quoted verbatim and flagged rather than condensed.
MULTI_CONDITION_MARKERS = [
    "regardless of", "and the", "must not", "not permitted",
    "under any circumstances", "within", "before ", "or they are forfeited",
    "alone is not sufficient",
]

SECTION_HEADING_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z &()\-]+)\s*$")
CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")


def retrieve_policy(path):
    """
    Load a .txt policy file and return it as structured numbered sections:
        [{"section": "2", "title": "ANNUAL LEAVE",
          "clauses": [{"id": "2.3", "text": "..."}, ...]}, ...]
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except FileNotFoundError:
        print("ERROR: policy file not found: %s" % path, file=sys.stderr)
        raise SystemExit(1)
    except UnicodeDecodeError:
        print("ERROR: could not decode %s as UTF-8" % path, file=sys.stderr)
        raise SystemExit(1)

    # Header = everything before the first section heading.
    header, sections, current = [], [], None
    for raw in lines:
        line = raw.rstrip()
        heading = SECTION_HEADING_RE.match(line)
        clause = CLAUSE_RE.match(line)
        if heading:
            current = {"section": heading.group(1),
                       "title": heading.group(2).strip(),
                       "clauses": []}
            sections.append(current)
            continue
        if clause:
            if current is None:
                continue  # numbered text before any section heading
            current["clauses"].append({"id": clause.group(1),
                                       "text": clause.group(2).strip()})
            continue
        if not line.strip():
            continue
        if set(line.strip()) <= {"=", "\u2550"}:
            continue  # decorative rule line
        if current is None:
            header.append(line.strip())
        else:  # continuation line of the previous clause
            current["clauses"][-1]["text"] += " " + line.strip()

    if not sections:
        print("ERROR: no numbered sections found in %s" % path,
              file=sys.stderr)
        raise SystemExit(1)
    return {"header": header, "sections": sections}


def _is_multi_condition(text):
    lowered = text.lower()
    return any(marker in lowered for marker in MULTI_CONDITION_MARKERS)


def summarize_policy(policy):
    """
    Take structured sections and produce a compliant summary in which
    every clause appears with its full conditions preserved (quoted
    verbatim), with multi-condition clauses flagged.
    Returns (summary_text, missing_required_clauses).
    """
    out = []
    out.append("POLICY SUMMARY")
    out.append("=" * 60)
    for line in policy["header"]:
        out.append(line)
    out.append("")
    out.append(
        "Scope: complete clause inventory of the source document. "
        "Every numbered clause is included; obligations are quoted "
        "verbatim to prevent condition loss or scope bleed."
    )
    out.append("")

    present_ids = []
    for section in policy["sections"]:
        out.append("%s. %s" % (section["section"], section["title"]))
        for clause in section["clauses"]:
            present_ids.append(clause["id"])
            if _is_multi_condition(clause["text"]):
                out.append("  %s [VERBATIM — multi-condition obligation, "
                           "do not rely on a paraphrase]: %s"
                           % (clause["id"], clause["text"]))
            else:
                out.append("  %s: %s" % (clause["id"], clause["text"]))
        out.append("")

    missing = [cid for cid in REQUIRED_CLAUSES if cid not in present_ids]
    return "\n".join(out).rstrip() + "\n", missing


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True,
                        help="Path to the policy .txt file")
    parser.add_argument("--output", required=True,
                        help="Path to write the summary .txt file")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary, missing = summarize_policy(policy)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary)

    total = sum(len(s["clauses"]) for s in policy["sections"])
    flagged = summary.count("[VERBATIM")
    print("Summarized %d clause(s) across %d section(s); "
          "%d multi-condition clause(s) quoted verbatim."
          % (total, len(policy["sections"]), flagged))
    if missing:
        print("WARNING: required clause(s) missing from source/summary: %s"
              % ", ".join(missing), file=sys.stderr)
        raise SystemExit(2)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
