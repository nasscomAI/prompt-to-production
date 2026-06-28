skills:
  - name: retrieve_documents
    description: Loads policy documents and indexes them by document and section.
    input: Policy document file paths.
    output: Indexed document collection.
    error_handling: Returns an error if a document cannot be loaded.

  - name: answer_question
    description: Answers questions using one source document and section citation.
    input: User question and indexed policy documents.
    output: Single-source answer with citation or refusal template.
    error_handling: Uses refusal template when information is not found.