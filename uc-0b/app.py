"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ClauseSection:
    clause_id: str
    heading: str
    raw_text: str
    source_line_span: Tuple[int, int]


def _read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def load_agent_requirements(agents_path: str) -> List[str]:
    """Extract required clause IDs from agents.md enforcement/intent text."""
    agents_text = _read_text_file(agents_path)

    parenthetical_list = re.search(r"\(([^)]*\d+\.\d+[^)]*)\)", agents_text)
    if parenthetical_list:
        candidates = re.findall(r"\b\d+\.\d+\b", parenthetical_list.group(1))
    else:
        candidates = re.findall(r"\b\d+\.\d+\b", agents_text)

    ordered_unique: List[str] = []
    for clause_id in candidates:
        if clause_id not in ordered_unique:
            ordered_unique.append(clause_id)

    if not ordered_unique:
        raise ValueError("No clause requirements found in agents.md")

    return ordered_unique


def load_skills_catalog(skills_path: str) -> List[str]:
    """Extract skill names and validate required UC-0B capabilities exist."""
    skills_text = _read_text_file(skills_path)
    skill_names = re.findall(r"^\s*-\s*name:\s*([A-Za-z0-9_\-]+)\s*$", skills_text, flags=re.MULTILINE)

    required = {"retrieve_policy", "summarize_policy"}
    missing = sorted(required.difference(set(skill_names)))
    if missing:
        raise ValueError(f"skills.md is missing required skills: {', '.join(missing)}")

    return skill_names


def retrieve_policy(input_path: str, required_clauses: List[str]) -> Dict[str, ClauseSection]:
    """Load a policy text file and map numbered clauses into structured sections."""
    text = _read_text_file(input_path)
    lines = text.splitlines()

    clause_header = re.compile(r"^\s*(\d+\.\d+)\s*(.*)$")
    sections: Dict[str, ClauseSection] = {}

    current_clause = None
    current_heading = ""
    start_line = 0
    buffer: List[str] = []

    def flush_clause(end_line: int) -> None:
        nonlocal current_clause, current_heading, start_line, buffer
        if not current_clause:
            return
        raw_text = "\n".join(buffer).strip()
        if current_clause not in sections:
            sections[current_clause] = ClauseSection(
                clause_id=current_clause,
                heading=current_heading.strip(),
                raw_text=raw_text,
                source_line_span=(start_line, end_line),
            )
        current_clause = None
        current_heading = ""
        start_line = 0
        buffer = []

    for i, line in enumerate(lines, start=1):
        match = clause_header.match(line)
        if match:
            flush_clause(i - 1)
            current_clause = match.group(1)
            current_heading = match.group(2)
            start_line = i
            buffer = [line.rstrip()]
        elif current_clause:
            buffer.append(line.rstrip())

    flush_clause(len(lines))

    # Keep only the required clause universe for compliance work.
    return {cid: sections[cid] for cid in required_clauses if cid in sections}


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def summarize_policy(sections: Dict[str, ClauseSection], required_clauses: List[str]) -> str:
    """Produce a constrained summary with explicit clause references and verification."""
    summary_lines: List[str] = []
    unresolved: List[str] = []

    for clause_id in required_clauses:
        section = sections.get(clause_id)
        if section is None or not section.raw_text.strip():
            unresolved.append(clause_id)
            summary_lines.append(f"[{clause_id}] UNRESOLVED: Clause missing in source input.")
            continue

        clause_text = _normalize_whitespace(section.raw_text)

        # Clause 5.2 requires both approvers; do not silently drop either condition.
        if clause_id == "5.2":
            lowered = clause_text.lower()
            has_dept_head = "department head" in lowered
            has_hr_director = "hr director" in lowered
            if not (has_dept_head and has_hr_director):
                unresolved.append(clause_id)
                summary_lines.append(
                    f"[{clause_id}] UNRESOLVED: \"{clause_text}\" (dual-approval condition not verifiable)."
                )
                continue

        summary_lines.append(f"[{clause_id}] {clause_text}")

    compliance_status = "PASS" if not unresolved else "REVIEW_REQUIRED"

    output_lines = [
        "HR Leave Policy Summary (UC-0B)",
        "",
        "Summary:",
        *summary_lines,
        "",
        "Verification:",
        f"- required_clause_count: {len(required_clauses)}",
        f"- summarized_clause_count: {len(summary_lines)}",
        f"- unresolved_clause_count: {len(unresolved)}",
        f"- unresolved_clauses: {', '.join(unresolved) if unresolved else 'none'}",
        f"- compliance_status: {compliance_status}",
    ]
    return "\n".join(output_lines) + "\n"


def write_output(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def main():
    parser = argparse.ArgumentParser(description="UC-0B compliant policy summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    parser.add_argument("--agents", default="agents.md", help="Path to agents.md")
    parser.add_argument("--skills", default="skills.md", help="Path to skills.md")
    args = parser.parse_args()

    required_clauses = load_agent_requirements(args.agents)
    load_skills_catalog(args.skills)

    sections = retrieve_policy(args.input, required_clauses)
    summary = summarize_policy(sections, required_clauses)
    write_output(args.output, summary)

    print(f"Wrote summary to: {args.output}")

if __name__ == "__main__":
    main()
