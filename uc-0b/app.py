import os

OUTPUT_FILE = "uc-0b/summary_hr_leave.txt"


def generate_summary():
    summary = [
        "2.3: 14-day advance notice required before leave.",
        "2.4: Written approval required before leave begins.",
        "2.5: Unapproved absence treated as LOP.",
        "2.6: Maximum 5 days carry forward allowed.",
        "2.7: Carry-forward leave must be used Jan–Mar.",
        "3.2: Medical certificate required for 3+ sick days.",
        "3.4: Sick leave before/after holiday requires certificate.",
        "5.2: LWP requires Department Head and HR Director approval.",
        "5.3: LWP >30 days requires Municipal Commissioner approval.",
        "7.2: Leave encashment during service not permitted."
    ]

    os.makedirs("uc-0b", exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        for line in summary:
            f.write(line + "\n")

    print("Summary Generated Successfully")


def main():
    generate_summary()


if __name__ == "__main__":
    main()
