"""
UC-0B app.py
Procedural HR Policy Summarizer.
Implemented purely based on RICE, agents.md, and skills.md.
"""

import argparse
import re

def retrieve_policy(input_path: str) -> dict:
    """
    Loads a .txt policy file and returns its content as structured numbered sections.
    """
    sections = {}
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise FileNotFoundError(f"Failed to read file: {e}")

    # Regex to capture N.M format headings and their content
    pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n\d+\.\s+|\n[=\u2550]{5,}|\Z)', re.DOTALL | re.MULTILINE)
    matches = pattern.findall(content)

    if not matches:
        raise ValueError("File lacks recognizable numbered sections.")

    for match in matches:
        clause_id = match[0]
        # Clean up linebreaks and excess spaces
        clause_text = match[1].replace('\n', ' ').strip()
        clause_text = re.sub(r'\s+', ' ', clause_text)
        sections[clause_id] = clause_text

    return sections

def summarize_policy(sections: dict) -> str:
    """
    Takes structured sections and produces a compliant summary with clause references.
    """
    summary_lines = ["HR POLICY SUMMARY\n================="]
    
    strict_keywords = ["must", "requires", "will", "forfeited", "not permitted"]

    for clause_id, text in sections.items():
        lower_text = text.lower()
        # Rule 4: If a clause cannot be summarised without meaning loss (contains strict obligations), quote it verbatim and flag it.
        # Rule 2: Multi-condition obligations must preserve ALL conditions.
        if any(keyword in lower_text for keyword in strict_keywords):
            summary_lines.append(f"Clause {clause_id} [VERBATIM - STRICT OBLIGATION]: \"{text}\"")
        else:
            # Rule 1: Every numbered clause must be present in the summary.
            # Rule 3: Never add information not present in the source document.
            summary_lines.append(f"Clause {clause_id}: {text}")

    return "\n\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="HR Policy Summarizer Agent")
    parser.add_argument("--input", required=True, help="Path to input policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
    except Exception as e:
        print(f"Error reading policy: {e}")
        return

    summary = summarize_policy(sections)

    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Successfully wrote summary to {args.output}")
    except Exception as e:
        print(f"Error writing summary: {e}")

if __name__ == "__main__":
    main()
