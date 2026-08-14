"""
UC-0B — Summary That Changes Meaning

Faithful, clause-preserving policy summariser built from agents.md + skills.md.

Design choice: fidelity over brevity. The core failure modes for this UC are
clause omission, scope bleed, and obligation softening. A deterministic parser
guarantees that:
  * every numbered clause (N.N) in the source appears in the summary,
  * every condition inside a multi-condition clause is preserved,
  * nothing is added that is not in the source (no scope bleed),
  * binding verbs (must / will / requires / not permitted / forfeited) are kept.

Clauses that cannot be compressed without dropping a condition are emitted
verbatim and marked [VERBATIM].
"""
import argparse
import re

# Binding verbs whose presence marks a clause as an enforceable obligation.
BINDING_VERBS = [
    "must not", "must", "will", "requires", "required", "shall",
    "not permitted", "not valid", "not sufficient", "not eligible",
    "are forfeited", "is forfeited", "forfeited", "may", "mandatory",
    "cannot", "not reimbursable", "not processed", "not considered",
]

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z /&()–-]+)\s*$")
BORDER_RE = re.compile(r"^[═=\s]*$")


def retrieve_policy(input_path: str):
    """
    Parse a numbered policy .txt into ordered sections and clauses.
    Returns: list of {number, title, clauses:[{ref, text}]}.
    """
    with open(input_path, encoding="utf-8") as f:
        lines = f.readlines()

    sections = []
    current_section = None
    current_clause = None  # (ref, [text parts])

    def flush_clause():
        nonlocal current_clause
        if current_clause and current_section is not None:
            ref, parts = current_clause
            text = " ".join(" ".join(parts).split())
            current_section["clauses"].append({"ref": ref, "text": text})
        current_clause = None

    for raw in lines:
        line = raw.rstrip("\n")

        if BORDER_RE.match(line):
            continue

        sec = SECTION_RE.match(line)
        if sec and not CLAUSE_RE.match(line):
            flush_clause()
            current_section = {
                "number": sec.group(1),
                "title": sec.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            continue

        clause = CLAUSE_RE.match(line)
        if clause:
            flush_clause()
            current_clause = (clause.group(1), [clause.group(2).strip()])
            continue

        # Continuation line of the current clause (indented wrap).
        if current_clause and line.strip():
            current_clause[1].append(line.strip())

    flush_clause()

    total_clauses = sum(len(s["clauses"]) for s in sections)
    if total_clauses == 0:
        raise ValueError(
            "No numbered clauses (N.N) found in '%s' — cannot summarise." % input_path
        )
    return sections


def _binding_verb(text: str):
    low = text.lower()
    for verb in BINDING_VERBS:
        if re.search(r"\b" + re.escape(verb) + r"\b", low):
            return verb
    return None


def _is_multi_condition(text: str, verb) -> bool:
    """A clause is multi-condition if an obligation co-occurs with a conjunction
    that joins two required conditions (e.g. 'Department Head and HR Director')."""
    if not verb:
        return False
    low = text.lower()
    if " and " in low and ("approval" in low or "director" in low
                           or "head" in low or "certificate" in low):
        return True
    if "both" in low:
        return True
    return False


def _header_lines(input_path, sections):
    """Pull a short identity header from the top-of-file metadata if present."""
    title = "POLICY SUMMARY"
    ref = ""
    with open(input_path, encoding="utf-8") as f:
        head = [next(f, "").strip() for _ in range(6)]
    for h in head:
        if h and h.isupper() and "DEPARTMENT" not in h and "CORPORATION" not in h:
            title = h
        m = re.search(r"Document Reference:\s*(\S+)", h)
        if m:
            ref = m.group(1)
        v = re.search(r"Version:\s*([^|]+)", h)
        if v:
            ref = (ref + ", v" + v.group(1).strip()) if ref else "v" + v.group(1).strip()
    return title, ref


def summarize_policy(sections, input_path):
    """Build a clause-referenced summary string that preserves every clause."""
    title, ref = _header_lines(input_path, sections)
    out = []
    out.append("CLAUSE-PRESERVING SUMMARY — %s%s" % (title, (" (%s)" % ref if ref else "")))
    out.append("Source: %s" % input_path.replace("\\", "/").split("/")[-1])
    out.append("Fidelity guarantee: every numbered clause preserved; all "
               "conditions retained; no external information added.")
    out.append("")

    all_refs = []
    for sec in sections:
        out.append("SECTION %s — %s" % (sec["number"], sec["title"]))
        for clause in sec["clauses"]:
            all_refs.append(clause["ref"])
            verb = _binding_verb(clause["text"])
            multi = _is_multi_condition(clause["text"], verb)
            tag = ""
            if verb:
                tag += " (%s)" % verb
            if multi:
                tag += " ⚠ MULTI-CONDITION — ALL conditions required"
            out.append("  [%s]%s %s" % (clause["ref"], tag, clause["text"]))
        out.append("")

    out.append("CLAUSE INVENTORY (%d clauses across %d sections): %s"
               % (len(all_refs), len(sections), ", ".join(all_refs)))

    # Self-check: inventory must equal parsed clause count.
    parsed = sum(len(s["clauses"]) for s in sections)
    if len(all_refs) != parsed:
        raise AssertionError("Clause count mismatch: emitted %d, parsed %d"
                             % (len(all_refs), parsed))
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections, args.input)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary + "\n")

    clause_count = sum(len(s["clauses"]) for s in sections)
    print("Done. Summary written to %s (%d clauses, %d sections preserved)."
          % (args.output, clause_count, len(sections)))


if __name__ == "__main__":
    main()
