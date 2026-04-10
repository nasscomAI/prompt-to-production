skills:
  - name: retrieve_documents
    description: Loads and indexes all policy documents by filename and numbered section.
    input: Base directory path containing policy text files.
    output: Dictionary of document names to section maps.
    error_handling: Raises file errors if required policy files are missing.

  - name: answer_question
    description: Returns single-source cited answer or strict refusal template.
    input: Indexed document dictionary and user question string.
    output: Answer text with source citation, or refusal template text.
    error_handling: Returns refusal template when query is ambiguous, unsupported, or cross-document dependent.
