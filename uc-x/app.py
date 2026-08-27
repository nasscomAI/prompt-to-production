"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os


def search_documents(question, docs_path):
    question = question.lower()

    for filename in os.listdir(docs_path):
        filepath = os.path.join(docs_path, filename)

        if not filename.endswith(".txt"):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().lower()

            if any(word in text for word in question.split()):
                return filename, text

    return None, None


def extract_answer(question, document_text):
    for line in document_text.splitlines():
        line_lower = line.lower()

        if any(word in line_lower for word in question.split()):
            return line.strip()

    return None


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--question", required=True)
    parser.add_argument("--docs", required=True)

    args = parser.parse_args()

    filename, text = search_documents(args.question, args.docs)

    if not filename:
        print("INFORMATION_NOT_FOUND")
        return

    answer = extract_answer(args.question, text)

    if not answer:
        print("INFORMATION_NOT_FOUND")
        return

    print(f"Answer: {answer}")
    print(f"Source: {filename}")


if __name__ == "__main__":
    main()
