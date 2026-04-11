def summarize(text):
    sentences = text.split(".")
    summary = sentences[0] if sentences else text
    return summary.strip()

if __name__ == "__main__":
    text = input("Enter text: ")
    print("Summary:", summarize(text))