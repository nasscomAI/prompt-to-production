import csv
import os

def read_documents(files):
    docs = {}
    for file in files:
        try:
            if file.endswith(".txt"):
                with open(file, "r", encoding="utf-8") as f:
                    docs[file] = f.read()
            elif file.endswith(".csv"):
                with open(file, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    docs[file] = list(reader)
        except Exception:
            docs[file] = None
    return docs

def process_query(query, docs):
    for file, content in docs.items():
        if not content:
            continue
        if isinstance(content, str):
            if query.lower() in content.lower():
                return f"Found in {file}: {query}"
        elif isinstance(content, list):
            for row in content:
                if any(query.lower() in str(v).lower() for v in row.values()):
                    return f"Found in {file}: {row}"
    return "Cannot determine"

def write_answer(answer, output_file):
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(answer)
        return "OK"
    except Exception:
        return "FAILED"

if __name__ == "__main__":
    files = [
        "data/policy-documents/policy_hr_leave.txt",
        "data/policy-documents/policy_it_acceptable_use.txt",
        "data/policy-documents/policy_finance_reimbursement.txt"
    ]
    query = "leave policy"
    output_file = "ucx_answer.txt"

    docs = read_documents(files)
    answer = process_query(query, docs)
    flag = write_answer(answer, output_file)

    print(f"Query processed. Flag: {flag}")