"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path


REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(input_path: str) -> dict:
    """Load policy text and parse numbered clauses into structured sections."""
    p = Path(input_path)
    if not p.exists():
        return {
            "ok": False,
            "error": f"Input file not found: {input_path}",
            "raw_text": "",
            "clauses": {},
            "flag": "NEEDS_REVIEW",
        }

    raw_text = p.read_text(encoding="utf-8")
    # Capture numbered clauses and their wrapped continuation lines.
    pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
    lines = raw_text.splitlines()

    clauses = {}
    current_id = None
    for line in lines:
        m = pattern.match(line)
        if m:
            current_id = m.group(1)
            clauses[current_id] = m.group(2).strip()
            continue

        if current_id and line.strip() and not re.match(r"^\s*═+\s*$", line):
            # Continue previous clause if this is an indented wrapped line.
            if line.startswith(" ") or line.startswith("\t"):
                clauses[current_id] = f"{clauses[current_id]} {line.strip()}".strip()
            else:
                current_id = None

    missing_required = [cid for cid in REQUIRED_CLAUSES if cid not in clauses]
    return {
        "ok": len(missing_required) == 0,
        "error": "" if not missing_required else f"Missing required clauses: {', '.join(missing_required)}",
        "raw_text": raw_text,
        "clauses": clauses,
        "flag": "NEEDS_REVIEW" if missing_required else "",
        "missing_required": missing_required,
    }


def _contains_all(text: str, words: list[str]) -> bool:
    t = text.lower()
    return all(w.lower() in t for w in words)


def summarize_policy(policy_data: dict) -> tuple[str, str]:
    """Produce clause-faithful summary with references and safe verbatim fallback."""
    clauses = policy_data.get("clauses", {})
    flagged = False
    output_lines = [
        "UC-0B Compliant Summary — HR Leave Policy",
        "",
    ]

    def safe_line(cid: str, summary_text: str, must_have: list[str]) -> str:
        nonlocal flagged
        source = clauses.get(cid, "")
        if not source:
            flagged = True
            return f"[{cid}] MISSING_CLAUSE — NEEDS_REVIEW"

        if must_have and not _contains_all(source, must_have):
            flagged = True
            return f"[{cid}] VERBATIM (NEEDS_REVIEW): {source}"

        return f"[{cid}] {summary_text}"

    output_lines.append(
        safe_line(
            "2.3",
            "Employees must submit leave applications at least 14 calendar days in advance using Form HR-L1.",
            ["must", "14", "advance"],
        )
    )
    output_lines.append(
        safe_line(
            "2.4",
            "Leave must receive written manager approval before commencement; verbal approval is not valid.",
            ["must", "written approval", "before", "verbal approval is not valid"],
        )
    )
    output_lines.append(
        safe_line(
            "2.5",
            "Unapproved absence will be recorded as Loss of Pay regardless of subsequent approval.",
            ["will", "loss of pay", "regardless of subsequent approval"],
        )
    )
    output_lines.append(
        safe_line(
            "2.6",
            "Employees may carry forward up to 5 unused annual leave days; any amount above 5 is forfeited on 31 December.",
            ["may carry forward", "maximum of 5", "forfeited on 31 december"],
        )
    )
    output_lines.append(
        safe_line(
            "2.7",
            "Carry-forward days must be used in January to March of the following year or they are forfeited.",
            ["must be used", "january", "march", "forfeited"],
        )
    )
    output_lines.append(
        safe_line(
            "3.2",
            "Sick leave of 3 or more consecutive days requires a medical certificate submitted within 48 hours of return.",
            ["3 or more", "requires", "medical certificate", "within 48 hours"],
        )
    )
    output_lines.append(
        safe_line(
            "3.4",
            "Sick leave immediately before or after a public holiday or annual leave requires a medical certificate regardless of duration.",
            ["requires", "medical certificate", "regardless of duration"],
        )
    )
    output_lines.append(
        safe_line(
            "5.2",
            "Leave Without Pay requires approval from both the Department Head and the HR Director; manager approval alone is insufficient.",
            ["requires", "department head", "hr director", "not sufficient"],
        )
    )
    output_lines.append(
        safe_line(
            "5.3",
            "Leave Without Pay exceeding 30 continuous days requires Municipal Commissioner approval.",
            ["exceeding 30", "requires", "municipal commissioner"],
        )
    )
    output_lines.append(
        safe_line(
            "7.2",
            "Leave encashment during service is not permitted under any circumstances.",
            ["not permitted", "under any circumstances"],
        )
    )

    if policy_data.get("missing_required"):
        flagged = True

    output_lines.append("")
    output_lines.append(f"flag: {'NEEDS_REVIEW' if flagged else ''}")
    return "\n".join(output_lines).strip() + "\n", ("NEEDS_REVIEW" if flagged else "")

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write policy summary")
    args = parser.parse_args()

    policy_data = retrieve_policy(args.input)
    if not policy_data.get("ok") and not policy_data.get("clauses"):
        raise ValueError(policy_data.get("error", "Failed to load policy."))

    summary, _ = summarize_policy(policy_data)
    Path(args.output).write_text(summary, encoding="utf-8")
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
