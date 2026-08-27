import argparse
import os

def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Input file not found")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError("File is empty")

    # Split into lines (simple structure)
    sections = content.split("\n")
    return sections


def summarize_policy(sections):
    summary = []
    needs_review = False

    for i, line in enumerate(sections, start=1):
        line = line.strip()
        if not line:
            continue

        # Simple rule-based summarization
        summary_line = f"{i}. {line}"

        # If too long → mark review
        if len(line.split()) > 25:
            needs_review = True

        summary.append(summary_line)

    if needs_review:
        summary.append("\n[NEEDS_REVIEW: Some clauses may be too long to safely summarize]")

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input policy file path")
    parser.add_argument("--output", required=True, help="Output summary file path")

    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print("✅ Summary generated successfully")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()