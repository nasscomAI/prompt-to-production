import argparse

def retrieve_policy(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readlines()


def summarize_policy(lines):
    summary = []
    
    for line in lines:
        line = line.strip()
        
        # Keep numbered clauses
        if line.startswith(("2.", "3.", "5.", "7.")):
            summary.append(line)
    
    return summary


def write_summary(summary_lines, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for line in summary_lines:
            f.write(line + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    policy_lines = retrieve_policy(args.input)
    summary = summarize_policy(policy_lines)
    write_summary(summary, args.output)

    print("Summary generated successfully.")