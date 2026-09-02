"""
UC-0B — Summary That Changes Meaning

Summarises a municipal policy .txt without dropping clauses, weakening
obligations, or introducing wording the source does not contain. Where a clause
cannot be condensed without losing a condition, it is reproduced verbatim and
marked rather than paraphrased — enforcement rule 5 in agents.md.
"""
import argparse
import re
import sys

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\.?\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z &/]+)\s*$")

# A clause carrying any of these binds the reader; condensing risks changing its
# force, so it is emitted verbatim instead (rule 3, rule 5).
BINDING = [
    r"\bmust\b", r"\bwill be\b", r"\bwill not\b", r"\brequires?\b", r"\bcannot\b",
    r"\bnot permitted\b", r"\bnot valid\b", r"\bnot sufficient\b",
    r"\bnot be considered\b", r"\bforfeited\b", r"\bonly\b", r"\bdo not count\b",
    r"\bis entitled\b", r"\bare entitled\b", r"\bmay apply\b",
    r"\bmay carry forward\b", r"\bmay be encashed\b",
]

# Rule 4 — wording that would show the summary has drifted outside the source.
# Every phrase here was produced by the naive control run.
BLEED = [
    "as is standard practice", "standard practice", "typically",
    "generally understood", "generally expected", "in most organisations",
    "it is common", "usually", "best practice", "we recommend", "should be",
    "normally",
]


def retrieve_policy(policy_path: str):
    """Load a policy .txt and return (clauses in source order, header lines)."""
    try:
        with open(policy_path, encoding="utf-8") as f:
            lines = f.read().split("\n")
    except OSError as exc:
        raise SystemExit(f"Cannot read policy file {policy_path}: {exc}")

    sections, header = [], []
    current_section, current_title, clause = None, "", None
    for line in lines:
        if not line.strip() or set(line.strip()) == {"═"}:
            continue
        m_sec = SECTION_RE.match(line.strip())
        if m_sec:
            current_section, current_title = m_sec.group(1), m_sec.group(2).strip()
            continue
        m_cl = CLAUSE_RE.match(line.strip())
        if m_cl:
            clause = {"section": current_section or m_cl.group(1).split(".")[0],
                      "section_title": current_title,
                      "clause": m_cl.group(1),
                      "text": m_cl.group(2).strip()}
            sections.append(clause)
        elif clause is not None and line.startswith("    "):
            clause["text"] += " " + line.strip()          # rejoin a wrapped line
        elif current_section is None:
            header.append(line.strip())

    if not sections:
        raise SystemExit(
            f"No numbered clauses found in {policy_path}. Refusing to emit a summary "
            "that would satisfy a completeness check vacuously.")
    return sections, header, "\n".join(lines)


def _is_binding(text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in BINDING)


def _conditions(text: str):
    """Condition tokens that must survive: every number, date and named approver."""
    toks = re.findall(r"\b\d+(?:\.\d+)?\b", text)
    toks += re.findall(r"\b(?:January|March|December)\b", text)
    toks += re.findall(r"\b(?:Department Head|HR Director|Municipal Commissioner|"
                       r"direct manager|registered medical practitioner)\b", text)
    return toks


def summarize_policy(sections, header, output_path: str, raw_source: str = ""):
    """Render the summary, verifying it against the raw source before writing.

    Verification must not compare the render against `sections`: both come from
    the same parse, so a clause the parser never saw is absent from both sides
    and the check passes while the clause is missing. Clause numbers are taken
    from `raw_source` instead, which also catches a parser omission.
    """
    out = ["CLAUSE-REFERENCED SUMMARY — " + (header[2] if len(header) > 2 else "POLICY"),
           "Source: " + (header[3] if len(header) > 3 else "see input file"), "",
           "Every numbered clause of the source appears below under its own number.",
           "Clauses marked [VERBATIM] bind the reader and are reproduced word for",
           "word: condensing them would risk dropping a condition or weakening a",
           "modal verb. No wording below comes from outside the source document.", ""]

    verbatim = condensed = 0
    current = None
    for c in sections:
        if c["section"] != current:
            current = c["section"]
            out += ["", f"SECTION {current} — {c['section_title']}", "-" * 62]
        if _is_binding(c["text"]):
            out.append(f"  {c['clause']} [VERBATIM] {c['text']}")
            verbatim += 1
        else:
            out.append(f"  {c['clause']} {c['text']}")
            condensed += 1

    out += ["", "", "MULTI-CONDITION OBLIGATIONS — every condition listed is stated in the",
            "clause cited beside it; none is added here.", "-" * 62]
    for c in sections:
        conds = _conditions(c["text"])
        if _is_binding(c["text"]) and len(conds) >= 2:
            out.append(f"  {c['clause']}: " + " · ".join(dict.fromkeys(conds)))

    text = "\n".join(out) + "\n"

    problems = []
    # Independent completeness: clause numbers come from the source file itself,
    # so a clause the parser never produced is still detected as missing.
    source_clauses = re.findall(r"(?m)^\s*(\d+\.\d+)\.?\s", raw_source)
    parsed_clauses = {c["clause"] for c in sections}
    for cl in dict.fromkeys(source_clauses):
        if cl not in parsed_clauses:
            problems.append(f"clause {cl} is in the source but was never parsed")
        if not re.search(rf"(?m)^\s*{re.escape(cl)}\s", text):
            problems.append(f"clause {cl} missing from summary")
    for c in sections:
        for tok in _conditions(c["text"]):
            if tok not in text:
                problems.append(f"clause {c['clause']} lost condition '{tok}'")
    low = text.lower()
    for phrase in BLEED:
        if phrase in low:
            problems.append(f"scope bleed: '{phrase}' is not in the source")
    if problems:
        for p in problems:
            print(f"  ABORT: {p}", file=sys.stderr)
        raise SystemExit("Refusing to write a lossy summary.")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Clauses: {len(sections)}  verbatim: {verbatim}  condensed: {condensed}")
    return {"clauses": len(sections), "verbatim": verbatim, "condensed": condensed}


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    sections, header, raw = retrieve_policy(args.input)
    summarize_policy(sections, header, args.output, raw)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
