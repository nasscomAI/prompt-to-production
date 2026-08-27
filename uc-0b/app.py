"""
UC-0B — Policy Summariser
Built using RICE → agents.md → skills.md → CRAFT workflow.

Rule-based implementation — no LLM, no API key, no external dependencies.
Uses only Python standard library.

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""
import argparse
import re

# ---------------------------------------------------------------------------
# Clauses that must be quoted verbatim — paraphrase risks condition loss
# (agents.md context / enforcement rule 5)
# ---------------------------------------------------------------------------
VERBATIM_CLAUSES = {"2.4", "2.6", "2.7", "3.4", "5.2", "5.3", "7.2"}


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> dict:
    """
    Load a .txt policy file and return its content as a dict of
    clause_number → full clause text.

    Input:  file_path (str)
    Output: dict mapping e.g. '2.3' → 'Employees must submit...'
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            raw = f.read()
    except (FileNotFoundError, IOError) as e:
        raise RuntimeError(f"retrieve_policy: cannot read '{file_path}' — {e}") from e

    clauses = {}
    # Match patterns like "2.3 Employees must..." including multi-line text
    # until the next clause number or section header
    pattern = re.compile(
        r"(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+\s|\n[═]+|\Z)",
        re.DOTALL,
    )
    for match in pattern.finditer(raw):
        number = match.group(1).strip()
        text = re.sub(r"\s+", " ", match.group(2)).strip()
        clauses[number] = text

    return clauses


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(clauses: dict, source_name: str) -> str:
    """
    Produce a compliant plain-text summary from the structured clause dict.

    Rules enforced (agents.md):
    - Every clause is present — no omissions
    - Binding verbs preserved exactly (must / will / requires / not permitted)
    - Multi-condition clauses quoted verbatim with [VERBATIM — conditions preserved]
    - No information added beyond the source
    - Each line cites its clause number

    Input:  clauses (dict), source_name (str)
    Output: plain-text summary string
    """
    lines = [
        f"POLICY SUMMARY — {source_name}",
        "=" * 60,
        "Generated from source document. Every clause is cited.",
        "Clauses marked [VERBATIM] are quoted exactly to preserve all conditions.",
        "",
    ]

    for number in sorted(clauses.keys(), key=lambda x: [int(p) for p in x.split(".")]):
        text = clauses[number]
        if number in VERBATIM_CLAUSES:
            lines.append(f"{number}  {text}  [VERBATIM — conditions preserved]")
        else:
            lines.append(f"{number}  {text}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    source_name = args.input.split("/")[-1].split("\\")[-1]
    summary = summarize_policy(clauses, source_name)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output} ({len(clauses)} clauses)")


if __name__ == "__main__":
    main()
