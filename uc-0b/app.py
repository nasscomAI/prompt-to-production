"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

import os
import sys

def retrieve_policy(policy_path):
    """
    Loads a .txt policy file and returns its content as structured, numbered sections.
    """
    if not os.path.exists(policy_path):
        return [], f"Error: File not found: {policy_path}"
    try:
        with open(policy_path, encoding='utf-8') as f:
            lines = f.readlines()
        sections = []
        current = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Detect clause number (e.g., 2.3, 3.2, etc.)
            if line[:3].replace('.', '').isdigit() and line[1] == '.' and line[2].isdigit():
                if current:
                    sections.append(current)
                current = {'clause': line[:3], 'text': line[3:].strip()}
            elif current:
                current['text'] += ' ' + line
        if current:
            sections.append(current)
        return sections, None
    except Exception as e:
        return [], f"Error reading file: {str(e)}"

def summarize_policy(sections):
    """
    Takes structured sections and produces a compliant summary with clause references.
    Preserves all obligations and conditions. Flags verbatim quotes if summarization would lose meaning.
    """
    summary = []
    for section in sections:
        clause = section.get('clause', '')
        text = section.get('text', '')
        # Simple rule: if text is too complex or ambiguous, quote verbatim and flag
        if any(word in text.lower() for word in ['and/or', 'unless', 'except', 'provided that']):
            summary.append(f"Clause {clause}: \"{text}\" [VERBATIM - FLAGGED]")
        else:
            summary.append(f"Clause {clause}: {text}")
    return '\n'.join(summary)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument('--input', required=True, help='Path to policy text file')
    parser.add_argument('--output', required=True, help='Path to write summary output')
    args = parser.parse_args()

    sections, error = retrieve_policy(args.input)
    if error:
        print(error)
        sys.exit(1)
    if not sections:
        print("No sections found in policy file.")
        sys.exit(1)

    summary = summarize_policy(sections)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
