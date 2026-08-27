def summarize(text):
    # simple summary: first sentence or first 8 words
    words = text.split()
    return " ".join(words[:8])


def main():
    text = input("Enter complaint: ")
    summary = summarize(text)
    print("Summary:", summary)


if __name__ == "__main__":
    main()