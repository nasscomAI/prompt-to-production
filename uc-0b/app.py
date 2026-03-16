import argparse

def summarize_text(text):
    sentences = text.split(".")
    summary = ".".join(sentences[:2]).strip()
    return summary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, required=True, help="Input document text")
    args = parser.parse_args()

    summary = summarize_text(args.text)
    print("Summary:")
    print(summary)

if __name__ == "__main__":
    main()