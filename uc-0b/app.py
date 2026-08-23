import argparse

def summarize_policy(text: str) -> str:
    """
    Simple summarizer: keeps each line as a summarized clause
    """

    lines = text.split("\n")
    summary = []

    for line in lines:
        line = line.strip()
        if line:
            summary.append("- " + line)

    return "\n".join(summary)


def main(input_path: str, output_path: str):

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            policy_text = f.read()

        summary = summarize_policy(policy_text)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)

        print("Summary created successfully.")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    main(args.input, args.output)