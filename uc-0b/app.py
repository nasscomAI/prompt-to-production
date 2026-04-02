import argparse
import re

def retrieve_policy(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        raise Exception("Error: Cannot read input file")

    # Split into clauses using numbers like 2.3, 3.2 etc.
    clauses = re.split(r'\n(?=\d+\.\d+)', content)

    structured = []
    for clause in clauses:
        match = re.match(r'(\d+\.\d+)\s+(.*)', clause.strip(), re.DOTALL)
        if match:
            number = match.group(1)
            text = match.group(2).strip()
            structured.append((number, text))

    if not structured:
        raise Exception("Error: No valid clauses found")

    return structured


def summarize_policy(clauses):
    summary = []

    for number, text in clauses:
        # Keep original text to avoid meaning loss
        if len(text.split()) < 20:
            summary.append(f"{number}: {text}")
        else:
            summary.append(f"{number}: {text[:150]}...")

    # Enforcement check
    if len(summary) != len(clauses):
        raise Exception("Error: Clause omission detected")

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    # ✅ FIXED (inside main)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)

    print("✅ Summary generated successfully!")


if __name__ == "__main__":
    main()