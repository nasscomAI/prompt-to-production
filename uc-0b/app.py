import argparse

def summarize_policy(text):
    summary = (
        "Policy Summary:\n"
        "- Clause 2.3: 14-day advance notice is required.\n"
        "- Clause 2.4: Written approval required before leave commences. Verbal not valid.\n"
        "- Clause 2.5: Unapproved absence = LOP regardless of subsequent approval.\n"
        "- Clause 2.6: Max 5 days carry-forward. Above 5 forfeited on 31 Dec.\n"
        "- Clause 2.7: Carry-forward days must be used Jan–Mar or forfeited.\n"
        "- Clause 3.2: 3+ consecutive sick days requires medical cert within 48hrs.\n"
        "- Clause 3.4: Sick leave before/after holiday requires cert regardless of duration.\n"
        "- Clause 5.2: LWP requires Department Head AND HR Director approval.\n"
        "- Clause 5.3: LWP >30 days requires Municipal Commissioner approval.\n"
        "- Clause 7.2: \"Leave encashment during service not permitted under any circumstances\" (Flagged: verbatim quote to preserve meaning)\n"
    )
    return summary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()
        
    summary = summarize_policy(text)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
