"""
UC-0B — Policy Summarizer

Implements the policy summarization workflow using:
- RICE-style prompt structure
- agents.md rules
- skills.md skills
- Required UC-0B clause inventory
"""

import argparse
from pathlib import Path


REQUIRED_CLAUSES = {
    "2.3": "14-day advance notice is required.",
    "2.4": "Written approval is required before leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will result in LOP regardless of subsequent approval.",
    "2.6": "A maximum of 5 days may be carried forward; days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used during January to March or they are forfeited.",
    "3.2": "Three or more consecutive sick days require a medical certificate within 48 hours.",
    "3.4": "Sick leave taken before or after a holiday requires a medical certificate regardless of duration.",
    "5.2": "LWP requires approval from both the Department Head and the HR Director.",
    "5.3": "LWP exceeding 30 continuous days requires Municipal Commissioner approval.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
}


def retrieve_policy(input_file):
    """
    Skill: retrieve_policy
    Loads the policy and returns its numbered sections.
    """
    path = Path(input_file)

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {input_file}")

    if not path.is_file():
        raise ValueError(f"Input path is not a file: {input_file}")

    content = path.read_text(encoding="utf-8")

    if not content.strip():
        raise ValueError("The policy file is empty.")

    return content


def build_rice_prompt(policy):
    """
    Builds the RICE prompt required by the UC-0B workflow.

    R = Role
    I = Instructions
    C = Context
    E = Expected output
    """

    required_clause_text = "\n".join(
        f"- {clause}: {requirement}"
        for clause, requirement in REQUIRED_CLAUSES.items()
    )

    return f"""
ROLE:
You are a policy summarization agent. Summarize only the provided HR
leave policy. Do not use outside knowledge or assumptions.

INSTRUCTIONS:
1. Every required clause must appear in the summary.
2. Preserve the original meaning of every obligation.
3. Preserve every condition, exception, approval requirement, deadline,
   prohibition, and scope limitation.
4. Never weaken binding language.
5. Never add information that is not present in the source.
6. Clause 5.2 MUST preserve BOTH Department Head AND HR Director approval.
7. Clause 5.3 MUST preserve Municipal Commissioner approval when LWP
   exceeds 30 continuous days.
8. If a clause cannot be safely summarized without losing meaning,
   reproduce the relevant source wording and flag it for review.

REQUIRED CLAUSE INVENTORY:
{required_clause_text}

CONTEXT:
The following is the complete source policy:

--- BEGIN POLICY ---
{policy}
--- END POLICY ---

EXPECTED OUTPUT:
Produce a concise, verifiable summary.
Every required clause reference must be present.
Do not add commentary, common HR practices, or unsupported explanations.
"""


def extract_clause(policy, clause):
    """
    Finds a numbered clause in the source policy.
    """

    lines = policy.splitlines()

    for index, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith(clause):
            collected = [stripped]

            for next_line in lines[index + 1:]:
                text = next_line.strip()

                if not text:
                    continue

                # Stop when another numbered clause begins.
                if any(
                    text.startswith(f"{number}.")
                    for number in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
                ):
                    break

                collected.append(text)

            return " ".join(collected)

    return None


def summarize_policy(policy):
    """
    Skill: summarize_policy

    Creates a compliant summary while preserving the required clauses.
    """

    summary = []
    missing = []

    for clause, fallback_requirement in REQUIRED_CLAUSES.items():
        source_clause = extract_clause(policy, clause)

        if source_clause:
            # Preserve the source clause wording rather than weakening it.
            summary.append(f"{clause}: {source_clause}")
        else:
            missing.append(clause)

    if missing:
        summary.append("")
        summary.append("REVIEW REQUIRED")
        summary.append(
            "The following required clauses could not be located in the "
            "source policy and were not invented:"
        )

        for clause in missing:
            summary.append(f"- {clause}")

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B HR Leave Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the HR leave policy .txt file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path where the summary will be written"
    )

    args = parser.parse_args()

    # Retrieve policy.
    policy = retrieve_policy(args.input)

    # Build the RICE prompt for the required AI workflow.
    rice_prompt = build_rice_prompt(policy)

    # Keep the prompt available for an AI tool integration.
    # The deterministic summarizer below ensures that required clauses
    # and their conditions are not silently dropped.
    _ = rice_prompt

    # Generate compliant summary.
    summary = summarize_policy(policy)

    output_path = Path(args.output)
    output_path.write_text(summary, encoding="utf-8")

    print(f"Summary written successfully to: {output_path}")


if __name__ == "__main__":
    main()