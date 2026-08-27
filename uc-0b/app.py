import argparse

PROMPT = """
Summarize the policy document section-by-section.

Requirements:
- Preserve every numbered clause
- Preserve all conditions and approvers
- Do not weaken obligations
- Do not add external HR assumptions
- Include clause references
- If meaning may be lost, quote the clause verbatim
"""

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        policy_text = f.read()

    summary = f"""
POLICY SUMMARY

{PROMPT}

SOURCE DOCUMENT:
{policy_text}
"""

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary written successfully.")

if __name__ == "__main__":
    main()