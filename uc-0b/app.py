import argparse
import os
import re
import sys

REQUIRED_CLAUSES = ["2.3","2.4","2.5","2.6","2.7","3.2","3.4","5.2","5.3","7.2"]

class PolicyError(Exception):
    pass

# Skill 1: retrieve_policy

def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        raise PolicyError(f"Input file not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        raise PolicyError(f"Unable to read file: {str(e)}")

    # Extract clauses like 2.3, 3.2 etc.
    pattern = re.compile(
    r"""(?P<clause>\d+\.\d+)\s+(?P<content>.*?)(?=\n\d+\.\d+\s+|$)""",
    re.DOTALL
)

    matches = pattern.findall(text)

    if not matches:
        raise PolicyError("Clause extraction failed; refusing to guess structure")

    structured = {}
    for clause, content in matches:
        structured[clause.strip()] = content.strip()

    return structured


# Skill 2: summarize_policy

def summarize_policy(structured):
    # Check all clauses present
    for c in REQUIRED_CLAUSES:
        if c not in structured:
            raise PolicyError(f"Missing required clause: {c}")

    lines = []

    for clause in REQUIRED_CLAUSES:
        content = structured[clause]

        # Enforcement: Never alter meaning → use verbatim as safe fallback
        summary_line = f"Clause {clause}: {content}"

        # Check Clause 5.2 dual approval explicitly
        if clause == "5.2":
            if not ("Department Head" in content and "HR Director" in content):
                raise PolicyError("Clause 5.2 missing dual approval condition")

        # Scope bleed check
        forbidden = ["typically","generally expected","standard practice"]
        for word in forbidden:
            if word in content.lower():
                raise PolicyError("Scope bleed detected in content")

        lines.append(summary_line)

    return "".join(lines)


# Main app

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    try:
        structured = retrieve_policy(args.input)
        summary = summarize_policy(structured)

        # Ensure output directory exists
        out_path = args.output
        os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else '.', exist_ok=True)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(summary)

        print("Summary generated successfully")

    except PolicyError as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
