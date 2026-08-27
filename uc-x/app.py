import argparse

def load_document(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().lower()
    except Exception as e:
        print("Error loading file:", e)
        return ""

def ask_question(content):
    while True:
        query = input("\nAsk question (type 'exit' to quit): ").lower()

        if query == "exit":
            break

        if not query.strip():
            print("Empty question ❌")
            continue

        # simple search logic
        if query in content:
            print("✅ Answer found in document")
        else:
            print("❌ No answer found")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to policy document")

    args = parser.parse_args()

    content = load_document(args.input)

    if content:
        print("Document loaded successfully ✅")
        ask_question(content)

if __name__ == "__main__":
    main()