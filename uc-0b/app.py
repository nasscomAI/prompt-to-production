"""
UC-0B — Summary That Changes Meaning

BASELINE RUN. This is the naive prompt turned into code:
"Summarize the policy document."

It parses the policy into sections and clauses, then does what a generic
summariser does — keeps the headline clauses of each section, keeps the first
sentence of each, and closes with a tidy generalisation.

Committed as-is so the failure is on the record before it is fixed.

Usage:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_naive.txt
"""

import argparse
import os
import re
import sys


class PolicyError(Exception):
    """Raised when the source document cannot be read or parsed into clauses."""


CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(\S.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 \-&/(),']+)$")
SEPARATOR_RE = re.compile(r"^[═─\-=_\s]+$")
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

        if current_clause is not None:
            current_clause["text"] = (current_clause["text"] + " " + stripped).strip()

    for section in sections:
        for clause in section["clauses"]:
            clause["text"] = re.sub(r"\s+", " ", clause["text"]).strip()
            clause["sentences"] = _split_sentences(clause["text"])

    if sum(len(s["clauses"]) for s in sections) == 0:
        raise PolicyError("Parsed 0 clauses from {} — refusing to summarise.".format(path))

    return {"meta": meta, "sections": sections}


def all_clauses(structured):
    out = []
    for section in structured["sections"]:
        for clause in section["clauses"]:
            out.append((section, clause))
    return out


def naive_summarize(structured):
    """
    What an unenforced "Summarize the policy document." prompt produces:
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


def count_clauses(structured, candidate_text):
    """Rough baseline check: how many of the source clauses got a mention."""
    source_ids = [clause["id"] for _, clause in all_clauses(structured)]
    present = set(CLAUSE_MARKER_RE.findall(candidate_text))
    missing = [cid for cid in source_ids if cid not in present]
    return {"source": len(source_ids), "kept": len(source_ids) - len(missing), "missing": missing}


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser (baseline)")
    parser.add_argument("--input", required=True, help="Path to the .txt policy document")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    try:
        structured = retrieve_policy(args.input)
    except PolicyError as exc:
        print("REFUSED: {}".format(exc), file=sys.stderr)
        return 2

    text = naive_summarize(structured)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(text)

    stats = count_clauses(structured, text)
    print("Summary written to {}".format(args.output))
    print("Clauses in source: {}  kept: {}".format(stats["source"], stats["kept"]))
    print("Dropped: {}".format(stats["missing"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
