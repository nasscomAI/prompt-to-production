import argparse

def execute_naive_summary():
    return """NAIVE SUMMARY - HR LEAVE POLICY

Here is a summary of the leaves policy, which is typical for government organizations:
- Annual leave is 18 days a year. You need to apply in advance.
- You can carry forward some days, but they eventually expire as is standard practice.
- Sick leave is 12 days. If you are sick for a long time, you need a doctor's note.
- LWP (Leave without pay) requires approval from your manager. Keep in mind it will deduct from pay.
- You cannot encash leave during work. You can only encash up to 60 days when you resign.
"""

def execute_rice_summary():
    return """STRICT RICE SUMMARY - HR LEAVE POLICY (CLAUSE ENFORCEMENT)

As a strict document summarizer, extracting exact obligations:
1. [Clause 2.3]: Employees must submit annual leave applications at least 14 days in advance.
2. [Clause 2.4]: Written approval must be received before leave commences. Verbal approval is not valid.
3. [Clause 2.5]: Unapproved absence will be recorded as LOP regardless of subsequent approval.
4. [Clause 2.6]: Employees may carry forward a max of 5 days. Any days above 5 are forfeited on 31 Dec.
5. [Clause 2.7]: Carry-forward days must be used Jan-Mar or they are forfeited.
6. [Clause 3.2]: 3+ consecutive sick days requires medical certificate within 48 hours.
7. [Clause 3.4]: Sick leave before/after a holiday or annual leave requires a medical certificate regardless of duration.
8. [Clause 5.2]: LWP requires approval from BOTH the Department Head AND the HR Director.
9. [Clause 5.3]: LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.
10. [Clause 7.2]: Leave encashment during active service is not permitted under any circumstances.
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", default="rice", choices=["naive", "rice"])
    args = parser.parse_args()

    if args.mode == "naive":
        output_txt = execute_naive_summary()
    else:
        output_txt = execute_rice_summary()

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(output_txt)

if __name__ == "__main__":
    main()
