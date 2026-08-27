import argparse

def main():

    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--question", required=True)

    args = parser.parse_args()

    question = args.question.lower()

    if "leave" in question:
        answer = "Employees are allowed leave according to HR leave policy."

    elif "reimbursement" in question:
        answer = "Finance reimbursement policy explains how employees claim expenses."

    elif "acceptable use" in question:
        answer = "IT acceptable use policy explains proper usage of company systems."

    else:
        answer = "Please check the policy documents for more information."

    print("Answer:", answer)


if __name__ == "__main__":
    main()