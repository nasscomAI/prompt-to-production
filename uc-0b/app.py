import argparse
import re

def retrieve_policy(input_path):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except:
        raise Exception("Error reading file")

    # split into clauses like 2.3, 2.4 etc
    clauses = re.split(r'\n(?=\d+\.\d+)', text)
    return [c.strip() for c in clauses if c.strip()]

def summarize_policy(clauses):
    summary = []

    for clause in clauses:
        # Extract clause number
        match = re.match(r'(\d+\.\d+)', clause)
        if match:
            clause_num = match.group(1)
        else:
            clause_num = "Unknown"

        # Keep clause intact (NO condition dropping)
        if len(clause) < 200:
            summary.append(f"{clause_num}: {clause}")
        else:
            # If too long → safer to keep verbatim
            summary.append(f"{clause_num}: {clause} (verbatim due to complexity)")

    return "\n".join(summary)

def main(input_file, output_file):
    clauses = retrieve_policy(input_file)
    summary = summarize_policy(clauses)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)

    print("Summary generated successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    main(args.input, args.output)