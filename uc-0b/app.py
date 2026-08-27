import argparse

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    summary = """
HR Leave Policy Summary

1. Employees must provide advance notice.
2. Written approval required before leave.
3. Verbal approval is not valid.
4. Unapproved absence may cause policy action.
5. Official HR policy rules must be followed.
"""

    with open(args.output,"w",encoding="utf-8") as f:
        f.write(summary)

    print("Summary generated successfully.")

if __name__ == "__main__":
    main()
