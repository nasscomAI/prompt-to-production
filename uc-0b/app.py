import argparse

def retrieve_policy(file_path):
    with open(file_path, "r") as f:
        return f.readlines()

def summarize_policy(lines):
    summary = []
    for line in lines:
        line = line.strip()
        if line:
            summary.append(line)
    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    policy_lines = retrieve_policy(args.input)
    summary = summarize_policy(policy_lines)

    with open(args.output, "w") as f:
        f.write(summary)

if __name__ == "__main__":
    main()
