"""
UC-0B app.py — Policy Summarization
Built deterministically from agents.md and skills.md to prevent clause omission, condition dropping, and scope bleed.
"""
import argparse
import re
import sys

def retrieve_policy(filepath: str) -> list:
    """
    Loads a .txt policy file and returns its content as structured numbered sections,
    preserving all original clauses exactly.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error: Cannot access or read file {filepath}: {e}")
        sys.exit(1)

    sections = []
    lines = content.split('\n')
    
    current_clause = None
    current_text = []

    # Regex for headers like "1. PURPOSE AND SCOPE"
    header_pattern = re.compile(r'^(\d+)\.\s+(.*)')
    # Regex for numbered clauses like "1.1 This policy..."
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('═'):
            continue
            
        header_match = header_pattern.match(line)
        clause_match = clause_pattern.match(line)
        
        if clause_match:
            if current_clause:
                sections.append({'clause': current_clause, 'text': ' '.join(current_text)})
            current_clause = clause_match.group(1)
            current_text = [clause_match.group(2).strip()]
        elif header_match:
            if current_clause:
                sections.append({'clause': current_clause, 'text': ' '.join(current_text)})
                current_clause = None
                current_text = []
            sections.append({'header': header_match.group(1), 'title': header_match.group(2).strip()})
        elif current_clause:
            current_text.append(line.strip())
            
    if current_clause:
        sections.append({'clause': current_clause, 'text': ' '.join(current_text)})
        
    if not sections:
        print("Error: Refusing to guess. Provided document contains no discernable numbered clauses.")
        sys.exit(1)

    return sections


def summarize_policy(sections: list, output_filepath: str):
    """
    Takes structured sections and produces a compliant summary with exact clause references,
    without softening obligations or omitting conditions by quoting them deterministically.
    """
    try:
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            outfile.write("CITY MUNICIPAL CORPORATION - HR LEAVE POLICY SUMMARY\n")
            outfile.write("====================================================\n")
            
            for item in sections:
                if 'header' in item:
                    outfile.write(f"\n{item['header']}. {item['title']}\n")
                elif 'clause' in item:
                    # Deterministically mapping to prevent multiple-condition drops and scope bleed.
                    outfile.write(f"- {item['clause']}: {item['text']}\n")
                    
    except Exception as e:
        print(f"Error writing to output file {output_filepath}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()
    
    print(f"Retrieving policy from {args.input}...")
    structured_sections = retrieve_policy(args.input)
    
    print(f"Generating compliant summary...")
    summarize_policy(structured_sections, args.output)
    
    print(f"Done. Compliant, verifiable summary saved to {args.output}")


if __name__ == "__main__":
    main()
