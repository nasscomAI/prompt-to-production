"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

# Skill: retrieve_policy
def retrieve_policy(file_path):
    sections = []
    with open(file_path, 'r') as f:
        content = f.read()
    # Simple clause extraction: match numbered clauses (e.g., 2.3, 2.4, etc.)
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)$', re.MULTILINE)
    for match in clause_pattern.finditer(content):
        sections.append({'clause': match.group(1), 'text': match.group(2)})
    return sections

# Skill: summarize_policy
ENFORCEMENT_CLAUSES = {
    '2.3': '14-day advance notice required',
    '2.4': 'Written approval required before leave commences. Verbal not valid.',
    '2.5': 'Unapproved absence = LOP regardless of subsequent approval',
    '2.6': 'Max 5 days carry-forward. Above 5 forfeited on 31 Dec.',
    '2.7': 'Carry-forward days must be used Jan–Mar or forfeited',
    '3.2': '3+ consecutive sick days requires medical cert within 48hrs',
    '3.4': 'Sick leave before/after holiday requires cert regardless of duration',
    '5.2': 'LWP requires Department Head AND HR Director approval',
    '5.3': 'LWP >30 days requires Municipal Commissioner approval',
    '7.2': 'Leave encashment during service not permitted under any circumstances'
}

def summarize_policy(sections):
    summary = []
    found_clauses = {s['clause']: s['text'] for s in sections}
    ENFORCEMENT_PHRASES = {
        '2.3': ['14-day advance notice'],
        '2.4': ['written approval', 'leave commences', 'verbal not valid'],
        '2.5': ['unapproved absence', 'LOP', 'subsequent approval'],
        '2.6': ['carry forward', 'maximum', 'forfeited'],
        '2.7': ['carry-forward', 'used', 'forfeited'],
        '3.2': ['sick days', 'medical certificate', '48 hours'],
        '3.4': ['sick leave', 'holiday', 'certificate'],
        '5.2': ['Department Head', 'HR Director', 'approval'],
        '5.3': ['LWP', '30 days', 'Municipal Commissioner'],
        '7.2': ['leave encashment', 'not permitted', 'service']
    }
    for clause, phrases in ENFORCEMENT_PHRASES.items():
        if clause in found_clauses:
            text = found_clauses[clause]
            matches = sum(phrase.lower() in text.lower() for phrase in phrases)
            if matches >= len(phrases) - 1:  # Allow one phrase to be missing before flagging
                summary.append(f"{clause}: {text}")
            else:
                summary.append(f"{clause}: [VERBATIM] {text} [FLAGGED: clause may lose meaning]")
        else:
            summary.append(f"{clause}: [MISSING] Clause not found in policy document.")
    return '\n'.join(summary)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    with open(args.output, 'w') as f:
        f.write(summary)
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
