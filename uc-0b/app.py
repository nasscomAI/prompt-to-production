import argparse
import os
import re
from typing import Dict, List, Tuple

def retrieve_policy(input_path: str) -> List[Tuple[str, str]]:
    """Loads the policy text file and returns the policy content organized by numbered clause sections."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)$")
    clauses: List[Tuple[str, str]] = []
    current_clause: str = ""
    current_text_lines: List[str] = []

    with open(input_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            stripped = line.strip()
            match = clause_pattern.match(stripped)

            if match:
                if current_clause:
                    clauses.append((current_clause, " ".join(current_text_lines).strip()))
                current_clause = match.group(1)
                current_text_lines = [match.group(2).strip()]
            elif current_clause and line.startswith(" "):
                current_text_lines.append(stripped)
            else:
                continue

    if current_clause:
        clauses.append((current_clause, " ".join(current_text_lines).strip()))

    if not clauses:
        raise ValueError("Unable to parse numbered clauses from policy document")

    return clauses


def _is_complex_clause(text: str) -> bool:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if len(sentences) > 1:
        return True
    lowered = text.lower()
    if " and " in lowered and "," in lowered:
        return True
    if " or " in lowered and "," in lowered:
        return True
    return False


def summarize_policy(sections: List[Tuple[str, str]]) -> str:
    """Takes structured policy sections and produces a compliant summary that preserves every clause and its conditions."""
    if not isinstance(sections, list) or not sections:
        raise ValueError("Invalid input: sections must be a non-empty list of numbered clauses")

    if not sections:
        raise ValueError("Invalid input: no numbered clauses found in policy document")

    summary_lines: List[str] = []
    for number, text in sections:
        normalized = " ".join(text.split())
        if not normalized:
            raise ValueError(f"Invalid clause text for {number}")
        if _is_complex_clause(normalized):
            summary_lines.append(f"{number}: \"{normalized}\" [VERBATIM FLAG]")
        else:
            summary_lines.append(f"{number}: {normalized}")

    return "\n".join(summary_lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0B policy summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as out_f:
        out_f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
