# UC-X: Ask My Documents
# Reads multiple TXT files and outputs answers.csv
# Ensures single-source attribution

import csv
import glob

def read_documents(folder_path):
    docs = []
    files = glob.glob(f"{folder_path}/*.txt")  # get all TXT files
    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            text = file.read()
            doc_id = f.split("/")[-1]  # file name as doc_id
            docs.append({"doc_id": doc_id, "text": text})
    return docs

def answer_question(docs, question):
    answers = []
    for doc in docs:
        if question.lower() in doc["text"].lower():
            answers.append({"doc_id": doc["doc_id"], "answer": doc["text"]})
    return answers

def save_results(answers, output_file):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["doc_id", "answer"])
        for ans in answers:
            writer.writerow([ans["doc_id"], ans["answer"]])

if __name__ == "__main__":
    folder_path = "../data/policy-documents"  # your TXT files folder
    output_file = "answers.csv"
    question = "leave policy"  # example question

    documents = read_documents(folder_path)
    answers = answer_question(documents, question)
    save_results(answers, output_file)

    print(f"UC-X processing complete. Output saved to {output_file}")