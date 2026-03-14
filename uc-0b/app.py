import os

INPUT_FILE = "../data/policy-documents/policy_hr_leave.txt"
OUTPUT_FILE = "summary_hr_leave.txt"


def read_document(file_path):
    """Reads the policy document"""
    if not os.path.exists(file_path):
        raise FileNotFoundError("Policy document not found")

    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()


def extract_clauses(lines):
    """Extracts meaningful clauses"""
    clauses = []
    for line in lines:
        line = line.strip()
        if line:
            clauses.append(line)
    return clauses


def generate_summary(clauses):
    """Generates a concise summary"""
    if not clauses:
        return "No clauses available to summarize."

    summary = clauses[:8]   # take first few important clauses
    return "\n".join(summary)


def main():
    try:
        lines = read_document(INPUT_FILE)
        clauses = extract_clauses(lines)
        summary = generate_summary(clauses)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(summary)

        print("Summary created:", OUTPUT_FILE)

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()