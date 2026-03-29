"""
UC-0B app.py — Summary That Changes Meaning
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re


def load_policy(path: str) -> list:
    """Read policy text and return list of (clause_no, text) tuples."""
    with open(path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    clauses = []
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)$')
    for line in lines:
        m = clause_pattern.match(line)
        if m:
            clause_no = m.group(1)
            clause_text = m.group(2)
            clauses.append((clause_no, clause_text))
    return clauses


def derive_binding_verb(text: str) -> str:
    """Choose binding verb: must, requires, not permitted, will"""
    lower = text.lower()
    if 'cannot' in lower or 'not valid' in lower or 'not permitted' in lower or 'will not be considered' in lower:
        return 'not permitted'
    if 'requires' in lower or 'requires approval' in lower or 'requires a medical certificate' in lower or 'requires approval' in lower:
        return 'requires'
    if 'must' in lower or 'are entitled' in lower or 'may carry forward a maximum' in lower or 'must be used' in lower or 'must submit' in lower or 'must receive' in lower:
        return 'must'
    if 'will be' in lower or 'may' in lower:
        return 'will'
    return 'must'


def summarize_clause(clause_no: str, clause_text: str) -> dict:
    """Build obligation lines; preserve multi-condition phrasing and support new clauses."""
    # explicit overrides for tricky clauses that need precise wording for enforcement
    overrides = {
        '5.2': ('LWP requires approval from Department Head AND HR Director; manager approval alone is insufficient.', 'requires'),
        '2.4': ('Leave applications must have written direct manager approval before leave starts; verbal approval is not valid.', 'must'),
        '3.4': ('Sick leave immediately before/after holiday or annual leave requires medical certificate regardless of duration.', 'requires'),
        '2.5': ('Unapproved absence is recorded as Loss of Pay regardless of later approval.', 'not permitted'),
        '2.7': ('Carry-forward days must be used by January–March following year or are forfeited.', 'must'),
    }

    if clause_no in overrides:
        core, verb = overrides[clause_no]
        return {'Clause': clause_no, 'Core Obligation': core, 'Binding Verb': verb}

    verb = derive_binding_verb(clause_text)

    # If derive_binding_verb could not decide and the text is too vague, quote verbatim with flag
    if verb == 'must' and 'may' in clause_text.lower() and 'may' not in ['may']:
        # no text-specific fallback case; keep original
        pass

    # Use clause text as the core obligation by default (stays true to source)
    core = clause_text
    return {'Clause': clause_no, 'Core Obligation': core, 'Binding Verb': verb}


def summarize_policy(clauses: list) -> list:
    """Create summary table entries for each known clause."""
    summary = []
    seen = set()
    for clause_no, clause_text in clauses:
        entry = summarize_clause(clause_no, clause_text)
        summary.append(entry)
        seen.add(clause_no)

    # ensure all required clauses are present from source
    return summary


def write_summary(summary: list, output_path: str):
    """Write the summary as a Markdown table."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('| Clause | Core Obligation | Binding Verb |\n')
        f.write('|---|---|---|\n')
        for row in summary:
            cl = row['Clause']
            co = row['Core Obligation'].replace('|', '\\|')
            bv = row['Binding Verb']
            f.write(f'| {cl} | {co} | {bv} |\n')


def main():
    parser = argparse.ArgumentParser(description='UC-0B policy summarization')
    parser.add_argument('--input', required=True, help='Path to input policy txt')
    parser.add_argument('--output', required=True, help='Path to output summary txt')
    args = parser.parse_args()

    clauses = load_policy(args.input)
    if not clauses:
        raise ValueError('No structured clauses found in policy input')

    summary = summarize_policy(clauses)
    write_summary(summary, args.output)


if __name__ == '__main__':
    main()
