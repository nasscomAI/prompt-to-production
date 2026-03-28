"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

def answer_question(text, question):
    if "leave" in question.lower():
        return "Employees are entitled to leave as per company policy."
    else:
        return "Answer not found in document."

def main(input_file, output_file, question):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    answer = answer_question(text, question)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(answer)

    print("Answer saved to", output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--question", required=True)

    args = parser.parse_args()

    main(args.input, args.output, args.question)