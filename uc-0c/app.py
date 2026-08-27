import os

def process_documents(folder="../data/policy-documents"):
    """
    Process documents and calculate word count
    """

    results = []

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)

        try:
            with open(filepath, "r") as file:
                content = file.read()

            word_count = len(content.split())

            results.append({
                "file": filename,
                "word_count": word_count
            })

        except Exception:
            results.append({
                "file": filename,
                "word_count": 0
            })

    return results


if __name__ == "__main__":

    docs = process_documents()

    for doc in docs:
        print(doc["file"], "->", doc["word_count"], "words")
