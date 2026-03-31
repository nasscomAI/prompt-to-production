skills:
  - name: retrieve_documents
    description: Loads all policy documents and prepares them for search.
    input: Folder path containing policy documents.
    output: Dictionary of document names mapped to their content.
    error_handling: If any file is missing, skip it and continue with available documents.

  - name: answer_question
    description: Finds answer in exactly one document and returns it with citation.
    input: Query string and loaded documents.
    output: Answer string with document name and section OR refusal message.
    error_handling: If multiple documents match or no match found, return refusal template.