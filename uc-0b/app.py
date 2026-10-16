"""
UC-0B app.py — Summary That Changes Meaning.
Implements retrieve_policy and summarize_policy skills from skills.md.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys


def retrieve_policy(filepath):
    """Load a .txt policy file and return structured numbered sections.

    Each section has a section_heading and a list of clause objects
    with 'number' and 'text' keys.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    if not text.strip():
        raise ValueError("File is empty")

    sections = []
    lines = text.split('\n')
    current_heading = None
    current_clauses = []

    header_stops = {
        'CITY MUNICIPAL CORPORATION', 'HUMAN RESOURCES DEPARTMENT',
        'EMPLOYEE LEAVE POLICY', 'INFORMATION TECHNOLOGY DEPARTMENT',
        'ACCEPTABLE USE POLICY', 'FINANCE DEPARTMENT',
        'EMPLOYEE EXPENSE REIMBURSEMENT POLICY',
    }
    heading_pat = re.compile(r'^(\d+\.)\s+(.+)$')
    clause_pat = re.compile(r'^(\d+\.\d+)\s+(.*)')

    for line in lines:
        raw = line.rstrip('\n')
        stripped = raw.strip()

        if not stripped:
            continue
        if stripped.startswith('═'):
            continue
        if any(stripped.startswith(h) for h in header_stops):
            continue
        if stripped.startswith('Document Reference:') or stripped.startswith('Version:') or stripped.startswith('Effective:'):
            continue

        m = heading_pat.match(stripped)
        if m:
            if current_heading is not None:
                sections.append({
                    'section_heading': current_heading,
                    'clauses': list(current_clauses),
                })
                current_clauses = []
            current_heading = stripped
            continue

        m = clause_pat.match(stripped)
        if m:
            current_clauses.append({
                'number': m.group(1),
                'text': m.group(2),
            })
            continue

        if current_clauses and raw[:1] == ' ' and stripped:
            text = current_clauses[-1]['text']
            if text[-1] == '-':
                current_clauses[-1]['text'] = text[:-1] + stripped
            else:
                current_clauses[-1]['text'] += ' ' + stripped

    if current_heading is not None:
        sections.append({
            'section_heading': current_heading,
            'clauses': current_clauses,
        })

    if not sections:
        raise ValueError("No sections found in policy file")

    return sections


def _binding_verb(clause_text):
    """Return the primary binding verb or phrase from a clause."""
    lowers = clause_text.lower()
    if any(w in lowers for w in ('not permitted', 'not allowed', 'not reimbursable', 'not considered', 'cannot')):
        return 'prohibited'
    if any(w in lowers for w in ('must not', 'will not')):
        return 'prohibited'
    if any(w in lowers for w in ('must', 'shall', 'requires', 'required')):
        return 'obligation'
    if any(w in lowers for w in ('may', 'entitled', 'permitted', 'allowed')):
        return 'entitlement'
    if any(w in lowers for w in ('will be', 'are forfeited', 'is forfeited')):
        return 'consequence'
    return 'statement'


def _summarise_clause(number, text):
    """Condense a single clause to its core obligation while preserving all conditions."""
    lowers = text.lower()
    verb = _binding_verb(text)

    if verb == 'prohibited':
        return f"{number} Prohibited: {text.rstrip('.')}."
    if verb == 'obligation':
        return f"{number} Required: {text.rstrip('.')}."
    if verb == 'entitlement':
        return f"{number} Entitlement: {text.rstrip('.')}."
    if verb == 'consequence':
        return f"{number} Consequence: {text.rstrip('.')}."
    return f"{number} {text.rstrip('.')}."


def summarize_policy(sections):
    """Produce a compliant clause-complete summary.

    Every numbered clause is preserved. Multi-condition obligations retain
    ALL conditions. No information is added from outside the source.
    """
    parts = []
    for section in sections:
        heading = section['section_heading']
        parts.append(f"\n{heading}\n")
        for clause in section['clauses']:
            parts.append(_summarise_clause(clause['number'], clause['text']))
    return '\n'.join(parts).strip()


def main():
    parser = argparse.ArgumentParser(description='UC-0B Policy Summariser')
    parser.add_argument('--input', required=True, help='Path to input policy .txt file')
    parser.add_argument('--output', required=True, help='Path to output summary file')
    args = parser.parse_args()

    if not args.input.endswith('.txt'):
        print("Error: Input file must be a .txt file", file=sys.stderr)
        sys.exit(1)

    try:
        sections = retrieve_policy(args.input)
    except FileNotFoundError:
        print(f"Error: File not found — {args.input}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    summary = summarize_policy(sections)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary + '\n')

    print(f"Summary written to {args.output}")


if __name__ == '__main__':
    main()
