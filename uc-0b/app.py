"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys


def retrieve_policy(path):
    pattern = re.compile(r'^(\d+(?:\.\d+)*)\s+(.*)')
    clauses = []
    current = None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for raw in f:
                line = raw.rstrip('\n')
                m = pattern.match(line.strip())
                if m:
                    if current:
                        clauses.append(current)
                    number = m.group(1).rstrip('.')
                    text = m.group(2).strip()
                    current = {'number': number, 'text': text}
                else:
                    if current is not None:
                        current['text'] += ' ' + line.strip()
    except FileNotFoundError:
        raise
    if current:
        clauses.append(current)
    # normalize whitespace
    for c in clauses:
        c['text'] = ' '.join(c['text'].split())
    return clauses


def needs_verbatim_flag(text):
    lt = text.lower()
    if 'not permitted' in lt:
        return True
    if 'forfeited' in lt:
        return True
    if 'will be recorded' in lt:
        return True
    if 'requires approval' in lt and ' and ' in lt:
        return True
    if 'department head' in lt and 'hr director' in lt:
        return True
    if len(text) > 140:
        return True
    return False


def summarize_policy(sections):
    summaries = []
    for s in sections:
        num = s['number']
        text = s['text']
        flag = needs_verbatim_flag(text)
        if not flag:
            # simple rephrase heuristics
            if re.search(r'\b(entitled to)\b', text, re.I):
                m = re.search(r'\b(entitled to)\b\s*(.*)', text, re.I)
                if m:
                    summary = 'Entitled to ' + m.group(2)
                else:
                    summary = text
            else:
                summary = text
        else:
            summary = text + ' [VERBATIM_QUOTED]'
        summaries.append({'number': num, 'summary': ' '.join(summary.split())})
    return summaries


def write_summary(out_path, summaries):
    with open(out_path, 'w', encoding='utf-8') as out:
        for s in summaries:
            out.write(f"{s['number']} — {s['summary']}\n")


def main():
    parser = argparse.ArgumentParser(description='UC-0B policy summariser')
    parser.add_argument('--input', required=True, help='Path to policy .txt')
    parser.add_argument('--output', required=True, help='Output summary filename')
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
    except FileNotFoundError:
        print(f"Input file not found: {args.input}", file=sys.stderr)
        sys.exit(2)

    if not sections:
        print('No numbered sections found in input file.', file=sys.stderr)
        sys.exit(3)

    summaries = summarize_policy(sections)
    write_summary(args.output, summaries)


if __name__ == '__main__':
    main()
