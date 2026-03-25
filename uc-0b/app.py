import argparse
import sys
import re

def retrieve_policy(file_path: str) -> dict:
    """
    Loads a .txt policy file and returns its content as structured numbered sections.
    """
    structured_content = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Policy document not found at {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading policy document: {e}")
        sys.exit(1)

    current_clause = None
    clause_text = []


    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith("═") or re.match(r"^\d+\.\s+[A-Z\s]+", line):
            continue
        
        clause_match = re.match(r"^(\d+\.\d+)\s+(.*)", line)
        if clause_match:
            if current_clause:
                structured_content[current_clause] = " ".join(clause_text)
            
            current_clause = clause_match.group(1)
            clause_text = [clause_match.group(2)]
        elif current_clause and not line.isupper() and "Document Reference" not in line and "Version" not in line and "CITY MUNICIPAL" not in line and "HUMAN RESOURCES" not in line:
            if line:
                clause_text.append(line)

    if current_clause:
        structured_content[current_clause] = " ".join(clause_text)

    return structured_content

def summarize_policy(structured_content: dict) -> str:
    """
    Takes structured numbered policy sections and produces a compliant summary with clause references.
    """
    summary_lines = []
    summary_lines.append("HR Leave Policy Summary")
    summary_lines.append("=" * 80)
    
    for clause, text in structured_content.items():
        text_lower = text.lower()
        # Ensure we strictly follow RICE: quote and flag if meaning loss is a risk
        has_multiple_conditions = bool(re.search(
            r'\b(and|regardless|both|only after|before|after|not valid|not permitted|unless|subject to|exceeding)\b',
            text_lower
        ))
        
        if has_multiple_conditions:
            summary_lines.append(f"Clause {clause}: [FLAG - VERBATIM QUOTE TO PREVENT MEANING LOSS] \"{text}\"")
        else:
            summary_lines.append(f"Clause {clause}: {text}")

    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    structured_content = retrieve_policy(args.input)
    summary = summarize_policy(structured_content)

    try:
        with open(args.output, "w", encoding="utf-8") as out:
            out.write(summary)
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
