import argparse

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    summary = """
HR Leave Policy Summary

1. Employees must provide advance notice for leave requests.
2. Written approval is required before leave starts.
3. Verbal approval alone is not valid.
4. Unapproved absence may lead to policy action.
5. Leave requests must follow official HR rules.
"""

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary file generated successfully.")

if __name__ == "__main__":
    main()
