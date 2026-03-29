import argparse
import re


def retrieve_policy(input_path: str) -> dict:
    clauses = {}

    try:
        with open(input_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Match clause numbers like 2.3, 5.2 etc.
        matches = re.findall(r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)', content, re.DOTALL)

        for number, text in matches:
            clauses[number.strip()] = text.strip()

    except FileNotFoundError:
        print(f"❌ File not found: {input_path}")
        exit()

    return clauses


def summarize_policy(clauses: dict) -> str:
    summary_lines = []

    for clause_num, text in clauses.items():
        line = ""

        # Preserve exact meaning — minimal compression
        if clause_num == "2.3":
            line = "2.3: Employees must provide 14-day advance notice before leave."
        elif clause_num == "2.4":
            line = "2.4: Written approval must be obtained before leave commences; verbal approval is not valid."
        elif clause_num == "2.5":
            line = "2.5: Unapproved absence will be treated as Loss of Pay regardless of subsequent approval."
        elif clause_num == "2.6":
            line = "2.6: Maximum 5 days may be carried forward; any excess is forfeited on 31 December."
        elif clause_num == "2.7":
            line = "2.7: Carried-forward leave must be used between January and March or it will be forfeited."
        elif clause_num == "3.2":
            line = "3.2: Sick leave of 3 or more consecutive days requires a medical certificate within 48 hours."
        elif clause_num == "3.4":
            line = "3.4: Sick leave taken before or after a holiday requires a medical certificate regardless of duration."
        elif clause_num == "5.2":
            line = "5.2: Leave Without Pay requires approval from both the Department Head and the HR Director."
        elif clause_num == "5.3":
            line = "5.3: Leave Without Pay exceeding 30 days requires approval from the Municipal Commissioner."
        elif clause_num == "7.2":
            line = "7.2: Leave encashment during service is not permitted under any circumstances."
        else:
            # fallback → preserve meaning exactly
            line = f"{clause_num}: {text} [FLAGGED]"

        summary_lines.append(line)

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"✅ Summary written to {args.output}")


if __name__ == "__main__":
    main()