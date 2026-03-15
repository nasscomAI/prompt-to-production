import os

def summarize_document(text):
    """
    Simple summarizer that returns the first 3 sentences
    """
    sentences = text.split(".")
    summary = ".".join(sentences[:3])
    return summary.strip() + "."


def process_documents(folder="../data/policy-documents"):
    """
    Process all documents in the folder and create summaries
    """

    results = []

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)

        try:
            with open(filepath, "r") as file:
                content = file.read()

            summary = summarize_document(content)

            results.append({
                "file": filename,
                "summary": summary
            })

        except Exception:
            results.append({
                "file": filename,
                "summary": "Error processing file"
            })

    return results


if __name__ == "__main__":

    summaries = process_documents()

    for item in summaries:
        print("\nFile:", item["file"])
        print("Summary:", item["summary"])
