import argparse


def retrieve_policy(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return "EMPTY_DOCUMENT"
            return content
    except FileNotFoundError:
        return "FILE_NOT_FOUND"


def summarize_policy(text):
    if text in ["EMPTY_DOCUMENT", "FILE_NOT_FOUND"]:
        return text

    lines = text.split("\n")
    summary = []
    current_clause = ""

    for line in lines:
        line = line.strip()

        # Detect clause number (e.g., 2.3, 3.4)
        if line and line[0].isdigit():
            if current_clause:
                summary.append(current_clause.strip())
            current_clause = line
        else:
            current_clause += " " + line

    if current_clause:
        summary.append(current_clause.strip())

    return "\n".join(summary)


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