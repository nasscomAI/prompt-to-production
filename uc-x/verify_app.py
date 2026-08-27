import subprocess
import os

def run_test(question):
    process = subprocess.Popen(
        ['python', 'app.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd='c:/Users/dileesh.k/Documents/GitHub/prompt-to-production/uc-x'
    )
    # Send the question and then 'exit'
    stdout, stderr = process.communicate(input=f"{question}\nexit\n")
    return stdout

test_cases = [
    ("Can I carry forward unused annual leave?", "policy_hr_leave.txt, Section 2.6"),
    ("Can I install Slack on my work laptop?", "policy_it_acceptable_use.txt, Section 2.3"),
    ("What is the home office equipment allowance?", "policy_finance_reimbursement.txt, Section 3.1"),
    ("Can I use my personal phone for work files from home?", "policy_it_acceptable_use.txt, Section 3.1"),
    ("What is the company view on flexible working culture?", "This question is not covered"),
    ("Can I claim DA and meal receipts on the same day?", "policy_finance_reimbursement.txt, Section 2.6"),
    ("Who approves leave without pay?", "policy_hr_leave.txt, Section 5.2")
]

print("Running UC-X Verification Tests...\n")
for question, expected in test_cases:
    print(f"Testing: {question}")
    output = run_test(question)
    if expected.lower() in output.lower():
        print("Result: PASS\n")
    else:
        print(f"Result: FAIL")
        print(f"Expected to find: {expected}")
        print(f"Actual output snippet: {output[-500:]}\n")
