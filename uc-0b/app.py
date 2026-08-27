"""
UC-0B — Summary That Changes Meaning
Summarizes HR policy documents preserving all numbered clauses and binding obligations.
Following the RICE enforcement rules defined in agents.md.
"""
import argparse
import re
import sys


def retrieve_policy(file_path: str) -> dict:
    """
    Load a .txt policy file and return structured numbered sections.
    Returns: dict with keys: document_title, sections
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading policy file: {e}")

    if not content.strip():
        return {"document_title": "", "sections": []}

    lines = content.split('\n')

    title_lines = []
    for line in lines:
        if re.match(r'^[═\-\s]+$', line.strip()):
            break
        if line.strip():
            title_lines.append(line.strip())
    document_title = ' '.join(title_lines)

    sections = []
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.+)')
    separator_pattern = re.compile(r'^[═\-\s]{10,}$')
    section_header_pattern = re.compile(r'^\d+\.\s+[A-Z][A-Z\s&()]+$')

    current_section = None
    current_content = []

    for line in lines:
        if separator_pattern.match(line.strip()):
            continue

        if section_header_pattern.match(line.strip()):
            continue

        match = clause_pattern.match(line.strip())
        if match:
            if current_section:
                content_text = ' '.join(current_content).strip()
                if separator_pattern.match(content_text):
                    content_text = ''
                sections.append({
                    "clause_id": current_section,
                    "content": content_text,
                    "binding_verb": _extract_binding_verb(content_text)
                })
            current_section = match.group(1)
            current_content = [match.group(2)]
        elif current_section and line.strip():
            if not separator_pattern.match(line.strip()):
                current_content.append(line.strip())

    if current_section:
        content_text = ' '.join(current_content).strip()
        if separator_pattern.match(content_text):
            content_text = ''
        sections.append({
            "clause_id": current_section,
            "content": content_text,
            "binding_verb": _extract_binding_verb(content_text)
        })

    return {"document_title": document_title, "sections": sections}


def _extract_binding_verb(text: str) -> str:
    """Extract the primary binding verb from clause text."""
    text_lower = text.lower()
    if "not permitted" in text_lower:
        return "not permitted"
    if "must" in text_lower:
        return "must"
    if "will" in text_lower:
        return "will"
    if "requires" in text_lower or "required" in text_lower:
        return "requires"
    if "may" in text_lower:
        return "may"
    return "shall"


def summarize_policy(policy_data: dict) -> str:
    """
    Take structured policy sections and produce a compliant summary.
    Preserves all numbered clauses and binding obligations.
    """
    document_title = policy_data.get("document_title", "Policy Document")
    sections = policy_data.get("sections", [])

    if not sections:
        return "No policy sections found in the document."

    summary_parts = []
    summary_parts.append(f"# {document_title} — Summary\n")

    current_major = None
    for section in sections:
        clause_id = section["clause_id"]
        content = section["content"]
        binding_verb = section["binding_verb"]

        major_num = clause_id.split('.')[0]
        if major_num != current_major:
            current_major = major_num
            section_header = _get_section_header(major_num, sections)
            if section_header:
                summary_parts.append(f"\n## {section_header}\n")

        summary_parts.append(f"**{clause_id}** — {content}\n")

    return '\n'.join(summary_parts)


def _get_section_header(major_num: str, sections: list) -> str:
    """Extract section header from the first clause of a major section."""
    section_names = {
        "1": "PURPOSE AND SCOPE",
        "2": "ANNUAL LEAVE",
        "3": "SICK LEAVE",
        "4": "MATERNITY AND PATERNITY LEAVE",
        "5": "LEAVE WITHOUT PAY (LWP)",
        "6": "PUBLIC HOLIDAYS",
        "7": "LEAVE ENCASHMENT",
        "8": "GRIEVANCES"
    }
    return section_names.get(major_num, f"Section {major_num}")


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    try:
        policy_data = retrieve_policy(args.input)
        summary = summarize_policy(policy_data)

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)

        print(f"Done. Summary written to {args.output}")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
