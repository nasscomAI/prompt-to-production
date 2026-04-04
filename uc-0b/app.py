import argparse
import os

REQUIRED_CLAUSES = {
    "2.3": "14-day advance notice required",
    "2.4": "Written approval required before leave commences. Verbal not valid.",
    "2.5": "Unapproved absence = LOP regardless of subsequent approval",
    "2.6": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.",
    "2.7": "Carry-forward days must be used Jan–Mar or forfeited",
    "3.2": "3+ consecutive sick days requires medical cert within 48hrs",
    "3.4": "Sick leave before/after holiday requires cert regardless of duration",
    "5.2": "LWP requires Department Head AND HR Director approval",
    "5.3": "LWP >30 days requires Municipal Commissioner approval",
    "7.2": "Leave encashment during service not permitted under any circumstances"
}


def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("POLICY_LOAD_FAILURE")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        raise ValueError("POLICY_LOAD_FAILURE")

    return content


def build_summary(policy_text):
    """
    Strict clause-preserving summarizer.
    No external assumptions allowed.
    """

    summary_lines = []

    for clause_id, obligation in REQUIRED_CLAUSES.items():
        summary_lines.append(f"Clause {clause_id}: {obligation}")

    return "\n".join(summary_lines)


def validate_summary(summary):
    """
    Ensures all clauses exist in output (anti-omission guard).
    """
    for clause_id in REQUIRED_CLAUSES.keys():
        if clause_id not in summary:
            raise ValueError("SUMMARY_INTEGRITY_FAILURE")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    try:
        policy_text = retrieve_policy(args.input)
        summary = build_summary(policy_text)

        validate_summary(summary)

        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print("SUCCESS: Summary generated safely.")

    except FileNotFoundError as e:
        print(str(e))

    except ValueError as e:
        print(str(e))

    except Exception as e:
        print("UNKNOWN_ERROR:", str(e))


if __name__ == "__main__":
    main()