skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number.
    input: List of file paths to policy documents.
    output: Indexed text content parsed by document name and section number.
    error_handling: Halt execution and log an error if a document cannot be read or indexed properly.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer + citation OR refusal template.
    input: User's question string and the retrieved document index.
    output: A specific factual answer including source document name + section number, OR the refusal template.
    error_handling: Return the exact refusal template if the question is ambiguous, requires cross-document blending, or is missing from the documents.
