import argparse
import os
import re
import sys

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

FORBIDDEN_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to"
]


# ---------------- SKILL 1: retrieve_policy ----------------
def retrieve_policy(file_path: str):
    if not os.path.exists(file_path):
        raise ValueError("Error: File path is invalid or file cannot be read")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        raise ValueError("Error: File access failure")

    if not content.strip():
        raise ValueError("Error: Invalid input content (empty file)")

    # Extract clauses like 2.3, 2.4 etc.
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        raise ValueError("Error: Ambiguous or unstructured document")

    structured = {}
    for clause, text in matches:
        structured[clause.strip()] = text.strip()

    return structured


# ---------------- SKILL 2: summarize_policy ----------------
def summarize_policy(structured_clauses: dict):
    # Check for missing clauses
    for clause in REQUIRED_CLAUSES:
        if clause not in structured_clauses:
            raise ValueError(f"Error: Clause omission detected - missing clause {clause}")

    summary_lines = []

    for clause in REQUIRED_CLAUSES:
        text = structured_clauses[clause]

        # Enforcement: no external additions
        for phrase in FORBIDDEN_PHRASES:
            if phrase in text.lower():
                raise ValueError("Error: Scope violation detected")

        # Multi-condition enforcement (Clause 5.2 critical)
        if clause == "5.2":
            if not ("department head" in text.lower() and "hr director" in text.lower()):
                raise ValueError("Error: Condition loss risk in clause 5.2")

        # Attempt safe summarization (minimal transformation)
        summarized = minimal_summarize(text)

        # If summarization risks meaning loss → verbatim + flag
        if is_meaning_changed(text, summarized):
            summary_lines.append(f"{clause}: {text} [VERBATIM - meaning preservation]")
        else:
            summary_lines.append(f"{clause}: {summarized}")

    return "\n".join(summary_lines)


def minimal_summarize(text: str):
    """
    Very conservative summarization: trims whitespace only.
    Avoids clause omission or obligation softening.
    """
    return " ".join(text.split())


def is_meaning_changed(original: str, summarized: str):
    """
    Detect risky summarization by checking loss of key obligation words.
    """
    key_terms = ["must", "requires", "will", "not permitted", "forfeited", "approval"]

    original_lower = original.lower()
    summarized_lower = summarized.lower()

    for term in key_terms:
        if term in original_lower and term not in summarized_lower:
            return True

    # Ensure multi-condition phrases preserved
    if "and" in original_lower and "and" not in summarized_lower:
        return True

    return False


# ---------------- MAIN APP ----------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input policy file path")
    parser.add_argument("--output", required=True, help="Output summary file name")

    args = parser.parse_args()

    try:
        structured = retrieve_policy(args.input)
        summary = summarize_policy(structured)

        # Final enforcement: ensure all clauses present in output
        for clause in REQUIRED_CLAUSES:
            if clause not in summary:
                raise ValueError(f"Error: Final output missing clause {clause}")

        # Write output
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print("Summary generated successfully.")

    except Exception as e:
        print(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()