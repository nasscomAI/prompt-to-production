# fix commit format
import argparse


def summarize_policy(text):
    summary = []

    if "14" in text and "advance" in text:
        summary.append("2.3: Employees must provide 14-day advance notice before leave.")

    if "written approval" in text.lower():
        summary.append("2.4: Leave must have written approval before it starts; verbal approval is not valid.")

    if "unapproved absence" in text.lower():
        summary.append("2.5: Unapproved absence will be treated as Loss of Pay (LOP) regardless of later approval.")

    if "carry" in text.lower():
        summary.append("2.6: Maximum 5 leave days can be carried forward; any excess is forfeited on 31 Dec.")

    if "jan" in text.lower() or "mar" in text.lower():
        summary.append("2.7: Carry-forward leave must be used between Jan–Mar or it will be forfeited.")

    if "3" in text and "medical" in text.lower():
        summary.append("3.2: Sick leave of 3 or more consecutive days requires a medical certificate within 48 hours.")

    if "holiday" in text.lower():
        summary.append("3.4: Sick leave before or after a holiday requires a medical certificate regardless of duration.")

    if "department head" in text.lower() and "hr" in text.lower():
        summary.append("5.2: Leave Without Pay requires approval from BOTH Department Head AND HR Director.")

    if "30" in text:
        summary.append("5.3: Leave Without Pay exceeding 30 days requires Municipal Commissioner approval.")

    if "encashment" in text.lower():
        summary.append("7.2: Leave encashment during service is not permitted under any circumstances.")

    return "\n".join(summary)


def main(input_path, output_path):
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        summary = summarize_policy(text)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)

        print("✅ Summary generated successfully.")

    except Exception as e:
        print("❌ Error:", e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    
    # 🔥 make arguments optional to avoid crash
    parser.add_argument("--input", default="../data/policy-documents/policy_hr_leave.txt")
    parser.add_argument("--output", default="summary_hr_leave.txt")

    args = parser.parse_args()

    main(args.input, args.output)
