skills:
  - name: retrieve_documents
    description: Loads all policy documents and indexes them by document name and section.
    input: Paths to policy document text files.
    output: Dictionary mapping document names to their contents.
    error_handling: If a file cannot be loaded, return an error and stop execution.

  - name: answer_question
    description: Searches the loaded policy documents for relevant clauses and returns a single-source answer with citation.
    input: User question and indexed policy documents.
    output: Answer string with document name and section citation OR refusal template.
    error_handling: If the answer cannot be found, return the refusal template.