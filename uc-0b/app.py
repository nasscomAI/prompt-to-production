"""
UC-0B — Summary That Changes Meaning
"""
import argparse
import re


def retrieve_policy(file_path: str) -> list:
    sections = []
    current_section = None
    current_content = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading policy file: {e}")

    for line in lines:
        line = line.rstrip('\n')

        if '═══' in line or line.strip() == '':
            if current_section:
                sections.append({
                    'section_number': current_section,
                    'clause_number': current_section,
                    'content': ' '.join(current_content).strip(),
                    'binding_verb': extract_binding_verb(' '.join(current_content))
                })
                current_section = None
                current_content = []
            continue

        section_match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if section_match:
            if current_section:
                sections.append({
                    'section_number': current_section,
                    'clause_number': current_section,
                    'content': ' '.join(current_content).strip(),
                    'binding_verb': extract_binding_verb(' '.join(current_content))
                })
            current_section = section_match.group(1)
            current_content = [section_match.group(2)]
        elif current_section and line.strip():
            current_content.append(line.strip())

    if current_section:
        sections.append({
            'section_number': current_section,
            'clause_number': current_section,
            'content': ' '.join(current_content).strip(),
            'binding_verb': extract_binding_verb(' '.join(current_content))
        })

    return sections


def extract_binding_verb(text: str) -> str:
    binding_verbs = ['must', 'shall', 'will', 'requires', 'not permitted', 'may', 'are forfeited']
    text_lower = text.lower()
    for verb in binding_verbs:
        if verb in text_lower:
            return verb
    return 'none'


def summarize_policy(sections: list) -> str:
    if not sections:
        return "Error: No sections provided for summarization."

    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("=" * 50)
    summary_lines.append("")

    section_groups = {}
    for section in sections:
        section_num = section['clause_number'].split('.')[0]
        if section_num not in section_groups:
            section_groups[section_num] = []
        section_groups[section_num].append(section)

    for section_num in sorted(section_groups.keys(), key=float):
        section_title = get_section_title(section_num)
        summary_lines.append(f"{section_num}. {section_title}")
        summary_lines.append("-" * 40)

        for s in section_groups[section_num]:
            clause_num = s['clause_number']
            content = s['content']

            if needs_verbatim(clause_num, content):
                summary_lines.append(f"  {clause_num}. [VERBATIM] \"{content}\"")
            else:
                summary_lines.append(f"  {clause_num}. {content}")

        summary_lines.append("")

    return '\n'.join(summary_lines)


def get_section_title(section_num: str) -> str:
    titles = {
        '1': 'PURPOSE AND SCOPE',
        '2': 'ANNUAL LEAVE',
        '3': 'SICK LEAVE',
        '4': 'MATERNITY AND PATERNITY LEAVE',
        '5': 'LEAVE WITHOUT PAY (LWP)',
        '6': 'PUBLIC HOLIDAYS',
        '7': 'LEAVE ENCASHMENT',
        '8': 'GRIEVANCES'
    }
    return titles.get(section_num, 'UNKNOWN SECTION')


def needs_verbatim(clause_num: str, content: str) -> bool:
    verbatim_clauses = ['2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    return clause_num in verbatim_clauses


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)

        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()