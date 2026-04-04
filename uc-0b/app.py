import os

def read_policy(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def identify_clauses(policy_text):
    clauses = []
    for line in policy_text.split("\n"):
        line = line.strip()
        if line:
            clauses.append(line)
    return clauses

def generate_summary(clauses):
    if not clauses:
        return "", "FAILED"
    summary = " ".join(clauses[:5])  # Take first 5 clauses as example
    return summary, "OK"

def write_summary(summary, output_path, flag):
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)
        return flag
    except Exception:
        return "FAILED"

if __name__ == "__main__":
    input_file = "data/policy-documents/policy_hr_leave.txt"
    output_file = "summary_hr_leave.txt"

    policy_text = read_policy(input_file)
    clauses = identify_clauses(policy_text)
    summary, flag = generate_summary(clauses)
    result_flag = write_summary(summary, output_file, flag)

    print(f"Summary generated. Flag: {result_flag}")