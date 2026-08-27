# skills.md — UC-X Ask My Documents

skills:
  - name: load_documents
    description: Loads all policy documents and returns their content.
    input: List of file paths (list)
    output: Dictionary with document names as keys and content as values
    error_handling: If file not found, raise FileNotFoundError. If file is empty, return empty string.

  - name: answer_question
    description: Answers a user question based ONLY on the loaded policy documents.
    input: Question string (str), documents dictionary (dict)
    output: Answer string or refusal template
    error_handling: If question not covered, return exact refusal template. If ambiguous, refuse.
