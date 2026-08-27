"""
UC-0B — Summary That Changes Meaning
Generate a summary from the HR leave policy document.
"""

INPUT_FILE = "../data/policy-documents/policy_hr_leave.txt"
OUTPUT_FILE = "summary_hr_leave.txt"


def summarize_policy(text):
    sentences = text.split(".")
    summary = ". ".join(sentences[:5])
    return summary


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    summary = summarize_policy(text)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary created:", OUTPUT_FILE)


if __name__ == "__main__":
    main()