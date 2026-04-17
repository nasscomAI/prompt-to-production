"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

def main():
    parser = argparse.ArgumentParser(description="UC-0B Document Summarizer")
    parser.add_argument("--input", required=True, help="Path to input document (e.g., policy_hr_leave.txt)")
    parser.add_argument("--output", required=True, help="Path to write summary output (e.g., summary_hr_leave.txt)")
    args = parser.parse_args()

    try:
        with open(args.input, encoding="utf-8") as infile:
            document_text = infile.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    summary = summarize_document(document_text)

    try:
        with open(args.output, "w", encoding="utf-8") as outfile:
            outfile.write(summary)
        print(f"Summary written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")


def summarize_document(document_text: str) -> str:
    """
    Summarizes a policy or procedural document, highlighting all changes that alter the original meaning.
    This is a placeholder implementation. Replace with actual logic as needed.
    """
    if not document_text.strip():
        return "[ERROR] Input document is empty or unreadable."
    # Placeholder: just echo the input for now, with a note
    return "[SUMMARY START]\n(This is a placeholder summary. Replace with actual logic.)\n" + document_text[:500] + "\n[SUMMARY END]"

if __name__ == "__main__":
    main()
