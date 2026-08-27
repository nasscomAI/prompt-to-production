import argparse

def load_document(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def answer_question(doc, question):

    q = question.lower()

    if q in doc.lower():
        return "Answer found in the document."

    return "No direct match found in the document."

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--doc", required=True)
    parser.add_argument("--question", required=True)

    args = parser.parse_args()

    doc = load_document(args.doc)

    answer = answer_question(doc, args.question)

    print(answer)

if __name__ == "__main__":
    main()