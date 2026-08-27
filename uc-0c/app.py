import argparse

def answer_question(policy_text, question):
    if question.lower() in policy_text.lower():
        return "Relevant information found in the policy."
    else:
        return "Answer not found in policy"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=str, required=True, help="Policy text")
    parser.add_argument("--question", type=str, required=True, help="Question")
    args = parser.parse_args()

    answer = answer_question(args.policy, args.question)
    print("Answer:")
    print(answer)

if __name__ == "__main__":
    main()
