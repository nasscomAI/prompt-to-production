"""
UC-0B app.py — Policy Document Summarization Agent
Built using RICE (agents.md) + Skills (skills.md) workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import os
from groq import Groq


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# Loads a .txt policy file, returns content as structured numbered sections.
# ---------------------------------------------------------------------------
def retrieve_policy(file_path: str) -> list[dict]:
    """
    Load a plain-text policy document and parse it into structured numbered sections.

    Args:
        file_path: Path to the policy .txt file.

    Returns:
        List of dicts with keys: 'clause_number', 'text'

    Raises:
        FileNotFoundError: If the file path is invalid.
        ValueError: If the file is empty or contains no numbered clauses.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        raise ValueError("Policy file is empty. Cannot proceed.")

    # Parse numbered clauses (e.g., "2.3", "3.2", "5.2", "7.2")
    # Pattern matches clause numbers like X.Y at the start of a line
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+?)(?=^\d+\.\d+\s|\Z)", re.MULTILINE | re.DOTALL)
    matches = clause_pattern.findall(content)

    if not matches:
        raise ValueError(
            "No numbered clauses detected in the document. "
            "Input must be a structured policy document with numbered sections."
        )

    sections = []
    for clause_number, text in matches:
        sections.append({
            "clause_number": clause_number,
            "text": text.strip()
        })

    return sections


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# Takes structured sections, produces compliant summary with clause references.
# ---------------------------------------------------------------------------
def summarize_policy(sections: list[dict]) -> str:
    """
    Summarize structured policy sections using an LLM, enforcing RICE rules.

    Args:
        sections: List of dicts with 'clause_number' and 'text' keys.

    Returns:
        Compliant summary string with clause references preserved.

    Raises:
        ValueError: If sections are empty or malformed.
    """
    if not sections:
        raise ValueError("No sections provided. Cannot summarize empty input.")

    for s in sections:
        if "clause_number" not in s or "text" not in s:
            raise ValueError(f"Malformed section detected: {s}. Each section must have 'clause_number' and 'text'.")

    # Format sections for the prompt
    formatted_sections = "\n\n".join(
        f"Clause {s['clause_number']}:\n{s['text']}" for s in sections
    )

    # System prompt derived from agents.md RICE framework
    system_prompt = """You are a policy document summarization agent. Your operational boundary is strictly limited to producing faithful, clause-complete summaries of HR policy documents. You do not interpret, extend, or editorialize the source material. You operate only on the text provided.

ENFORCEMENT RULES — you must follow ALL of these:
1. Every numbered clause in the source must appear in your summary with its clause reference (e.g., 2.3, 3.2, 5.2).
2. Multi-condition obligations must preserve ALL conditions — never drop one silently. Example: if a clause requires approval from BOTH Department Head AND HR Director, both must appear.
3. Never add information, qualifiers, or context not present in the source document. Zero scope bleed. Do NOT use phrases like "as is standard practice", "typically in government organisations", or "employees are generally expected to".
4. Binding verbs (must, will, requires, not permitted, may, are forfeited) must be preserved exactly — never soften 'must' to 'should' or 'requires' to 'is recommended'.
5. If a clause cannot be summarised without meaning loss, quote it verbatim and flag it with [VERBATIM — meaning loss risk].
6. Do not add any introductory or concluding commentary. Output only the summary."""

    user_prompt = f"""Summarize the following policy clauses. Follow ALL enforcement rules strictly.

{formatted_sections}"""

    client = Groq()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    summary = response.choices[0].message.content.strip()
    return summary


# ---------------------------------------------------------------------------
# Main pipeline: retrieve → summarize → write output
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Policy Document Summarization Agent"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input policy .txt file",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path for the output summary .txt file",
    )
    args = parser.parse_args()

    # Step 1: Retrieve and structure the policy
    print(f"[retrieve_policy] Loading: {args.input}")
    sections = retrieve_policy(args.input)
    print(f"[retrieve_policy] Parsed {len(sections)} clauses.")

    # Step 2: Summarize with enforcement rules
    print("[summarize_policy] Generating compliant summary...")
    summary = summarize_policy(sections)
    print("[summarize_policy] Summary generated.")

    # Step 3: Write output
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"[output] Written to: {args.output}")


if __name__ == "__main__":
    main()
