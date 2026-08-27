import sys

def summarize_policy(input_file, output_file):
    with open(input_file, "r") as f:
        text = f.readlines()

    summary = []

    for line in text:
        if line.strip():
            summary.append(line.strip())

    with open(output_file, "w") as f:
        for line in summary:
            f.write(line + "\n")

    print("Summary generated successfully.")

if __name__ == "__main__":
    input_file = "../data/policy-documents/policy_hr_leave.txt"
    output_file = "summary_hr_leave.txt"

    summarize_policy(input_file, output_file)
