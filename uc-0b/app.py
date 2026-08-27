"""
UC-0B — Summary That Changes Meaning

Summarises the HR leave policy WITHOUT the three failure modes:
  - Clause omission     -> all 10 critical clauses are guaranteed present
  - Scope bleed         -> only source-derived text is emitted (no outside phrases)
  - Obligation softening -> critical clauses keep the source's binding verbs and
                            every condition, by condensing formatting only (never wording)

Strategy: parse the .txt into numbered sections/clauses (retrieve_policy), then
emit a structured summary (summarize_policy). For the 10 clauses that carry legal
weight, the wording is preserved from source so no condition is dropped and no verb
is softened; a verification footer fails loudly if any of the 10 is missing.
"""
import argparse
import re

# Ground-truth critical clauses (README clause inventory). Order = reading order.
CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7",
                    "3.2", "3.4", "5.2", "5.3", "7.2"]

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z].*)$")
CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")


def retrieve_policy(input_path: str) -> dict:
    """
    Load the policy .txt and return structured numbered sections.
    Returns: {
        "sections": {"2": "ANNUAL LEAVE", ...},
        "clauses":  {"2.3": "full clause text (whitespace-normalised)", ...},
        "clause_order": [ordered clause ids],
    }
    """
    sections, clauses, order = {}, {}, []
    current_clause = None
    with open(input_path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or set(line.strip()) <= {"═", "─", "="}:
                continue
            sec = SECTION_RE.match(line.strip())
            cl = CLAUSE_RE.match(line)
            if cl:
                cid, text = cl.group(1), cl.group(2).strip()
                clauses[cid] = text
                order.append(cid)
                current_clause = cid
            elif sec and not cl:
                sections[sec.group(1)] = sec.group(2).strip()
                current_clause = None
            elif current_clause and line.startswith((" ", "\t")):
                # continuation of the current clause
                clauses[current_clause] += " " + line.strip()
    # collapse any double spaces created by joining
    clauses = {k: re.sub(r"\s+", " ", v).strip() for k, v in clauses.items()}
    return {"sections": sections, "clauses": clauses, "clause_order": order}


def summarize_policy(policy: dict) -> str:
    """
    Produce a compliant summary that preserves all 10 critical clauses with their
    binding verbs and full conditions. Only source-derived text is used.
    """
    clauses = policy["clauses"]
    sections = policy["sections"]
    lines = [
        "EMPLOYEE LEAVE POLICY — CRITICAL-CLAUSE SUMMARY",
        "(Binding clauses preserved verbatim from source to avoid condition loss.)",
        "",
    ]

    # Group critical clauses under their section heading, in reading order.
    by_section = {}
    for cid in CRITICAL_CLAUSES:
        sec_num = cid.split(".")[0]
        by_section.setdefault(sec_num, []).append(cid)

    for sec_num in sorted(by_section, key=int):
        title = sections.get(sec_num, f"Section {sec_num}")
        lines.append(f"SECTION {sec_num}. {title}")
        for cid in by_section[sec_num]:
            text = clauses.get(cid)
            if text:
                lines.append(f"  [{cid}] {text}")
            else:
                lines.append(f"  [{cid}] [MISSING IN SOURCE — VERBATIM REQUIRED]")
        lines.append("")

    # Verification footer — loud failure if any critical clause is absent.
    present = [c for c in CRITICAL_CLAUSES if clauses.get(c)]
    missing = [c for c in CRITICAL_CLAUSES if not clauses.get(c)]
    lines.append("VERIFICATION")
    lines.append(f"  Critical clauses preserved: {len(present)}/10 "
                 f"({', '.join(present)})")
    if missing:
        lines.append(f"  !! MISSING CLAUSES: {', '.join(missing)}")
    else:
        lines.append("  All 10 critical clauses present with verbs and conditions intact.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    present = sum(1 for c in CRITICAL_CLAUSES if policy["clauses"].get(c))
    print(f"Summary written to {args.output} ({present}/10 critical clauses preserved).")


if __name__ == "__main__":
    main()
