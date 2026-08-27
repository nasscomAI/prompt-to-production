import argparse

def load_document(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def answer_question(document, question):
    if not document:
        return "INSUFFICIENT_INFORMATION"

    doc_lower = document.lower()
    question_lower = question.lower()

    # Simple keyword matching
    for sentence in document.split("."):
        if any(word in sentence.lower() for word in question_lower.split()):
            return sentence.strip()

    return "INSUFFICIENT_INFORMATION"


def main():
    parser = argparse.ArgumentParser(description="UC-X QA System")
    parser.add_argument("--doc", required=True, help="Path to document")
    parser.add_argument("--question", required=True, help="Question to answer")
    args = parser.parse_args()

    document = load_document(args.doc)
    answer = answer_question(document, args.question)

    print("Answer:")
    print(answer)


if __name__ == "__main__":
    main()