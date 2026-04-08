"""UC-0B policy summarizer with clause-level validation."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


class ValidationError(Exception):
    """Raised when policy extraction or validation fails."""


def load_text_file(path: Path) -> str:
    if path.suffix.lower() != ".txt":
        raise ValidationError(f"Input file must be a .txt file: {path}")
    if not path.exists() or not path.is_file():
        raise ValidationError(f"Input file not found: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValidationError(f"Could not read file: {path}") from exc
    if not text.strip():
        raise ValidationError(f"Input file is empty: {path}")
    return text


def parse_numbered_sections(raw_text: str) -> List[Dict[str, str]]:
    lines = raw_text.splitlines()
    sections: List[Dict[str, str]] = []
    current_id = None
    current_lines: List[str] = []

    heading_pattern = re.compile(r"^\s*(\d+(?:\.\d+)*)\s*[\).:-]?\s*(.*)$")

    separator_pattern = re.compile(r"^\s*[\-=*_~#\u2500-\u257F\u2580-\u259F]{8,}\s*$")

    for line in lines:
        match = heading_pattern.match(line)
        if match:
            clause_id = match.group(1)
            trailing = match.group(2).strip()

            if current_id is not None:
                body = "\n".join(current_lines).strip()
                if body:
                    sections.append({"clause_id": current_id, "text": body})

            current_id = clause_id
            current_lines = [trailing] if trailing else []
            continue

        if current_id is not None:
            if separator_pattern.match(line):
                continue
            current_lines.append(line.rstrip())

    if current_id is not None:
        body = "\n".join(current_lines).strip()
        if body:
            sections.append({"clause_id": current_id, "text": body})

    if not sections:
        raise ValidationError("No numbered clauses could be parsed from input policy.")

    return sections


def extract_required_clause_ids(agents_text: str) -> List[str]:
    match = re.search(r"required clauses\s*\(([^)]+)\)", agents_text, flags=re.IGNORECASE)
    if not match:
        raise ValidationError("Could not find required clause list in agents.md.")

    clause_ids = re.findall(r"\d+(?:\.\d+)+", match.group(1))
    if not clause_ids:
        raise ValidationError("Required clause list in agents.md is empty or invalid.")
    return clause_ids


def extract_skill_names(skills_text: str) -> List[str]:
    names = re.findall(r"^\s*-\s*name:\s*([a-zA-Z0-9_\-]+)\s*$", skills_text, flags=re.MULTILINE)
    if not names:
        raise ValidationError("No skill names found in skills.md.")
    return names


def retrieve_policy(file_path: Path) -> Dict[str, object]:
    raw_text = load_text_file(file_path)
    sections = parse_numbered_sections(raw_text)
    return {"sections": sections, "raw_text": raw_text}


def summarize_policy(
    sections: Sequence[Dict[str, str]], required_clause_ids: Sequence[str]
) -> Dict[str, object]:
    section_map = {item["clause_id"]: item["text"].strip() for item in sections if item.get("clause_id")}

    missing = [clause_id for clause_id in required_clause_ids if clause_id not in section_map]
    if missing:
        raise ValidationError(
            "Missing required clauses in input policy: " + ", ".join(missing)
        )

    summary_lines: List[str] = []
    quoted_clauses: List[str] = []
    for clause_id in required_clause_ids:
        clause_text = section_map[clause_id]
        # Use verbatim text for strict meaning preservation.
        summary_lines.append(f"{clause_id}: \"{clause_text}\"")
        quoted_clauses.append(clause_id)

    return {
        "summary_text": "\n".join(summary_lines),
        "included_clause_ids": list(required_clause_ids),
        "quoted_clauses": quoted_clauses,
    }


def validate_skill_contract(skills_text: str) -> None:
    names = extract_skill_names(skills_text)
    required = {"retrieve_policy", "summarize_policy"}
    missing = sorted(required.difference(names))
    if missing:
        raise ValidationError(
            "skills.md is missing required skills: " + ", ".join(missing)
        )


def build_summary(input_path: Path, output_path: Path, agents_path: Path, skills_path: Path) -> Tuple[List[str], Dict[str, object]]:
    agents_text = agents_path.read_text(encoding="utf-8")
    skills_text = skills_path.read_text(encoding="utf-8")

    required_clause_ids = extract_required_clause_ids(agents_text)
    validate_skill_contract(skills_text)

    retrieved = retrieve_policy(input_path)
    result = summarize_policy(retrieved["sections"], required_clause_ids)

    output_path.write_text(result["summary_text"] + "\n", encoding="utf-8")
    return required_clause_ids, result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize HR leave policy while preserving required clause meaning."
    )
    parser.add_argument("--input", required=True, type=Path, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, type=Path, help="Path to output summary file")
    parser.add_argument(
        "--agents",
        default=Path("agents.md"),
        type=Path,
        help="Path to agents.md file with R.I.C.E requirements",
    )
    parser.add_argument(
        "--skills",
        default=Path("skills.md"),
        type=Path,
        help="Path to skills.md file with required skills",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        required_clause_ids, result = build_summary(
            input_path=args.input,
            output_path=args.output,
            agents_path=args.agents,
            skills_path=args.skills,
        )
    except ValidationError as exc:
        raise SystemExit(f"ValidationError: {exc}") from exc

    print("Summary generated successfully.")
    print("Required clauses:", ", ".join(required_clause_ids))
    print("Included clauses:", ", ".join(result["included_clause_ids"]))
    print("Quoted clauses:", ", ".join(result["quoted_clauses"]))


if __name__ == "__main__":
    main()
