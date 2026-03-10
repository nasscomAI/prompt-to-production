import os
import csv

documents_folder = "data/policy-documents/"
test_file = "data/city-test-files/test_pune.csv"
output_file = "results_ucx.txt"

def answer_query(document_text, query):
    # Placeholder: in real scenario, implement actual QA logic
    if query.lower() in document_text.lower():
        return "Answer found in document"
    else:
        return "NEEDS_REVIEW"

with open(test_file, newline='', encoding='utf-8') as csv_in, \
     open(output_file, 'w', encoding='utf-8') as out_file:

    reader = csv.DictReader(csv_in)

    for row in reader:
        query = row.get("question", "")
        # For simplicity, just check the first document
        doc_file = os.listdir(documents_folder)[0]
        with open(os.path.join(documents_folder, doc_file), 'r', encoding='utf-8') as f:
            doc_text = f.read()
            answer = answer_query(doc_text, query)
            out_file.write(f"Query: {query}\nAnswer: {answer}\n\n")

print(f"Document query completed. Results saved to {output_file}")