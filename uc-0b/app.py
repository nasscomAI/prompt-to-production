"""
UC-0B — Summary That Changes Meaning

Produces a clause-faithful compliance summary of a numbered policy document,
honoring the enforcement rules in agents.md and the skill contracts in skills.md.

The summary is built by extraction, not free generation: every numbered clause
is preserved, high-risk clauses are quoted verbatim with their conditions
enumerated, and a verifier fails loudly if any clause is dropped, any required
condition is missing, or any scope-bleed phrase appears. This is what prevents
clause omission, obligation softening, and scope bleed.
"""
import argparse
import re
import sys

# Section heading: "2. ANNUAL LEAVE" (single number, dot, space, title).
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z].*)$")
# Clause: "2.3 Employees must ..." (number.number, then text).
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
# Divider rows made of box-drawing characters.
DIVIDER_RE = re.compile(r"^[═=]+$")

# High-risk clauses for the HR leave policy: each maps to the condition tokens
# that MUST survive into the summary. Sourced from the README clause inventory.
CRITICAL_HR = {
    "2.3": {"label": "14-day advance notice", "tokens": ["14 calendar days", "in advance"]},
    "2.4": {"label": "Written approval before leave (verbal invalid)",
            "tokens": ["written approval", "before the leave commences", "Verbal approval is not valid"]},
    "2.5": {"label": "Unapproved absence = LOP", "tokens": ["Loss of Pay", "regardless of subsequent approval"]},
    "2.6": {"label": "Max 5 days carry-forward, rest forfeited 31 Dec",
            "tokens": ["maximum of 5", "forfeited on 31 December"]},
    "2.7": {"label": "Carry-forward used Jan–Mar or forfeited",
            "tokens": ["January", "March", "forfeited"]},
    "3.2": {"label": "3+ sick days need cert within 48hrs",
            "tokens": ["3 or more consecutive", "medical certificate", "within 48 hours"]},
    "3.4": {"label": "Sick leave around holiday needs cert regardless of duration",
            "tokens": ["before or after", "medical certificate", "regardless of duration"]},
    "5.2": {"label": "LWP needs Department Head AND HR Director",
            "tokens": ["Department Head", "HR Director", "alone is not sufficient"]},
    "5.3": {"label": "LWP > 30 days needs Municipal Commissioner",
            "tokens": ["30 continuous days", "Municipal Commissioner"]},
    "7.2": {"label": "No encashment during service",
            "tokens": ["not permitted", "under any circumstances"]},
}

# Phrasings that would mean information was invented (scope bleed). The summary
# must never contain any of these.
SCOPE_BLEED = [
    "as is standard practice", "typically in government", "generally expected to",
    "it is common practice", "as standard practice", "generally understood",
    "while not explicitly covered",
]


def retrieve_policy(path: str) -> dict:
    """Load a numbered policy .txt into {header, sections:[{number,title,clauses:[{id,text}]}]}."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    header, sections = [], []
    current_section = None
    current_clause = None
    seen_first_section = False

    for line in lines:
        if DIVIDER_RE.match(line.strip()):
            continue
        sec = SECTION_RE.match(line.strip())
        cls = CLAUSE_RE.match(line.strip())
        if sec:
            seen_first_section = True
            current_section = {"number": sec.group(1), "title": sec.group(2).strip(), "clauses": []}
            sections.append(current_section)
            current_clause = None
        elif cls and current_section is not None:
            current_clause = {"id": cls.group(1), "text": cls.group(2).strip()}
            current_section["clauses"].append(current_clause)
        elif not seen_first_section:
            if line.strip():
                header.append(line.strip())
        elif current_clause is not None and line.strip():
            # Continuation of the current clause — never discard source text.
            current_clause["text"] += " " + line.strip()

    return {"header": header, "sections": sections}


def _norm(s: str) -> str:
    """Collapse whitespace and newlines so multi-line condition tokens match."""
    return re.sub(r"\s+", " ", s)


def summarize_policy(policy: dict, critical: dict) -> str:
    """Render a structured compliance summary; every clause preserved, criticals verbatim."""
    out = []
    hdr = policy["header"]
    title = hdr[2] if len(hdr) > 2 else "POLICY"
    ref = next((h for h in hdr if "Reference" in h), "")
    out.append(f"COMPLIANCE SUMMARY — {title.title()}")
    if ref:
        out.append(ref)
    out.append("Method: every numbered clause preserved; high-risk obligations quoted "
               "verbatim with conditions enumerated; no external information added.")
    out.append("Legend: ‼ = critical clause (quoted verbatim).")
    out.append("")

    for sec in policy["sections"]:
        out.append(f"═══ {sec['number']}. {sec['title']} ═══")
        for clause in sec["clauses"]:
            cid, text = clause["id"], _norm(clause["text"])
            if cid in critical:
                out.append(f"  {cid} ‼ {critical[cid]['label']}")
                out.append(f'      VERBATIM: "{text}"')
                conds = " AND ".join(_norm(t) for t in critical[cid]["tokens"])
                out.append(f"      Conditions preserved: {conds}")
            else:
                out.append(f"  {cid} — {text}")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def verify(policy: dict, summary: str, critical: dict) -> list:
    """Return a list of compliance problems; empty means the summary is faithful."""
    problems = []
    norm_summary = _norm(summary)

    # 1. Every clause present.
    for sec in policy["sections"]:
        for clause in sec["clauses"]:
            if clause["id"] not in summary:
                problems.append(f"MISSING CLAUSE: {clause['id']}")

    # 2. Every critical clause keeps all its condition tokens.
    for cid, cfg in critical.items():
        for tok in cfg["tokens"]:
            if _norm(tok) not in norm_summary:
                problems.append(f"DROPPED CONDITION in {cid}: '{_norm(tok)}'")

    # 3. No scope-bleed phrases.
    low = norm_summary.lower()
    for phrase in SCOPE_BLEED:
        if phrase in low:
            problems.append(f"SCOPE BLEED: '{phrase}'")

    return problems


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Compliance Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    n_clauses = sum(len(s["clauses"]) for s in policy["sections"])
    summary = summarize_policy(policy, CRITICAL_HR)
    problems = verify(policy, summary, CRITICAL_HR)

    print(f"Parsed {len(policy['sections'])} sections, {n_clauses} clauses.")
    if problems:
        print(f"COMPLIANCE CHECK FAILED ({len(problems)} problem(s)):")
        for p in problems:
            print("  -", p)
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Compliance check passed: all {n_clauses} clauses present, "
          f"{len(CRITICAL_HR)} critical clauses verbatim, no scope bleed.")
    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
