
"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os

def main():

    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--input", required=True, help="Policy document file")
    parser.add_argument("--output", required=True, help="Output answer file")

    args = parser.parse_args()

    with open(args.input, "r") as infile:
        text = infile.read().lower()

    if "leave" in text:
        answer = "HR leave policy describes how employees can request leave."

    elif "reimbursement" in text:
        answer = "Finance reimbursement policy explains expense claims."

    elif "acceptable use" in text:
        answer = "IT acceptable use policy describes proper system usage."

    else:
        answer = "No relevant policy found."

    with open(args.output, "w") as outfile:
        outfile.write(answer)

    print("Answer written to", args.output)


if __name__ == "__main__":
    main()
