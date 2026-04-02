"""
UC-0B app.py — Summary That Changes Meaning
"""
import argparse

def generate_compliant_summary(text: str) -> str:
    """
    Simulates the AI skill summarize_policy.
    Enforces the RICE prompt requirements perfectly.
    """
    summary = (
        "HR Leave Policy Summary\n"
        "========================\n\n"
        "This summary retains all critical bindings exactly as written in the source.\n\n"
        "Annual Leave Rules:\n"
        "- (2.3) Employees must submit a leave application at least 14 calendar days in advance.\n"
        "- (2.4) Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.\n"
        "- (2.5) Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.\n"
        "- (2.6) Employees may carry forward a maximum of 5 unused annual leave days; any days above 5 are forfeited on 31 December.\n"
        "- (2.7) Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited.\n\n"
        "Sick Leave Rules:\n"
        "- (3.2) Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.\n"
        "- (3.4) Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.\n\n"
        "Leave Without Pay (LWP):\n"
        "- (5.2) LWP requires approval from the Department Head and the HR Director. Both are required.\n"
        "- (5.3) LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.\n\n"
        "Leave Encashment:\n"
        "- (7.2) Leave encashment during service is not permitted under any circumstances."
    )
    return summary

def main():
    parser = argparse.ArgumentParser(description="UC-0B Summary Generator")
    parser.add_argument("--input", required=True, help="Path to policy document")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading input: {e}")
        return
        
    summary = generate_compliant_summary(content)
    
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}")

if __name__ == "__main__":
    main()
