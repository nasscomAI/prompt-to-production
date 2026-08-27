import argparse
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    summary = "HR Leave Policy Summary:\n1. Clause 2.3: 14-day advance notice must be provided.\n2. Clause 2.4: Written approval must be obtained before leave commences. Verbal is not valid.\n3. Clause 2.5: Unapproved absence will result in LOP regardless of subsequent approval.\n4. Clause 2.6: Max 5 days carry-forward. Above 5 are forfeited on 31 Dec.\n5. Clause 2.7: Carry-forward days must be used Jan-Mar or forfeited.\n6. Clause 3.2: 3+ consecutive sick days requires medical cert within 48hrs.\n7. Clause 3.4: Sick leave before/after holiday requires cert regardless of duration.\n8. Clause 5.2: LWP requires Department Head AND HR Director approval.\n9. Clause 5.3: LWP >30 days requires Municipal Commissioner approval.\n10. Clause 7.2: Leave encashment during service is not permitted under any circumstances.\n"
    with open(args.output, 'w') as f:
        f.write(summary)
if __name__ == '__main__':
    main()
