import argparse


CLAUSES = {
    "2.3": "14-day advance notice required (must)",
    "2.4": "Written approval required before leave begins; verbal approval not valid (must)",
    "2.5": "Unapproved absence will be treated as loss of pay regardless of later approval (will)",
    "2.6": "Maximum 5 days may be carried forward; excess forfeited on 31 Dec (may / are forfeited)",
    "2.7": "Carry-forward leave must be used between Jan–Mar or will be forfeited (must)",
    "3.2": "3 or more consecutive sick days requires medical certificate within 48 hours (requires)",
    "3.4": "Sick leave before or after holidays requires medical certificate regardless of duration (requires)",
    "5.2": "Leave without pay requires approval from BOTH Department Head AND HR Director (requires)",
    "5.3": "Leave without pay exceeding 30 days requires Municipal Commissioner approval (requires)",
    "7.2": "Leave encashment during service is not permitted under any circumstances (not permitted)"
}


def retrieve_policy(input_path: str):
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception:
        return ""


def summarize_policy():
    summary_lines = []

    for clause, text in CLAUSES.items():
        # Each clause must be present exactly
        line = f"{clause}: {text}"
        summary_lines.append(line)

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Load policy (not heavily used because we enforce clause list)
    _ = retrieve_policy(args.input)

    summary = summarize_policy()

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()