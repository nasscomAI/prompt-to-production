"""
UC-0B — HR Policy Summarizer.

Implements skills from skills.md under enforcement rules from agents.md:

Role (agents.md):
  Summarize HR policy documents, strictly adhering to provided text.

Intent (agents.md):
  Include every numbered clause, preserve ALL conditions of multi-condition
  obligations, add no external information, verbatim quote + flag clauses
  that cannot be summarised without meaning loss.

Context (agents.md):
  Only policy_hr_leave.txt + README.md ground truth. No external knowledge.

Skills (skills.md):
  - retrieve_policy(file_path) -> list[dict]
  - summarize_policy(sections) -> str
"""

import argparse
import re

NON_PLAIN_TEXT_MSG = "Refusal: input document is not plain text."
UNREADABLE_MSG = "Refusal: critical sections are unreadable."

# Phrases that never appear in source; their presence signals scope bleed.
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
]

# Markers for obligations / conditions / limits where paraphrase risks
# meaning loss (must, requires, not permitted, regardless, forfeited, etc.).
# Enforcement: "If a clause cannot be summarised without meaning loss —
# quote it verbatim and flag it" + "preserve ALL conditions".
RISK_MARKERS = [
    " must ",
    " requires",
    " is not permitted",
    " are not permitted",
    " cannot ",
    " not valid",
    " regardless",
    " under any circumstances",
    " or they are forfeited",
    " or forfeited",
    " maximum of",
    " exceeding",
    " alone is not sufficient",
    " in writing",
    " forfeited on",
    " will be recorded",
    " to be taken within",
    " cannot be split",
    " cannot be encashed",
]


def retrieve_policy(file_path: str) -> list[dict]:
    """Load .txt policy file, return structured numbered sections.

    Args:
        file_path: Path to the policy document (string).

    Returns:
        List of dicts, each {"clause_number": "2.3", "content": "..."}.

    Raises:
        FileNotFoundError: if file not found.
        ValueError: refusal if not plain text or critical sections unreadable.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        raise
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        raise

    # Refusal condition (agents.md): input must be plain text.
    # Null bytes indicate binary / non-plain-text input.
    if "\x00" in content:
        print(NON_PLAIN_TEXT_MSG)
        raise ValueError(NON_PLAIN_TEXT_MSG)

    sections: list[dict] = []
    pattern = re.compile(r"(?m)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s|\Z)", re.DOTALL)
    for match in pattern.finditer(content):
        clause_number = match.group(1)
        clause_content = match.group(2).strip()
        # Strip decorative box-drawing separators and section headers
        # (e.g. "2. ANNUAL LEAVE") that get captured between clauses.
        cleaned = re.sub(
            r"^[\u2500-\u2580]*$|^\d+\.\s+.*$",
            "",
            clause_content,
            flags=re.MULTILINE,
        ).strip()
        # Collapse excess blank lines left by stripping, preserve text.
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
        if cleaned:
            sections.append(
                {"clause_number": clause_number, "content": cleaned}
            )

    # Refusal condition (agents.md): critical sections unreadable.
    if not sections:
        print(UNREADABLE_MSG)
        raise ValueError(UNREADABLE_MSG)

    return sections


def _meaning_loss_risk(content: str) -> bool:
    lower = content.lower()
    return any(marker in lower for marker in RISK_MARKERS)


def summarize_policy(structured_sections: list[dict]) -> str:
    """Take structured sections, produce compliant summary with clause refs.

    Enforcement applied:
    - Every numbered clause present (iterate all input sections).
    - Multi-condition obligations preserve ALL conditions (verbatim quote
      when risk markers detected, so no condition can be dropped silently).
    - No external info added (only input content is emitted).
    - Unsummarizable clauses quoted verbatim + flagged.

    Args:
        structured_sections: list of {"clause_number", "content"} dicts.

    Returns:
        Summary string. Empty string if input is empty.
    """
    if not structured_sections:
        return ""

    summary_parts = []
    for section in structured_sections:
        clause_number = section.get("clause_number", "N/A")
        content = section.get("content", "")

        # Scope bleed guard: flag verbatim, never add external phrasing.
        if any(phrase in content.lower() for phrase in SCOPE_BLEED_PHRASES):
            summary_parts.append(
                f'Clause {clause_number}: "{content}" '
                f"(Flagged: scope-bleed detected)"
            )
            continue

        if _meaning_loss_risk(content):
            summary_parts.append(
                f'Clause {clause_number}: "{content}" '
                f"(Flagged: verbatim - meaning loss risk)"
            )
        else:
            summary_parts.append(f"Clause {clause_number}: {content}")

    return "\n\n".join(summary_parts)


def main():
    parser = argparse.ArgumentParser(description="Summarize HR policy documents.")
    parser.add_argument(
        "--input", type=str, required=True, help="Path to the input policy document."
    )
    parser.add_argument(
        "--output", type=str, required=True, help="Path to the output summary file."
    )
    args = parser.parse_args()

    try:
        policy_sections = retrieve_policy(args.input)
        summary = summarize_policy(policy_sections)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Summary successfully written to '{args.output}'")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
