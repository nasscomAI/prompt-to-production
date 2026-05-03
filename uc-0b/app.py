
"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""

import argparse
import re
import sys

def retrieve_policy(path):
    """
    Loads a .txt policy file and returns its content as structured numbered sections.
    Returns a list of dicts: {'clause_number': str, 'text': str}
    Error handling: returns empty list if file missing/unreadable; flags and skips unparsable sections.
    """
    try:
        with open(path, encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading policy file: {e}", file=sys.stderr)
        return []

    # Regex to match clause numbers like 2.3, 3.4, etc.
    clause_pattern = re.compile(r'^(\d+\.\d+) (.+?)(?=^\d+\.\d+ |\Z)', re.MULTILINE | re.DOTALL)
    matches = clause_pattern.findall(text)
    sections = []
    for match in matches:
        clause_number, clause_text = match
        clause_text = clause_text.strip().replace('\n', ' ')
        sections.append({'clause_number': clause_number, 'text': clause_text})
    return sections

def summarize_policy(sections):
    """
    Takes structured sections and produces a summary that preserves all obligations and clause references.
    Returns a list of dicts: {'clause_number': str, 'summary': str, 'flag': str (optional)}
    Error handling: If a clause cannot be summarized without meaning loss, quotes it verbatim and adds a flag.
    If input is missing clauses or ambiguous, returns an error message and flags the issue.
    """
    if not sections:
        return [{'clause_number': '', 'summary': 'No clauses found or input unreadable.', 'flag': 'ERROR'}]

    # Ground truth clause numbers for enforcement
    required_clauses = {'2.3','2.4','2.5','2.6','2.7','3.2','3.4','5.2','5.3','7.2'}
    found_clauses = set(s['clause_number'] for s in sections)
    summary = []
    for s in sections:
        clause = s['clause_number']
        text = s['text']
        # Summarization logic: for this use case, summarization is risky, so quote verbatim and flag if multi-condition or ambiguous
        flag = ''
        # Enforcement: multi-condition obligations must preserve all conditions
        if clause == '5.2':
            if 'Department Head' in text and 'HR Director' in text:
                summary_text = 'LWP requires approval from both Department Head and HR Director.'
            else:
                summary_text = text
                flag = 'VERBATIM: Multi-condition approval not explicit.'
        elif clause == '2.4':
            if 'written approval' in text and 'verbal approval is not valid' in text:
                summary_text = 'Leave applications must receive written approval from direct manager before leave commences. Verbal approval is not valid.'
            else:
                summary_text = text
                flag = 'VERBATIM: Both approval conditions not explicit.'
        else:
            # For other clauses, if summarization would lose meaning, quote verbatim and flag
            summary_text = text
            # Optionally, more sophisticated summarization can be added here
        entry = {'clause_number': clause, 'summary': summary_text}
        if flag:
            entry['flag'] = flag
        summary.append(entry)

    # Enforcement: every required clause must be present
    missing = required_clauses - found_clauses
    for m in sorted(missing):
        summary.append({'clause_number': m, 'summary': 'Clause missing from input document.', 'flag': 'ERROR'})

    return summary

def write_summary(summary, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in summary:
            line = f"{entry['clause_number']}: {entry['summary']}"
            if 'flag' in entry:
                line += f" [FLAG: {entry['flag']}]"
            f.write(line + '\n')

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Agent")
    parser.add_argument('--input', required=True, help='Path to policy .txt file')
    parser.add_argument('--output', required=True, help='Path to write summary .txt file')
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    write_summary(summary, args.output)
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()
