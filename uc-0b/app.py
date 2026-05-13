def main():

    # Read policy file
    with open("../data/policy-documents/policy_hr_leave.txt", "r", encoding="utf-8") as f:
        text = f.read()

    # Naive summary
    summary = f"""
You are a compliance policy summarizer.

Rules:
- Include every numbered clause.
- Never remove conditions.
- Never soften obligations.
- Never add external information.
- Preserve approval chains exactly.
- Mention clause numbers in summary.
- If meaning may change, quote the clause exactly.

Policy document:

{text}
"""

    # Save output
    with open("summary_hr_leave.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary generated successfully!")

if __name__ == "__main__":
    main()