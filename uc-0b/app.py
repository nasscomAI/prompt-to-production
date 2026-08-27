"""
UC-0B — Policy Summariser (Summary That Changes Meaning)

Built from the RICE contract in agents.md and the skill specs in skills.md.
Deterministic, stdlib-only: no network/LLM calls, so it runs in any workshop
environment and produces the SAME output every run.

Why deterministic quoting instead of free-text paraphrase:
  The failure mode this UC targets is meaning loss — clause omission, scope bleed,
  and obligation softening. A paraphrasing summariser is exactly what drops
  clause 5.2's second approver or downgrades "must" to "should". This tool instead
  GUARANTEES the enforcement contract by construction:
    - every numbered clause is emitted, tagged with its clause number  (no omission)
    - the 10 high-risk clauses are emitted verbatim and marked [BINDING] (no softening)
    - only source text is written                                       (no scope bleed)
    - a COMPLETENESS CHECK footer proves every tracked clause is present,
      and that clause 5.2 still names BOTH approvers.

Enforcement encoded here (see agents.md):
  - completeness: every numbered clause present, clause-number tagged
  - preserve all conditions: clause 5.2 must keep Department Head AND HR Director
  - preserve binding strength: binding clauses quoted verbatim, never re-verbed
  - no scope bleed: nothing written that is not traceable to a source clause
  - refusal/flag: a missing tracked clause fails the run instead of summarising quietly
"""
import argparse
import re
import sys

# The 10 clauses the README marks as high-risk. These are emitted verbatim
# and verified present in the COMPLETENESS CHECK footer.
TRACKED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
]

# Multi-approver / multi-condition clauses: both tokens must survive (the 5.2 trap).
CONDITION_GUARDS = {
    "5.2": ["Department Head", "HR Director"],
}

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z &/()-]+)\s*$")
CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*\S)\s*$")
# Banner / divider decoration made of box-drawing or rule characters — never clause text.
DECORATION_RE = re.compile(r"^[\s═=_\-–—│┃|]+$")


def retrieve_policy(input_path: str) -> dict:
    """
    Load the .txt policy and return structured, numbered sections + a flat index.

    Returns:
      {
        "sections": [ {number, title, clauses:[{number, text}]}, ... ],
        "index":    { "2.3": "full clause text", ... },
      }
    Fails loudly if the file is missing/unreadable — an empty inventory must
    never be summarised silently.
    """
    with open(input_path, encoding="utf-8-sig") as f:
        lines = f.readlines()

    sections = []
    index = {}
    current_section = None
    current_clause = None  # (number, [text parts])

    def _flush_clause():
        nonlocal current_clause
        if current_clause and current_section is not None:
            number, parts = current_clause
            text = re.sub(r"\s+", " ", " ".join(parts)).strip()
            current_section["clauses"].append({"number": number, "text": text})
            index[number] = text
        current_clause = None

    for raw in lines:
        line = raw.rstrip("\n")

        sec_match = SECTION_RE.match(line)
        if sec_match:
            _flush_clause()
            current_section = {
                "number": sec_match.group(1),
                "title": sec_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            continue

        clause_match = CLAUSE_RE.match(line)
        if clause_match and current_section is not None:
            _flush_clause()
            current_clause = (clause_match.group(1), [clause_match.group(2)])
            continue

        # Continuation line: belongs to the clause currently being built.
        # Skip divider/banner decoration so it never bleeds into clause text.
        if current_clause is not None and line.strip() and not DECORATION_RE.match(line):
            current_clause[1].append(line.strip())
        # Anything else (banner, dividers, blank lines) is decoration → ignore.

    _flush_clause()
    return {"sections": sections, "index": index}


def summarize_policy(policy: dict, output_path: str) -> bool:
    """
    Produce a clause-referenced summary that preserves every clause, all
    conditions, and each binding verb. Only source text is written.

    Returns True if the completeness contract holds, False if any tracked clause
    is missing or a guarded condition was dropped (the run is marked FAILED but an
    output file is still written so the failure is visible).
    """
    index = policy["index"]
    tracked = set(TRACKED_CLAUSES)
    out = []

    out.append("POLICY SUMMARY — CMC EMPLOYEE LEAVE POLICY (HR-POL-001)")
    out.append("Generated deterministically from source. Every clause preserved; no external content added.")
    out.append("=" * 72)
    out.append("")

    for section in policy["sections"]:
        out.append(f"SECTION {section['number']} — {section['title']}")
        for clause in section["clauses"]:
            num = clause["number"]
            marker = " [BINDING]" if num in tracked else ""
            out.append(f"  {num}{marker}  {clause['text']}")
        out.append("")

    # --- COMPLETENESS CHECK footer: proves the enforcement contract ---
    out.append("=" * 72)
    out.append("COMPLETENESS CHECK (agents.md enforcement)")
    out.append("-" * 72)

    ok = True
    for num in TRACKED_CLAUSES:
        if num not in index:
            ok = False
            out.append(f"  {num}: MISSING — FLAG FOR REVIEW (clause absent from source parse)")
            continue

        text = index[num]
        # Condition guard: multi-approver / multi-condition clauses keep every token.
        dropped = [tok for tok in CONDITION_GUARDS.get(num, []) if tok.lower() not in text.lower()]
        if dropped:
            ok = False
            out.append(f"  {num}: CONDITION DROPPED — missing {', '.join(dropped)}")
        else:
            note = ""
            if num in CONDITION_GUARDS:
                note = f" (both conditions present: {', '.join(CONDITION_GUARDS[num])})"
            out.append(f"  {num}: PRESENT{note}")

    out.append("-" * 72)
    out.append(f"RESULT: {'PASS — all tracked clauses present, no conditions dropped' if ok else 'FAILED — see flags above'}")
    out.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    return ok


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    n_clauses = sum(len(s["clauses"]) for s in policy["sections"])
    print(f"Parsed {len(policy['sections'])} section(s), {n_clauses} clause(s).")

    ok = summarize_policy(policy, args.output)
    print(f"Summary written to {args.output}")
    if ok:
        print("COMPLETENESS: PASS — all 10 tracked clauses present, no conditions dropped.")
    else:
        print("COMPLETENESS: FAILED — a tracked clause is missing or a condition was dropped. See footer.")
        sys.exit(1)


if __name__ == "__main__":
    main()
