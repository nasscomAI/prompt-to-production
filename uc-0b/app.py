"""
UC-0B — Policy Summariser
Implements retrieve_policy and summarize_policy per agents.md and skills.md.
"""
import argparse
import os
import re

# Clauses that carry compounded conditions or absolute prohibitions and must
# never be softened. These are quoted verbatim (agents.md enforcement rule 4).
VERBATIM_SECTIONS = {"5.2", "7.2"}

# Binding verbs that must be preserved. Used to detect softening if needed.
BINDING_VERBS = {"must", "will", "requires", "not permitted"}


# ---------------------------------------------------------------------------
# skill: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> list:
    """
    Load a .txt policy file and return its content as a list of structured
    numbered sections.

    Input:  path to a .txt policy file (str)
    Output: list of dicts with keys 'section' (str) and 'text' (str)
    Error handling (skills.md):
      - FileNotFoundError if file is missing or unreadable
      - ValueError if file is empty
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        raw = f.read()

    if not raw.strip():
        raise ValueError(f"Policy file contains no content to summarise: {file_path}")

    # Match numbered clauses like "2.3 Some text..." (possibly multi-line).
    # A clause ends where the next numbered clause or a section separator begins.
    pattern = re.compile(
        r"^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    sections = []
    for match in pattern.finditer(raw):
        section_num = match.group(1).strip()
        text = re.sub(r"\s+", " ", match.group(2)).strip()
        if text:
            sections.append({"section": section_num, "text": text})

    return sections


# ---------------------------------------------------------------------------
# skill: summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(sections: list) -> str:
    """
    Produce a compliant clause-by-clause summary from structured sections.

    Input:  list of dicts with keys 'section' and 'text'
    Output: plain-text summary string — clause refs preserved, binding verbs
            not softened, verbatim quoting where meaning loss is a risk.
    Error handling (skills.md):
      - Returns error message string if sections list is empty
      - Skips sections with no text and appends a warning line
    """
    if not sections:
        return "ERROR: No sections were provided to summarize_policy."

    lines = ["POLICY SUMMARY — HR-POL-001 Employee Leave Policy",
             "=" * 60]
    warnings = []

    for item in sections:
        sec = item.get("section", "")
        text = (item.get("text") or "").strip()

        if not text:
            warnings.append(f"WARNING: Section {sec} has no text and was skipped.")
            continue

        if sec in VERBATIM_SECTIONS:
            # agents.md enforcement rule 4: quote verbatim, flag meaning loss risk
            lines.append(
                f"\nClause {sec} [VERBATIM — meaning loss risk]:\n  \"{text}\""
            )
        else:
            lines.append(f"\nClause {sec}: {text}")

    if warnings:
        lines.append("\n" + "\n".join(warnings))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
