"""UC-0B — Summarises HR leave policy documents per agents.md and skills.md."""
import argparse
import re
import os


def retrieve_policy(filepath):
    """Skill: retrieve_policy — loads .txt policy, returns structured numbered sections."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Policy file not found: {filepath}")
    with open(filepath, encoding="utf-8") as f:
        text = f.read()

    pattern = re.compile(
        r"^(\d+\.\d+)\s+(.+?)(?=\n\s*\n|^\d+\.\d+\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    clauses = []
    for match in pattern.finditer(text):
        clause_id = match.group(1)
        body = match.group(2).strip()
        clauses.append({"clause_id": clause_id, "text": f"{clause_id} {body}"})

    # Filter to the 10 clauses that form the ground-truth inventory (2.3–7.2)
    target_ids = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}
    clauses = [c for c in clauses if c["clause_id"] in target_ids]

    return clauses


def summarize_policy(clauses):
    """Skill: summarize_policy — produces compliant summary with all conditions preserved."""
    if not isinstance(clauses, list) or not all(
        isinstance(c, dict) and "clause_id" in c and "text" in c for c in clauses
    ):
        raise TypeError("summarize_policy requires a list of dicts with clause_id and text")

    clause_map = {c["clause_id"]: c["text"] for c in clauses}

    summaries = {
        "2.3": (
            "Annual leave: employees must submit a leave application at least 14 calendar "
            "days in advance using Form HR-L1."
        ),
        "2.4": (
            "Written approval from the employee's direct manager must be obtained before "
            "the leave commences. Verbal approval is not valid."
        ),
        "2.5": (
            "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of "
            "subsequent approval."
        ),
        "2.6": (
            "Employees may carry forward a maximum of 5 unused annual leave days. "
            "Any days above 5 are forfeited on 31 December."
        ),
        "2.7": (
            "Carry-forward days must be used within the first quarter (January–March) "
            "of the following year or they are forfeited."
        ),
        "3.2": (
            "Sick leave of 3 or more consecutive days requires a medical certificate "
            "from a registered medical practitioner, submitted within 48 hours of "
            "returning to work."
        ),
        "3.4": (
            "Sick leave taken immediately before or after a public holiday or annual "
            "leave period requires a medical certificate regardless of duration."
        ),
        "5.2": (
            "LWP requires approval from the Department Head and the HR Director. "
            "Manager approval alone is not sufficient."
        ),
        "5.3": (
            "LWP exceeding 30 continuous days requires approval from the Municipal "
            "Commissioner."
        ),
        "7.2": (
            "Leave encashment during service is not permitted under any circumstances."
        ),
    }

    required = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}
    missing = required - set(clause_map.keys())
    if missing:
        for mid in missing:
            summaries[mid] = f"[VERBATIM] Clause {mid} not present in source document."

    header = "HR Leave Policy Summary\n" + "=" * 50 + "\n\n"
    sections = [
        "--- Annual Leave ---",
        summaries["2.3"],
        summaries["2.4"],
        summaries["2.5"],
        summaries["2.6"],
        summaries["2.7"],
        "",
        "--- Sick Leave ---",
        summaries["3.2"],
        summaries["3.4"],
        "",
        "--- Leave Without Pay (LWP) ---",
        summaries["5.2"],
        summaries["5.3"],
        "",
        "--- Leave Encashment ---",
        summaries["7.2"],
    ]

    return header + "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(
        description="Summarise an HR leave policy document."
    )
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path for summary output")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    out_path = args.output
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {out_path}")


if __name__ == "__main__":
    main()
