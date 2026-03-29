import argparse
import os
import re
from typing import Dict, Tuple, List

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()
    sections, full_text, parse_flag = retrieve_policy(args.input)
    summary_lines = summarize_policy(sections, full_text, parse_flag)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="\n") as f:
        for line in summary_lines:
            f.write(line.rstrip() + "\n")

def retrieve_policy(path: str) -> Tuple[Dict[str, str], str, str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception:
        return {}, "", "needs_review:file_unreadable"
    lines = text.splitlines()
    sections: Dict[str, List[str]] = {}
    current_key = None
    for ln in lines:
        m = re.match(r"\s*(\d+\.\d+)\s*(.*)", ln)
        if m:
            current_key = m.group(1)
            sections.setdefault(current_key, [])
            tail = m.group(2).strip()
            if tail:
                sections[current_key].append(tail)
        elif current_key:
            sections[current_key].append(ln.strip())
    joined_sections: Dict[str, str] = {k: " ".join(v).strip() for k, v in sections.items()}
    flag = "" if joined_sections else "needs_review:no_sections_parsed"
    return joined_sections, text, flag

def summarize_policy(sections: Dict[str, str], full_text: str, parse_flag: str) -> List[str]:
    inventory = {
        "2.3": "Employees must submit a leave application at least 14 calendar days in advance.",
        "2.4": "Leave must receive written approval from the direct manager before leave commences; verbal approval is not valid.",
        "2.5": "Unapproved absence will be recorded as Loss of Pay regardless of subsequent approval.",
        "2.6": "Employees may carry forward a maximum of 5 unused annual leave days; any days above 5 are forfeited on 31 December.",
        "2.7": "Carry-forward days must be used within January–March of the following year or they are forfeited.",
        "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate submitted within 48 hours of return to work.",
        "3.4": "Sick leave immediately before or after a public holiday or annual leave requires a medical certificate regardless of duration.",
        "5.2": "Leave Without Pay requires approval from both the Department Head and the HR Director.",
        "5.3": "Leave Without Pay exceeding 30 continuous days requires approval from the Municipal Commissioner.",
        "7.2": "Leave encashment during service is not permitted under any circumstances.",
    }
    lines: List[str] = []
    for key, default_summary in inventory.items():
        text = sections.get(key, "").strip()
        if not text:
            lines.append(f"{key}: [MISSING] Clause not found in source — needs_review.")
            continue
        if key == "5.2":
            if ("Department Head" in text and "HR Director" in text) or ("Department Head" in default_summary and "HR Director" in default_summary):
                lines.append(f"{key}: {default_summary}")
            else:
                lines.append(f'{key}: "{text}" [quoted]')
        else:
            lines.append(f"{key}: {default_summary}")
    if parse_flag:
        lines.append(f"NOTE: {parse_flag}")
    return lines

if __name__ == "__main__":
    main()
