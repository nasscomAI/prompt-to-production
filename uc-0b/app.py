import argparse
import re

def load_policy(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_clauses(policy_text):
    """
    Extract numbered clauses like 2.3, 3.4, 5.2 etc.
    """
    pattern = r"(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)"
    matches = re.findall(pattern, policy_text, re.DOTALL)

    clauses = {}
    for number, text in matches:
        clauses[number] = text.strip().replace("\n", " ")
    return clauses

def summarize_clause(number, text):
    """
    Simple deterministic summarization preserving key obligations.
    """
    text = text.replace("shall", "must")
    text = text.replace("will be", "will be")
    text = text.replace("is required to", "must")

    return f"{number} → {text}"

def generate_summary(clauses):
    summary_lines = []
    for number in sorted(clauses.keys(), key=lambda x: float(x)):
        summary_lines.append(summarize_clause(number, clauses[number]))
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Policy input file")
    parser.add_argument("--output", required=True, help="Summary output file")
    args = parser.parse_args()

    policy_text = load_policy(args.input)
    clauses = extract_clauses(policy_text)
    summary = generate_summary(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print("✅ Summary generated without OpenAI API")

if __name__ == "__main__":
    main()