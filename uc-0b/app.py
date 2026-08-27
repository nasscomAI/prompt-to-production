import argparse

def summarize_policy(text):
    lines = text.split("\n")
    summary = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Keep strong policy language
        if any(word in line.lower() for word in ["must", "requires", "not permitted", "shall"]):
            summary.append(f"- {line}")
        else:
            # still include but mark as general
            summary.append(f"- {line}")

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    summary = summarize_policy(text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary generated successfully!")


if __name__ == "__main__":
    main()