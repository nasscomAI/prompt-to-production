skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number
    input: No input required (loads from hardcoded paths)
    output: Indexed dictionary of policy documents keyed by document name and section number
    error_handling: Returns empty index and reports error if any policy file is missing, unreadable, or not found at the expected path

  - name: answer_question
    description: Searches indexed documents for the answer to a user question, returns answer from a single source document with citation OR the refusal template
    input: User question as plain text string; indexed policy documents
    output: Answer string with source document name + section number citation, or the exact refusal template
    error_handling: If question matches no document content, returns the refusal template verbatim. If question matches multiple documents, must pick one single source or return the refusal template rather than blending.
