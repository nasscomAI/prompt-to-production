skills:
  - name: load_document
    description: Loads and reads the content of a document from a file.
    input: File path as a string.
    output: Document content as a string or None if failed.
    error_handling: Returns None if file cannot be read or encoding fails.

  - name: answer_question
    description: Extracts an answer from the document based on the user’s question.
    input: Document text (string) and question (string).
    output: A string answer or "INSUFFICIENT_INFORMATION".
    error_handling: If no relevant information is found, returns "INSUFFICIENT_INFORMATION" instead of guessing.
