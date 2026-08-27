"""
UC-0B app.py — HR Policy Summarization Agent
Implements skills: retrieve_policy, summarize_policy
Agent constraints sourced from: agents.md + skills.md
Run: python app.py --input <policy.txt> --output <summary.txt>
"""

import argparse
import re
import sys


# ---------------------------------------------------------------------------
# Agent enforcement rules (mirrors agents.md)
# ---------------------------------------------------------------------------
ENFORCEMENT_RULES = (
    "1. Every numbered clause must be present in the summary.\n"
    "2. Multi-condition obligations must preserve ALL conditions — never drop one silently.\n"
    "3. Never add information not present in the source document.\n"
    "4. If a clause cannot be summarised without meaning loss — quote it verbatim "
    "and prefix the line with [VERBATIM - MEANING LOSS RISK]."
)


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# Source: skills.md → retrieve_policy
# ---------------------------------------------------------------------------
def retrieve_policy(file_path: str) -> str:
    """
    Loads a .txt policy file and returns its content as structured numbered sections.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if the file contains no numbered sections.
        IOError: if the file cannot be read.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"[retrieve_policy] Policy file not found: {file_path}"
        )
    except OSError as exc:
        raise IOError(
            f"[retrieve_policy] Cannot read file '{file_path}': {exc}"
        ) from exc

    # Validate that numbered sections exist (e.g. 2.3, 3.4, 5.2 …)
    if not re.search(r"\b\d+\.\d+", content):
        raise ValueError(
            "[retrieve_policy] File contains no numbered sections. "
            "Halting — do not attempt to infer or reconstruct content."
        )

    return content


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# Source: skills.md → summarize_policy
# ---------------------------------------------------------------------------
def summarize_policy(structured_sections: str) -> str:
    """
    Takes structured numbered policy sections and produces a compliant
    clause-by-clause summary with clause references.

    Returns a prompt string ready to be sent to an LLM of your choice.
    Wire up your preferred LLM call here.
    """
    user_prompt = (
        "You are an HR Policy Summarization Agent.\n\n"
        "ENFORCEMENT RULES (non-negotiable):\n"
        f"{ENFORCEMENT_RULES}\n\n"
        "OUTPUT FORMAT:\n"
        "For each clause produce exactly one line: Clause <number>: <summary>\n"
        "Do not add preamble, footnotes, or any text not tied to a specific clause.\n\n"
        "Summarise the following HR policy document clause by clause:\n"
        "--- POLICY DOCUMENT START ---\n"
        f"{structured_sections}\n"
        "--- POLICY DOCUMENT END ---"
    )
    return user_prompt


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0B — HR Policy Summarization Agent"
    )
    parser.add_argument(
        "--input",
        required=True,
        metavar="POLICY_FILE",
        help="Path to the .txt HR policy document",
    )
    parser.add_argument(
        "--output",
        required=True,
        metavar="SUMMARY_FILE",
        help="Path where the clause-by-clause summary will be written",
    )
    args = parser.parse_args()

    # Skill 1 — retrieve_policy
    print(f"[retrieve_policy] Loading: {args.input}")
    try:
        policy_text = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError, IOError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"[retrieve_policy] Loaded {len(policy_text)} characters.")

    # Skill 2 — summarize_policy
    print("[summarize_policy] Generating clause-by-clause summary …")
    try:
        summary = summarize_policy(policy_text)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    # Write output
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary)
    print(f"[summarize_policy] Summary written to: {args.output}")


if __name__ == "__main__":
    main()
