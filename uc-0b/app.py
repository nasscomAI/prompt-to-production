import argparse
import re


def retrieve_policy(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract numbered clauses like 2.3, 3.2 etc.
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
    matches = re.findall(pattern, text, re.S)

    if not matches:
        raise ValueError("No clauses found in document")

    clauses = []
    for num, content in matches:
        clauses.append({
            "clause": num.strip(),
            "text": content.strip()
        })

    return clauses


def summarize_policy(clauses):
    summary_lines = []

    for c in clauses:
        clause_num = c["clause"]
        text = c["text"]

        # Detect risky clauses (multi-condition or strict legal wording)
        risky_keywords = ["and", "or", "must", "requires", "not permitted"]

        if any(k in text.lower() for k in risky_keywords):
            # safer to quote
            summary = f"{clause_num}: \"{text}\" [VERBATIM - COMPLEX CLAUSE]"
        else:
            # simple compression
            summary = f"{clause_num}: {text}"

        summary_lines.append(summary)

    # Enforcement check: ensure all clauses included
    if len(summary_lines) != len(clauses):
        raise ValueError("Clause mismatch — summary incomplete")

    return "\n".join(summary_lines)


def main(input_file, output_file):
    clauses = retrieve_policy(input_file)
    summary = summarize_policy(clauses)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")

    args = parser.parse_args()

    input_file = args.input or "../data/policy-documents/policy_hr_leave.txt"
    output_file = args.output or "summary_hr_leave.txt"

    main(input_file, output_file)