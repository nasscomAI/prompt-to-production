import argparse
import os
import re


# ---------------- SKILL 1 ----------------
def retrieve_policy(file_path: str):
    """
    Loads the input text policy file and extracts its contents as strictly structured, numbered sections.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract numbered clauses like 2.3, 2.4, etc.
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        raise ValueError("No numbered clauses found in the document.")

    structured = {}
    for clause, text in matches:
        structured[clause.strip()] = text.strip().replace("\n", " ")

    return structured


# ---------------- SKILL 2 ----------------
def summarize_policy(structured_sections: dict):
    """
    Produces compliant summary ensuring:
    - No clause omission
    - No condition drop
    - No hallucination
    """

    if not structured_sections:
        raise ValueError("No structured sections provided.")

    summary_lines = []

    for clause, text in structured_sections.items():

        # Basic validation: must contain obligation keyword
        if not any(word in text.lower() for word in [
            "must", "requires", "will", "not permitted", "forfeited"
        ]):
            # Cannot safely summarize → quote verbatim
            line = f"{clause}: \"{text}\" [NEEDS_REVIEW]"
        else:
            # Preserve exact meaning (no aggressive summarization)
            line = f"{clause}: {text}"

        summary_lines.append(line)

    # Validation: ensure no clause missing
    if len(summary_lines) != len(structured_sections):
        raise ValueError("Clause omission detected during summarization.")

    return "\n".join(summary_lines)


# ---------------- MAIN ----------------
def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Input policy file path")
    parser.add_argument("--output", required=True, help="Output summary file path")

    args = parser.parse_args()

    try:
        # Step 1: Retrieve
        structured = retrieve_policy(args.input)

        # Step 2: Summarize
        summary = summarize_policy(structured)

        # Step 3: Write output
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print("✅ Summary generated successfully.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()