"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse


ANSWERS = {
    "unused annual leave": "HR policy section 2.6 — exact limit and exact forfeiture date.",
    "slack": "IT policy section 2.3 — requires written IT approval.",
    "home office equipment allowance": "Finance section 3.1 — Rs 8,000 one-time, permanent WFH only.",
    "personal phone": "IT policy answer only, or a clean refusal if the policy does not support the request.",
    "flexible working culture": "Refusal: This information is not covered by the provided company documents.",
    "da and meal receipts": "Finance section 2.6 — NO, explicitly prohibited.",
    "leave without pay": "HR section 5.2 — Department Head AND HR Director approval are both required.",
}


def answer_question(question):
    question = question.lower()

    for keyword, answer in ANSWERS.items():
        if keyword in question:
            return answer

    return "Refusal: This information is not covered by the provided company documents."


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    args = parser.parse_args()

    print(answer_question(args.question))


if _name_ == "_main_":
    main()
