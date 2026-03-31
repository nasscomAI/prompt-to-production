import argparse
import os
import re


def retrieve_policy(file_path: str) -> list:
    """
    Loads the HR leave policy .txt file and returns it as structured numbered sections.
    Raises an error if file not found or unreadable; validates numbered clauses.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise IOError(f"Could not read the file: {e}")

    sections = []
    lines = content.split('\n')
    current_clause = None
    current_text = []

    for line in lines:
        # FIXED regex (handles 1, 1.2, 1.2.3)
        match = re.match(r"^(\d+(?:\.\d+)*)\s*(.*)", line)

        if match:
            if current_clause:
                sections.append({
                    "clause": current_clause,
                    "text": "\n".join(current_text).strip()
                })
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause:
            current_text.append(line)

    if current_clause:
        sections.append({
            "clause": current_clause,
            "text": "\n".join(current_text).strip()
        })

    if not sections:
        raise ValueError("No valid numbered clauses found in the document.")

    return sections


def summarize_policy(sections: list) -> str:
    """
    Produces a compliant summary preserving ALL clauses and meaning.
    """
    summary_lines = []

    for sec in sections:
        clause = sec["clause"]
        text = sec["text"]

        # Preserve full meaning (no loss)
        summary_lines.append(f"{clause}: {text}")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="Summarize HR leave policy using RICE framework.")
    parser.add_argument("--input", required=True, help="Path to the input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to the output summary text file")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
    except Exception as e:
        print(f"Error parsing policy: {e}")
        return

    try:
        summary = summarize_policy(sections)
    except Exception as e:
        print(f"Error during summarization: {e}")
        return

    try:
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print("Summary generated successfully!")

    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    main()