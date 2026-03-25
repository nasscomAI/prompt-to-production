import argparse

def retrieve_policy(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        raise Exception("Error: File not found or unreadable")

def summarize_policy(text):
    sentences = text.split(".")
    summary = ". ".join(sentences[:5])
    return summary.strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)
    summary = summarize_policy(policy_text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print("✅ Summary generated successfully!")

if __name__ == "__main__":
    main()