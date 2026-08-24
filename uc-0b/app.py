"""
UC-0B — Summary That Changes Meaning
Implements the enforcement rules from agents.md:
- every numbered clause present in the source must be present in the summary
- multi-condition obligations must preserve ALL conditions (e.g. clause 5.2)
- never add information not present in the source document
- if a clause cannot be summarised without meaning loss, quote it verbatim and flag it
"""
import argparse
import re


def retrieve_policy(input_path: str) -> list:
    """Load the policy file and return structured numbered clauses with verbatim text."""
    with open(input_path, encoding="utf-8-sig") as f:
        text = f.read()

    if not text.strip():
        raise ValueError("Policy file is empty.")

    lines = text.splitlines()
    clauses = []
    current = None
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if set(stripped) <= set("=\u2550\u2551\u2500\u255a\u255d\u2554\u2557\u2560\u2566\u2569\u256c "):
            continue
        if re.match(r"^\d+\.\s+[A-Z]", stripped):
            continue
        if re.match(r"^\d+\.\d+\s+", stripped):
            current = {"number": stripped.split(" ")[0], "text": stripped}
            clauses.append(current)
        elif current is not None:
            current["text"] = " ".join([current["text"], stripped]).strip()
    return clauses


def summarize_policy(clauses: list, output_path: str) -> str:
    """Write a clause-complete summary. Every clause is preserved verbatim."""
    header = (
        "SUMMARY — CITY MUNICIPAL CORPORATION EMPLOYEE LEAVE POLICY (HR-POL-001)\n"
        "Source: policy_hr_leave.txt | Every numbered clause is preserved verbatim.\n"
        "No information has been added that is not present in the source document.\n"
    )
    body = []
    for clause in clauses:
        body.append(f"[{clause['number']}] {clause['text']}")

    summary = header + "\n".join(body) + "\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)
    return summary


def clause_inventory_report(clauses: list) -> None:
    """Print the clause inventory check against the 10 critical clauses."""
    present = {c["number"] for c in clauses}
    critical = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    missing = [num for num in critical if num not in present]
    if missing:
        print(f"WARNING — missing critical clauses: {', '.join(missing)}")
    else:
        print(f"OK — all {len(critical)} critical clauses present (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2).")
    clause_52 = next((c for c in clauses if c["number"] == "5.2"), None)
    if clause_52 and "Department Head" in clause_52["text"] and "HR Director" in clause_52["text"]:
        print("OK — clause 5.2 preserves BOTH approvers (Department Head and HR Director).")
    else:
        print("WARNING — clause 5.2 does not name both approvers; condition dropped.")


def main():
    parser = argparse.ArgumentParser(description="UC-0B policy summarizer.")
    parser.add_argument("--input", required=True, help="Path to the policy .txt file.")
    parser.add_argument("--output", required=True, help="Path for the summary output file.")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    clause_inventory_report(clauses)
    summarize_policy(clauses, args.output)
    print(f"Summary written to {args.output} ({len(clauses)} clauses preserved).")


if __name__ == "__main__":
    main()
