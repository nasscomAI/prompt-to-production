skills:
  - name: retrieve_documents
    description: Find the most relevant document based on user question
    input: question string
    output: document name and content
    error_handling: return None if no matching document found

  - name: answer_question
    description: Extract answer from document based on question
    input: question string and document text
    output: answer string
    error_handling: return "Not found in documents" if answer not found