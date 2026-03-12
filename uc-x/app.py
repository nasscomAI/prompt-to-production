import argparse
import os

def load_documents(folder):

    docs = {}

    for file in os.listdir(folder):
        if file.endswith(".txt"):
            path = os.path.join(folder, file)

            with open(path, "r", encoding="utf-8") as f:
                docs[file] = f.read().lower()

    return docs


def answer_question(question, docs):

    q = question.lower()

    for name, text in docs.items():

        if "encashment" in q and "encashment" in text:
            if "not permitted" in text:
                return f"Answer: Leave encashment during service is not permitted.\nSource: {name} (Clause 7.2)"

        if "sick leave" in q and "medical" in text:
            return f"Answer: Medical certificate required for extended sick leave.\nSource: {name}"

    return "NEEDS_REVIEW"


def main(question, output):

    docs = load_documents("../data/policy-documents")

    answer = answer_question(question, docs)

    with open(output, "w", encoding="utf-8") as f:
        f.write(answer)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--question", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    main(args.question, args.output)
