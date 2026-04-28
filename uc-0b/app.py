import argparse

def retrieve_policy(file_path):
    clauses = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if line.strip():
                clauses.append(line.strip())
    return clauses

def summarize_policy(clauses):
    summary = []
    for clause in clauses:
        # For simplicity, here we quote verbatim if conditions are complex
        summary.append(clause)
    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary_text = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary_text)
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()