"""
UC-0B — HR Leave Policy Summarizer.

The script reads the HR leave policy text file, extracts numbered clauses,
and writes a summary file that preserves the critical clauses and conditions
required by the workshop assignment.
"""
import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def load_workflow_context(base_dir: Path) -> Dict[str, object]:
    """Read the UC-0B agent and skill documents so the summarizer uses them as workflow guidance."""
    agents_path = base_dir / "agents.md"
    skills_path = base_dir / "skills.md"
    if not agents_path.exists() or not skills_path.exists():
        raise FileNotFoundError("agents.md and skills.md must exist for UC-0B workflow execution")

    agents_text = agents_path.read_text(encoding="utf-8")
    skills_text = skills_path.read_text(encoding="utf-8")

    role_match = re.search(r"role:\s*>\s*(.+?)(?=\n\nintent:)", agents_text, re.S)
    intent_match = re.search(r"intent:\s*>\s*(.+?)(?=\n\ncontext:)", agents_text, re.S)
    context_match = re.search(r"context:\s*>\s*(.+?)(?=\nenforcement:)", agents_text, re.S)

    required_clause_ids: List[str] = []
    for enforcement_text in re.findall(r'^\s*-\s*"(.*?)"\s*$', agents_text, flags=re.M):
        clause_ids = re.findall(r"\b\d+\.\d+\b", enforcement_text)
        for clause_id in clause_ids:
            if clause_id not in required_clause_ids:
                required_clause_ids.append(clause_id)

    skill_names = re.findall(r"^\s*-\s*name:\s*(\w+)", skills_text, flags=re.M)
    return {
        "agents_text": agents_text,
        "skills_text": skills_text,
        "role": " ".join(re.sub(r"\s+", " ", role_match.group(1)).split()).strip() if role_match else "",
        "intent": " ".join(re.sub(r"\s+", " ", intent_match.group(1)).split()).strip() if intent_match else "",
        "context": " ".join(re.sub(r"\s+", " ", context_match.group(1)).split()).strip() if context_match else "",
        "required_clauses": required_clause_ids or REQUIRED_CLAUSES,
        "skills": skill_names,
    }


def retrieve_policy(input_path: str) -> Dict[str, str]:
    """Parse a policy text file into a mapping of clause IDs to clause text."""
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()
    clauses: Dict[str, str] = {}
    current_clause_id: Optional[str] = None
    current_lines: List[str] = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if re.fullmatch(r"[═=\-]+", line):
            continue
        if re.match(r"^\d+\.\s+[A-Z]", line) and not re.match(r"^\d+\.\d+\b", line):
            if current_clause_id is not None:
                clauses[current_clause_id] = " ".join(part.strip() for part in current_lines if part.strip())
                current_clause_id = None
                current_lines = []
            continue

        match = re.match(r"^(\d+\.\d+)\b", line)
        if match:
            if current_clause_id is not None:
                clauses[current_clause_id] = " ".join(part.strip() for part in current_lines if part.strip())
            current_clause_id = match.group(1)
            current_lines = [re.sub(r"^\d+\.\d+\s*", "", line).strip()]
        elif current_clause_id is not None:
            current_lines.append(line)

    if current_clause_id is not None:
        clauses[current_clause_id] = " ".join(part.strip() for part in current_lines if part.strip())

    return clauses


def summarize_policy(clauses: Dict[str, str], required_clause_ids: Optional[List[str]] = None, workflow_context: Optional[Dict[str, object]] = None) -> str:
    """Build a faithful summary that preserves each required clause using workflow guidance from agents.md and skills.md."""
    required = list(required_clause_ids or (workflow_context or {}).get("required_clauses") or REQUIRED_CLAUSES)
    missing = [clause_id for clause_id in required if clause_id not in clauses]
    if missing:
        raise ValueError(f"Missing required clauses: {', '.join(missing)}")

    summary_lines = [
        "HR Leave Policy Summary",
        "======================",
        "",
        "Generated from UC-0B agents.md and skills.md guidance.",
        "",
    ]

    if workflow_context:
        summary_lines.append(f"Role: {workflow_context.get('role', '')}")
        skills = workflow_context.get("skills", [])
        if skills:
            summary_lines.append(f"Skills used: {', '.join(skills)}")
        summary_lines.append("")

    for clause_id in required:
        summary_lines.append(f"{clause_id}: {clauses[clause_id]}")

    return "\n".join(summary_lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize the HR leave policy")
    parser.add_argument("--input", default="../data/policy-documents/policy_hr_leave.txt", help="Path to the HR leave policy text file")
    parser.add_argument("--output", default="summary_hr_leave.txt", help="Path where the summary should be written")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    input_path = Path(args.input)
    if input_path.is_absolute():
        resolved_input = input_path
    elif input_path.exists():
        resolved_input = input_path.resolve()
    else:
        cwd_input = (Path.cwd() / input_path).resolve()
        resolved_input = cwd_input if cwd_input.exists() else (repo_root / input_path).resolve()

    output_path = Path(args.output)
    if output_path.is_absolute():
        resolved_output = output_path
    elif output_path.exists() or output_path.parent == Path('.'):
        resolved_output = (Path.cwd() / output_path).resolve()
    else:
        resolved_output = (Path.cwd() / output_path).resolve()

    uc0b_dir = Path(__file__).resolve().parent
    workflow_context = load_workflow_context(uc0b_dir)
    clauses = retrieve_policy(str(resolved_input))
    summary = summarize_policy(clauses, workflow_context=workflow_context)
    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(summary, encoding="utf-8")
    print(f"Wrote summary to {resolved_output}")
    print(summary)


if __name__ == "__main__":
    main()
