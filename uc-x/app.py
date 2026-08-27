"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

def main():
    parser = argparse.ArgumentParser(description="UC-X Document Q&A")
    parser.add_argument("--question", required=True, help="User question to answer")
    parser.add_argument("--document", required=True, help="Path to input document (e.g., policy_hr_leave.txt)")
    parser.add_argument("--output", required=True, help="Path to write answer output (e.g., answer.txt)")
    args = parser.parse_args()

    try:
        with open(args.document, encoding="utf-8") as infile:
            document_text = infile.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    answer = answer_question(args.question, document_text, args.document)

    try:
        with open(args.output, "w", encoding="utf-8") as outfile:
            outfile.write(answer)
        print(f"Answer written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")


def answer_question(question: str, document_text: str, document_path: str) -> str:
    """
    Answers a user question by searching the provided document and extracting relevant information with citation.
    This is a placeholder implementation. Replace with actual logic as needed.
    """
    if not document_text.strip():
        return f"[ERROR] Document {document_path} is empty or unreadable."
    # Placeholder: just echo the question and cite the document
    return f"[ANSWER START]\nQuestion: {question}\n(Document: {document_path})\n[ANSWER END]"

if __name__ == "__main__":
    main()
