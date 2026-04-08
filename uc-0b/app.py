"""
UC-0B app.py — Simple working implementation
Processes a text input and generates structured output.
"""

import argparse


def process_input(text):
    text_lower = text.lower()

    category = "General"
    priority = "Standard"
    reason = ""
    flag = ""

    # Example simple rules
    if "error" in text_lower or "fail" in text_lower:
        category = "System Issue"

    elif "slow" in text_lower or "delay" in text_lower:
        category = "Performance"

    elif "login" in text_lower or "password" in text_lower:
        category = "Authentication"

    # Priority detection
    if "urgent" in text_lower or "critical" in text_lower:
        priority = "Urgent"

    # Reason generation
    reason = f'Classification based on input text containing keywords.'

    return category, priority, reason, flag


def main():
    parser = argparse.ArgumentParser(description="UC-0B Application Processor")
    parser.add_argument("--text", required=True, help="Input text to process")

    args = parser.parse_args()

    category, priority, reason, flag = process_input(args.text)

    print("Result:")
    print(f"Category: {category}")
    print(f"Priority: {priority}")
    print(f"Reason: {reason}")
    print(f"Flag: {flag}")


if __name__ == "__main__":
    main()
