import argparse


def load_documents():
    docs = {}

    files = {
        "hr": "../data/policy-documents/policy_hr_leave.txt",
        "it": "../data/policy-documents/policy_it_acceptable_use.txt",
        "finance": "../data/policy-documents/policy_finance_reimbursement.txt"
    }

    for name, path in files.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                # remove empty lines
                docs[name] = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Error loading {name}: {e}")
            docs[name] = []

    return docs


def is_valid_line(line):
    """Skip titles and useless lines"""
    if line.isupper():  # skip titles like "EMPLOYEE LEAVE POLICY"
        return False
    if len(line.split()) < 4:  # skip very short lines
        return False
    return True


def ask_question(docs, question):
    question_words = question.lower().split()

    best_doc = None
    max_matches = 0

    # 🔥 Step 1: Find best matching document
    for doc_name, lines in docs.items():
        match_count = 0

        for line in lines:
            if any(word in line.lower() for word in question_words):
                match_count += 1

        if match_count > max_matches:
            max_matches = match_count
            best_doc = doc_name

    # 🔥 Step 2: Return meaningful line from that document
    if best_doc and docs[best_doc]:

        # Try to find best matching meaningful line
        for line in docs[best_doc]:
            if not is_valid_line(line):
                continue

            if any(word in line.lower() for word in question_words):
                return f"[Source: {best_doc}] {line}"

        # ✅ fallback → return first meaningful line
        for line in docs[best_doc]:
            if is_valid_line(line):
                return f"[Source: {best_doc}] {line}"

    return "No relevant answer found"


def main():
    parser = argparse.ArgumentParser(description="Ask questions from policy documents")
    parser.add_argument("--question", type=str, required=True, help="Enter your question")

    args = parser.parse_args()

    docs = load_documents()
    answer = ask_question(docs, args.question)

    print(answer)


if __name__ == "__main__":
    main()