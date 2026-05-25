import argparse
import re


def retrieve_policy(input_file):
    with open(input_file, "r", encoding="utf-8") as file:
        content = file.read()

    pattern = r'(\d+\.\d+)(.*?)(?=\n\d+\.\d+|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)

    sections = []

    for clause, text in matches:
        cleaned_text = text.strip().replace("\n", " ")
        sections.append({
            "clause": clause,
            "text": cleaned_text
        })

    return sections


def summarize_policy(sections):
    summary = []

    for section in sections:
        clause = section["clause"]
        text = section["text"]

        important_words = [
            "must",
            "requires",
            "required",
            "not permitted",
            "forfeited",
            "approval"
        ]

        preserve_verbatim = any(word in text.lower() for word in important_words)

        if preserve_verbatim:
            summary.append(f"Clause {clause}: {text}")
        else:
            shortened = text[:180]
            summary.append(f"Clause {clause}: {shortened}")

    return "\n\n".join(summary)


def save_summary(output_file, summary):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    sections = retrieve_policy(args.input)

    summary = summarize_policy(sections)

    save_summary(args.output, summary)

    print(f"Summary saved to {args.output}")