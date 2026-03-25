import argparse

def summarize_policy(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    summary = []
    current_section = None

    for line in lines:
        if "PURPOSE AND SCOPE" in line:
            current_section = "Purpose and Scope"
            summary.append("\nPurpose and Scope:")
        elif "ANNUAL LEAVE" in line:
            current_section = "Annual Leave"
            summary.append("\nAnnual Leave:")
        elif "SICK LEAVE" in line:
            current_section = "Sick Leave"
            summary.append("\nSick Leave:")
        elif "MATERNITY AND PATERNITY LEAVE" in line:
            current_section = "Maternity and Paternity Leave"
            summary.append("\nMaternity and Paternity Leave:")
        elif "LEAVE WITHOUT PAY" in line:
            current_section = "Leave Without Pay")
            summary.append("\nLeave Without Pay:")
        elif "PUBLIC HOLIDAYS" in line:
            current_section = "Public Holidays"
            summary.append("\nPublic Holidays:")
        elif "LEAVE ENCASHMENT" in line:
            current_section = "Leave Encashment"
            summary.append("\nLeave Encashment:")
        elif "GRIEVANCES" in line:
            current_section = "Grievances"
            summary.append("\nGrievances:")
        elif line[0].isdigit():
            summary.append(f"- {line}")

    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as infile:
        text = infile.read()

    result = summarize_policy(text)

    with open(args.output, "w", encoding="utf-8") as outfile:
        outfile.write(result)

    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
